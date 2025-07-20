#!/usr/bin/env python3
"""
Script to enhance data.jsonl with new fields:
1. target_function_prompt / target_method_prompt
2. Updated body_position 
3. Additional indent fields
"""

import json
import os
import re
from pathlib import Path


def get_file_lines(file_path):
    """Read all lines from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def get_line_indent(line):
    """Get the indentation of a line as a string."""
    return line[:len(line) - len(line.lstrip())]


def find_class_start_line(file_lines, class_name, start_search_line=1):
    """Find the line number where a class definition starts."""
    class_pattern = rf'^\s*class\s+{re.escape(class_name)}\s*[\(\:]'
    
    for i, line in enumerate(file_lines):
        if i >= start_search_line - 1:  # Convert to 0-based index
            if re.match(class_pattern, line):
                return i + 1  # Convert back to 1-based index
    return None


def extract_signature_content(file_lines, signature_position):
    """Extract the content of signature lines."""
    start_line, end_line = signature_position
    signature_lines = file_lines[start_line-1:end_line]  # Convert to 0-based index
    return ''.join(signature_lines).rstrip()


def extract_target_prompt(file_lines, start_line, end_line):
    """Extract target prompt content from file lines."""
    prompt_lines = file_lines[start_line-1:end_line]  # Convert to 0-based index
    return ''.join(prompt_lines).rstrip()


def process_function_sample(sample, source_code_root):
    """Process a function sample to add new fields."""
    print(f"Processing function: {sample['namespace']}")
    
    # Get function name from namespace
    function_name = sample['namespace'].split('.')[-1]
    
    # Read source file
    completion_path = os.path.join(source_code_root, sample['completion_path'])
    file_lines = get_file_lines(completion_path)
    if not file_lines:
        return sample
    
    # Extract signature content
    signature_content = extract_signature_content(file_lines, sample['signature_position'])
    
    # Extract target function prompt (from signature to body start - 1)
    sig_start = sample['signature_position'][0]
    body_start = sample['body_position'][0] 
    target_prompt_end = body_start - 1
    
    target_function_prompt = extract_target_prompt(file_lines, sig_start, target_prompt_end)
    
    # Get function signature indent
    sig_line = file_lines[sample['signature_position'][0] - 1]
    function_indent = get_line_indent(sig_line)
    
    # Update sample with new fields
    sample['target_function_prompt'] = target_function_prompt
    sample['signature_content'] = signature_content
    sample['function_indent'] = function_indent
    
    # Update body_position: from signature start to original body end
    sample['body_position'] = [sample['signature_position'][0], sample['body_position'][1]]
    
    return sample


def process_method_sample(sample, source_code_root):
    """Process a method sample to add new fields."""
    print(f"Processing method: {sample['namespace']}")
    
    # Extract class and method names from namespace
    namespace_parts = sample['namespace'].split('.')
    method_name = namespace_parts[-1]
    class_name = namespace_parts[-2]
    
    # Read source file
    completion_path = os.path.join(source_code_root, sample['completion_path'])
    file_lines = get_file_lines(completion_path)
    if not file_lines:
        return sample
    
    # Find class start line
    class_start_line = find_class_start_line(file_lines, class_name)
    if class_start_line is None:
        print(f"Warning: Could not find class {class_name} in {completion_path}")
        return sample
    
    # Extract signature content
    signature_content = extract_signature_content(file_lines, sample['signature_position'])
    
    # Extract target method prompt (from class start to body start - 1)
    body_start = sample['body_position'][0]
    target_prompt_end = body_start - 1
    
    target_method_prompt = extract_target_prompt(file_lines, class_start_line, target_prompt_end)
    
    # Get class and method indent
    class_line = file_lines[class_start_line - 1]
    class_indent = get_line_indent(class_line)
    
    method_line = file_lines[sample['signature_position'][0] - 1]
    method_indent = get_line_indent(method_line)
    
    # Update sample with new fields
    sample['target_method_prompt'] = target_method_prompt
    sample['signature_content'] = signature_content
    sample['class_indent'] = class_indent
    sample['method_indent'] = method_indent
    
    # Update body_position: from class start to original body end
    sample['body_position'] = [class_start_line, sample['body_position'][1]]
    
    return sample


def enhance_data_file(data_file_path, source_code_root, output_file_path):
    """Enhance the data.jsonl file with new fields."""
    print(f"Enhancing {data_file_path}...")
    
    enhanced_samples = []
    total_samples = 0
    
    with open(data_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                sample = json.loads(line.strip())
                total_samples += 1
                
                if sample['type'] == 'function':
                    enhanced_sample = process_function_sample(sample, source_code_root)
                elif sample['type'] == 'method':
                    enhanced_sample = process_method_sample(sample, source_code_root)
                else:
                    print(f"Unknown type: {sample['type']} at line {line_num}")
                    enhanced_sample = sample
                
                enhanced_samples.append(enhanced_sample)
                
                if line_num % 100 == 0:
                    print(f"Processed {line_num} samples...")
                    
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                # Keep original sample on error
                enhanced_samples.append(sample)
    
    # Write enhanced data to output file
    print(f"Writing enhanced data to {output_file_path}...")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for sample in enhanced_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"Enhancement complete! Processed {total_samples} samples.")
    return enhanced_samples


def main():
    """Main function to run the enhancement process."""
    data_file = "data.jsonl"
    source_code_root = "Source_Code"
    output_file = "data_enhanced.jsonl"
    
    # Check if files exist
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found!")
        return
    
    if not os.path.exists(source_code_root):
        print(f"Error: {source_code_root} directory not found!")
        return
    
    # Run enhancement
    enhanced_samples = enhance_data_file(data_file, source_code_root, output_file)
    
    # Print statistics
    functions = sum(1 for s in enhanced_samples if s['type'] == 'function')
    methods = sum(1 for s in enhanced_samples if s['type'] == 'method')
    
    print(f"\nStatistics:")
    print(f"Total samples: {len(enhanced_samples)}")
    print(f"Functions: {functions}")
    print(f"Methods: {methods}")
    print(f"Enhanced data saved to: {output_file}")


if __name__ == "__main__":
    main()

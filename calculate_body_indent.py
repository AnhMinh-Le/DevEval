import json
import os
from pathlib import Path

def calculate_body_indent(source_code_root, completion_path, body_position):
    """
    Calculate the indentation of function body based on body_position
    
    Args:
        source_code_root: Root path of source code
        completion_path: Relative path to the source file
        body_position: [start_line, end_line] of function body (1-indexed)
    
    Returns:
        String representing the indentation (e.g., "    " for 4 spaces)
    """
    try:
        full_path = os.path.join(source_code_root, completion_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: File not found: {full_path}")
            print(f"  Completion path: {completion_path}")
            return ""
        
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start_line, end_line = body_position
        
        # Convert to 0-indexed
        start_idx = start_line - 1
        end_idx = end_line - 1
        
        if start_idx >= len(lines) or end_idx >= len(lines):
            print(f"Warning: Line numbers out of range for file {completion_path}")
            print(f"  File has {len(lines)} lines, but body_position is {body_position}")
            return ""
        
        # Look for the first non-empty line in the function body
        for i in range(start_idx, min(end_idx + 1, len(lines))):
            line = lines[i]
            if line.strip():  # Non-empty line
                # Calculate indentation
                indent_length = len(line) - len(line.lstrip())
                return ' ' * indent_length
        
        # If no non-empty line found, return empty string
        return ""
        
    except Exception as e:
        print(f"Error processing {completion_path}: {e}")
        print(f"  Body position: {body_position}")
        print(f"  Full path: {os.path.join(source_code_root, completion_path)}")
        return ""

def process_data_file(data_file_path, source_code_root, output_file_path):
    """
    Process data.jsonl file and add body_indent field to each entry
    """
    print(f"Processing {data_file_path}...")
    
    with open(data_file_path, 'r', encoding='utf-8') as f_input, \
         open(output_file_path, 'w', encoding='utf-8') as f_output:
        
        total_processed = 0
        successful = 0
        
        for line_num, line in enumerate(f_input, 1):
            try:
                data = json.loads(line)
                
                # Calculate body indent
                body_indent = calculate_body_indent(
                    source_code_root,
                    data['completion_path'], 
                    data['body_position']
                )
                
                # Add body_indent field
                data['body_indent'] = body_indent
                
                # Write to output file
                json.dump(data, f_output, ensure_ascii=False)
                f_output.write('\n')
                
                total_processed += 1
                if body_indent:
                    successful += 1
                
                if total_processed % 100 == 0:
                    print(f"Processed {total_processed} entries... (Success: {successful})")
                    
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                print(f"  Line content: {line[:100]}...")  # First 100 chars
                continue
    
    print(f"Completed! Processed {total_processed} entries.")
    print(f"Successfully calculated indent for {successful} entries.")
    print(f"Failed or empty indent for {total_processed - successful} entries.")

def main():
    # Configuration
    data_file_path = 'data.jsonl'
    source_code_root = 'Source_Code'
    output_file_path = 'data_new.jsonl'
    
    # Check if input files exist
    if not os.path.exists(data_file_path):
        print(f"Error: {data_file_path} not found!")
        return
    
    if not os.path.exists(source_code_root):
        print(f"Error: {source_code_root} directory not found!")
        return
    
    # Process the data file
    process_data_file(data_file_path, source_code_root, output_file_path)
    
    print(f"Output saved to: {output_file_path}")

if __name__ == '__main__':
    main()

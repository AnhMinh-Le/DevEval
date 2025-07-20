import json
import re

def parse_function_body(response: str, namespace: str, sample_data: dict) -> str:
    """
    Parse function/method body according to the new logic:
    
    For functions:
    - Case 1: If def function_name found, keep the entire block (remove if __name__ == main)
    - Case 2: If no def function_name, concat target_function_prompt + remaining code
    
    For methods:
    - Case 1: If class name found, keep entire block (remove if __name__ == main)
    - Case 2a: If def method_name found, extract method body + concat with target_method_prompt
    - Case 2b: If no def method_name, concat target_method_prompt + remaining code (as method body)
    """
    
    # Extract basic info
    namespace_parts = namespace.split('.')
    sample_type = sample_data.get('type')
    
    if sample_type == 'function':
        function_name = namespace_parts[-1]
        return _parse_function_case(response, function_name, sample_data)
    elif sample_type == 'method':
        method_name = namespace_parts[-1]
        class_name = namespace_parts[-2]
        return _parse_method_case(response, class_name, method_name, sample_data)
    else:
        # Fallback to old behavior
        return _apply_indentation(response, "")


def _parse_function_case(response: str, function_name: str, sample_data: dict) -> str:
    """Handle function parsing cases."""
    # Clean the response
    code_block = _clean_response(response)
    
    # Check if function definition exists
    if _has_function_definition(code_block, function_name):
        # Case 1: Keep entire block, apply function_indent
        final_code = _remove_main_block(code_block)
        return _apply_indentation(final_code, sample_data.get('function_indent', ''))
    else:
        # Case 2: Concat target_function_prompt + code (as function body)
        target_prompt = sample_data.get('target_function_prompt', '')
        function_indent = sample_data.get('function_indent', '')
        body_indent = sample_data.get('body_indent', '    ')
        
        # Apply function_indent to target_prompt
        indented_prompt = _apply_indentation(target_prompt, function_indent)
        
        # Apply body_indent to remaining code (function body)
        indented_body = _apply_indentation(code_block, body_indent)
        
        return indented_prompt + '\n' + indented_body


def _parse_method_case(response: str, class_name: str, method_name: str, sample_data: dict) -> str:
    """Handle method parsing cases."""
    # Clean the response
    code_block = _clean_response(response)
    
    # Check if class definition exists
    if _has_class_definition(code_block, class_name):
        # Case 1: Keep entire block, apply indent
        final_code = _remove_main_block(code_block)
        return _apply_indentation(final_code, sample_data.get('class_indent', ''))
    else:
        # Cases 2a and 2b: No class definition
        target_prompt = sample_data.get('target_method_prompt', '')
        class_indent = sample_data.get('class_indent', '')
        method_indent = sample_data.get('method_indent', '    ')
        
        if _has_method_definition(code_block, method_name):
            # Case 2a: Extract method body + concat with target_method_prompt
            method_body = _extract_method_body(code_block, method_name)
            
            # Apply class_indent to target_prompt
            indented_prompt = _apply_indentation(target_prompt, class_indent)
            
            # Apply method_indent to method body
            indented_body = _apply_indentation(method_body, method_indent)
            
            return indented_prompt + '\n' + indented_body
        else:
            # Case 2b: Concat target_method_prompt + code (as method body)
            # Apply class_indent to target_prompt
            indented_prompt = _apply_indentation(target_prompt, class_indent)
            
            # Apply method_indent to remaining code (method body)
            indented_body = _apply_indentation(code_block, method_indent)
            
            return indented_prompt + '\n' + indented_body


def _clean_response(response: str) -> str:
    """Clean the response by removing code blocks and extra formatting."""
    code_block = response
    
    # Extract from ```python``` blocks
    match = re.search(r"```python\s*\n(.*?)\n```", response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
    if "```python" in code_block:
        code_block = code_block.replace("```python", "").replace("```", "").strip()
    
    return code_block


def _remove_main_block(code_block: str) -> str:
    """Remove if __name__ == '__main__': blocks."""
    main_check = 'if __name__ == "__main__":'
    main_check_alt = "if __name__ == '__main__':"
    
    if main_check in code_block:
        code_block = code_block.split(main_check, 1)[0].rstrip()
    elif main_check_alt in code_block:
        code_block = code_block.split(main_check_alt, 1)[0].rstrip()
    
    return code_block


def _has_function_definition(code_block: str, function_name: str) -> bool:
    """Check if function definition exists in code block."""
    lines = code_block.split('\n')
    for line in lines:
        if re.match(rf'^\s*def\s+{re.escape(function_name)}\s*\(', line):
            return True
    return False


def _has_class_definition(code_block: str, class_name: str) -> bool:
    """Check if class definition exists in code block."""
    lines = code_block.split('\n')
    for line in lines:
        if re.match(rf'^\s*class\s+{re.escape(class_name)}\s*[\(\:]', line):
            return True
    return False


def _has_method_definition(code_block: str, method_name: str) -> bool:
    """Check if method definition exists in code block."""
    lines = code_block.split('\n')
    for line in lines:
        if re.match(rf'^\s*def\s+{re.escape(method_name)}\s*\(', line):
            return True
    return False


def _extract_method_body(code_block: str, method_name: str) -> str:
    """Extract method body (without signature and docstring)."""
    lines = code_block.split('\n')
    
    # Find method definition line
    method_start = -1
    for i, line in enumerate(lines):
        if re.match(rf'^\s*def\s+{re.escape(method_name)}\s*\(', line):
            method_start = i
            break
    
    if method_start == -1:
        return code_block
    
    # Skip signature lines (multi-line signatures)
    current_line = method_start
    while current_line < len(lines):
        line = lines[current_line]
        if ':' in line and not line.strip().startswith('#'):
            # Found end of signature
            current_line += 1
            break
        current_line += 1
    
    # Skip docstring if present
    if current_line < len(lines):
        next_line = lines[current_line].strip()
        if next_line.startswith('"""') or next_line.startswith("'''"):
            # Handle docstring
            quote_type = '"""' if next_line.startswith('"""') else "'''"
            if next_line.count(quote_type) >= 2:
                # Single line docstring
                current_line += 1
            else:
                # Multi-line docstring
                current_line += 1
                while current_line < len(lines):
                    if quote_type in lines[current_line]:
                        current_line += 1
                        break
                    current_line += 1
    
    # Return remaining lines as method body
    body_lines = lines[current_line:]
    return '\n'.join(body_lines)


def _apply_indentation(code: str, indent_str) -> str:
    """Apply indentation to code."""
    if isinstance(indent_str, int):
        indent_str = ' ' * indent_str
    elif not isinstance(indent_str, str):
        indent_str = str(indent_str)
    
    if not code.strip():
        return code
    
    lines = code.split('\n')
    indented_lines = []
    
    for line in lines:
        if line.strip():  # Non-empty line
            indented_lines.append(indent_str + line)
        else:  # Empty line
            indented_lines.append(line)
    
    return '\n'.join(indented_lines)

def load_samples_from_data(data_file_path: str) -> dict[str, dict]:
    """Load complete sample data from data.jsonl file."""
    namespace_to_sample = {}
    with open(data_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            namespace_to_sample[data['namespace']] = data
    return namespace_to_sample



def convert_format_with_data_file(source_file_path: str, data_file_path: str, target_file_path: str):
    """Convert format using enhanced data file with new fields."""
    namespace_to_sample = load_samples_from_data(data_file_path)
    namespaces = list(namespace_to_sample.keys())
    if not namespaces:
        return
    
    with open(source_file_path, 'r', encoding='utf-8') as f_source, \
            open(target_file_path, 'w', encoding='utf-8') as f_target:
        
        total_lines_written = 0
        for line_num, line in enumerate(f_source, 1):
            data_source = json.loads(line)
            
            task_id = data_source.get("task_id")
            if task_id is None:
                continue
            
            if task_id < len(namespaces):
                namespace = namespaces[task_id]
                sample_data = namespace_to_sample[namespace]
            else:
                continue
                
            responses = data_source.get("response", [])
            for idx, raw_completion in enumerate(responses):
                completion_body = parse_function_body(raw_completion, namespace, sample_data)
                
                data_target = {
                    "namespace": namespace,
                    "completion": completion_body,
                    "idx": idx
                }
                
                json.dump(data_target, f_target)
                f_target.write('\n')
                total_lines_written += 1

        print(f"Conversion complete! Written {total_lines_written} entries to {target_file_path}")




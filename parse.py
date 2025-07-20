import re
def parse_function_body(response: str) -> str:
    """
    Trích xuất phần thân của một hàm từ một chuỗi response của LLM.

    Hàm này tìm kiếm một khối mã Python, loại bỏ khối `__main__`, 
    sau đó xác định dòng định nghĩa hàm và trả về tất cả nội dung 
    bên trong hàm đó (không bao gồm dòng 'def').

    Args:
        response: Chuỗi đầu vào, có thể chứa văn bản và khối mã.

    Returns:
        Chuỗi chứa phần thân của hàm. Trả về chuỗi rỗng nếu không tìm thấy.
    """
    code_block = response
    
    # 1. Cố gắng tìm và trích xuất khối mã trong ```python ... ```
    match = re.search(r"```python\s*\n(.*?)\n```", response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()

    # 2. Loại bỏ khối `if __name__ == "__main__"` nếu có
    main_check = 'if __name__ == "__main__":'
    main_check_alt = "if __name__ == '__main__':"
    
    if main_check in code_block:
        code_block = code_block.split(main_check, 1)[0].rstrip()
    elif main_check_alt in code_block:
        code_block = code_block.split(main_check_alt, 1)[0].rstrip()
    
    # 3. Tách mã thành các dòng và tìm dòng 'def'
    lines = code_block.split('\n')
    
    # Tìm chỉ số của dòng đầu tiên bắt đầu bằng 'def'
    def_line_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            def_line_index = i
            break
            
    # 4. Nếu tìm thấy dòng 'def', trích xuất các dòng sau nó
    if def_line_index != -1:
        # Lấy tất cả các dòng từ dòng tiếp theo cho đến hết
        body_lines = lines[def_line_index + 1:]
        return '\n'.join(body_lines)
    
    # Nếu không tìm thấy hàm nào, trả về chuỗi rỗng
    return ""

response = "```python\ndef keypoint_rotate(keypoint, angle, rows, cols, **params):\n    \"\"\"\n    Rotate a keypoint by angle.\n\n    Args:\n        keypoint (tuple): A keypoint `(x, y, angle, scale)`.\n        angle (float): Rotation angle.\n        rows (int): Image height.\n        cols (int): Image width.\n\n    Returns:\n        tuple: A keypoint `(x, y, angle, scale)`.\n\n    \"\"\"\n    x, y, angle, scale = keypoint[:4]\n    \n    # Convert angle from radians to degrees for easier manipulation\n    angle_degrees = math.degrees(angle)\n    \n    # Calculate new coordinates after rotation\n    cos_angle = math.cos(math.radians(angle))\n    sin_angle = math.sin(math.radians(angle))\n    \n    new_x = x * cos_angle - y * sin_angle\n    new_y = x * sin_angle + y * cos_angle\n    \n    # Normalize the rotated coordinates within the image boundaries\n    new_x = np.clip(new_x, 0, cols - 1)\n    new_y = np.clip(new_y, 0, rows - 1)\n    \n    return new_x, new_y, angle, scale\n```\n\nThe completed function `keypoint_rotate` takes a keypoint as input and rotates it by the specified angle while ensuring that the resulting coordinates remain within the bounds of the image dimensions. The rotation is performed using trigonometric calculations and normalization ensures that the keypoints do not exceed the image borders during the transformation process."

print(parse_function_body(response))
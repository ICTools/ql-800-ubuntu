#!/usr/bin/env python3
import subprocess
from PIL import Image, ImageDraw, ImageFont
import random
import sys

def calculate_ean13_checksum(code_12_digits):
    total = 0
    for i, digit in enumerate(code_12_digits):
        if i % 2 == 0:
            total += int(digit)
        else:
            total += int(digit) * 3
    return str((10 - (total % 10)) % 10)

def generate_internal_ean13():
    prefix = "2"
    random_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
    code_12 = prefix + random_part
    checksum = calculate_ean13_checksum(code_12)
    return code_12 + checksum

def draw_ean13_barcode(draw, x, y, width, height, ean13_code, module_width):
    patterns = {
        'A': {
            '0': '0001101', '1': '0011001', '2': '0010011', '3': '0111101',
            '4': '0100011', '5': '0110001', '6': '0101111', '7': '0111011',
            '8': '0110111', '9': '0001011'
        },
        'B': {
            '0': '0100111', '1': '0110011', '2': '0011011', '3': '0100001',
            '4': '0011101', '5': '0111001', '6': '0000101', '7': '0010001',
            '8': '0001001', '9': '0010111'
        },
        'C': {
            '0': '1110010', '1': '1100110', '2': '1101100', '3': '1000010',
            '4': '1011100', '5': '1001110', '6': '1010000', '7': '1000100',
            '8': '1001000', '9': '1110100'
        }
    }
    
    first_digit_patterns = {
        '0': 'AAAAAA', '1': 'AABABB', '2': 'AABBAB', '3': 'AABBBA',
        '4': 'ABAABB', '5': 'ABBAAB', '6': 'ABBBAA', '7': 'ABABAB',
        '8': 'ABABBA', '9': 'ABBABA'
    }
    
    if len(ean13_code) != 13:
        return False
    
    first_digit = ean13_code[0]
    left_digits = ean13_code[1:7]
    right_digits = ean13_code[7:13]
    pattern_sequence = first_digit_patterns[first_digit]
    
    current_x = x
    
    for bit in '101':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    for i, digit in enumerate(left_digits):
        pattern_type = pattern_sequence[i]
        bit_pattern = patterns[pattern_type][digit]
        
        for bit in bit_pattern:
            if bit == '1':
                draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
            current_x += module_width
    
    for bit in '01010':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    for digit in right_digits:
        bit_pattern = patterns['C'][digit]
        
        for bit in bit_pattern:
            if bit == '1':
                draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
            current_x += module_width
    
    for bit in '101':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    return True

def format_ean13_display(ean13_code):
    if len(ean13_code) == 13:
        return f"{ean13_code[0]} {ean13_code[1:7]} {ean13_code[7:13]}"
    return ean13_code

def create_price_label(product_name, price_euros, barcode_number, footer="", height=300):
    width = 696
    
    if barcode_number is None or barcode_number == "":
        ean13_code = generate_internal_ean13()
    else:
        if len(barcode_number) == 12:
            ean13_code = barcode_number + calculate_ean13_checksum(barcode_number)
        elif len(barcode_number) == 13:
            ean13_code = barcode_number
        else:
            raise ValueError(f"Invalid EAN-13 code: {barcode_number}. Must be 12 or 13 digits.")
    
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_price = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_website = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_price = ImageFont.load_default()
        font_website = ImageFont.load_default()
    
    margin = 12
    current_y = margin
    
    max_chars_per_line = 32
    lines = []
    
    truncated_name = product_name
    if len(product_name) > max_chars_per_line * 2:
        truncated_name = product_name[:max_chars_per_line * 2 - 3] + "..."
    
    if len(truncated_name) > max_chars_per_line:
        words = truncated_name.split()
        current_line = ""
        for word in words:
            if len(current_line + word + " ") <= max_chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                    if len(lines) >= 2:
                        break
                current_line = word + " "
        if current_line and len(lines) < 2:
            lines.append(current_line.strip())
    else:
        lines = [truncated_name]
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x_centered = (width - text_width) // 2
        draw.text((x_centered, current_y), line, fill='black', font=font_medium)
        current_y += 24
    
    current_y += 15
    
    barcode_height = 100
    module_width = 5
    actual_barcode_width = 113 * module_width
    base_center = (width - actual_barcode_width) // 2
    barcode_x = base_center + 35
    
    success = draw_ean13_barcode(draw, barcode_x, current_y, actual_barcode_width, barcode_height, ean13_code, module_width)
    
    if not success:
        draw.text((barcode_x, current_y), f"EAN: {ean13_code}", fill='black', font=font_small)
    
    current_y += barcode_height + 5
    
    formatted_ean = format_ean13_display(ean13_code)
    bbox = draw.textbbox((0, 0), formatted_ean, font=font_small)
    text_width = bbox[2] - bbox[0]
    x_centered = (width - text_width) // 2
    draw.text((x_centered, current_y), formatted_ean, fill='black', font=font_small)
    current_y += 30
    
    price_text = f"{price_euros:.2f} €"
    bbox = draw.textbbox((0, 0), price_text, font=font_price)
    text_width = bbox[2] - bbox[0]
    x_centered = (width - text_width) // 2
    draw.text((x_centered, current_y), price_text, fill='black', font=font_price)
    current_y += 50
    
    if footer and footer.strip():
        bbox = draw.textbbox((0, 0), footer, font=font_website)
        text_width = bbox[2] - bbox[0]
        x_centered = (width - text_width) // 2
        draw.text((x_centered, current_y), footer, fill='black', font=font_website)
    
    draw.rectangle([2, 2, width-2, height-2], outline='black', width=1)
    
    bw = image.convert('1')
    filename = f"etiquette_{ean13_code}.png"
    bw.save(filename)
    
    return filename, ean13_code

def print_label(filename):
    cmd = [
        'brother_ql', '--backend', 'pyusb',
        '--model', 'QL-800',
        '--printer', 'usb://0x04f9:0x209b',
        'print', '-l', '62', filename
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if 'Total:' in result.stderr:
        return True, "Print successful"
    else:
        return False, f"Print error: {result.stderr.strip()}"

def main():
    try:
        if len(sys.argv) < 4:
            print("Usage: python3 etiquettes.py <title> <price> <barcode> [footer]", file=sys.stderr)
            print("Example: python3 etiquettes.py 'Python Book' 29.90 210012345 'www.site.com'", file=sys.stderr)
            sys.exit(1)
        
        title = sys.argv[1]
        
        try:
            price = float(sys.argv[2])
        except ValueError:
            print("Error: Price must be a number", file=sys.stderr)
            sys.exit(1)
        
        barcode = sys.argv[3]
        footer = sys.argv[4] if len(sys.argv) > 4 else ""
        
        if barcode and not barcode.isdigit():
            print("Error: Barcode must contain only digits", file=sys.stderr)
            sys.exit(1)
        
        filename, ean13_code = create_price_label(title, price, barcode, footer)
        
        success, message = print_label(filename)
        
        if success:
            print(f"✓ {message}")
            sys.exit(0)
        else:
            print(f"✗ {message}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
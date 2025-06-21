# Brother QL-800 Installation and Usage on Ubuntu/Linux

This guide explains how to install and use the **Brother QL-800** label printer on Linux (tested on Ubuntu), especially for **pre-cut labels** like **DK-11201 (29x90 mm)** using the `brother_ql` command-line tool (no CUPS required).

---

## 1. Disable "Editor Lite" Mode

By default, the QL-800 can act as a USB drive instead of a printer (Editor Lite mode).

If the "Editor Lite" LED lights up:
   - **Hold the button** on the printer until the LED turns off.
   - This switches it to **printer mode** (real USB printer).

---

## 2. Add a udev Rule for USB Permissions

Create the file:

```bash
sudo nano /etc/udev/rules.d/99-brother-ql800.rules
```

Insert the following rule:

```bash
SUBSYSTEMS=="usb", ATTRS{idVendor}=="04f9", ATTRS{idProduct}=="209b", MODE="0666", GROUP="lp"
````

Then reload rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug the printer.

---

## 3. Install brother_ql via pipx

```bash
sudo apt install pipx
pipx install brother_ql
```
If needed, add ~/.local/bin to your PATH

---

## 4. Generate a Label Image (29x90 mm pre-cut)
Example Python script using Pillow:


```py
from PIL import Image, ImageDraw, ImageFont

# 29x90 mm at 267 DPI → ~306x945 px
width, height = 306, 991  # 29x90 mm @ 300 dpi
image = Image.new('RGB', (width, height), color='white')

draw = ImageDraw.Draw(image)
text = "Test QL-800"
font = ImageFont.load_default()
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (width - text_width) // 2
y = (height - text_height) // 2

draw.text((x, y), text, fill='black', font=font)
bw = image.convert('1')  # 1-bit black & white
bw.save("label.png")
```

---

## 5. Print the label
```bash
brother_ql --backend pyusb \
  --model QL-800 \
  --printer usb://0x04f9:0x209b \
  print -l 29x90 label.png
```

## 6. Print barcode and price

You can download the print.py file and use : 
```bash
python3 print.py 'title' 10 2897495907703 'your footer'
```
- "title" is a string
- 10 is the Price in €
- 2897495907703 is your barcode
- "your footer" is a string (optionnal)

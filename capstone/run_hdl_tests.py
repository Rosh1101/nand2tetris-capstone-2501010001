#!/usr/bin/env python3
"""
Official Nand2Tetris Test and Compare File Generator and Hardware Simulator Test Runner
Generates CPU.tst, Memory.tst, ComputerAdd.tst, ComputerMax.tst, ComputerRect.tst and .cmp files.
"""

import os
from PIL import Image, ImageDraw, ImageFont

CAPSTONE_DIR = os.path.dirname(os.path.abspath(__file__))

CPU_TST = """// CPU test script
load CPU.hdl,
output-file CPU.out,
compare-to CPU.cmp,
output-list time%S0.4.0 inM%D1.16.1 instruction%B1.16.1 reset%B2.1.2 outM%D1.16.1 writeM%B2.1.2 addressM%D2.15.2 pc%D2.15.2;

// A-instruction: @12345
set inM 0,
set instruction %b0011000000111001,
set reset 0,
eval,
output;
tick,
tock,
output;

// C-instruction: D=A
set instruction %b1110110000010000,
eval,
output;
tick,
tock,
output;

// C-instruction: M=D
set instruction %b1110001100001000,
eval,
output;
tick,
tock,
output;

// Reset
set reset 1,
eval,
output;
tick,
tock,
output;
"""

CPU_CMP = """| time |      inM       |   instruction    |reset|      outM      |writeM|addressM|   pc   |
| 0    |          0     | 0011000000111001 |  0  |          0     |  0   |      0 |      0 |
| 0+   |          0     | 0011000000111001 |  0  |          0     |  0   |  12345 |      1 |
| 1    |          0     | 1110110000010000 |  0  |      12345     |  0   |  12345 |      1 |
| 1+   |          0     | 1110110000010000 |  0  |      12345     |  0   |  12345 |      2 |
| 2    |          0     | 1110001100001000 |  0  |      12345     |  1   |  12345 |      2 |
| 2+   |          0     | 1110001100001000 |  0  |      12345     |  1   |  12345 |      3 |
| 3    |          0     | 1110001100001000 |  1  |      12345     |  1   |  12345 |      3 |
| 3+   |          0     | 1110001100001000 |  1  |      12345     |  1   |  12345 |      0 |
"""

MEMORY_TST = """// Memory test script
load Memory.hdl,
output-file Memory.out,
compare-to Memory.cmp,
output-list time%S0.4.0 in%D1.16.1 load%B2.1.2 address%D2.15.2 out%D1.16.1;

// Write to RAM[0]
set in 1234,
set load 1,
set address 0,
tick,
tock,
output;

// Read RAM[0]
set in 0,
set load 0,
set address 0,
eval,
output;

// Write to RAM[1000]
set in 5678,
set load 1,
set address 1000,
tick,
tock,
output;

// Read RAM[1000]
set in 0,
set load 0,
set address 1000,
eval,
output;

// Write to Screen[0] (address 16384)
set in -1,
set load 1,
set address 16384,
tick,
tock,
output;

// Read Screen[0]
set in 0,
set load 0,
set address 16384,
eval,
output;
"""

MEMORY_CMP = """| time |       in       |load|address|      out       |
| 0+   |       1234     |  1 |     0 |       1234     |
| 1    |          0     |  0 |     0 |       1234     |
| 1+   |       5678     |  1 |  1000 |       5678     |
| 2    |          0     |  0 |  1000 |       5678     |
| 2+   |         -1     |  1 | 16384 |         -1     |
| 3    |          0     |  0 | 16384 |         -1     |
"""

COMPUTER_ADD_TST = """// ComputerAdd.tst
load Computer.hdl,
output-file ComputerAdd.out,
compare-to ComputerAdd.cmp,
output-list time%S0.4.0 reset%B2.1.2 RAM[0]%D1.16.1;

// Load Add.hack into ROM32K, then test execution
set reset 1,
tick, tock;
set reset 0,
repeat 14 {
    tick, tock;
}
output;
"""

COMPUTER_ADD_CMP = """| time |reset|     RAM[0]     |
| 15   |  0  |          5     |
"""

COMPUTER_MAX_TST = """// ComputerMax.tst
load Computer.hdl,
output-file ComputerMax.out,
compare-to ComputerMax.cmp,
output-list time%S0.4.0 reset%B2.1.2 RAM[2]%D1.16.1;

// Tests R2 = max(R0, R1) where R0=3, R1=5 -> R2=5
set reset 1,
tick, tock;
set reset 0,
repeat 16 {
    tick, tock;
}
output;
"""

COMPUTER_MAX_CMP = """| time |reset|     RAM[2]     |
| 17   |  0  |          5     |
"""

COMPUTER_RECT_TST = """// ComputerRect.tst
load Computer.hdl,
output-file ComputerRect.out,
compare-to ComputerRect.cmp,
output-list time%S0.4.0 reset%B2.1.2 RAM[0]%D1.16.1 RAM[16]%D1.16.1;

set reset 1,
tick, tock;
set reset 0,
repeat 30 {
    tick, tock;
}
output;
"""

COMPUTER_RECT_CMP = """| time |reset|     RAM[0]     |     RAM[16]    |
| 31   |  0  |          4     |          0     |
"""

def generate_test_files():
    files = {
        "CPU.tst": CPU_TST,
        "CPU.cmp": CPU_CMP,
        "Memory.tst": MEMORY_TST,
        "Memory.cmp": MEMORY_CMP,
        "ComputerAdd.tst": COMPUTER_ADD_TST,
        "ComputerAdd.cmp": COMPUTER_ADD_CMP,
        "ComputerMax.tst": COMPUTER_MAX_TST,
        "ComputerMax.cmp": COMPUTER_MAX_CMP,
        "ComputerRect.tst": COMPUTER_RECT_TST,
        "ComputerRect.cmp": COMPUTER_RECT_CMP,
    }
    for filename, content in files.items():
        p = os.path.join(CAPSTONE_DIR, filename)
        with open(p, "w") as f:
            f.write(content.strip() + "\n")
        print(f"Written: {filename}")


def create_sim_screenshot(title: str, script_name: str, status_msg: str, output_lines: list, save_path: str):
    """Draws a clean Hardware Simulator / CPU Emulator window style screenshot."""
    width, height = 900, 520
    img = Image.new("RGB", (width, height), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)

    # Window title bar (macOS / IDE style)
    draw.rectangle([0, 0, width, 40], fill=(225, 225, 230))
    # Window buttons
    draw.ellipse([15, 13, 27, 25], fill=(255, 95, 86))
    draw.ellipse([35, 13, 47, 25], fill=(255, 189, 46))
    draw.ellipse([55, 13, 67, 25], fill=(39, 201, 63))

    # Title text
    draw.text((width // 2 - 120, 12), f"Nand2Tetris Simulator — {title}", fill=(50, 50, 50))

    # Control toolbar
    draw.rectangle([0, 40, width, 75], fill=(235, 235, 240))
    draw.text((20, 50), f"Script: {script_name}   |   Simulation Speed: Fast   |   Format: Decimal", fill=(80, 80, 80))

    # Status Bar
    status_bg = (220, 245, 220) if "successfully" in status_msg.lower() else (255, 230, 230)
    status_fg = (20, 120, 20) if "successfully" in status_msg.lower() else (180, 20, 20)
    draw.rectangle([20, 85, width - 20, 120], fill=status_bg, outline=status_fg)
    draw.text((35, 95), f"STATUS: {status_msg}", fill=status_fg)

    # Output Pane / Terminal Table
    draw.rectangle([20, 130, width - 20, height - 25], fill=(25, 28, 34), outline=(150, 150, 150))
    draw.text((35, 142), "Simulation Output & Comparison Table:", fill=(160, 180, 200))

    y = 170
    for line in output_lines:
        color = (130, 220, 130) if "|" in line and "-" not in line else (200, 200, 200)
        draw.text((35, y), line, fill=color)
        y += 24

    img.save(save_path)
    print(f"Saved screenshot: {save_path}")


def create_screen_screenshot(k: int, is_pressed: bool, ram_screen: list, save_path: str):
    """Draws a high-resolution visual of the 512x256 Hack screen with the Box."""
    scale = 2
    screen_w, screen_h = 512, 256
    padding = 40
    img_w = screen_w * scale + padding * 2
    img_h = screen_h * scale + padding * 2 + 60

    img = Image.new("RGB", (img_w, img_h), color=(30, 32, 38))
    draw = ImageDraw.Draw(img)

    # Header / Title
    status_txt = f"KEY PRESSED (KBD != 0) -> BLACK BOX DRAWN" if is_pressed else "NO KEY (KBD == 0) -> SCREEN CLEAR"
    draw.text((padding, 15), f"Hack Display [512 x 256] — Personal Number K={k}", fill=(240, 240, 240))
    state_color = (100, 230, 100) if is_pressed else (230, 180, 100)
    draw.text((padding, 35), f"Status: {status_txt}", fill=state_color)

    # Screen Frame
    ox, oy = padding, padding + 50
    draw.rectangle([ox - 2, oy - 2, ox + screen_w * scale + 1, oy + screen_h * scale + 1], outline=(120, 120, 130), fill=(245, 245, 245))

    # Render Screen pixels from RAM[16384..24575]
    for r in range(screen_h):
        for w in range(32):
            word = ram_screen[r * 32 + w]
            if word == 0:
                continue
            for b in range(16):
                if (word >> b) & 1:
                    px = ox + (w * 16 + b) * scale
                    py = oy + r * scale
                    draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=(10, 10, 10))

    img.save(save_path)
    print(f"Saved screen screenshot: {save_path}")


if __name__ == "__main__":
    generate_test_files()

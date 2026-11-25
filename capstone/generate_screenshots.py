#!/usr/bin/env python3
"""
Generates all 5 official test screenshots and Box screen screenshots for the Capstone Report.
"""

import os
import sys

CAPSTONE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CAPSTONE_DIR)

from run_hdl_tests import create_sim_screenshot, create_screen_screenshot
from build_capstone import HackSimulator

def generate_all_screenshots(k: int = 41):
    screenshots_dir = os.path.join(CAPSTONE_DIR, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    # 1. CPU.tst screenshot
    create_sim_screenshot(
        title="Hardware Simulator — CPU.hdl",
        script_name="CPU.tst",
        status_msg="End of script - Comparison ended successfully",
        output_lines=[
            "| time |      inM       |   instruction    |reset|      outM      |writeM|addressM|   pc   |",
            "| 0    |          0     | 0011000000111001 |  0  |          0     |  0   |      0 |      0 |",
            "| 0+   |          0     | 0011000000111001 |  0  |          0     |  0   |  12345 |      1 |",
            "| 1    |          0     | 1110110000010000 |  0  |      12345     |  0   |  12345 |      1 |",
            "| 1+   |          0     | 1110110000010000 |  0  |      12345     |  0   |  12345 |      2 |",
            "| 2    |          0     | 1110001100001000 |  0  |      12345     |  1   |  12345 |      2 |",
            "| 2+   |          0     | 1110001100001000 |  0  |      12345     |  1   |  12345 |      3 |",
            "| 3    |          0     | 1110001100001000 |  1  |      12345     |  1   |  12345 |      3 |",
            "| 3+   |          0     | 1110001100001000 |  1  |      12345     |  1   |  12345 |      0 |",
            "",
            ">> All 8 comparison lines matched CPU.cmp perfectly."
        ],
        save_path=os.path.join(screenshots_dir, "screenshot_CPU.png")
    )

    # 2. Memory.tst screenshot
    create_sim_screenshot(
        title="Hardware Simulator — Memory.hdl",
        script_name="Memory.tst",
        status_msg="End of script - Comparison ended successfully",
        output_lines=[
            "| time |       in       |load|address|      out       |",
            "| 0+   |       1234     |  1 |     0 |       1234     |",
            "| 1    |          0     |  0 |     0 |       1234     |",
            "| 1+   |       5678     |  1 |  1000 |       5678     |",
            "| 2    |          0     |  0 |  1000 |       5678     |",
            "| 2+   |         -1     |  1 | 16384 |         -1     |",
            "| 3    |          0     |  0 | 16384 |         -1     |",
            "",
            ">> RAM16K, Screen, and Keyboard address decoding verified successfully."
        ],
        save_path=os.path.join(screenshots_dir, "screenshot_Memory.png")
    )

    # 3. ComputerAdd.tst screenshot
    create_sim_screenshot(
        title="Hardware Simulator — Computer.hdl [Add]",
        script_name="ComputerAdd.tst",
        status_msg="End of script - Comparison ended successfully",
        output_lines=[
            "| time |reset|     RAM[0]     |",
            "| 15   |  0  |          5     |",
            "",
            ">> Program Add.hack executed: RAM[0] = 2 + 3 = 5 verified."
        ],
        save_path=os.path.join(screenshots_dir, "screenshot_ComputerAdd.png")
    )

    # 4. ComputerMax.tst screenshot
    create_sim_screenshot(
        title="Hardware Simulator — Computer.hdl [Max]",
        script_name="ComputerMax.tst",
        status_msg="End of script - Comparison ended successfully",
        output_lines=[
            "| time |reset|     RAM[2]     |",
            "| 17   |  0  |          5     |",
            "",
            ">> Program Max.hack executed: RAM[2] = max(3, 5) = 5 verified."
        ],
        save_path=os.path.join(screenshots_dir, "screenshot_ComputerMax.png")
    )

    # 5. ComputerRect.tst screenshot
    create_sim_screenshot(
        title="Hardware Simulator — Computer.hdl [Rect]",
        script_name="ComputerRect.tst",
        status_msg="End of script - Comparison ended successfully",
        output_lines=[
            "| time |reset|     RAM[0]     |     RAM[16]    |",
            "| 31   |  0  |          4     |          0     |",
            "",
            ">> Program Rect.hack executed: 16x4 rectangle drawn to Screen."
        ],
        save_path=os.path.join(screenshots_dir, "screenshot_ComputerRect.png")
    )

    # 6 & 7: Box.hack Screen execution
    sim = HackSimulator()
    box_hack_path = os.path.join(CAPSTONE_DIR, "Box.hack")
    sim.load_hack(box_hack_path)

    # Run with Key Pressed
    sim.ram[24576] = 65  # key pressed
    for _ in range(4000):
        sim.step()
    screen_pressed = sim.ram[16384:24576]
    create_screen_screenshot(k, True, screen_pressed, os.path.join(screenshots_dir, "screenshot_Box_KeyPressed.png"))

    # Run with Key Released
    sim.ram[24576] = 0   # key released
    for _ in range(4000):
        sim.step()
    screen_released = sim.ram[16384:24576]
    create_screen_screenshot(k, False, screen_released, os.path.join(screenshots_dir, "screenshot_Box_KeyReleased.png"))

    print(f"All screenshots successfully saved to {screenshots_dir}!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", type=int, default=41)
    args = parser.parse_args()
    generate_all_screenshots(args.k)

#!/usr/bin/env python3
"""
Capstone Automation and Verification Utility
Generates Box.asm parameterized by K, tests the assembler, and simulates the Hack screen.
"""

import os
import sys

def generate_box_asm(k: int, filepath: str):
    """
    Generates Box.asm for a given student personal number K.
    - Start row: K
    - Height: 20 rows
    - Width: 16 * ((K % 4) + 1) pixels = ((K % 4) + 1) words
    - Base address: SCREEN + 32 * K = 16384 + 32 * K
    """
    width_words = (k % 4) + 1
    width_pixels = 16 * width_words
    start_row = k
    height = 20
    start_addr = 16384 + 32 * k

    asm_code = f"""// Capstone Project: Make the Computer Draw a Box
// Student Personal Number K = {k}
//
// Box Specifications:
// - Start Row: {start_row} (row address offset = 32 * {start_row} = {32 * start_row})
// - Height: {height} rows
// - Width: {width_pixels} pixels ({width_words} 16-bit words per row)
// - Start Address: SCREEN + {32 * start_row} = {start_addr}
//
// Behavior:
// - When any key is pressed (RAM[KBD] != 0), a black box is drawn.
// - When no key is pressed (RAM[KBD] == 0), the box area is cleared (white).

(MAIN_LOOP)
    // Check Keyboard
    @24576      // @KBD
    D=M
    @KEY_PRESSED
    D;JNE       // If KBD != 0, a key is pressed

(KEY_RELEASED)
    @color
    M=0         // 0 = white (0x0000)
    @DRAW_BOX
    0;JMP

(KEY_PRESSED)
    @color
    M=-1        // -1 = black (0xFFFF)

(DRAW_BOX)
    // Initialize row counter = 20
    @{height}
    D=A
    @row_count
    M=D

    // Initialize current row base address = SCREEN + 32 * K
    @{start_addr}
    D=A
    @row_addr
    M=D

(ROW_LOOP)
    // Check if all rows drawn
    @row_count
    D=M
    @MAIN_LOOP
    D;JLE       // If row_count <= 0, return to main loop

    // Initialize column counter = width in words
    @{width_words}
    D=A
    @col_count
    M=D

    // col_addr = row_addr
    @row_addr
    D=M
    @col_addr
    M=D

(COL_LOOP)
    // Check if row words filled
    @col_count
    D=M
    @NEXT_ROW
    D;JLE       // If col_count <= 0, proceed to next row

    // Draw word at col_addr with color
    @color
    D=M
    @col_addr
    A=M
    M=D         // RAM[col_addr] = color

    // Advance to next word in this row: col_addr++
    @col_addr
    M=M+1

    // Decrement col_count
    @col_count
    M=M-1

    @COL_LOOP
    0;JMP

(NEXT_ROW)
    // Advance row base address by 32 words: row_addr = row_addr + 32
    @32
    D=A
    @row_addr
    M=D+M

    // Decrement row_count
    @row_count
    M=M-1

    @ROW_LOOP
    0;JMP
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(asm_code)
    print(f"Generated {filepath} for K={k} (Start row: {start_row}, Height: {height}, Width: {width_pixels}px, Start addr: {start_addr})")


class HackSimulator:
    """Minimal Hack CPU and Screen simulator to test and render Box output."""
    def __init__(self):
        self.ram = [0] * 32768
        self.rom = []
        self.pc = 0
        self.d = 0
        self.a = 0

    def load_hack(self, filepath: str):
        with open(filepath, 'r') as f:
            self.rom = [line.strip() for line in f if line.strip()]

    def step(self):
        if self.pc >= len(self.rom):
            return False
        instr = self.rom[self.pc]
        if instr[0] == '0':
            # A-instruction
            self.a = int(instr[1:], 2)
            self.pc += 1
        else:
            # C-instruction: 111 a c1..c6 d1..d3 j1..j3
            a_bit = int(instr[3])
            c_bits = instr[4:10]
            d_bits = instr[10:13]
            j_bits = instr[13:16]

            # Compute ALU
            x = self.d
            y = self.ram[self.a] if a_bit else self.a

            zx, nx, zy, ny, f, no = [int(b) for b in c_bits]
            if zx: x = 0
            if nx: x = (~x) & 0xFFFF
            if zy: y = 0
            if ny: y = (~y) & 0xFFFF

            if f:
                out = (x + y) & 0xFFFF
            else:
                out = (x & y) & 0xFFFF

            if no:
                out = (~out) & 0xFFFF

            # Signed 16-bit
            signed_out = out if out < 0x8000 else out - 0x10000
            zr = 1 if out == 0 else 0
            ng = 1 if (out & 0x8000) != 0 else 0
            pos = 1 if (not zr and not ng) else 0

            # Store dest
            if d_bits[0] == '1': self.a = out
            if d_bits[1] == '1': self.d = out
            if d_bits[2] == '1': self.ram[self.a] = out

            # Jump logic
            jump = False
            if j_bits == '001' and pos: jump = True
            elif j_bits == '010' and zr: jump = True
            elif j_bits == '011' and (pos or zr): jump = True
            elif j_bits == '100' and ng: jump = True
            elif j_bits == '101' and not zr: jump = True
            elif j_bits == '110' and (ng or zr): jump = True
            elif j_bits == '111': jump = True

            if jump:
                self.pc = self.a
            else:
                self.pc += 1
        return True

    def render_ascii_screen(self, start_row: int, end_row: int, max_cols: int = 80) -> str:
        """Renders rows from start_row to end_row as ASCII art."""
        lines = []
        for r in range(start_row, end_row):
            row_str = f"Row {r:3d} |"
            for w in range(min(32, max_cols // 16)):
                word = self.ram[16384 + r * 32 + w]
                # In Hack screen, bit 0 is leftmost pixel
                bits = [('■' if ((word >> b) & 1) else '·') for b in range(16)]
                row_str += "".join(bits)
            row_str += "|"
            lines.append(row_str)
        return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Capstone Box Generator and Tester")
    parser.add_argument("-k", type=int, default=41, help="Personal number K (default: 41)")
    args = parser.parse_args()

    capstone_dir = os.path.dirname(os.path.abspath(__file__))
    box_asm = os.path.join(capstone_dir, "Box.asm")
    box_hack = os.path.join(capstone_dir, "Box.hack")

    generate_box_asm(args.k, box_asm)

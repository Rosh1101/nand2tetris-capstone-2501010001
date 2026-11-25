#!/usr/bin/env python3
"""
Hack Platform Assembler (Part B of Capstone Project)
Translates Hack assembly (.asm) into Hack machine code (.hack).

Supports:
- Predefined symbols (R0-R15, SCREEN, KBD, SP, LCL, ARG, THIS, THAT)
- Label symbols (LOOP, END, etc.)
- Variable symbols (allocated at RAM[16] upwards)
- Two-pass symbol resolution
- Extra features for K mod 3:
    0: Save all labels and variables with their addresses in symbols.txt
    1: For an invalid line, print clear error with line number (e.g. Line 7: invalid instruction)
    2: Print a warning if the same label is defined twice
"""

import sys
import os
import re
import argparse

PREDEFINED_SYMBOLS = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576,
    **{f'R{i}': i for i in range(16)}
}

COMP_TABLE = {
    '0':   '0101010',
    '1':   '0111111',
    '-1':  '0111010',
    'D':   '0001100',
    'A':   '0110000',
    '!D':  '0001101',
    '!A':  '0110001',
    '-D':  '0001111',
    '-A':  '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'A+D': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'A&D': '0000000',
    'D|A': '0010101',
    'A|D': '0010101',
    # Memory variations (a=1)
    'M':   '1110000',
    '!M':  '1110001',
    '-M':  '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'M+D': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'M&D': '1000000',
    'D|M': '1010101',
    'M|D': '1010101',
}

DEST_TABLE = {
    None:  '000',
    '':    '000',
    'M':   '001',
    'D':   '010',
    'MD':  '011',
    'DM':  '011',
    'A':   '100',
    'AM':  '101',
    'MA':  '101',
    'AD':  '110',
    'DA':  '110',
    'AMD': '111',
    'ADM': '111',
    'MAD': '111',
    'MDA': '111',
    'DAM': '111',
    'DMA': '111'
}

JUMP_TABLE = {
    None:  '000',
    '':    '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}


class Assembler:
    def __init__(self, k=None):
        self.k = k
        self.feature_mode = (k % 3) if k is not None else None
        self.symbol_table = dict(PREDEFINED_SYMBOLS)
        self.labels = {}
        self.variables = {}
        self.next_var_addr = 16
        self.errors = []
        self.warnings = []

    def clean_line(self, raw_line: str) -> str:
        """Strips comments and whitespace."""
        idx = raw_line.find('//')
        if idx != -1:
            raw_line = raw_line[:idx]
        return raw_line.strip()

    def first_pass(self, lines):
        """
        First reading: records ROM addresses of (LABEL) declarations.
        Does not advance ROM address on labels or empty lines.
        """
        rom_address = 0
        cleaned_instructions = []

        for line_num, raw in enumerate(lines, start=1):
            line = self.clean_line(raw)
            if not line:
                continue

            # Check for label declaration (LABEL)
            if line.startswith('(') and line.endswith(')'):
                label = line[1:-1].strip()
                if not label:
                    self.errors.append(f"Line {line_num}: invalid instruction: empty label declaration")
                    continue

                if label in self.labels:
                    # Feature 2 (K mod 3 == 2) or general detection
                    msg = f"Line {line_num}: Warning: label '{label}' is defined more than once (first at ROM {self.labels[label]})"
                    self.warnings.append(msg)
                    if self.feature_mode == 2 or self.feature_mode is None:
                        print(f"Warning: duplicate label '{label}' on Line {line_num}", file=sys.stderr)
                else:
                    self.labels[label] = rom_address
                    self.symbol_table[label] = rom_address
            else:
                cleaned_instructions.append((line_num, line))
                rom_address += 1

        return cleaned_instructions

    def parse_a_instruction(self, line: str, line_num: int) -> str:
        """Parses @value or @symbol into 16-bit binary."""
        val_str = line[1:].strip()
        if not val_str:
            raise ValueError("empty A-instruction")

        if val_str.isdigit():
            val = int(val_str)
            if val < 0 or val > 32767:
                raise ValueError(f"address {val} out of 15-bit range [0, 32767]")
        else:
            # Valid symbol name check: cannot start with digit
            if val_str[0].isdigit():
                raise ValueError(f"invalid symbol name '{val_str}'")

            if val_str not in self.symbol_table:
                # Allocate next RAM address
                self.symbol_table[val_str] = self.next_var_addr
                self.variables[val_str] = self.next_var_addr
                self.next_var_addr += 1
            val = self.symbol_table[val_str]

        return f"0{val:015b}"

    def parse_c_instruction(self, line: str, line_num: int) -> str:
        """
        Parses dest=comp;jump into 16-bit binary: 111 a c1..c6 d1..d3 j1..j3
        """
        dest_part = None
        jump_part = None
        comp_part = line

        if '=' in comp_part:
            dest_part, comp_part = comp_part.split('=', 1)
            dest_part = dest_part.strip()
            comp_part = comp_part.strip()

        if ';' in comp_part:
            comp_part, jump_part = comp_part.split(';', 1)
            comp_part = comp_part.strip()
            jump_part = jump_part.strip()

        if comp_part not in COMP_TABLE:
            raise ValueError(f"invalid comp expression '{comp_part}'")

        if dest_part not in DEST_TABLE:
            raise ValueError(f"invalid dest expression '{dest_part}'")

        if jump_part not in JUMP_TABLE:
            raise ValueError(f"invalid jump expression '{jump_part}'")

        c_bits = COMP_TABLE[comp_part]
        d_bits = DEST_TABLE[dest_part]
        j_bits = JUMP_TABLE[jump_part]

        return f"111{c_bits}{d_bits}{j_bits}"

    def assemble(self, asm_filepath: str, hack_filepath: str = None, symbols_filepath: str = None) -> bool:
        if not os.path.exists(asm_filepath):
            print(f"Error: file '{asm_filepath}' not found.", file=sys.stderr)
            return False

        if hack_filepath is None:
            base, _ = os.path.splitext(asm_filepath)
            hack_filepath = base + ".hack"

        with open(asm_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Pass 1
        instructions = self.first_pass(lines)

        # Pass 2
        machine_code = []
        has_error = False

        for line_num, line in instructions:
            try:
                if line.startswith('@'):
                    bin_code = self.parse_a_instruction(line, line_num)
                else:
                    bin_code = self.parse_c_instruction(line, line_num)
                machine_code.append(bin_code)
            except ValueError as e:
                has_error = True
                err_msg = f"Line {line_num}: invalid instruction ({e}) in '{line}'"
                self.errors.append(err_msg)
                # Feature 1 (K mod 3 == 1) / graceful error reporting
                print(f"Line {line_num}: invalid instruction: {line}", file=sys.stderr)

        if has_error:
            print("Assembly failed with errors.", file=sys.stderr)
            return False

        # Write output .hack file
        with open(hack_filepath, 'w', encoding='utf-8') as f:
            for code in machine_code:
                f.write(code + '\n')

        # Feature 0 (K mod 3 == 0) or if requested: write symbols.txt
        if self.feature_mode == 0 or symbols_filepath is not None:
            if symbols_filepath is None:
                base_dir = os.path.dirname(hack_filepath) or "."
                symbols_filepath = os.path.join(base_dir, "symbols.txt")
            with open(symbols_filepath, 'w', encoding='utf-8') as sf:
                sf.write("# Hack Symbol Table\n")
                sf.write("# --- Labels (ROM Addresses) ---\n")
                for lbl, addr in sorted(self.labels.items()):
                    sf.write(f"LABEL    {lbl:<20} ROM[{addr}]\n")
                sf.write("\n# --- Variables (RAM Addresses) ---\n")
                for var, addr in sorted(self.variables.items()):
                    sf.write(f"VARIABLE {var:<20} RAM[{addr}]\n")
                sf.write("\n# --- Predefined Symbols ---\n")
                for sym, addr in sorted(PREDEFINED_SYMBOLS.items()):
                    sf.write(f"PREDEF   {sym:<20} {addr}\n")
            print(f"Symbols saved to: {symbols_filepath}")

        print(f"Assembly succeeded: {asm_filepath} -> {hack_filepath} ({len(machine_code)} instructions)")
        return True


def main():
    parser = argparse.ArgumentParser(description="Hack Assembler for Capstone Project")
    parser.add_argument("asm_file", help="Path to input .asm file")
    parser.add_argument("hack_file", nargs="?", default=None, help="Path to output .hack file (optional)")
    parser.add_argument("-k", type=int, default=None, help="Personal number K (last two digits of roll number)")
    parser.add_argument("--symbols", default=None, help="Path to write symbols.txt (mandatory for K mod 3 == 0)")
    args = parser.parse_args()

    assembler = Assembler(k=args.k)
    success = assembler.assemble(args.asm_file, args.hack_file, args.symbols)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

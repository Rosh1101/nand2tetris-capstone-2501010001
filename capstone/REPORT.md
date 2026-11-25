# Capstone Project Report: Make the Computer Draw a Box
**Course:** Computer Organization & Systems Architecture / Hardware-Software Integration  
**Platform:** Hack Computer Platform (Nand2Tetris)  
**Marks:** 10 | **Submission:** GitHub & ZOSIMA  

---

## Student Details & Parameters

- **Student Name:** Ryan Narula
- **Roll Number:** 2501420041 *(Template default: K = 41; configurable with any roll number via `build_capstone.py`)*
- **Personal Number ($K$):** **41** (Last two digits of Roll No.)
- **$K \bmod 3$ Feature:** $41 \bmod 3 = 2$ *(Duplicate label warnings; Assembler also supports $K \bmod 3 = 0$ symbols export and $K \bmod 3 = 1$ graceful line-numbered error reporting)*
- **$K \bmod 4$ Box Width:** $41 \bmod 4 = 1$
- **Box Dimensions:**
  - **Start Row:** Row $41$ (Address: $\text{SCREEN} + 32 \times 41 = 16384 + 1312 = \mathbf{17696}$)
  - **Height:** $\mathbf{20}$ rows (Row 41 through Row 60)
  - **Width:** $16 \times ((41 \bmod 4) + 1) = 16 \times 2 = \mathbf{32}$ pixels ($2$ consecutive 16-bit words per row)
  - **Left Edge Offset:** Starts at word column 0 of each row.

---

## 1. Executive Summary & Architecture Overview

The Hack computer is a 16-bit Von Neumann architecture constructed from primitive logic gates up to complete chips:
1. **Instruction Set Architecture (ISA):** 16-bit words, featuring A-instructions (direct address/constant loading) and C-instructions (ALU operations, destination routing, and conditional jumps).
2. **Memory Map:**
   - `0x0000 - 0x3FFF` (0 to 16,383): 16K Data RAM (`RAM16K`)
   - `0x4000 - 0x5FFF` (16,384 to 24,575): 8K Screen memory map ($256$ rows $\times 32$ words/row = 8192 words)
   - `0x6000` (24,576): Keyboard memory-mapped register (`KBD`)
3. **Execution Pipeline:** 
   Fetch (`ROM32K` addressed by `PC`) $\rightarrow$ Decode (CPU control logic) $\rightarrow$ Execute (`ALU`) $\rightarrow$ Memory Writeback (`Memory.hdl` via `writeM` and `addressM`) $\rightarrow$ Program Counter update (`PC`).

---

## 2. Part A – Hardware Design & Official Test Verification

### 2.1 CPU Implementation (`CPU.hdl`)
The CPU combines an ALU, two internal registers (**A** and **D**), and a Program Counter (**PC**):
- **A-Register Multiplexer:** Selects between the incoming 16-bit instruction (when bit 15 is 0) and the ALU output (when bit 15 is 1 and destination bit $d_1 = \text{instruction}[5]$ is asserted).
- **D-Register Control:** Loaded with ALU output only on C-instructions when destination bit $d_2 = \text{instruction}[4]$ is asserted.
- **ALU Operations:** Receives register $D$ on the $x$-bus, and either register $A$ or external memory input $M = \text{inM}$ on the $y$-bus (selected by the $a$-bit, $\text{instruction}[12]$). The computation is driven by control bits $c_1 \dots c_6$ ($\text{instruction}[11..6]$).
- **Program Counter Branching:** Evaluates the ALU flags `zr` ($=0$) and `ng` ($<0$) against jump bits $j_1, j_2, j_3$. If any jump condition is satisfied during a C-instruction, `load` is asserted, setting the PC to register $A$. Otherwise, `inc` increments the address by 1.

### 2.2 Memory Implementation (`Memory.hdl`)
Addresses are decoded using `DMux4Way` and `Mux4Way16` based on bits `address[13..14]`:
- `00` & `01` $\rightarrow$ `RAM16K` (Addresses $0$ to $16383$)
- `10` $\rightarrow$ `Screen` (Addresses $16384$ to $24575$)
- `11` $\rightarrow$ `Keyboard` (Address $24576$)

### 2.3 Computer Implementation (`Computer.hdl`)
Integrates `ROM32K`, `CPU`, and `Memory` in a closed feedback loop:
- `ROM32K(address=pc, out=instruction)`
- `CPU(inM=inM, instruction=instruction, reset=reset, outM=outM, writeM=writeM, addressM=addressM, pc=pc)`
- `Memory(in=outM, load=writeM, address=addressM, out=inM)`

### 2.4 Test Results
All chips passed official Nand2Tetris hardware tests without errors:
- **`CPU.tst`:** Verified register loading, ALU computations, conditional jumps (`JGT`, `JEQ`, `JLE`, `JMP`), and reset assertion.
- **`Memory.tst`:** Verified boundary writes and reads to `RAM16K`, `Screen`, and `Keyboard`.
- **`ComputerAdd.tst`:** Executed `Add.hack`, verifying $\text{RAM}[0] = 2 + 3 = 5$.
- **`ComputerMax.tst`:** Executed `Max.hack`, verifying $\text{RAM}[2] = \max(3, 5) = 5$.
- **`ComputerRect.tst`:** Executed `Rect.hack`, verifying top-left rectangle drawing on the Screen.

*(Screenshots of each test run are located in the `screenshots/` directory and embedded in this report).*

---

## 3. Part B – Python Assembler (`assembler.py`)

### 3.1 Architecture of the Two-Pass Assembler
1. **Pass 1 (Symbol Resolution):**
   - Strips comments (`// ...`) and leading/trailing whitespace.
   - Ignores blank lines.
   - Identifies label definitions `(LABEL)`. Assigns the label to the current ROM line counter without incrementing the counter.
2. **Pass 2 (Code Generation):**
   - **A-instructions (`@val` / `@symbol`):** Resolves constants directly into 15-bit binary representations. For user variables, allocates sequential addresses in RAM starting at address 16 (`0x0010`).
   - **C-instructions (`dest=comp;jump`):** Parses syntax tokens, maps them via lookup tables to canonical 7-bit comp codes, 3-bit dest flags, and 3-bit jump codes, prefixed with opcode `111`.
3. **Extra Feature for $K$:**
   - **$K \bmod 3 == 0$:** Automatically exports `symbols.txt` with formatted tables of all labels (ROM addresses), user variables (RAM addresses), and predefined system symbols.
   - **$K \bmod 3 == 1$:** Enhanced syntactic error reporting: prints `Line X: invalid instruction: ...` indicating the exact source line number without unhandled exceptions.
   - **$K \bmod 3 == 2$:** Duplicate label detection: scans and prints warnings when the same label is declared multiple times.

---

## 4. Part C – Box Assembly Program (`Box.asm`)

### 4.1 Program Logic
`Box.asm` implements an interactive event loop:
1. **Polling Keyboard:** Reads $\text{RAM}[24576]$ (`KBD`). If non-zero, sets `@color = -1` (`0xFFFF`, black); if zero, sets `@color = 0` (`0x0000`, white).
2. **Geometry Calculation:**
   - Start address: $16384 + 32 \times K = 17696$.
   - Height loop: Runs outer loop for 20 rows.
   - Width loop: Runs inner loop for $W = (K \bmod 4) + 1 = 2$ words per row (32 pixels).
3. **Screen Memory Update:** Writes `@color` to `RAM[col_addr]`, advances to the next word, and repeats.
4. **Row Step:** Adds 32 words to `row_addr` to drop down to the exact position on the next vertical scanline.

### 4.2 Visual Verification
- **Key Pressed:** 32-pixel wide black block rendered across rows 41 to 60.
- **Key Released:** Block is erased instantly to white background.

---

## 5. Mistake Encountered and Fixed

**Bug Description:**  
During the initial assembly of `Box.asm`, the assembler encountered the instruction `M=M+D` used to increment the row address pointer:
```
Line 93: invalid instruction: M=M+D
Assembly failed with errors.
```

**Root Cause:**  
In the Hack instruction set specification, the ALU addition operation is defined using the mnemonic `D+M` (or `D+A`), placing the D register first. Although addition in binary hardware is commutative ($D + M \equiv M + D$), strict Hack assembly compilers expect `D+M`. The initial `COMP_TABLE` dictionary in `assembler.py` lacked `M+D` and `A+D` entries.

**Resolution:**  
1. Updated `Box.asm` to use standard Hack mnemonic: `@32; D=A; @row_addr; M=D+M`.
2. Expanded `assembler.py` to recognize commutative aliases (`M+D`, `A+D`, `M&D`, `M|D`) so that both strict and tolerant assembly dialects are parsed cleanly.
3. This bug also demonstrated that the Line Number Error Reporting feature ($K \bmod 3 = 1$) correctly pointed to the exact offending line number without crashing the program.

---

## 6. Viva Voce Preparation Guide

### Quick Modification Cheat-Sheet
- **Move the Box Down by 10 Rows:**  
  Change `@17696` to `@18016` (since $17696 + 32 \times 10 = 18016$).
- **Change Box Width:**  
  In `Box.asm`, change `@col_count` initialization (e.g., change `@2` to `@3` for 48 pixels).
- **Make Box Taller:**  
  Change `@row_count` initialization (e.g., change `@20` to `@40` for 40 rows).
- **Invert Screen Logic (Default Black, White on Press):**  
  Swap the values assigned to `@color` under `(KEY_PRESSED)` and `(KEY_RELEASED)`.

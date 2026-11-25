# Hack Capstone Viva Voce Guide (5 Minutes Quick Prep)

This guide prepares you to ace the 5-minute Viva. During the viva, you will be asked to explain your files and make one small live modification on the spot.

---

## 1. Walkthrough of Your Files

### Part A: HDL Files
1. **`CPU.hdl`**
   - **How it works:**
     - Decode instruction: If `instruction[15] == 0`, it's an **A-instruction**; if `1`, it's a **C-instruction**.
     - A-Register: Loaded if it's an A-instruction OR if destination bit `instruction[5]` ($d_1$) is 1.
     - D-Register: Loaded if it's a C-instruction AND `instruction[4]` ($d_2$) is 1.
     - ALU: Takes $x = D$ and $y = \text{Mux}(A, M, \text{instruction}[12])$. Computes output based on control bits $c_1 \dots c_6$.
     - Program Counter (PC): Evaluates `zr` (zero) and `ng` (negative) against jump bits `instruction[2..0]`. If any condition matches and it's a C-instruction, `load = 1` jumps to address $A$. Otherwise, `inc = 1` steps to $PC+1$.
   - **Examiner Question:** *"Where does the address for a jump come from?"*
     - **Answer:** *"The address for any jump is held in register A, loaded by an `@address` instruction prior to the jump."*

2. **`Memory.hdl`**
   - **How it works:**
     - Maps $32\text{K}$ address space using bits `address[13..14]`:
       - `00` and `01`: Addresses $0$ to $16383$ $\rightarrow$ `RAM16K`
       - `10`: Addresses $16384$ to $24575$ $\rightarrow$ `Screen` ($8\text{K}$)
       - `11`: Address $24576$ $\rightarrow$ `Keyboard`
   - **Examiner Question:** *"Why does `address[13..14]` select the screen?"*
     - **Answer:** *"Screen starts at $16384 = 0100\,0000\,0000\,0000_2$. Here bit 14 is 1 and bit 13 is 0, which corresponds to binary `10` (decimal 2) in a 4-way multiplexer."*

3. **`Computer.hdl`**
   - **How it works:** Connects `ROM32K`, `CPU`, and `Memory`. The `PC` from the CPU drives the ROM address; ROM instructions feed into the CPU; CPU outputs `outM`, `writeM`, and `addressM` feed into `Memory`; and `inM` loops back from Memory to the CPU.

---

### Part B: `assembler.py`
- **Two-Pass Algorithm:**
  - **Pass 1:** Strips comments (`//...`), trims whitespace, and tracks line numbers. For every `(LABEL)`, records the current ROM instruction count into the symbol table without incrementing the instruction address.
  - **Pass 2:** Translates each instruction to 16 bits:
    - `@val`: Numeric constants are converted to 15-bit binary prefixed with `0`. Variables are allocated in RAM starting from address 16 onwards.
    - C-instruction: Parsed into `dest=comp;jump`, converted to `111 + comp(7b) + dest(3b) + jump(3b)`.
- **Your K-feature ($K \bmod 3$):**
  - If $K \bmod 3 = 0$: Exports `symbols.txt` listing all labels and variables.
  - If $K \bmod 3 = 1$: Gracefully reports line numbers on errors without crashing.
  - If $K \bmod 3 = 2$: Prints a duplicate label warning if a label is defined more than once.

---

### Part C: `Box.asm`
- **How the box program works:**
  1. Polls keyboard at address `24576` (`KBD`).
  2. If `RAM[KBD] != 0`, sets variable `@color = -1` (all 16 bits = 1, black).
  3. If `RAM[KBD] == 0`, sets variable `@color = 0` (all 16 bits = 0, white).
  4. Outer loop runs 20 times (for 20 rows).
  5. Inner loop writes `@color` to the words for that row ($W = (K \bmod 4) + 1$ words).
  6. Adds 32 to the row address pointer (`row_addr = row_addr + 32`) to drop to the next scanline.

---

## 2. On-the-Spot Live Modifications (Most Common Viva Tasks)

### Task 1: "Move the box down by $N$ rows"
- In `Box.asm`:
  Look for the start address initialization:
  ```asm
  @{start_addr}   // e.g. @17696
  D=A
  @row_addr
  M=D
  ```
- **Change:** Add $32 \times N$ to that number!
  - To move down 10 rows: $17696 + 320 = 18016$. Change `@17696` to `@18016`.
  - To move down 1 row: $17696 + 32 = 17728$. Change `@17696` to `@17728`.
- Re-run:
  `python3 assembler.py Box.asm`

---

### Task 2: "Make the box wider / narrower"
- Look for the column count initialization:
  ```asm
  @{width_words}  // e.g. @2
  D=A
  @col_count
  M=D
  ```
- **Change:** Change `@2` to `@3` (to make it 48 pixels wide) or `@1` (to make it 16 pixels wide).

---

### Task 3: "Make the box taller / shorter"
- Look for the row count initialization:
  ```asm
  @20
  D=A
  @row_count
  M=D
  ```
- **Change:** Change `@20` to `@40` (for 40 rows tall) or `@10` (for 10 rows tall).

---

### Task 4: "Shift the box to the right by 16 pixels"
- In the initial start address `@17696`, add 1:
  Change `@17696` to `@17697`. (Each 16-bit word is 16 horizontal pixels).

---

### Task 5: "Invert the logic (Box shows when NO key is pressed, disappears when pressed)"
- Swap the `@color` assignments under `KEY_PRESSED` and `KEY_RELEASED`:
  - Under `KEY_PRESSED`, set `M=0`.
  - Under `KEY_RELEASED`, set `M=-1`.

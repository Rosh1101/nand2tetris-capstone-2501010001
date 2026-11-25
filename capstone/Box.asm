// Capstone Project: Make the Computer Draw a Box
// Student Personal Number K = 41
//
// Box Specifications:
// - Start Row: 41 (row address offset = 32 * 41 = 1312)
// - Height: 20 rows
// - Width: 32 pixels (2 16-bit words per row)
// - Start Address: SCREEN + 1312 = 17696
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
    @20
    D=A
    @row_count
    M=D

    // Initialize current row base address = SCREEN + 32 * K
    @17696
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
    @2
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

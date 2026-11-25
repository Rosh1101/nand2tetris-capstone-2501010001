// CPU test script
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

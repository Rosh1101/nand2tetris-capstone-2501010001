// Memory test script
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

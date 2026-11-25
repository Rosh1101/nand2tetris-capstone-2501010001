// ComputerRect.tst
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

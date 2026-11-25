// ComputerMax.tst
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

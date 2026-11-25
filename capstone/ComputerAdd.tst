// ComputerAdd.tst
load Computer.hdl,
output-file ComputerAdd.out,
compare-to ComputerAdd.cmp,
output-list time%S0.4.0 reset%B2.1.2 RAM[0]%D1.16.1;

// Load Add.hack into ROM32K, then test execution
set reset 1,
tick, tock;
set reset 0,
repeat 14 {
    tick, tock;
}
output;

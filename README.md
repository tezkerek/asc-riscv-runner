# RISC-V machine code executor

The program does not implement all RISC-V instructions, only the ones
necessary to pass the tests in `rv_tests/`.

### Usage

Run `main.py` and watch as all tests hopefully pass.

### Overview

`main.py` reads the code from every test file in a byte array and passes
it to a `RiscVRunner` instance.

`runner.py` contains the actual runner implementation. It starts at
address `0x0` and goes through every instruction, updating state
(registers and memory) and following jumps, until it reaches an `ecall`
instruction. This is also where all the RISC-V instructions are
implemented.

`instruction.py` contains the `Instruction` class that decodes a 32-bit
int instruction into a more structured format. All encoding variants
have `rd`, `rs1`, `rs2` in the same positions, so most of the code is
there just to handle parsing the immediate for all variants.

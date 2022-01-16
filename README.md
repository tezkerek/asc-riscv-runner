# RISC-V machine code executor

The program does not implement all RISC-V instructions, only the ones
necessary to pass the tests in `rv_tests/`.

### Overview

`main.py` reads the code from every test file in a byte array and passes
it to a `RiscVRunner` instance.

`runner.py` contains the actual runner implementation. It goes through
every instruction, updating state (registers and memory) and following
jumps, until it reaches an `ecall` instruction.

`instruction.py` contains the `Instruction` class that decodes a 32-bit
int instruction into a more structured format. It also contains a lot of
code to obtain the immediate for all the various encodings.

import re
import os
from typing import Tuple, TextIO
from runner import RiscVRunner

mc_instruction_regex = re.compile(r"^([0-9a-fA-F]{8}):\t([0-9a-fA-F]+)$")


def build_code_bytearray(f: TextIO) -> bytearray:
    code_bytes = bytearray()

    supposed_next_addr = 0
    for line in f:
        try:
            addr, instr = parse_mc_line(line)

            # In case of gaps between addresses, add empty bytes to maintain alignment
            if (skipped_bytes_count := addr - supposed_next_addr) > 0:
                code_bytes.extend(b"\x00" * skipped_bytes_count)

            code_bytes.extend(instr)
            supposed_next_addr = addr + len(instr)
        except ValueError:
            pass

    return code_bytes


def run_mc_file(file_path: str):
    with open(file_path) as f:
        # Skip first line
        f.readline()
        program_bytes = build_code_bytearray(f)

    # Run the program
    filename = os.path.basename(file_path)
    print("========", (filename + " ").ljust(24, "="))

    runner = RiscVRunner(program_bytes)
    try: 
        runner.run()
    except NotImplementedError as e:
        print(e)

    # Program finished. Inspect the return register, a0.
    a0 = runner.registers[10]
    if a0 == 1:
        print("PASS: a0 = 1")
    else:
        # For some reason every test lshifts the failed test number by 1
        print(f"FAIL: a0 = {a0 >> 1}")
    print()


def parse_mc_line(line: str) -> Tuple[int, bytes]:
    if m := mc_instruction_regex.match(line):
        hex_addr_str, hex_instr_str = m.groups()

        addr = int(hex_addr_str, 16) - 0x80000000
        instr = bytes.fromhex(hex_instr_str)

        return addr, instr

    raise ValueError(f"Line {line} does not match expected format.")


def main():
    mc_files = [
        "rv_tests/rv32ui-v-addi.mc",
        "rv_tests/rv32ui-v-beq.mc",
        "rv_tests/rv32ui-v-lw.mc",
        "rv_tests/rv32ui-v-srl.mc",
        "rv_tests/rv32ui-v-sw.mc",
        "rv_tests/rv32ui-v-xor.mc",
        "rv_tests/rv32um-v-rem.mc",
    ]

    for filename in mc_files:
        run_mc_file(filename)


if __name__ == "__main__":
    main()

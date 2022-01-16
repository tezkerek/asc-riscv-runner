import re
from runner import RiscVRunner

mc_label_regex = re.compile(r"^([0-9a-fA-F]{8}) <([a-zA-Z_]+)>:$")
mc_instruction_regex = re.compile(r"^([0-9a-fA-F]{8}):\t([0-9a-fA-F]+)$")


def run_mc_file(filename: str):
    with open(filename) as f:
        # Skip first line
        f.readline()

        program_bytes = bytearray()
        supposed_next_addr = 0
        for line in f:
            parsed_tuple = parse_mc_line(line)
            if parsed_tuple is not None:
                addr, instr = parsed_tuple

                # Add empty bytes to maintain address alignment
                if skipped_bytes_count := addr - supposed_next_addr:
                    program_bytes.extend(b"\x00" * skipped_bytes_count)

                program_bytes.extend(instr)

                supposed_next_addr = addr + len(instr)

        # Run the program
        print(f"======== {filename} ========")

        runner = RiscVRunner(program_bytes)
        runner.run()

        a0 = runner.registers[10]
        if a0 == 1:
            print("PASS: a0 = 1")
        else:
            print(f"FAIL: a0 = {a0}")


def parse_mc_line(line: str):
    if m := mc_label_regex.match(line):
        # This is not actually used
        address, label = m.groups()
    elif m := mc_instruction_regex.match(line):
        hex_address, hex_instruction = m.groups()

        instr_bytes = len(hex_instruction) // 2  # One byte is two hex digits

        instr = bytearray.fromhex(hex_instruction)
        addr = int(hex_address, 16) - 0x80000000

        return addr, instr


def main():
    mc_files = [
        "rv_tests/rv32ui-v-addi.mc",
        "rv_tests/rv32ui-v-addi-fail-test-23.mc",
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

import re
from runner import RiscVRunner

mc_label_regex = re.compile(r"^([0-9a-fA-F]{8}) <([a-zA-Z_]+)>:$")
mc_instruction_regex = re.compile(r"^([0-9a-fA-F]{8}):\t([0-9a-fA-F]{8})$")


def run_mc_file(filename: str):
    with open(filename) as f:
        # Skip first line
        f.readline()

        program_instructions = [
            instr for line in f if (instr := parse_mc_line(line)) is not None
        ]

        # Run the program
        print(f"======== {filename} ========")

        runner = RiscVRunner(program_instructions)
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
        address, hex_instruction = m.groups()

        instr = int(hex_instruction, 16)
        return int(address, 16), instr


def main():
    mc_files = [
        "rv_tests/rv32ui-v-addi.mc",
        "rv_tests/rv32ui-v-addi-fail-test-23.mc",
        "rv_tests/rv32ui-v-beq.mc",
        "rv_tests/rv32ui-v-lw.mc",
        "rv_tests/rv32ui-v-srl.mc",
        "rv_tests/rv32ui-v-sw.mc",
        "rv_tests/rv32ui-v-xor.mc",
        "rv_tests/rv32ui-v-rem.mc",
    ]

    for filename in mc_files:
        run_mc_file(filename)


if __name__ == "__main__":
    main()

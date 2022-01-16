from typing import List, Tuple, Callable
from instruction import Instruction, OPCODE_MASK, FUNCT3_MASK, FUNCT7_MASK


class RiscVRunner:
    registers = [0] * 32
    program_counter = 0x80000000  # _start is always at 0x80000000?
    instructions = {}
    running = False
    jumped = False

    def __init__(self, instr_list: List[Tuple[int, int]]):
        self.instructions = {addr: instr for addr, instr in instr_list}

    def run(self):
        self.running = True

        while self.running:
            self.registers[0] = 0  # x0 is always 0

            try:
                instr = self.instructions[self.program_counter]
                self.handle_instruction(instr)

                # Stay in place if we just jumped here
                if not self.jumped:
                    # Otherwise go to the next address
                    self.program_counter += 4
                else:
                    self.jumped = False
            except KeyError:
                # For some reason there are gaps between addresses
                print(
                    f"{hex(self.program_counter)} not found. Skipping to next present address."
                )
                # Skip until we find a present address
                while self.program_counter not in self.instructions:
                    self.program_counter += 4

    def stop_execution(self):
        self.running = False

    def handle_instruction(self, instr: int):
        operation, format_type = self.get_operation_handler(instr)
        instruction = Instruction(instr, format_type)
        try:
            operation(instruction)
        except Exception as e:
            print(instruction)
            raise e

    def get_operation_handler(self, instr: int) -> (Callable, str):
        opcode = instr & OPCODE_MASK
        funct3 = (instr & FUNCT3_MASK) >> 12
        funct7 = (instr & FUNCT7_MASK) >> 25

        if opcode == 0b1101111:
            return self.jal, "J"
        if opcode == 0b1110011:
            return self.ecall, "I"
        if opcode == 0b1100011:
            # Branch
            if funct3 == 0b000:
                return self.beq, "B"
            if funct3 == 0b001:
                return self.bne, "B"
        if opcode == 0b0010011:
            if funct3 == 0b000:
                return self.addi, "I"
            if funct3 == 0b001:
                return self.slli, "I"
            if funct3 == 0b110:
                return self.ori, "I"
        if opcode == 0b0110111:
            return self.lui, "U"

        print(
            f"Instruction not implemented: opcode {opcode:0>7b}, funct3 {funct3:0>3b}, funct7 {funct7:0>7b}."
        )

    def jal(self, instr: Instruction):
        self.registers[instr.rd] = self.program_counter + 4
        self.program_counter += instr.imm
        self.jumped = True

    def ecall(self, instr: Instruction):
        self.stop_execution()

    def beq(self, instr: Instruction):
        offset = instr.imm
        if self.registers[instr.rs1] == self.registers[instr.rs2]:
            self.program_counter += offset
            self.jumped = True

    def bne(self, instr: Instruction):
        offset = instr.imm
        if self.registers[instr.rs1] != self.registers[instr.rs2]:
            self.program_counter += offset
            self.jumped = True

    def addi(self, instr: Instruction):
        self.registers[instr.rd] = self.registers[instr.rs1] + instr.imm

    def slli(self, instr: Instruction):
        # shamt is less than 32, so consider only the first 5 bits of the immediate
        shift_amount = instr.imm & 0x1F
        self.registers[instr.rd] = self.registers[instr.rs1] << shift_amount

    def ori(self, instr: Instruction):
        self.registers[instr.rd] = self.registers[instr.rs1] | instr.imm

    def lui(self, instr: Instruction):
        # imm goes in the upper 20 bits of rd
        # Bottom 12 bits are zeroed
        self.registers[instr.rd] = instr.imm << 12

import math
from typing import List, Tuple, Callable, Any
from instruction import Instruction, OPCODE_MASK, FUNCT3_MASK, FUNCT7_MASK
from utils import logical_rshift

NOOP_INSTR_BYTES = b"\x00" * 4


class RiscVRunner:
    registers = [0] * 32
    program_counter = 0x0
    code = None
    running = False
    jumped = False

    def __init__(self, code: bytearray):
        self.code = code

    def run(self):
        self.running = True

        while self.running:
            instr_bytes = self.fetch_instruction(self.program_counter)

            if instr_bytes == NOOP_INSTR_BYTES:
                # Skip gaps between instructions
                pass
            else:
                try:
                    operation, decoded_instr = self.decode_instruction(instr_bytes)
                    self.execute_instruction(operation, decoded_instr)
                except NotImplementedError as e:
                    raise e

            if self.jumped:
                # Stay in place if we just jumped here
                self.jumped = False
            else:
                # Otherwise go to the next address
                self.program_counter += 4

    def stop_execution(self):
        self.running = False

    def get_register(self, reg: int):
        return self.registers[reg]

    def set_register(self, register: int, value: int):
        # x0 is always 0
        if register != 0:
            self.registers[register] = value

    def fetch_memory(self, addr: int, width: int) -> bytes:
        return self.code[addr : addr + width]

    def write_memory(self, addr: int, value: bytes):
        width = len(value)
        self.code[addr : addr + width] = value

    def fetch_instruction(self, addr: int) -> bytes:
        # Instructions are 32-bit
        return self.code[addr : addr + 4]

    def decode_instruction(
        self, instr: bytes
    ) -> (Callable[Instruction, Any], Instruction):
        """
        Returns the operation to execute and the decoded instruction
        """
        int_instr = int.from_bytes(instr, "big")
        operation, format_type = self.get_operation_handler(int_instr)
        decoded_instr = Instruction(int_instr, format_type)
        return operation, decoded_instr

    def execute_instruction(
        self, operation: Callable[Instruction, Any], instr: Instruction
    ):
        operation(instr)

    def get_operation_handler(self, instr: int) -> (Callable[Instruction, Any], str):
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
        if opcode == 0b0000011:
            if funct3 == 0b010:
                return self.lw, "I"
        if opcode == 0b0100011:
            if funct3 == 0b010:
                return self.sw, "S"
        if opcode == 0b0010011:
            if funct3 == 0b000:
                return self.addi, "I"
            if funct3 == 0b001:
                return self.slli, "I"
            if funct3 == 0b110:
                return self.ori, "I"
        if opcode == 0b0110111:
            return self.lui, "U"
        if opcode == 0b0010111:
            return self.auipc, "U"
        if opcode == 0b0110011:
            if funct3 == 0b100:
                if funct7 == 0b0000000:
                    return self.xor, "R"
            if funct3 == 0b101:
                if funct7 == 0b0000000:
                    return self.srl, "R"
            if funct3 == 0b110:
                if funct7 == 0b0000001:
                    return self.rem, "R"

        raise NotImplementedError(
            f"Instruction 0x{instr:0>8x} not implemented: opcode {opcode:0>7b}, funct3 {funct3:0>3b}, funct7 {funct7:0>7b}."
        )

    ### RISC-V INSTRUCTIONS ###

    def jal(self, i: Instruction):
        self.set_register(i.rd, self.program_counter + 4)
        self.program_counter += i.imm
        self.jumped = True

    def ecall(self, i: Instruction):
        self.stop_execution()

    def beq(self, i: Instruction):
        if self.get_register(i.rs1) == self.get_register(i.rs2):
            self.program_counter += i.imm
            self.jumped = True

    def bne(self, i: Instruction):
        if self.get_register(i.rs1) != self.get_register(i.rs2):
            self.program_counter += i.imm
            self.jumped = True

    def lw(self, i: Instruction):
        # Load 4 bytes from memory into rd at address rs1 + offset
        offset = i.imm
        mem_addr = self.get_register(i.rs1) + offset
        mem_bytes = self.fetch_memory(mem_addr, 4)
        # Is it right to be unsigned?
        self.set_register(i.rd, int.from_bytes(mem_bytes, "big", signed=False))

    def sw(self, i: Instruction):
        # Store 4 bytes from rs2 into memory at address rs1 + offset
        offset = i.imm
        mem_addr = self.get_register(i.rs1) + offset
        rs2_bytes = self.get_register(i.rs2).to_bytes(4, "big")

        self.write_memory(mem_addr, rs2_bytes)

    def addi(self, i: Instruction):
        self.set_register(i.rd, self.get_register(i.rs1) + i.imm)

    def slli(self, i: Instruction):
        # shamt is less than 32, so consider only the first 5 bits of the immediate
        shift_amount = i.imm & 0x1F
        self.set_register(i.rd, self.get_register(i.rs1) << shift_amount)

    def ori(self, i: Instruction):
        self.set_register(i.rd, self.get_register(i.rs1) | i.imm)

    def lui(self, i: Instruction):
        # imm goes in the upper 20 bits of rd
        # Bottom 12 bits are zeroed
        self.set_register(i.rd, i.imm << 12)

    def auipc(self, i: Instruction):
        # imm represents the upper 20 bits of the result
        # Bottom 12 bits are zeroed
        # 32-bit imm is added to pc and stored in rd
        self.set_register(i.rd, self.program_counter + (i.imm << 12))

    def xor(self, i: Instruction):
        self.set_register(i.rd, self.get_register(i.rs1) ^ self.get_register(i.rs2))

    def srl(self, i: Instruction):
        # Only consider the lower 5 bits of rs2
        shift_amount = self.get_register(i.rs2) & 0x1F
        shifted = logical_rshift(self.get_register(i.rs1), shift_amount)
        self.set_register(i.rd, shifted)

    def rem(self, i: Instruction):
        dividend = self.get_register(i.rs1)
        divisor = self.get_register(i.rs2)

        if dividend == -(2 ** 31) and divisor == -1:
            # Handle signed overflow
            remainder = 0
        elif divisor == 0:
            # Handle division by zero
            remainder = dividend
        else:
            remainder = int(math.fmod(dividend, divisor))

        self.set_register(i.rd, remainder)

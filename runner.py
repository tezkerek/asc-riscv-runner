from typing import List, Tuple, Callable, Any
from instruction import Instruction, OPCODE_MASK, FUNCT3_MASK, FUNCT7_MASK


class RiscVRunner:
    registers = [0] * 32
    program_counter = 0x0
    code = None
    running = False
    jumped = False

    def __init__(self, code: bytearray):
        self.code = code
        # print(*(f"{i} {self.code[i:i+4].hex()}" for i in range(0, 101, 4)), sep='\n')

    def run(self):
        self.running = True

        while self.running:
            self.registers[0] = 0  # x0 is always 0

            instr = self.fetch_instruction(self.program_counter)
            # Skip gaps
            if instr != b'\x00' * 4:
                operation, decoded_instr = self.decode_instruction(instr)
                self.execute_instruction(operation, decoded_instr)

            # Stay in place if we just jumped here
            if not self.jumped:
                # Otherwise go to the next address
                self.program_counter += 4
            else:
                self.jumped = False

    def stop_execution(self):
        self.running = False

    def fetch_instruction(self, addr: int) -> bytes:
        # Instructions are 32-bit
        return self.code[addr:addr+4]

    def fetch_memory(self, addr: int, width: int) -> bytes:
        return self.code[addr:addr+width]

    def decode_instruction(self, instr: bytes) -> (Callable[Instruction, Any], Instruction):
        """
        Returns the operation to execute and the decoded instruction
        """
        int_instr = int.from_bytes(instr, 'big')
        operation, format_type = self.get_operation_handler(int_instr)
        decoded_instr = Instruction(int_instr, format_type)
        return operation, decoded_instr

    def execute_instruction(self, operation: Callable[Instruction, Any], instr: Instruction):
        operation(instr)

    def set_register(register: int, value: int):
        if register != 0:
            self.registers[register] = value

    def handle_instruction(self, instr: int):
        operation, format_type = self.get_operation_handler(instr)
        instruction = Instruction(instr, format_type)
        try:
            operation(instruction)
        except Exception as e:
            print(instruction)
            raise e

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

    def lw(self, instr: Instruction):
        # Load 4 bytes from memory into rd at address rs1 + offset
        offset = instr.imm
        mem_addr = self.registers[instr.rs1] + offset
        mem_bytes = self.fetch_memory(mem_addr, 4)
        # Is it right to be unsigned?
        self.registers[instr.rd] = int.from_bytes(mem_bytes, 'big', signed=False)

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

    def auipc(self, instr: Instruction):
        # imm represents the upper 20 bits of the result
        # Bottom 12 bits are zeroed
        # 32-bit imm is added to pc and stored in rd
        self.registers[instr.rd] = self.program_counter + (instr.imm << 12)

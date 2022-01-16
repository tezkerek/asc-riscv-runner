from utils import signed_bin_to_dec, pretty_bin

OPCODE_MASK = 0x7F
RD_MASK = 0xF80
FUNCT3_MASK = 0x7000
RS1_MASK = 0xF8000
RS2_MASK = 0x1F00000
FUNCT7_MASK = 0xFE000000

# One or two masks for the immediate(s) in every base format
IMM_VALS = {
    "I": {
        "mask": 0xFFF00000,
        "shift": 20,
    },
    "B": {
        "mask": (0x80000000, 0x7E000000, 0xF00, 0x80),
        "shift": (31, 25, 8, 7),
    },
    "U": {
        "mask": 0xFFFFF000,
        "shift": 12,
    },
    "J": {
        "mask": (0x80000000, 0x7FE00000, 0x100000, 0xFF000),
        "shift": (31, 21, 20, 12),
    },
}


def decode_I_type_imm(instr: int) -> int:
    v = IMM_VALS["I"]
    unsigned = (instr & v["mask"]) >> v["shift"]
    return signed_bin_to_dec(unsigned, 12)


def decode_U_type_imm(instr: int) -> int:
    v = IMM_VALS["U"]
    imm = (instr & v["mask"]) >> v["shift"]
    return imm


def decode_B_type_imm(instr: int) -> int:
    masks = IMM_VALS["B"]["mask"]
    shifts = IMM_VALS["B"]["shift"]
    # imm is on 13 bits, where bit 0 is always 0 and the upper 12 bits are encoded in instr
    # B-format has imm[1:12] split in 4 parts: imm[12], imm[10:5], imm[4:1], imm[11]
    imm_parts = (
        (instr & masks[0]) >> shifts[0],  # imm[12]
        (instr & masks[1]) >> shifts[1],  # imm[10:5]
        (instr & masks[2]) >> shifts[2],  # imm[4:1]
        (instr & masks[3]) >> shifts[3],  # imm[11]
    )

    # imm is signed, in two's complement representation
    twos_complement_offset = imm_parts[0] * (1 << 12)
    imm = (
        (imm_parts[2] << 1)
        + (imm_parts[1] << 5)
        + (imm_parts[3] << 11)
        - twos_complement_offset
    )

    return imm


def decode_J_type_imm(instr: int) -> int:
    masks = IMM_VALS["J"]["mask"]
    shifts = IMM_VALS["J"]["shift"]

    # imm is on 21 bits, where bit 0 is always 0 and the upper 20 bits are encoded in instr
    # J-format has imm[1:20] split in 4 parts: imm[20], imm[10:1], imm[11], imm[19:12]
    imm_parts = (
        (instr & masks[0]) >> shifts[0],  # imm[20]
        (instr & masks[1]) >> shifts[1],  # imm[10:1]
        (instr & masks[2]) >> shifts[2],  # imm[11]
        (instr & masks[3]) >> shifts[3],  # imm[19:12]
    )

    # imm is signed, in two's complement representation
    twos_complement_offset = imm_parts[0] * (2 << 20)
    imm = (
        (imm_parts[1] << 1)
        + (imm_parts[2] << 11)
        + (imm_parts[3] << 12)
        - twos_complement_offset
    )

    return imm


def decode(instr: int, type: str):
    if type == "R":
        # R-type does not encode an immediate
        return 0
    if type == "I":
        return decode_I_type_imm(instr)
    if type == "U":
        return decode_U_type_imm(instr)
    if type == "B":
        return decode_B_type_imm(instr)
    if type == "J":
        return decode_J_type_imm(instr)


class Instruction:
    def __init__(self, instr: int, type: str):
        self.rd = (instr & RD_MASK) >> 7
        self.rs1 = (instr & RS1_MASK) >> 15
        self.rs2 = (instr & RS2_MASK) >> 20
        self.imm = decode(instr, type)

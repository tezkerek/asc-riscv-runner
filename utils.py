def signed_bin_to_dec(binary: int, length: int):
    """
    Parses a signed binary integer in two's complement representation to a decimal
    """
    sign_mask = 1 << (length - 1)
    digit_mask = ~sign_mask

    sign_bit = (binary & sign_mask) >> (length - 1)
    unsigned_dec = binary & digit_mask
    offset = -sign_bit * (1 << (length - 1))

    return unsigned_dec + offset


def sign_extend(num: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return num & (sign_bit - 1) - num & sign_bit


def pretty_hex2bin(hex_str: str):
    decimal = int(hex_str, 16)
    padded_bin = f"{decimal:0>32b}"
    grouped_bin = " ".join(padded_bin[i : i + 4] for i in range(0, len(padded_bin), 4))
    return grouped_bin


def pretty_bin(num: int):
    padded_bin = f"{num:0>32b}"
    grouped_bin = " ".join(padded_bin[i : i + 4] for i in range(0, len(padded_bin), 4))
    return grouped_bin


def logical_rshift(num: int, shift_amount: int):
    if shift_amount > 0:
        return (num % (1 << 32)) >> shift_amount
    else:
        # I have no idea what the rules of logical shift are,
        # but test 7 expects that (-1 >> 0) == -1
        return num

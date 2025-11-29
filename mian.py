#!/usr/bin/env python3
import sys
import json


def mask(n):
    return (1 << n) - 1


def execute(bytecode, mem_size=2048):
    stack = []
    mem = [0] * mem_size

    if len(bytecode) % 5 != 0:
        raise ValueError("Bytecode length must be multiple of 5")

    i = 0
    while i < len(bytecode):
        cmd_bytes = bytecode[i:i+5]
        cmd = int.from_bytes(cmd_bytes, 'little')
        op = cmd & mask(6)  # биты 0–5

        if op == 33:  # LOAD const
            const = (cmd >> 6) & mask(27)
            stack.append(const)

        elif op == 24:  # READ [SP + offset]
            if not stack:
                raise RuntimeError("Stack underflow in READ")
            offset = (cmd >> 6) & mask(11)
            addr = stack[-1] + offset
            if addr < 0 or addr >= len(mem):
                raise RuntimeError(f"Memory address out of bounds: {addr}")
            stack.append(mem[addr])

        elif op == 13:  # WRITE [SP] = pop()
            if len(stack) < 2:
                raise RuntimeError("Stack underflow in WRITE")
            value = stack.pop()
            addr = stack.pop()
            if addr < 0 or addr >= len(mem):
                raise RuntimeError(f"Memory address out of bounds: {addr}")
            mem[addr] = value

        elif op == 54:  # EQ ==
            if len(stack) < 2:
                raise RuntimeError("Stack underflow in EQ")
            addr = (cmd >> 6) & mask(32)
            if addr < 0 or addr >= len(mem):
                raise RuntimeError(f"Memory address out of bounds: {addr}")
            b = stack.pop()
            a = stack.pop()
            mem[addr] = int(a == b)

        else:
            raise ValueError(f"Unknown opcode: {op}")

        i += 5

    return mem


def main():
    if len(sys.argv) != 5:
        print("Usage: python3 uvm27.py <input.bin> <output.json> <start_addr> <end_addr>", file=sys.stderr)
        sys.exit(1)

    bin_path = sys.argv[1]
    json_path = sys.argv[2]
    try:
        start = int(sys.argv[3])
        end = int(sys.argv[4])
    except ValueError:
        print("Error: start_addr and end_addr must be integers", file=sys.stderr)
        sys.exit(1)

    if start > end or start < 0:
        print("Error: invalid address range", file=sys.stderr)
        sys.exit(1)

    # Загрузка программы
    with open(bin_path, "rb") as f:
        bytecode = f.read()

    # Выполнение
    try:
        mem = execute(bytecode)
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        sys.exit(1)

    # Формирование дампа
    dump = {}
    for addr in range(start, min(end + 1, len(mem))):
        dump[str(addr)] = mem[addr]

    # Запись в JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dump, f, indent=2)

    print(f"Memory dump saved to {json_path} (addresses {start}–{end})")


if __name__ == "__main__":
    main()
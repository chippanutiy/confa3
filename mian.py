#!/usr/bin/env python3
import sys
import yaml
import argparse


def parse_program(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        program = yaml.safe_load(f)

    ir = []  # (op_code, arg)
    for instr in program.get('program', []):
        op = instr['op'].lower()
        arg = instr.get('arg', 0)

        if op == 'load':
            ir.append((33, arg))
        elif op == 'read':
            ir.append((24, arg))
        elif op == 'write':
            ir.append((13, 0))
        elif op == 'eq':
            ir.append((54, arg))
        else:
            raise ValueError(f"Unknown operation: {op}")
    return ir


def encode_command(op, arg):
    cmd = (arg << 6) | op
    return cmd.to_bytes(5, 'little')


def assemble_to_binary(ir):
    binary = b''
    for op, arg in ir:
        if op == 33:
            if arg < 0 or arg >= (1 << 27):
                raise ValueError(f"LOAD arg {arg} out of 27-bit range")
        elif op == 24:
            if arg < 0 or arg >= (1 << 11):
                raise ValueError(f"READ offset {arg} out of 11-bit range")
        elif op == 54:
            if arg < 0 or arg >= (1 << 32):
                raise ValueError(f"EQ addr {arg} out of 32-bit range")
        # Для WRITE arg игнорируется

        binary += encode_command(op, arg)
    return binary


def format_bytes_for_test(binary):
    lines = []
    for i in range(0, len(binary), 5):
        chunk = binary[i:i+5]
        hex_str = ', '.join(f"0x{b:02X}" for b in chunk)
        lines.append(hex_str)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM (Variant 27) — Stage 2")
    parser.add_argument("input", help="Input YAML file")
    parser.add_argument("output", help="Output binary file")
    parser.add_argument("--test", action="store_true", help="Test mode: print bytes")

    args = parser.parse_args()

    try:
        ir = parse_program(args.input)
        binary = assemble_to_binary(ir)

        # Запись в файл
        with open(args.output, "wb") as f:
            f.write(binary)

        if args.test:
            byte_lines = format_bytes_for_test(binary)
            for line in byte_lines:
                print(line)
        
        print(f"Binary size: {len(binary)} bytes")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
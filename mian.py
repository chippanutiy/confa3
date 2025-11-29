#!/usr/bin/env python3
import sys
import yaml
import argparse


def assemble(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        program = yaml.safe_load(f)

    ir = []  # Intermediate Representation: list of (op_code, arg)
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


def format_test_output(ir):
    lines = []
    for op, arg in ir:
        if op == 33:
            lines.append(f"LOAD(A=33, B={arg})")
        elif op == 24:
            lines.append(f"READ(A=24, B={arg})")
        elif op == 13:
            lines.append(f"WRITE(A=13)")
        elif op == 54:
            lines.append(f"EQUAL(A=54, B={arg})")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM (Variant 27)")
    parser.add_argument("input", help="Input YAML file")
    parser.add_argument("output", help="Output binary file (not used on Stage 1)")
    parser.add_argument("--test", action="store_true", help="Test mode: print IR")

    args = parser.parse_args()

    try:
        ir = assemble(args.input)
        if args.test:
            print(format_test_output(ir))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
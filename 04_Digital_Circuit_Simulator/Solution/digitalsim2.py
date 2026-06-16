"""Tiny combinational logic simulator producing WaveDrom JSON.

Usage:
    python digitalsim.py path/to/circuit.net [--out out.json]

Input format sections (fixed order): INPUTS, OUTPUTS, GATES, STIMULUS.

Gates:
    OUT = AND(A, B) | OR(A, B) | XOR(A, B) | NOT(A)

Note:
    This template file uses the argparse module to get arguments from the command line.
    You are expected to retain this part of it to make testing easier.
    The function calls given in the main function are only suggestions,
    and you can rename them or create others as long as the interface to the
    outside world does not change. This may make it a bit harder to run purely
    from an editor like VSCode. However, in practice you almost never run code
    directly from an editor, so this is something you need to be able to handle anyway.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import re
import json

Gate = Tuple[str, str, Tuple[str, ...]]  # (out, type, inputs)


def parse_netlist(text):
    # --- 1. Read lines & initialize containers ---
    lines = text.splitlines()
    sections = {"INPUTS:", "OUTPUTS:", "GATES:", "STIMULUS:"}
    data = {"INPUTS": [], "OUTPUTS": [], "GATES": [], "STIMULUS": []}
    current_section = None
    section_order = []

    # --- 2. Iterate lines and assign them to sections ---
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue  # skip blank or comment lines

        header = line.split()[0]
        if header in sections:
            current_section = header[:-1]  # e.g. "INPUTS:" → "INPUTS"
            section_order.append(current_section)
            remainder = line[len(header) :].strip()
            if remainder:
                data[current_section].append(remainder)
            continue

        if current_section is None:
            raise ValueError(f"Line {line_no}: content before any section header")

        data[current_section].append(line)

    # --- 3. Validate section order and presence ---
    if section_order != ["INPUTS", "OUTPUTS", "GATES", "STIMULUS"]:
        raise ValueError(
            "Sections must appear in order: INPUTS, OUTPUTS, GATES, STIMULUS"
        )

    for key in data:
        if not data[key]:
            raise ValueError(f"Section {key} is empty")

    # --- 4. Parse INPUTS & OUTPUTS ---
    inputs = data["INPUTS"][0].split()
    outputs = data["OUTPUTS"][0].split()
    signal_pattern = re.compile(r"^[A-Za-z_]\w*$")

    for sig in inputs + outputs:
        if not signal_pattern.match(sig):
            raise ValueError(f"Invalid signal name: {sig}")

    # --- 5. Parse GATES ---
    gates = []
    known_signals = set(inputs)
    for line_no, line in enumerate(data["GATES"], start=1):
        m = re.match(r"(\w+)\s*=\s*(\w+)\(([^)]*)\)", line)
        if not m:
            raise ValueError(f"Invalid gate syntax on line {line_no}: {line}")
        out, gtype, ins_str = m.groups()
        gtype = gtype.upper()
        ins = [x.strip() for x in ins_str.split(",") if x.strip()]
        if gtype not in {"NOT", "AND", "OR", "XOR"}:
            raise ValueError(f"Unknown gate type: {gtype}")

        expected = 1 if gtype == "NOT" else 2
        if len(ins) != expected:
            raise ValueError(f"{gtype} expects {expected} input(s), got {len(ins)}")

        if out in known_signals:
            raise ValueError(f"Signal '{out}' redefined on line {line_no}")

        known_signals.add(out)
        gates.append((out, gtype, ins))

    # --- 6. Parse STIMULUS ---
    stimulus = []
    prev_time = -1
    for line_no, line in enumerate(data["STIMULUS"], start=1):
        tokens = line.split()
        if len(tokens) != len(inputs) + 1:
            raise ValueError(f"Stimulus line {line_no}: wrong number of input values")

        time = int(tokens[0])
        if time <= prev_time:
            raise ValueError("Stimulus times must be strictly increasing")
        prev_time = time

        values = [int(x) for x in tokens[1:]]
        if any(v not in (0, 1) for v in values):
            raise ValueError(
                f"Stimulus line {line_no}: invalid logic value (only 0 or 1 allowed)"
            )
        stimulus.append((time, values))

    # --- 7. Return structured result ---
    return {
        "INPUTS": inputs,
        "OUTPUTS": outputs,
        "GATES": gates,
        "STIMULUS": stimulus,
    }


def single_gate(gate, inputs):
    if gate == "AND":
        return inputs[0] and inputs[1]
    elif gate == "OR":
        return inputs[0] or inputs[1]
    elif gate == "XOR":
        v1 = inputs[0]
        v2 = inputs[1]l
        return ((not v1) and v2) or (v1 and (not v2))
    elif gate == "NOT":
        return not inputs[0]


def eval_gate(inputs, outputs, gates, input_value):
    values = {}
    for j in range(len(inputs)):
        values[inputs[j]] = input_value[1][j]

    for i in range(len(gates)):
        current_gate = gates[i]
        num_val = [values[k] for k in current_gate[2]]
        gate_type = current_gate[1]
        result = single_gate(gate_type, num_val)
        values[current_gate[0]] = result

    return values


def topological_sort(parsed_data):
    declared_variables = parsed_data["INPUTS"].copy()
    new_order = []
    leftover_events = parsed_data["GATES"].copy()

    while leftover_events:
        i = 0
        while i < len(leftover_events):
            required_variables = leftover_events[i][2]
            available = all(j in declared_variables for j in required_variables)
            if available:
                declared_variables.append(leftover_events[i][0])
                new_order.append(leftover_events[i])
                leftover_events.pop(i)
            else:
                i += 1

    sorted_data = parsed_data.copy()
    sorted_data["GATES"] = new_order
    return sorted_data


def simulate(sorted_data):
    inputs = sorted_data["INPUTS"]
    outputs = sorted_data["OUTPUTS"]
    gates = sorted_data["GATES"]
    output_vals = []

    for j in range(len(sorted_data["STIMULUS"])):
        current_inputs = sorted_data["STIMULUS"][j]
        output_vals.append(eval_gate(inputs, outputs, gates, current_inputs))

    return output_vals


def to_wavedrom_json(data, waves):
    signals = []
    inputs = data["INPUTS"]
    outputs = data["OUTPUTS"]
    variables_and_waves = {}

    for j in range(len(waves)):
        current_wave = waves[j]
        for i in current_wave:
            if i not in variables_and_waves:
                variables_and_waves[i] = str(current_wave[i])
            else:
                variables_and_waves[i] += str(current_wave[i])
    signals = [{"name": k, "wave": variables_and_waves[k]} for k in variables_and_waves]
    return json.dumps({"signal": signals}, indent=2)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist", help=".net file path")
    ap.add_argument("--out", "-o", help="output JSON path")
    args = ap.parse_args(argv)

    text = Path(args.netlist).read_text()
    nl = parse_netlist(text)
    sorted_data = topological_sort(nl)
    waves = simulate(nl)
    js = to_wavedrom_json(sorted_data, waves)

    out_path = args.out
    if not out_path:
        p = Path(args.netlist)
        out_path = str(p.with_suffix(".json"))

    Path(out_path).write_text(js + "\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

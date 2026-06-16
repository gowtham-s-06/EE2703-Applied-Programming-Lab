"""Tiny combinational logic simulator producing WaveDrom JSON.

Usage:
  python digitalsim.py path/to/circuit.net [--out out.json]

Input format sections (fixed order): INPUTS, OUTPUTS, GATES, STIMULUS.
Gates: OUT = AND(A, B) | OR(A, B) | XOR(A, B) | NOT(A)

Note: this template file uses the `argparse` module to get arguments
from the command line.  You are expected to retain this part of it
to make testing easier.  The function calls given in the `main` function
are only suggestions, and you can rename them or create others as long
as the interface to the outside world does not change.

This may make it a bit harder to run purely from an editor like VSCode.
However, in practice you almost never run code directly from an editor,
so this is something you need to be able to handle anyway.
"""

import sys
import argparse
from pathlib import Path
import json
from typing import List


def parse_netlist(text):
    """
    Parses a digital circuit description written in netlist format and validates its structure.

    The netlist must contain the following sections in order:
        INPUTS:
        OUTPUTS:
        GATES:
        STIMULUS:

    Each section defines signals, gate connections, and input stimuli for simulation.
    
    Parameters:
    text : str
        The full text of the circuit netlist file.

    Returns:
    dict
        A structured dictionary with the following keys:
        {
            "INPUTS":   list[str]                 # Names of all input signals
            "OUTPUTS":  list[str]                 # Names of all output signals
            "GATES":    list[tuple[str, str, list[str]]]  
                        # Each gate as (output_name, gate_type, [input_names])
            "STIMULUS": list[tuple[int, list[int]]]  
                        # Each entry as (time, [input_values])
        }

    Raises:
    ValueError
        If any of the following validation errors occur:
        - Sections are missing or out of order.
        - Signal names are invalid (must be alphanumeric with underscores, starting with a letter/_).
        - Unknown gate type or wrong number of inputs to a gate.
        - Redefinition or use of undefined signals.
        - Empty sections.
        - Invalid or non-monotonic stimulus times.
        - Stimulus lines with non-binary or missing input values.
    """

    # Read lines & initialize containers
    lines = text.splitlines()

    sections = {"INPUTS:", "OUTPUTS:", "GATES:", "STIMULUS:"}
    data = {"INPUTS": [], "OUTPUTS": [], "GATES": [], "STIMULUS": []}
    current_section = None
    section_order = []

    # Iterate lines and assign them to sections
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue  # skip blank or comment lines

        header = line.split()[0]
        if header in sections:
            current_section = header[:-1]  # e.g. "INPUTS:" → "INPUTS"
            section_order.append(current_section)
            remainder = line[len(header) :].strip()
            if remainder:  # To take in data after the section header, on the same line
                data[current_section].append(remainder)
            continue

        if current_section is None:
            raise ValueError(f"Line {line_no}: content before any section header")

        data[current_section].append(line)

    # Validate section order and presence
    if section_order != ["INPUTS", "OUTPUTS", "GATES", "STIMULUS"]:
        raise ValueError(
            "Sections must appear in order: INPUTS, OUTPUTS, GATES, STIMULUS"
        )

    for key in data:
        if not data[key]:
            raise ValueError(f"Section {key} is empty")

    # Parse INPUTS & OUTPUTS
    inputs = data["INPUTS"][0].split()
    outputs = data["OUTPUTS"][0].split()

    # Function to validate signal names (alphanumeric + underscores, starting with letter/_)
    def is_valid_signal_name(sig):
        if not sig:
            return False
        return all(ch.isalnum() or ch == "_" for ch in sig)

    # Check all signal names
    for sig in inputs + outputs:
        if not is_valid_signal_name(sig):
            raise ValueError(f"Invalid signal name: {sig}")

    # Parse GATES
    gates = []
    known_signals = set(inputs)
    for line_no, line in enumerate(data["GATES"], start=1):
        # Expect lines like: OUT = GATETYPE(IN1, IN2)
        if "=" not in line or "(" not in line or not line.endswith(")"):
            raise ValueError(
                f"Invalid gate syntax on gate section line {line_no}: {line}"
            )

        # Split at the '=' sign
        parts = line.split("=", 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid gate syntax on gate section line {line_no}: {line}"
            )

        out = parts[0].strip()
        right = parts[1].strip()

        # Separate gate type and input list
        if "(" not in right:
            raise ValueError(
                f"Missing '(' in gate definition on gate section line {line_no}: {line}"
            )

        gtype, ins_str = right.split("(", 1)
        gtype = gtype.strip().upper()

        # Remove trailing ')'
        if not ins_str.endswith(")"):
            raise ValueError(
                f"Missing ')' in gate definition on gate section line {line_no}: {line}"
            )

        ins_str = ins_str[:-1].strip()

        # Split inputs by comma
        ins = [x.strip() for x in ins_str.split(",") if x.strip()]

        if gtype not in {"NOT", "AND", "OR", "XOR"}:
            raise ValueError(f"Unknown gate type: {gtype}")
        # Checking number of arguments for each gate type
        expected = 1 if gtype == "NOT" else 2
        if len(ins) != expected:
            raise ValueError(f"{gtype} expects {expected} input(s), got {len(ins)}")

        if out in known_signals:
            raise ValueError(f"Signal '{out}' redefined on gate section line {line_no}")

        known_signals.add(out)
        gates.append((out, gtype, ins))

    # Check if any variables have been used, but not declared anywhere
    for out, gtype, ins in gates:
        for s in ins:
            if s not in known_signals:
                raise ValueError(
                    f"Undefined signal '{s}' used in gate {out} = {gtype}({', '.join(ins)})"
                )
    # Parse STIMULUS
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
        # Checking is inputs are binary or not
        values = [int(x) for x in tokens[1:]]
        if any(v not in (0, 1) for v in values):
            raise ValueError(
                f"Stimulus line {line_no}: invalid logic value (only 0 or 1 allowed)"
            )

        stimulus.append((time, values))

    # Return structured result
    return {
        "INPUTS": inputs,
        "OUTPUTS": outputs,
        "GATES": gates,
        "STIMULUS": stimulus,
    }


def eval_gate(gate, inputs):
    """
    Evaluates the logical output of a single gate given its type and input values.

    Parameters:
    gate : str
        The type of logic gate to evaluate. Must be one of:
        {"AND", "OR", "XOR", "NOT"}.
    inputs : list[bool]
        List of input boolean values to the gate.
        - AND, OR, XOR expect exactly 2 inputs.
        - NOT expects exactly 1 input.

    Returns:
    bool
        The resulting output value of the logic gate operation.
    """
    if gate == "AND":
        return inputs[0] and inputs[1]
    elif gate == "OR":
        return inputs[0] or inputs[1]
    elif gate == "XOR":
        # A XOR B = (NOT(A) AND B) OR (A AND NOT(B))
        v1 = inputs[0]
        v2 = inputs[1]
        val = (not (v1) and v2) or (v1 and not (v2))
        return val
    elif gate == "NOT":
        return not (inputs[0])


def topological_sort(parsed_data):
    """
    Performs a topological sort of the circuit gates based on signal dependencies using Kahn's algorithm.

    Parameters:
        parsed_data (dict): Parsed circuit data.

    Returns:
        dict: A copy of parsed_data with "GATES" sorted in a valid evaluation order.

    Raises:
        ValueError: If a circular dependency or undefined signal is detected.
    """
    inputs = parsed_data['INPUTS']
    gates = parsed_data['GATES']
    # Build dependency graph as normal dict of lists
    graph = {}  # adjacency list
    indegree = {}  # counts of incoming edges
    declared = set(inputs)

    # Initialize graph and indegree dicts
    for out_var, gate_type, in_vars in gates:
        indegree[out_var] = len(in_vars)
        for var in in_vars:
            if var in graph:
                graph[var].append(out_var)
            else:
                graph[var] = [out_var]

    # Initialize queue with variables that are already available (inputs)
    queue = list(inputs)
    new_order = []

    while queue:
        var = queue.pop(0)  # pop from front, ie, deque
        for dependent in graph.get(var, []):
            indegree[dependent] -= 1 # Since var is known, we can reduce indegree of unknown dependent variable
            if indegree[dependent] == 0: # Now we completely know the previously unknown dependent variable
                # find the gate that produces this variable
                for g in gates:
                    if g[0] == dependent:
                        new_order.append(g)
                        break
                queue.append(dependent) # Add to queue of known variables

    # Check if all gates were added (cycle detection)
    if len(new_order) != len(gates):
        raise ValueError("Cycle detected or unresolved dependencies.")
    sorted_data = parsed_data.copy()
    sorted_data["GATES"] = new_order
    return sorted_data


def simulate(sorted_data):
    """
    Simulates the logic circuit over time based on the provided stimulus data.

    Parameters:
        sorted_data (dict): Parsed and topologically sorted circuit data.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents the 
                    signal values at one timestep.

    Raises:
        ValueError: If a signal is used before being defined (indicating an error 
                    in topological ordering or undefined input).
    """
    inputs = sorted_data["INPUTS"]
    outputs = sorted_data["OUTPUTS"]
    gates = sorted_data["GATES"]
    all_signals = set(inputs)  # Set of all variables
    for out, _, _ in gates:
        all_signals.add(out)

    waves = []  # Used to hold the values of all variables at each timestep
    # I could have stored only input and output variables, but in case if anyone wants to see the intermediate variables, it will be really easy to do so with this approach
    for timestep in sorted_data["STIMULUS"]:
        # Initialize inputs for this time step
        # timestep has the structure (timestamp,[inputs])
        values = {sig: val for sig, val in zip(inputs, timestep[1])}

        # Evaluate all gates in topological order
        for out, gtype, ins in gates:
            try:
                ins_values = [values[s] for s in ins]
            except KeyError as e:
                raise ValueError(
                    f"Signal {e.args[0]} used before definition; "
                    f"topological order may be wrong."
                )
            values[out] = eval_gate(gtype, ins_values)

        # Ensure outputs exist
        for sig in all_signals:
            if sig not in values:
                values[sig] = 0  # purely cosmetic (for missing signals)

        # Store a copy of current state
        waves.append(values.copy())

    return waves


def to_wavedrom_json(data, waves):
    """
    Converts the simulated signal values into a WaveDrom-compatible JSON string.

    Parameters:
        data (dict): Parsed and sorted circuit data.
        waves (list[dict]): List of dictionaries representing signal values at each timestep.

    Returns:
        str: A JSON-formatted string in WaveDrom format, where each signal has a
             'name' and 'wave' string.
    """
    # Collect all signals
    inputs = data["INPUTS"]
    outputs = data["OUTPUTS"]
    gates = data["GATES"]

    # Intermediates = gate outputs that are not final outputs
    # intermediates = [out for out, _, _ in gates if out not in outputs]

    # Desired display order: inputs, outputs
    ordered_signals = inputs + outputs

    # Build waveforms for each signal
    var_to_wave = {v: "" for v in ordered_signals}
    for timestep in waves:
        for v in ordered_signals:
            val = timestep.get(
                v
            )  # Get corresponding value of that variable in this timestep
            var_to_wave[v] += str(int(val))  # Add it to string of values

    # Convert to WaveDrom format
    signal_list = [{"name": v, "wave": var_to_wave[v]} for v in ordered_signals]
    # I use json.dumps to create a standard json output formatted dictionary
    return json.dumps({"signal": signal_list},indent=2)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist", help=".net file path")
    ap.add_argument("--out", "-o", help="output JSON path")
    args = ap.parse_args(argv)

    # Read from the command line argument
    text = Path(args.netlist).read_text()
    nl = parse_netlist(text)
    sorted_data = topological_sort(nl)
    waves = simulate(sorted_data)
    js = to_wavedrom_json(sorted_data, waves)

    # Automatically generate output path from input filename
    # if not explicitly provided
    out_path = args.out
    if not out_path:
        p = Path(args.netlist)
        out_path = str(p.with_suffix(".json"))
    Path(out_path).write_text(js + "\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

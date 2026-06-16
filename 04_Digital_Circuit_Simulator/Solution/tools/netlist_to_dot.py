"""Generate a Graphviz DOT graph from a tiny .net circuit file.

Usage:
  python netlist_to_dot.py path/to/circuit.net [-o out.dot]

You can view the dot file that is generated online at 
https://dreampuf.github.io/GraphvizOnline/

or you can install GraphViz on your own system and then run:
  dot -Tsvg out.dot -o out.svg

This script only parses the small format used in assignments/digitalsim:
  - Sections in order: INPUTS, OUTPUTS, GATES, STIMULUS
  - Gates: OUT = AND(A,B) | OR(A,B) | XOR(A,B) | NOT(A)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


Gate = Tuple[str, str, Tuple[str, ...]]  # (out, type, inputs)


def parse_netlist(text: str) -> Tuple[List[str], List[str], List[Gate]]:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and not ln.startswith("#")]

    def expect(prefix: str, idx: int) -> int:
        if idx >= len(lines) or not lines[idx].startswith(prefix):
            raise ValueError(f"Expected '{prefix}' section")
        return idx

    i = expect("INPUTS:", 0)
    inputs = lines[i].split(":", 1)[1].strip().split()
    i += 1

    i = expect("OUTPUTS:", i)
    outputs = lines[i].split(":", 1)[1].strip().split()
    i += 1

    i = expect("GATES:", i)
    i += 1

    gate_re = re.compile(r"^(?P<out>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
                         r"(?P<type>AND|OR|XOR|NOT)\s*\(\s*"
                         r"(?P<args>[A-Za-z0-9_,\s]+)\s*\)\s*$")
    gates: List[Gate] = []
    while i < len(lines) and not lines[i].startswith("STIMULUS:"):
        m = gate_re.match(lines[i])
        if not m:
            raise ValueError(f"Invalid gate line: '{lines[i]}'")
        out = m.group("out")
        typ = m.group("type")
        args = tuple(a.strip() for a in m.group("args").split(","))
        gates.append((out, typ, args))
        i += 1

    return inputs, outputs, gates


def to_dot(inputs: List[str], outputs: List[str], gates: List[Gate]) -> str:
    # Collect all signal names driven by gates
    gate_outs = {o for (o, _t, _ins) in gates}
    signals = set(inputs) | gate_outs | set(outputs)

    parts: List[str] = []
    parts.append("digraph G {")
    parts.append("  rankdir=LR;")
    parts.append("  node [fontname=Helvetica, fontsize=11];")
    parts.append("  graph [splines=true, nodesep=0.5, ranksep=0.7];")

    # Inputs as ellipses (light gray)
    for s in inputs:
        parts.append(
            f"  \"sig_{s}\" [label=\"{s}\", shape=ellipse, style=filled, fillcolor=\"#eeeeee\", penwidth=1.2];"
        )

    # Outputs as doublecircle
    for s in outputs:
        parts.append(
            f"  \"sig_{s}\" [label=\"{s}\", shape=doublecircle, style=filled, fillcolor=\"#f7f7f7\", penwidth=1.4];"
        )

    # Intermediate signals as tiny dots with side labels
    for s in sorted(signals - set(inputs) - set(outputs)):
        parts.append(
            f"  \"sig_{s}\" [label=\"\", xlabel=\"{s}\", shape=point, width=0.06, height=0.06, penwidth=1.0];"
        )

    # Gates as larger highlighted rounded boxes
    for out, typ, _ins in gates:
        parts.append(
            f"  \"gate_{out}\" [label=\"{typ}\", shape=box, style=\"rounded,filled\", fillcolor=\"#fffbe6\", "
            f"color=\"#444444\", penwidth=2, fontsize=13, fixedsize=true, width=1.4, height=0.9];"
        )

    # Edges: signal -> gate (inputs), and gate -> signal (output)
    for out, _typ, ins in gates:
        for s in ins:
            parts.append(f"  \"sig_{s}\" -> \"gate_{out}\";")
        parts.append(f"  \"gate_{out}\" -> \"sig_{out}\";")

    parts.append("}")
    return "\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist", help=".net file path")
    ap.add_argument("--out", "-o", help="output .dot path (defaults to stdout)")
    args = ap.parse_args()

    text = Path(args.netlist).read_text()
    inputs, outputs, gates = parse_netlist(text)
    dot = to_dot(inputs, outputs, gates)
    if args.out:
        Path(args.out).write_text(dot)
    else:
        print(dot, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

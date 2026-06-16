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
from typing import List

def parse_netlist(text: str):
    pass


def eval_gate():
    pass

def simulate():
    pass

def to_wavedrom_json():
    pass

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist", help=".net file path")
    ap.add_argument("--out", "-o", help="output JSON path")
    args = ap.parse_args(argv)

    # Read from the command line argument
    text = Path(args.netlist).read_text()
    nl = parse_netlist(text)
    waves = simulate(nl)
    js = to_wavedrom_json(nl, waves)

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

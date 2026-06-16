#!/usr/bin/env python3
"""
Keyboard Layout Optimization via Simulated Annealing


Notes:
- Cost is total Euclidean distance between consecutive characters.
- Coordinates are fixed (QWERTY-staggered grid). Optimization swaps assignments.

This base code uses Python "types" - these are optional, but very helpful
for debugging and to help with editing.

"""

import argparse
import json
import math
import os
import random
import string
import time
import warnings
from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt  # type: ignore


Point = Tuple[float, float]
Layout = Dict[str, Point]


def qwerty_coordinates(chars: str) -> Layout:
    """Return QWERTY grid coordinates for the provided character set.

    The grid is a simple staggered layout (units are arbitrary):
    - Row 0: qwertyuiop at y=0, x in [0..9]
    - Row 1: asdfghjkl at y=1, x in [0.5..8.5]
    - Row 2: zxcvbnm at y=2, x in [1..6]
    - Space at (4.5, 3)
    Characters not present in the grid default to the space position.
    """
    row0 = "qwertyuiop"
    row1 = "asdfghjkl"
    row2 = "zxcvbnm"

    coords: Layout = {}
    for i, c in enumerate(row0):
        coords[c] = (float(i), 0.0)
    for i, c in enumerate(row1):
        coords[c] = (0.5 + float(i), 1.0)
    for i, c in enumerate(row2):
        coords[c] = (1.0 + float(i), 2.0)
    coords[" "] = (4.5, 3.0)

    # Backfill for requested chars; unknowns get space position.
    space_xy = coords[" "]
    for ch in chars:
        if ch not in coords:
            coords[ch] = space_xy
    return coords


def initial_layout() -> Layout:
    """Create an initial layout mapping chars to some arbitrary positions of letters."""

    # Start with identity for letters and space; others mapped to space.
    base_keys = "abcdefghijklmnopqrstuvwxyz "

    # Get coords - or use coords of space as default
    layout = qwerty_coordinates(base_keys)
    return layout


def preprocess_text(text: str, chars: str) -> str:
    """Lowercase and filter to the allowed character set; map others to space."""
    lower_text = text.lower()
    new_text = ""
    for i in lower_text:
        # Add spaces for unknown characters
        if i not in chars:
            new_text += " "
        else:
            new_text += i

    return new_text


def Euclid_dist(pt1: Point, pt2: Point) -> float:
    x_dist = pt1[0] - pt2[0]
    y_dist = pt1[1] - pt2[1]
    return (x_dist**2 + y_dist**2) ** 0.5


def path_length_cost(text: str, layout: Layout) -> float:
    """Sum Euclidean distances across consecutive characters in text."""
    total_dist = 0
    for i in range(len(text) - 1):
        pt1 = layout[text[i]]
        pt2 = layout[text[i + 1]]
        # Calculate distance between the 2 adjacent characters
        dist = Euclid_dist(pt1, pt2)
        total_dist += dist
    return total_dist


######
# Define any other useful functions, such as to create new layout etc.
######


def get_neighbour(layout: Layout, rng: random.Random) -> Layout:
    new_layout = layout.copy()  # Create a copy of existing layout
    # Take any 2 random unique characters from current layout
    i, j = rng.sample(sorted(layout), 2)
    # Swap those characters in the copy
    new_layout[i], new_layout[j] = new_layout[j], new_layout[i]
    return new_layout  # Return the new layout


# Dataclass is like a C struct - you can use it just to store data if you wish
# It provides some convenience functions for assignments, printing etc.
@dataclass
class SAParams:
    iters: int = 50000
    t0: float = 1.0  # Initial temperature setting
    alpha: float = 0.999  # geometric decay per iteration
    epoch: int = 1  # iterations per temperature step (1 = per-iter decay)


def simulated_annealing(
    text: str,
    layout: Layout,
    params: SAParams,
    rng: random.Random,
) -> Tuple[Layout, float, List[float], List[float]]:
    """Simulated annealing to minimize path-length cost over character swaps.

    Returns best layout, best cost, and two lists:
    - best cost up to now (monotonically decreasing)
    - cost of current solution (may occasionally go up)
    These will be used for plotting
    """
    # Simulated annealing algorithm
    # Calculate initial distance
    current_layout = layout.copy()
    current_distance = path_length_cost(text, layout)
    # Create a layout to store the best layout with lowest distance
    best_layout = current_layout.copy()
    best_distance = current_distance

    temp = params.t0
    # Append in the initial quantities in required lists
    distances = [current_distance]
    best_layouts = [best_layout.copy()]
    best_distances = [best_distance]
    num_iterations = params.iters
    for i in range(num_iterations):
        neighbour_layout = get_neighbour(current_layout, rng)
        neighbour_distance = path_length_cost(text, neighbour_layout)
        try:
            p = math.exp((current_distance - neighbour_distance) / temp)
        except OverflowError:

            warnings.warn("Overflow encountered in exp", RuntimeWarning)
            p = float("inf")
        if neighbour_distance < current_distance or rng.random() < p:
            current_layout = neighbour_layout
            current_distance = neighbour_distance

            if current_distance < best_distance:
                best_layout = current_layout.copy()
                best_distance = current_distance

        # Reduce temperature only every `epoch` steps
        if (i + 1) % params.epoch == 0:
            temp *= params.alpha

        # Save the sequences of various quantities
        distances.append(current_distance)
        best_layouts.append(best_layout.copy())
        best_distances.append(best_distance)

    return best_layout, best_distance, best_distances, distances


def plot_costs(
    layout: Layout, best_trace: List[float], current_trace: List[float]
) -> None:

    # Plot cost trace
    out_dir = "."
    plt.figure(figsize=(6, 3))
    plt.plot(best_trace, lw=1.5)
    plt.plot(current_trace, lw=1.5)
    plt.xlabel("Iteration")
    plt.ylabel("Best Cost")
    plt.title("Best Cost vs Iteration")
    plt.tight_layout()
    path = os.path.join(out_dir, f"cost_trace.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

    # Plot layout scatter
    xs, ys, labels = [], [], []
    for ch, (x, y) in layout.items():
        xs.append(x)
        ys.append(y)
        labels.append(ch)

    plt.figure(figsize=(6, 3))
    plt.scatter(xs, ys, s=250, c="#1f77b4")
    for x, y, ch in zip(xs, ys, labels):
        plt.text(
            x,
            y,
            ch,
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.15", fc="#1f77b4", ec="none", alpha=0.9),
        )
    plt.gca().invert_yaxis()
    plt.title("Optimized Layout")
    plt.axis("equal")
    plt.tight_layout()
    path = os.path.join(out_dir, f"layout.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def load_text(filename) -> str:
    if filename is not None:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback demo text
    return (
        "the quick brown fox jumps over the lazy dog\n" "APL is the best course ever\n"
    )


def sweep_sa(
    filename: str | None = None,
    vary: str = "t0",  # "t0" or "iters"
    start: float | int = 1.0,
    stop: float | int = 0.05,
    step: float | int = 0.05,
    fixed_t0: float = 1.0,  # used when varying iters
    fixed_iters: int = 5000,  # used when varying t0
    alpha: float = 0.999,
    seed: int = 0,
) -> None:
    """
    Sweeps over either initial temperature (t0) or iterations, runs SA, and plots Final Cost.
    Parameters:
    vary : str
        Choose which parameter to vary: "t0" or "iters".
    start, stop, step : float or int
        Sweep range for chosen parameter.
    fixed_t0 : float
        Fixed initial temperature when sweeping iterations.
    fixed_iters : int
        Fixed number of iterations when sweeping temperature.
    """

    # Setup text and baseline
    chars_list = "abcdefghijklmnopqrstuvwxyz "
    layout0 = initial_layout()
    raw_text = load_text(filename)
    text = preprocess_text(raw_text, chars_list)
    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY) cost: {baseline_cost:.4f}")

    values, final_costs = [], []

    # Sweep loop
    val = start
    while val >= stop - 1e-9 if vary == "t0" else val <= stop + 1e-9:
        rng = random.Random(seed)
        if vary == "t0":
            params = SAParams(iters=fixed_iters, alpha=alpha, t0=val)
        else:  # vary == "iters"
            params = SAParams(iters=int(val), alpha=alpha, t0=fixed_t0)

        start_time = time.time()
        best_layout, best_cost, *_ = simulated_annealing(text, layout0, params, rng)
        duration = time.time() - start_time

        if vary == "t0":
            print(
                f"t0={val:.2f} | Final cost={best_cost:.4f} "
                f"| Improvement={(baseline_cost - best_cost):.4f} "
                f"| Runtime={duration:.2f}s"
            )
        else:
            print(
                f"iters={int(val)} | Final cost={best_cost:.4f} "
                f"| Improvement={(baseline_cost - best_cost):.4f} "
                f"| Runtime={duration:.2f}s"
            )

        values.append(val)
        final_costs.append(best_cost)

        val = val - step if vary == "t0" else val + step

    # Plot
    plt.figure(figsize=(7, 5))
    plt.plot(values, final_costs, marker="o", color="tab:blue", linewidth=2)

    if vary == "t0":
        plt.gca().invert_xaxis()
        plt.xlabel("Initial Temperature (t₀)")
        plt.title("Final Optimized Cost vs Initial Temperature")
    else:
        plt.xlabel("Iterations")
        plt.title("Final Optimized Cost vs Iterations")

    plt.ylabel("Final Optimized Cost")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

    print(f"\nPlot generated: Final Optimized Cost vs {vary}")


def main(filename: str | None = None) -> None:
    rng = random.Random(0)
    chars_list = "abcdefghijklmnopqrstuvwxyz "

    # Initial assignment - QWERTY
    layout0 = initial_layout()

    # Prepare text and evaluate baseline
    raw_text = load_text(filename)
    text = preprocess_text(raw_text, chars_list)
    # print(text)
    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY assignment) cost: {baseline_cost:.4f}")

    # Annealing - give parameter values
    params = SAParams(iters=5000, alpha=0.999, t0=1, epoch=1)
    start = time.time()
    best_layout, best_cost, best_trace, current_trace = simulated_annealing(
        text, layout0, params, rng
    )
    dur = time.time() - start
    print(
        f"Optimized cost: {best_cost:.4f}  (improvement {(baseline_cost - best_cost):.4f})"
    )
    print(f"Runtime: {dur:.2f}s over {params.iters} iterations")

    plot_costs(best_layout, best_trace, current_trace)


if __name__ == "__main__":
    filename = None
    main(filename)

    # The below function was used to plot how best cost varies with different initial temperatures.
    """sweep_sa(
        filename=filename,
        vary="t0",
        start=1.0,
        stop=0.05,
        step=0.05,
        fixed_iters=5000,
        alpha=0.999,
    )
    """
    # The below function was used to plot how best cost varies with different number of iterations.
    """
    sweep_sa(
        filename=filename,
        vary="iters",
        start=250,
        stop=5000,
        step=250,
        fixed_t0=1.0,
        alpha=0.999,
    )"""

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
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
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
    current_layout = layout
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

        p = np.exp((current_distance - neighbour_distance) / temp)
        if neighbour_distance < current_distance or rng.random() < p:
            current_layout = neighbour_layout
            current_distance = neighbour_distance

            if current_distance < best_distance:
                best_layout = current_layout.copy()
                best_distance = current_distance
        # Reduce temperature after a iteration
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


def main(filename: str | None = None) -> None:

    chars_list = "abcdefghijklmnopqrstuvwqxyz "

    # Initial assignment - QWERTY
    layout0 = initial_layout()

    # Prepare text and evaluate baseline
    raw_text = load_text(filename)
    text = preprocess_text(raw_text, chars_list)
    # print(text)
    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY assignment) cost: {baseline_cost:.4f}")
    t01 = 1.0
    for j in range(20):
        rng = random.Random(0)
        # Annealing - give parameter values
        params = SAParams(iters=5000, alpha=0.999, t0=t01)
        start = time.time()
        best_layout, best_cost, best_trace, current_trace = simulated_annealing(
            text, layout0, params, rng
        )
        dur = time.time() - start
        print(
            f"Optimized cost: {best_cost:.4f} for t0 :{t01} (improvement {(baseline_cost - best_cost):.4f})"
        )
        print(f"Runtime: {dur:.2f}s over {params.iters} iterations")
        t01 -= 0.05
    plot_costs(best_layout, best_trace, current_trace)


def sweep_temperature_vs_cost(
    filename: str | None = None,
    start_t0: float = 1.0,
    stop_t0: float = 0.05,
    step: float = 0.05,
    iters: int = 5000,
    alpha: float = 0.999,
    seed: int = 0,
) -> None:
    """
    Runs simulated annealing for a range of t0 values and plots Final Cost vs t0.

    Parameters
    ----------
    filename : str or None
        Input text file name to load text from.
    start_t0 : float
        Starting initial temperature (default 1.0).
    stop_t0 : float
        Lower limit for t0 sweep (default 0.05).
    step : float
        Step size to decrease t0 each run (default 0.05).
    iters : int
        Number of SA iterations for each run.
    alpha : float
        Cooling factor for SA.
    seed : int
        Random seed for reproducibility.
    """

    # Characters and baseline
    chars_list = "abcdefghijklmnopqrstuvwqxyz "
    layout0 = initial_layout()
    raw_text = load_text(filename)
    text = preprocess_text(raw_text, chars_list)
    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY assignment) cost: {baseline_cost:.4f}")

    # Prepare storage for results
    t0_values = []
    final_costs = []

    # Sweep over t0
    t0 = start_t0
    while t0 >= stop_t0 - 1e-9:  # small epsilon to include stop_t0
        rng = random.Random(seed)
        params = SAParams(iters=iters, alpha=alpha, t0=t0)

        start_time = time.time()
        best_layout, best_cost, best_trace, current_trace = simulated_annealing(
            text, layout0, params, rng
        )
        duration = time.time() - start_time

        print(
            f"t0={t0:.2f} | Final cost={best_cost:.4f} "
            f"| Improvement={(baseline_cost - best_cost):.4f} "
            f"| Runtime={duration:.2f}s"
        )

        # Save results
        t0_values.append(t0)
        final_costs.append(best_cost)

        # Decrease temperature
        t0 -= step

    # ---- Plot Final Cost vs t0 ----
    plt.figure(figsize=(7, 5))
    plt.plot(t0_values, final_costs, marker="o", color="tab:blue", linewidth=2)
    plt.gca().invert_xaxis()  # Higher t0 on left, lower on right
    plt.xlabel("Initial Temperature (t₀)")
    plt.ylabel("Final Optimized Cost")
    plt.title("Final Optimized Cost vs Initial Temperature")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

    print("\nPlot generated: Final Optimized Cost vs t0")


def sweep_iteration_vs_cost(
    filename: str | None = None,
    start_iter: int = 250,
    stop_iter: int = 5000,
    step: int = 250,
    iters: int = 5000,
    alpha: float = 0.999,
    seed: int = 0,
) -> None:
    """
    Runs simulated annealing for a range of t0 values and plots Final Cost vs t0.

    Parameters
    ----------
    filename : str or None
        Input text file name to load text from.
    start_t0 : float
        Starting initial temperature (default 1.0).
    stop_t0 : float
        Lower limit for t0 sweep (default 0.05).
    step : float
        Step size to decrease t0 each run (default 0.05).
    iters : int
        Number of SA iterations for each run.
    alpha : float
        Cooling factor for SA.
    seed : int
        Random seed for reproducibility.
    """

    # Characters and baseline
    chars_list = "abcdefghijklmnopqrstuvwqxyz "
    layout0 = initial_layout()
    raw_text = load_text(filename)
    text = preprocess_text(raw_text, chars_list)
    baseline_cost = path_length_cost(text, layout0)
    print(f"Baseline (QWERTY assignment) cost: {baseline_cost:.4f}")

    # Prepare storage for results
    iter_values = []
    final_costs = []

    # Sweep over t0
    iterns = start_iter
    while iterns <= stop_iter + 1e-9:  # small epsilon to include stop_t0
        rng = random.Random(seed)
        params = SAParams(iters=iterns, alpha=alpha)

        start_time = time.time()
        best_layout, best_cost, best_trace, current_trace = simulated_annealing(
            text, layout0, params, rng
        )
        duration = time.time() - start_time

        print(
            f"iters={iterns} | Final cost={best_cost:.4f} "
            f"| Improvement={(baseline_cost - best_cost):.4f} "
            f"| Runtime={duration:.2f}s"
        )

        # Save results
        iter_values.append(iterns)
        final_costs.append(best_cost)

        # Decrease temperature
        iterns += step

    # ---- Plot Final Cost vs t0 ----
    plt.figure(figsize=(7, 5))
    plt.plot(iter_values, final_costs, marker="o", color="tab:blue", linewidth=2)
    # plt.gca().invert_xaxis()  # Higher t0 on left, lower on right
    plt.xlabel("Iterations")
    plt.ylabel("Final Optimized Cost")
    plt.title("Final Optimized Cost vs Iterations")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

    print("\nPlot generated: Final Optimized Cost vs iters")


if __name__ == "__main__":
    filename = "text.txt"
    sweep_iteration_vs_cost(filename)

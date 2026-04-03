"""
DeadlockVis - Resource Allocation Graph Analyzer
CSE323 Operating System Design Project

An interactive tool for visualizing and detecting deadlocks in resource allocation graphs.
Supports cycle detection, Banker's Algorithm, and real-time graph visualization.

Usage:
    python main.py

Requirements:
    - Python 3.10+
    - networkx
    - matplotlib
    - tkinter (usually included with Python)
"""

import sys
import tkinter as tk
from gui import DeadlockGUI


def check_dependencies():
    """Check if required packages are installed"""
    missing = []

    try:
        import networkx
    except ImportError:
        missing.append("networkx")

    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print("Error: Missing required packages.")
        print(f"Please install: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        sys.exit(1)


def main():
    """Main entry point"""
    print("=" * 60)
    print("DeadlockVis - Resource Allocation Graph Analyzer")
    print("CSE323 Operating System Design Project")
    print("=" * 60)
    print()

    check_dependencies()

    root = tk.Tk()
    app = DeadlockGUI(root)

    print("GUI loaded successfully!")
    print("Features:")
    print("  - Add processes and resources")
    print("  - Create allocation and request edges")
    print("  - Automatic deadlock detection")
    print("  - Visual cycle highlighting")
    print("  - Deadlock resolution tools")
    print("  - Save/load scenarios")
    print()

    root.mainloop()


if __name__ == "__main__":
    main()

# 🔴 DeadlockVis — Visualize Deadlocks, Master Operating Systems

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/NetworkX-Graph%20Analysis-2E8B57" />
  <img src="https://img.shields.io/badge/Matplotlib-Visualization-FF6B6B" />
  <img src="https://img.shields.io/badge/License-Educational%20Use-blue" />
</p>

<p align="center">
  <b>An interactive playground for exploring Resource Allocation Graphs, Deadlock Detection, and OS concepts.</b>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-demo-video">Demo</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-tech-stack">Tech Stack</a>
</p>

---

## 🎬 Demo Video

> 🎥 **[Watch the 4-minute Demo](your-video-link-here)** — See DeadlockVis in action!

![Demo Preview](assets/demo-preview.png) <!-- Replace with actual screenshot -->

---

## ✨ What is DeadlockVis?

**DeadlockVis** is a graphical tool that brings Operating System concepts to life. Instead of staring at textbook diagrams, you can **build** your own Resource Allocation Graphs, **watch** deadlocks form in real-time, and **experiment** with resolution strategies.

### Perfect For:
- **Students** learning about deadlocks in OS courses
- **Educators** demonstrating RAG concepts
- **Developers** exploring graph algorithms
- **Curious minds** who want to understand why your computer sometimes freezes

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/ImtiazHassan/deadlockvis.git
cd deadlockvis

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```

That's it! The GUI will open and you're ready to explore.

---

## 🎮 Features

### 🏗️ Interactive Graph Builder
| Feature | Description |
|---------|-------------|
| **Drag-and-Drop Interface** | Add processes and resources with simple clicks |
| **Visual Edge Creation** | Create allocation and request edges with dropdown menus |
| **Real-Time Updates** | See the graph update instantly as you build |
| **Persistent Layout** | Node positions stay consistent as you edit |

### 🔍 Three Deadlock Detection Algorithms

```
┌─────────────────────────────────────────────────────────┐
│  1️⃣  Cycle Detection (RAG Method)                      │
│      → For single-instance resources                    │
│      → O(V + E) time complexity                         │
│      → Finds cycles in the Resource Allocation Graph    │
├─────────────────────────────────────────────────────────┤
│  2️⃣  Wait-For Graph Conversion                         │
│      → For multi-instance resources                     │
│      → Reduces RAG to process-only graph                │
│      → Detects cycles in the reduced graph              │
├─────────────────────────────────────────────────────────┤
│  3️⃣  Banker's Algorithm                                │
│      → For deadlock avoidance                           │
│      → Finds safe sequences                             │
│      → Determines if system is in safe state            │
└─────────────────────────────────────────────────────────┘
```

### 🚨 Visual Deadlock Detection
- 🔴 **Red Highlighting**: Deadlocked processes turn red
- 📊 **Status Panel**: Real-time system state display
- 🔍 **Cycle Visualization**: See exactly which nodes form the deadlock
- 📝 **Method Detection**: Shows which algorithm detected the deadlock

### 🛠️ Deadlock Resolution Tools
- **Process Termination**: Remove a deadlocked process and release its resources
- **Resource Preemption**: Forcefully reallocate resources to break the cycle
- **Instant Feedback**: See the system return to SAFE state

### 📚 Built-In Learning Examples
| Example | Description |
|---------|-------------|
| **Simple Deadlock** | Classic P1↔P2 circular wait with 2 resources |
| **Multi-Instance** | Complex scenario with resource counting |
| **Safe State** | Demonstrates a valid safe sequence |

### 💾 Save & Share
- Save scenarios as JSON files
- Export graph visualizations as PNG/PDF/SVG
- Load previous work instantly

---

## 🎨 Visual Language

DeadlockVis uses intuitive color coding:

```
🔵 Blue Circles    = Processes
🟩 Green Squares  = Resources
➡️ Solid Green     = Allocation edges (Resource → Process)
➡️ Dashed Orange   = Request edges (Process → Resource)
🔴 Red Nodes       = Deadlocked processes
```

---

## 🧠 How It Works

### Creating Your First Deadlock

```
Step 1: Add Processes
        → Click "Add Process" for P1 and P2

Step 2: Add Resources  
        → Click "Add Resource" for R1 and R2

Step 3: Create Allocations
        → From: R1, To: P1, Click "Allocate"
        → From: R2, To: P2, Click "Allocate"

Step 4: Create Requests
        → From: P1, To: R2, Click "Request"
        → From: P2, To: R1, Click "Request"
        
Result: DEADLOCK DETECTED! 🔴
```

### Understanding the Output

When you click **"Detect Deadlock"**, the system:

1. **Analyzes** the current graph structure
2. **Runs** all three detection algorithms
3. **Highlights** deadlocked processes in red
4. **Reports** which algorithm detected the issue
5. **Shows** the involved processes

---

## 🛠️ Tech Stack

```python
{
    "Language": "Python 3.10+",
    "GUI Framework": "Tkinter + CustomTkinter",
    "Graph Library": "NetworkX",
    "Visualization": "Matplotlib",
    "Data Format": "JSON",
    "Architecture": "MVC Pattern"
}
```

### Project Structure

```
deadlockvis/
│
├── 📄 main.py              # Application entry point
├── 🖥️  gui.py              # GUI implementation (Tkinter)
├── 📊 graph.py             # Core algorithms & data structures
├── 📋 requirements.txt     # Python dependencies
├── 📖 README.md            # This file
│
└── 💾 examples/            # Saved scenario files (optional)
    ├── simple_deadlock.json
    ├── multi_instance.json
    └── safe_state.json
```

---

## 📊 Algorithms in Detail

### 1. Cycle Detection for Single-Instance Resources

```python
def detect_deadlock_single_instance(graph):
    """
    Uses DFS to find cycles in the Resource Allocation Graph.
    A cycle indicates deadlock when resources have single instances.
    """
    try:
        cycle = nx.find_cycle(graph, orientation='original')
        return True, cycle_nodes
    except NetworkXNoCycle:
        return False, None
```

### 2. Wait-For Graph Method

```
Original RAG                    Wait-For Graph
┌─────────┐                    ┌─────────┐
│  P1 ────┼──► R2 ────┐        │  P1 ────┼──► P2
│  ▲      │           │   →    │         │
│  │      │           │        │         │
│  R1 ◄───┘          P2        │  P2 ◄───┘
└─────────┘                    └─────────┘
```

### 3. Banker's Algorithm

- **Input**: Allocation matrix, Max matrix, Available resources
- **Process**: Find a process that can complete with available resources
- **Output**: Safe sequence or deadlocked processes

---

## 🎯 Learning Outcomes

By using DeadlockVis, you'll understand:

| Concept | Understanding |
|---------|---------------|
| 🔗 Resource Allocation Graphs | How processes and resources relate |
| 🔄 Circular Wait | How deadlocks form visually |
| 🔍 Detection Methods | Different algorithms for different scenarios |
| 🛠️ Resolution Strategies | Termination vs Preemption trade-offs |
| 🧮 Banker's Algorithm | Deadlock avoidance in practice |

---

## 🏆 Skills Showcased

```
┌────────────────────────────────────────────┐
│  🧠 Problem Solving                        │
│     → Graph theory application              │
│     → State management                      │
│     → Algorithm optimization                │
├────────────────────────────────────────────┤
│  💻 Software Development                   │
│     → Modular architecture                │
│     → Cross-platform compatibility        │
│     → Clean code practices                │
├────────────────────────────────────────────┤
│  🎨 User Experience                        │
│     → Intuitive interface design          │
│     → Visual feedback systems             │
│     → Educational tool creation           │
└────────────────────────────────────────────┘
```

---

## 🎓 Course Information

| | |
|---|---|
| **Course** | CSE323 - Operating System Design |
| **Institution** | North South University |
| **Semester** | Spring 2026 |
| **Project Type** | Educational Tool Development |

---

## 🤝 Contributing

Found a bug? Have an idea? Contributions welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Enhancement
- [ ] Animated algorithm step-through
- [ ] Deadlock prevention mode
- [ ] Multi-threaded simulation
- [ ] Export to LaTeX/TikZ diagrams
- [ ] Web-based version with Flask

---

## 📜 License

This project is for **educational purposes**. Feel free to use it for:
- ✅ Personal learning
- ✅ Classroom demonstrations
- ✅ OS course projects
- ✅ Algorithm visualization

Please provide attribution if you use this code in your own projects.

---

## 🙏 Acknowledgments

- **Course Instructor** for guidance on OS concepts
- **NetworkX** team for the excellent graph library
- **Matplotlib** team for visualization capabilities
- **CustomTkinter** for modern UI components

---

## 📬 Contact

<p align="center">
  <a href="mailto:imtiazcochassan@gmail.com">
    <img src="https://img.shields.io/badge/Email-Contact%20Me-red?style=flat-square&logo=gmail" />
  </a>
  <a href="https://www.linkedin.com/in/imtiaz-hassan-10b250181">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin" />
  </a>
</p>

<p align="center">
  <b>Made with ❤️ and lots of ☕ by ImtiazHassan</b>
</p>

---

<p align="center">
  <i>"Understanding deadlocks is the first step to preventing them."</i>
</p>

<p align="center">
  ⭐ Star this repo if it helped you understand deadlocks! ⭐
</p>

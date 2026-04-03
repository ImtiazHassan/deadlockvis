# Technical Report: DeadlockVis Project
## CSE323 Operating System Design

---

## Project Overview
**DeadlockVis** is an interactive Resource Allocation Graph (RAG) analyzer that visualizes deadlock scenarios in operating systems. The application enables users to build custom deadlock scenarios, detect deadlocks using multiple algorithms, and resolve them interactively.

**Technologies Used:** Python, NetworkX, Matplotlib, Tkinter, CustomTkinter

---

## Challenges Faced

### Challenge 1: Real-Time Graph Visualization Integration

**Situation:**
The project required displaying an interactive Resource Allocation Graph that updates in real-time as users add processes, resources, and edges. The main challenge was integrating Matplotlib's static plotting capabilities with Tkinter's event-driven GUI framework, while ensuring the graph layout remained stable and readable as nodes were added or removed.

**Task:**
I needed to create a seamless visualization system where:
- The graph updates instantly after every user action
- Node positions remain consistent (not jumping around)
- Different node types (processes vs resources) are visually distinguishable
- Edges show direction and type (allocation vs request)

**Action:**
1. Implemented `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg` to embed matplotlib plots within the Tkinter frame
2. Used NetworkX's `spring_layout` with a fixed random seed (seed=42) to maintain consistent node positioning across updates
3. Created separate drawing functions for process nodes (blue circles), resource nodes (green squares), allocation edges (solid green), and request edges (dashed orange)
4. Added a `draw_graph()` method that clears and redraws the entire graph on each update, ensuring visual consistency
5. Implemented color-coded highlighting for deadlocked processes (red) to provide immediate visual feedback

**Result:**
The visualization system now updates smoothly in real-time, providing users with clear visual feedback. The graph maintains consistent layouts, and color coding makes it easy to distinguish between different elements. Users can immediately see when a deadlock occurs through red highlighting of affected processes.

---

### Challenge 2: Implementing Multiple Deadlock Detection Algorithms

**Situation:**
The project required implementing not just one, but three different deadlock detection algorithms to handle various scenarios: single-instance resources, multi-instance resources, and safe state determination. Each algorithm has different requirements and data structure needs.

**Task:**
I needed to implement and integrate:
1. **Cycle Detection** for single-instance resources using the Resource Allocation Graph
2. **Wait-For Graph** conversion and cycle detection for multi-instance scenarios
3. **Banker's Algorithm** for deadlock avoidance and safe state checking

**Action:**
1. **Cycle Detection:** Used NetworkX's `find_cycle()` function on the Resource Allocation Graph. Implemented error handling with `NetworkXNoCycle` exception to detect when no cycle exists.

2. **Wait-For Graph:** Created a `get_wait_for_graph()` method that converts the RAG to a reduced graph containing only processes. For each request edge (Pi → R), I added edges from Pi to all processes holding instances of R.

3. **Banker's Algorithm:** Implemented the safety algorithm that:
   - Built allocation and need matrices from process data
   - Tracked available resource instances
   - Iteratively found processes that could complete with available resources
   - Returned either a safe sequence or a list of deadlocked processes

4. Created a unified `is_deadlocked()` method that runs all three algorithms in sequence and returns which method detected the deadlock.

**Result:**
The application successfully detects deadlocks across all scenarios. The status panel displays which algorithm was used for detection, helping users understand the appropriate method for different resource configurations. The Banker's Algorithm correctly identifies safe sequences when they exist, providing educational value for understanding deadlock avoidance.

---

### Challenge 3: Cross-Platform GUI Consistency

**Situation:**
The application needed to run on different operating systems (Windows, Linux, macOS) with consistent visual appearance. Tkinter's default styling varies across platforms, and CustomTkinter components sometimes render differently depending on the system's DPI settings and theme.

**Task:**
Ensure the GUI looks consistent and professional across all platforms, with:
- Readable text and appropriate contrast
- Proper widget sizing and spacing
- Consistent color scheme regardless of OS theme
- No clipping or layout issues

**Action:**
1. Standardized font usage by avoiding system-specific fonts and using basic Arial throughout
2. Used `ttk.Style().theme_use('clam')` as a base theme for consistent cross-platform appearance
3. Explicitly set background and foreground colors for all widgets to override OS defaults
4. Used `matplotlib.use('TkAgg')` before importing pyplot to ensure consistent backend
5. Added proper padding and grid configurations to prevent widget clipping
6. Tested on Windows 11 and documented any platform-specific considerations

**Result:**
The application maintains a consistent dark-themed appearance across platforms. Text remains readable with high contrast, and the layout stays intact regardless of the operating system's default settings. The color-coded interface (blue for processes, green for resources, etc.) works uniformly on all tested systems.

---

### Challenge 4: Managing Complex Graph State

**Situation:**
The Resource Allocation Graph requires tracking complex relationships between processes and resources, including: current allocations, pending requests, resource instance counts, and graph topology. Managing this state while allowing dynamic modifications (adding/removing nodes and edges) risked data inconsistencies.

**Task:**
Build a robust state management system that:
- Maintains consistency between the graph structure and node data
- Handles edge cases (e.g., removing a process that's holding resources)
- Supports serialization/deserialization for save/load functionality
- Prevents invalid states (e.g., allocating more resources than available)

**Action:**
1. Created dedicated `Process` and `Resource` classes to encapsulate node-specific data
2. Implemented the `ResourceAllocationGraph` class as the central state manager
3. Added validation in resource allocation methods to prevent over-allocation
4. Created cleanup methods (`remove_process`, `remove_resource`) that properly release all associated resources and edges
5. Implemented `to_dict()` and `from_dict()` methods for JSON serialization, ensuring all state is preserved
6. Used dictionary lookups (O(1)) instead of list iterations for efficient node access

**Result:**
The state management system is robust and handles all edge cases gracefully. Users can add, remove, and modify nodes and edges without causing data corruption. The save/load feature preserves complete graph state, allowing users to save complex scenarios and resume work later. The application handles invalid operations gracefully with informative error messages.

---

### Challenge 5: Educational Value and User Experience

**Situation:**
Since this is an educational tool for learning about deadlocks, the interface needed to be intuitive for students who may not be familiar with Resource Allocation Graphs. The challenge was balancing feature richness with simplicity, and providing feedback that teaches rather than just displays.

**Task:**
Create an interface that:
- Guides users through creating deadlock scenarios
- Provides immediate feedback on system state
- Explains concepts through visual cues
- Includes preset examples for learning

**Action:**
1. Designed the control panel with clear sections: Add Process, Add Resource, Create Edge, and Actions
2. Implemented a status panel showing current system state in color-coded text (green for safe, red for deadlock)
3. Added a node list treeview showing current allocations and requests for each process
4. Created three preset examples accessible from the menu:
   - Simple Deadlock: Classic two-process, two-resource deadlock
   - Multi-Instance Deadlock: Complex scenario with multiple instances
   - Safe State: Example showing a valid safe sequence
5. Color-coded graph elements with a legend in the title
6. Added tooltips and informative status messages

**Result:**
The application successfully serves as an educational tool. Students can immediately understand the relationship between the graph structure and deadlock conditions. The preset examples provide starting points for learning, and the visual feedback reinforces theoretical concepts from the textbook. The interface is intuitive enough that users can create their first deadlock scenario within minutes of opening the application.

---

## Skills Demonstrated

| Skill | Application |
|-------|-------------|
| **Data Structures** | Graph representation using adjacency lists, dictionaries for O(1) lookups |
| **Algorithms** | Cycle detection, graph traversal, Banker's Algorithm implementation |
| **GUI Development** | Tkinter event handling, custom widget creation, layout management |
| **Software Architecture** | Modular design with separation of concerns (graph logic vs GUI) |
| **Visualization** | Matplotlib integration, NetworkX graph rendering, color theory for UI |
| **File I/O** | JSON serialization for save/load functionality |
| **Problem Solving** | Handling edge cases, state consistency, cross-platform compatibility |

---

## Conclusion

This project successfully demonstrates practical application of operating system concepts through interactive visualization. The challenges faced and resolved reflect real-world software development scenarios including cross-platform compatibility, complex state management, and user experience design. The resulting tool provides educational value for understanding deadlock detection and resolution in operating systems.

---

**Report Prepared By:** Mohammad Imtiaz Hassan\
**ID:** 2321196642\
**Course:** CSE323 - Operating System Design (Section 1)\
**Institution:** North South University\  
**Date:** April 2026

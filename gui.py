"""
GUI for Deadlock Detection Tool using Tkinter
Fun and Colorful Version - Fixed for Windows
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

from graph import ResourceAllocationGraph


# Color palette - High contrast for visibility
COLORS = {
    'bg': '#1a1a2e',
    'bg_light': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    'text': '#ffffff',
    'text_dark': '#cccccc',
    'process': '#00d9ff',
    'process_deadlock': '#ff006e',
    'resource': '#7ae582',
    'allocation': '#38b000',
    'request': '#ff9f1c',
    'button': '#4361ee',
    'button_hover': '#3f37c9',
    'panel': '#2d1b4e',
}


class AnimatedButton(tk.Canvas):
    """Custom animated button with hover effects"""

    def __init__(self, parent, text, command, width=120, height=35, bg_color=None):
        self.bg_color = bg_color or COLORS['button']
        self.hover_color = COLORS['button_hover']
        self.text = text
        self.command = command

        super().__init__(parent, width=width, height=height,
                        bg=COLORS['panel'], highlightthickness=0,
                        cursor='hand2')

        self.normal_color = self.bg_color
        self.current_color = self.normal_color

        self.round_rect = self.create_rounded_rect(2, 2, width-2, height-2,
                                                   radius=10, fill=self.normal_color)
        self.text_item = self.create_text(width//2, height//2, text=text,
                                         fill='white', font=('Arial', 9, 'bold'))

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        self.current_color = self.hover_color
        self.itemconfig(self.round_rect, fill=self.hover_color)

    def on_leave(self, event):
        self.current_color = self.normal_color
        self.itemconfig(self.round_rect, fill=self.normal_color)

    def on_click(self, event):
        self.itemconfig(self.round_rect, fill='#2d00f7')

    def on_release(self, event):
        self.itemconfig(self.round_rect, fill=self.current_color)
        if self.command:
            self.command()


class DeadlockGUI:
    """Main GUI class for the Deadlock Detection Tool"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DeadlockVis - Resource Allocation Graph Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg'])
        self.root.minsize(1200, 800)

        self.rag = ResourceAllocationGraph()
        self.selected_node = None
        self.node_positions = {}

        # Use standard fonts that exist on all systems
        self.title_font = ('Arial', 18, 'bold')
        self.header_font = ('Arial', 11, 'bold')
        self.text_font = ('Arial', 10)
        self.small_font = ('Arial', 9)

        self.setup_styles()
        self.create_widgets()
        self.create_menu()

    def setup_styles(self):
        """Configure ttk styles with colors - simplified for compatibility"""
        style = ttk.Style()
        style.theme_use('clam')

        # Frame styles
        style.configure('Card.TFrame', background=COLORS['bg_light'])

        # Label styles
        style.configure('Title.TLabel',
                     font=self.title_font,
                     foreground=COLORS['highlight'],
                     background=COLORS['bg'])

        style.configure('Header.TLabel',
                     font=self.header_font,
                     foreground=COLORS['process'],
                     background=COLORS['bg_light'])

        style.configure('Info.TLabel',
                     font=self.text_font,
                     foreground=COLORS['text'],
                     background=COLORS['bg_light'])

        # Treeview - use standard style to avoid visibility issues
        style.configure('Custom.Treeview',
                     background=COLORS['bg_light'],
                     foreground=COLORS['text'],
                     fieldbackground=COLORS['bg_light'],
                     rowheight=25)

        style.configure('Custom.Treeview.Heading',
                     background=COLORS['panel'],
                     foreground=COLORS['text'],
                     font=self.header_font)

        # Combobox - keep it simple
        style.configure('Custom.TCombobox',
                     background=COLORS['accent'])

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main container
        main_frame = tk.Frame(self.root, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configure main frame
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)

        # Title
        self.create_title(main_frame)

        # Left panel - Controls
        left_card = tk.Frame(main_frame, bg=COLORS['bg_light'],
                            highlightbackground=COLORS['highlight'],
                            highlightthickness=2, bd=0)
        left_card.grid(row=1, column=0, sticky='nsew', padx=(0, 10), pady=10)
        left_card.grid_columnconfigure(0, weight=1)

        self.create_control_panel(left_card)

        # Right panel - Graph
        right_card = tk.Frame(main_frame, bg=COLORS['bg_light'],
                             highlightbackground=COLORS['process'],
                             highlightthickness=2, bd=0)
        right_card.grid(row=1, column=1, sticky='nsew', pady=10)
        right_card.grid_rowconfigure(0, weight=1)
        right_card.grid_columnconfigure(0, weight=1)

        self.create_graph_panel(right_card)

        # Bottom panel - Status
        status_card = tk.Frame(main_frame, bg=COLORS['bg_light'],
                              highlightbackground=COLORS['resource'],
                              highlightthickness=2, bd=0)
        status_card.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)

        self.create_status_panel(status_card)

    def create_title(self, parent):
        """Create title"""
        title_frame = tk.Frame(parent, bg=COLORS['bg'])
        title_frame.grid(row=0, column=0, columnspan=2, pady=15)

        title = tk.Label(title_frame,
                        text="DeadlockVis",
                        font=self.title_font,
                        bg=COLORS['bg'],
                        fg=COLORS['highlight'])
        title.pack()

        subtitle = tk.Label(title_frame,
                           text="Interactive Resource Allocation Graph Analyzer",
                           font=self.text_font,
                           bg=COLORS['bg'],
                           fg=COLORS['text_dark'])
        subtitle.pack()

    def create_control_panel(self, parent):
        """Create the control panel"""
        row = 0

        # Add Process section
        process_frame = tk.LabelFrame(parent, text="[+] Add Process",
                                     font=self.header_font,
                                     bg=COLORS['bg_light'],
                                     fg=COLORS['process'],
                                     padx=10, pady=10)
        process_frame.grid(row=row, column=0, sticky='ew', pady=5)
        process_frame.grid_columnconfigure(0, weight=1)

        self.process_name = tk.Entry(process_frame, font=self.text_font,
                                    bg='white', fg='black',
                                    relief='solid', justify='center')
        self.process_name.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.process_name.insert(0, f"P{len(self.rag.processes) + 1}")

        add_proc_btn = AnimatedButton(process_frame, "Add Process",
                                     self.add_process, width=120,
                                     bg_color=COLORS['process'])
        add_proc_btn.grid(row=1, column=0, pady=5)

        row += 1

        # Add Resource section
        resource_frame = tk.LabelFrame(parent, text="[+] Add Resource",
                                      font=self.header_font,
                                      bg=COLORS['bg_light'],
                                      fg=COLORS['resource'],
                                      padx=10, pady=10)
        resource_frame.grid(row=row, column=0, sticky='ew', pady=5)

        tk.Label(resource_frame, text="Name:", bg=COLORS['bg_light'],
                fg=COLORS['text'], font=self.text_font).grid(row=0, column=0, sticky='w')
        self.resource_name = tk.Entry(resource_frame, font=self.text_font,
                                     bg='white', fg='black',
                                     relief='solid', width=10)
        self.resource_name.grid(row=0, column=1, padx=5)
        self.resource_name.insert(0, f"R{len(self.rag.resources) + 1}")

        tk.Label(resource_frame, text="Instances:", bg=COLORS['bg_light'],
                fg=COLORS['text'], font=self.text_font).grid(row=1, column=0, sticky='w', pady=5)
        self.resource_instances = tk.Spinbox(resource_frame, from_=1, to=10, width=5,
                                            font=self.text_font)
        self.resource_instances.grid(row=1, column=1, pady=5, sticky='w')
        self.resource_instances.delete(0, 'end')
        self.resource_instances.insert(0, "1")

        add_res_btn = AnimatedButton(resource_frame, "Add Resource",
                                    self.add_resource, width=120,
                                    bg_color=COLORS['resource'])
        add_res_btn.grid(row=2, column=0, columnspan=2, pady=5)

        row += 1

        # Create Edge section
        edge_frame = tk.LabelFrame(parent, text="[+] Create Edge",
                                  font=self.header_font,
                                  bg=COLORS['bg_light'],
                                  fg=COLORS['request'],
                                  padx=10, pady=10)
        edge_frame.grid(row=row, column=0, sticky='ew', pady=5)
        edge_frame.grid_columnconfigure(1, weight=1)

        tk.Label(edge_frame, text="From:", bg=COLORS['bg_light'],
                fg=COLORS['text'], font=self.text_font).grid(row=0, column=0, sticky='w')
        self.edge_from = ttk.Combobox(edge_frame, state='readonly', width=15)
        self.edge_from.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        tk.Label(edge_frame, text="To:", bg=COLORS['bg_light'],
                fg=COLORS['text'], font=self.text_font).grid(row=1, column=0, sticky='w')
        self.edge_to = ttk.Combobox(edge_frame, state='readonly', width=15)
        self.edge_to.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        tk.Label(edge_frame, text="Count:", bg=COLORS['bg_light'],
                fg=COLORS['text'], font=self.text_font).grid(row=2, column=0, sticky='w')
        self.edge_count = tk.Spinbox(edge_frame, from_=1, to=10, width=5,
                                    font=self.text_font)
        self.edge_count.grid(row=2, column=1, sticky='w', pady=5)
        self.edge_count.delete(0, 'end')
        self.edge_count.insert(0, "1")

        # Edge buttons
        btn_frame = tk.Frame(edge_frame, bg=COLORS['bg_light'])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)

        req_btn = AnimatedButton(btn_frame, "Request -->",
                                self.request_edge, width=100,
                                bg_color=COLORS['request'])
        req_btn.pack(side='left', padx=5)

        alloc_btn = AnimatedButton(btn_frame, "<-- Allocate",
                                  self.allocate_edge, width=100,
                                  bg_color=COLORS['allocation'])
        alloc_btn.pack(side='left', padx=5)

        row += 1

        # Actions section
        actions_frame = tk.LabelFrame(parent, text="[!] Actions",
                                     font=self.header_font,
                                     bg=COLORS['bg_light'],
                                     fg=COLORS['highlight'],
                                     padx=10, pady=10)
        actions_frame.grid(row=row, column=0, sticky='ew', pady=5)

        btn_grid = tk.Frame(actions_frame, bg=COLORS['bg_light'])
        btn_grid.pack()

        detect_btn = AnimatedButton(btn_grid, "Detect Deadlock",
                                   self.detect_deadlock, width=120,
                                   bg_color='#8338ec')
        detect_btn.grid(row=0, column=0, padx=5, pady=3)

        resolve_btn = AnimatedButton(btn_grid, "Resolve",
                                    self.resolve_deadlock, width=120,
                                    bg_color='#ff006e')
        resolve_btn.grid(row=0, column=1, padx=5, pady=3)

        example_btn = AnimatedButton(btn_grid, "Examples",
                                    self.load_example_dialog, width=120,
                                    bg_color='#3a86ff')
        example_btn.grid(row=1, column=0, padx=5, pady=3)

        clear_btn = AnimatedButton(btn_grid, "Clear All",
                                  self.clear_graph, width=120,
                                  bg_color='#fb5607')
        clear_btn.grid(row=1, column=1, padx=5, pady=3)

        row += 1

        # Node list
        list_frame = tk.LabelFrame(parent, text="[+] Current Nodes",
                                  font=self.header_font,
                                  bg=COLORS['bg_light'],
                                  fg=COLORS['text'],
                                  padx=5, pady=5)
        list_frame.grid(row=row, column=0, sticky='nsew', pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Treeview with proper styling
        self.node_tree = ttk.Treeview(list_frame, columns=('Type', 'Info'),
                                     show='tree', height=8,
                                     style='Custom.Treeview')
        self.node_tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                 command=self.node_tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.node_tree.configure(yscrollcommand=scrollbar.set)

        self.node_tree.heading('#0', text='Node')
        self.node_tree.heading('Type', text='Type')
        self.node_tree.heading('Info', text='Info')

        remove_btn = AnimatedButton(list_frame, "Remove Selected",
                                   self.remove_selected_node, width=200,
                                   bg_color='#ff006e')
        remove_btn.grid(row=1, column=0, columnspan=2, pady=5)

        parent.grid_rowconfigure(row, weight=1)

    def create_graph_panel(self, parent):
        """Create the matplotlib graph visualization"""
        # Create figure with dark background
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.fig.patch.set_facecolor(COLORS['bg_light'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS['bg_light'])

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Toolbar
        toolbar_frame = tk.Frame(parent, bg=COLORS['bg_light'])
        toolbar_frame.grid(row=1, column=0, sticky='ew', pady=5)

        refresh_btn = AnimatedButton(toolbar_frame, "Refresh",
                                    self.draw_graph, width=100,
                                    bg_color=COLORS['process'])
        refresh_btn.pack(side='left', padx=5)

        save_btn = AnimatedButton(toolbar_frame, "Save Image",
                                 self.save_image, width=120,
                                 bg_color=COLORS['resource'])
        save_btn.pack(side='left', padx=5)

    def create_status_panel(self, parent):
        """Create status panel with high contrast text"""
        # Status label
        self.status_label = tk.Label(parent,
                                    text="System Status: SAFE - No Deadlock Detected",
                                    font=('Arial', 12, 'bold'),
                                    bg=COLORS['bg_light'],
                                    fg=COLORS['resource'])
        self.status_label.pack(side='left', padx=20)

        # Method label
        self.method_label = tk.Label(parent,
                                    text="Detection Method: Ready",
                                    font=self.text_font,
                                    bg=COLORS['bg_light'],
                                    fg=COLORS['text'])
        self.method_label.pack(side='left', padx=20)

        # Algorithm info
        self.algo_info = tk.Label(parent,
                                 text="Algorithms: Cycle Detection | Wait-For Graph | Banker's",
                                 font=('Arial', 8),
                                 bg=COLORS['bg_light'],
                                 fg='#888888')
        self.algo_info.pack(side='right', padx=20)

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Graph", command=self.clear_graph)
        file_menu.add_command(label="Save Graph", command=self.save_graph)
        file_menu.add_command(label="Load Graph", command=self.load_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Examples", menu=examples_menu)
        examples_menu.add_command(label="Simple Deadlock",
                                 command=lambda: self.load_example("simple"))
        examples_menu.add_command(label="Multi-Instance Deadlock",
                                 command=lambda: self.load_example("multi"))
        examples_menu.add_command(label="No Deadlock (Safe)",
                                 command=lambda: self.load_example("safe"))

    def update_comboboxes(self):
        """Update the edge from/to comboboxes"""
        process_names = [p.name for p in self.rag.processes.values()]
        resource_names = [r.name for r in self.rag.resources.values()]

        self.edge_from['values'] = process_names + resource_names
        self.edge_to['values'] = process_names + resource_names

    def update_node_tree(self):
        """Update the node treeview"""
        for item in self.node_tree.get_children():
            self.node_tree.delete(item)

        # Add processes
        for pid, process in self.rag.processes.items():
            allocated = ", ".join([f"{r}:{c}" for r, c in process.allocated_resources.items()]) or "None"
            requested = ", ".join([f"{r}:{c}" for r, c in process.requested_resources.items()]) or "None"
            info = f"Allocated: {allocated} | Requested: {requested}"
            self.node_tree.insert('', 'end', text=process.name,
                                 values=('Process', info))

        # Add resources
        for rid, resource in self.rag.resources.items():
            info = f"{resource.available_instances}/{resource.total_instances} available"
            self.node_tree.insert('', 'end', text=resource.name,
                                 values=('Resource', info))

    def add_process(self):
        """Add a process to the graph"""
        name = self.process_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Process name cannot be empty")
            return

        pid = f"proc_{len(self.rag.processes)}"
        self.rag.add_process(pid, name)
        self.process_name.delete(0, tk.END)
        self.process_name.insert(0, f"P{len(self.rag.processes) + 1}")

        self.update_comboboxes()
        self.update_node_tree()
        self.draw_graph()

    def add_resource(self):
        """Add a resource to the graph"""
        name = self.resource_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Resource name cannot be empty")
            return

        try:
            instances = int(self.resource_instances.get())
        except ValueError:
            instances = 1

        rid = f"res_{len(self.rag.resources)}"
        self.rag.add_resource(rid, instances, name)
        self.resource_name.delete(0, tk.END)
        self.resource_name.insert(0, f"R{len(self.rag.resources) + 1}")

        self.update_comboboxes()
        self.update_node_tree()
        self.draw_graph()

    def request_edge(self):
        """Create a request edge"""
        from_name = self.edge_from.get()
        to_name = self.edge_to.get()

        if not from_name or not to_name:
            messagebox.showerror("Error", "Please select both from and to nodes")
            return

        from_process = None
        to_resource = None

        for pid, p in self.rag.processes.items():
            if p.name == from_name:
                from_process = pid
                break

        for rid, r in self.rag.resources.items():
            if r.name == to_name:
                to_resource = rid
                break

        if from_process is None or to_resource is None:
            messagebox.showerror("Error", "Request edge must go from Process to Resource")
            return

        count = int(self.edge_count.get())
        self.rag.request_resource(from_process, to_resource, count)

        self.update_node_tree()
        self.draw_graph()
        self.detect_deadlock()

    def allocate_edge(self):
        """Create an allocation edge"""
        from_name = self.edge_from.get()
        to_name = self.edge_to.get()

        if not from_name or not to_name:
            messagebox.showerror("Error", "Please select both from and to nodes")
            return

        from_resource = None
        to_process = None

        for rid, r in self.rag.resources.items():
            if r.name == from_name:
                from_resource = rid
                break

        for pid, p in self.rag.processes.items():
            if p.name == to_name:
                to_process = pid
                break

        if from_resource is None or to_process is None:
            messagebox.showerror("Error", "Allocation edge must go from Resource to Process")
            return

        count = int(self.edge_count.get())
        if not self.rag.request_resource(to_process, from_resource, count):
            messagebox.showinfo("Info", "Resource not available. Request edge added instead.")

        self.update_node_tree()
        self.draw_graph()
        self.detect_deadlock()

    def remove_selected_node(self):
        """Remove the selected node"""
        selected = self.node_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a node to remove")
            return

        item = selected[0]
        name = self.node_tree.item(item, 'text')

        for pid, p in list(self.rag.processes.items()):
            if p.name == name:
                self.rag.remove_process(pid)
                break

        for rid, r in list(self.rag.resources.items()):
            if r.name == name:
                self.rag.remove_resource(rid)
                break

        self.update_comboboxes()
        self.update_node_tree()
        self.draw_graph()
        self.detect_deadlock()

    def detect_deadlock(self):
        """Run deadlock detection"""
        is_deadlocked, nodes, method = self.rag.is_deadlocked()

        if is_deadlocked:
            self.status_label.configure(
                text=f"DEADLOCK DETECTED! Involved: {', '.join(nodes)}",
                fg=COLORS['process_deadlock']
            )
            self.method_label.configure(
                text=f"Detection Method: {method}",
                fg=COLORS['highlight']
            )
        else:
            self.status_label.configure(
                text="System Status: SAFE - No Deadlock Detected",
                fg=COLORS['resource']
            )
            self.method_label.configure(
                text="Detection Method: -",
                fg=COLORS['text']
            )

        self.draw_graph(highlight_nodes=nodes if is_deadlocked else [])

    def resolve_deadlock(self):
        """Break deadlock"""
        is_deadlocked, nodes, method = self.rag.is_deadlocked()

        if not is_deadlocked:
            messagebox.showinfo("All Good!", "No deadlock detected - system is safe!")
            return

        result = messagebox.askyesno("Resolve Deadlock",
            f"Deadlock detected involving: {', '.join(nodes)}\n\n"
            "Would you like to:\n"
            "YES = Terminate a deadlocked process\n"
            "NO = Preempt a resource")

        if result:
            process_name = nodes[0]
            for pid in list(self.rag.processes.keys()):
                if self.rag.processes[pid].name == process_name:
                    self.rag.remove_process(pid)
                    messagebox.showinfo("Success!", f"Process {process_name} terminated - Deadlock resolved!")
                    break
        else:
            process_name = nodes[0]
            for pid, p in self.rag.processes.items():
                if p.name == process_name and p.allocated_resources:
                    rid = list(p.allocated_resources.keys())[0]
                    resource_name = self.rag.resources[rid].name
                    self.rag.release_resource(pid, rid)
                    messagebox.showinfo("Success!", f"Resource {resource_name} preempted - Deadlock resolved!")
                    break

        self.update_comboboxes()
        self.update_node_tree()
        self.draw_graph()
        self.detect_deadlock()

    def clear_graph(self):
        """Clear the graph"""
        if messagebox.askyesno("Confirm", "Clear all nodes and edges?"):
            self.rag = ResourceAllocationGraph()
            self.update_comboboxes()
            self.update_node_tree()
            self.draw_graph()
            self.status_label.configure(
                text="System Status: SAFE - No Deadlock Detected",
                fg=COLORS['resource']
            )
            self.method_label.configure(text="Detection Method: Ready", fg=COLORS['text'])

    def load_example_dialog(self):
        """Show example selection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Example")
        dialog.configure(bg=COLORS['bg'])
        dialog.geometry("300x200")
        dialog.transient(self.root)

        tk.Label(dialog, text="Choose an Example",
                font=self.header_font, bg=COLORS['bg'],
                fg=COLORS['highlight']).pack(pady=10)

        examples = [
            ("Simple Deadlock", "simple", COLORS['process_deadlock']),
            ("Multi-Instance Deadlock", "multi", COLORS['request']),
            ("No Deadlock (Safe)", "safe", COLORS['resource'])
        ]

        for name, key, color in examples:
            btn = tk.Button(dialog, text=name, font=self.text_font,
                          bg=color, fg='white', width=25,
                          command=lambda k=key: [self.load_example(k), dialog.destroy()])
            btn.pack(pady=5)

    def load_example(self, example_type="simple"):
        """Load a preset example"""
        self.rag = ResourceAllocationGraph()

        if example_type == "simple":
            self.rag.add_process("p1", "P1")
            self.rag.add_process("p2", "P2")
            self.rag.add_resource("r1", 1, "R1")
            self.rag.add_resource("r2", 1, "R2")

            self.rag.request_resource("p1", "r1", 1)
            self.rag.request_resource("p2", "r2", 1)
            self.rag.request_resource("p1", "r2", 1)
            self.rag.request_resource("p2", "r1", 1)

        elif example_type == "multi":
            self.rag.add_process("p1", "P1")
            self.rag.add_process("p2", "P2")
            self.rag.add_process("p3", "P3")
            self.rag.add_resource("r1", 3, "R1")
            self.rag.add_resource("r2", 3, "R2")

            self.rag.request_resource("p1", "r1", 2)
            self.rag.request_resource("p2", "r2", 2)
            self.rag.request_resource("p3", "r1", 1)
            self.rag.request_resource("p1", "r2", 1)
            self.rag.request_resource("p2", "r1", 1)

        elif example_type == "safe":
            self.rag.add_process("p1", "P1")
            self.rag.add_process("p2", "P2")
            self.rag.add_resource("r1", 2, "R1")
            self.rag.add_resource("r2", 2, "R2")

            self.rag.request_resource("p1", "r1", 1)
            self.rag.request_resource("p2", "r2", 1)

        self.update_comboboxes()
        self.update_node_tree()
        self.draw_graph()
        self.detect_deadlock()

    def save_graph(self):
        """Save graph to JSON"""
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.rag.to_dict(), f, indent=2)
            messagebox.showinfo("Success!", f"Graph saved to {filename}")

    def load_graph(self):
        """Load graph from JSON"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.rag = ResourceAllocationGraph.from_dict(data)
            self.update_comboboxes()
            self.update_node_tree()
            self.draw_graph()
            self.detect_deadlock()
            messagebox.showinfo("Success!", f"Graph loaded from {filename}")

    def save_image(self):
        """Save graph as image"""
        filename = filedialog.asksaveasfilename(defaultextension=".png",
                                               filetypes=[("PNG files", "*.png"),
                                                         ("PDF files", "*.pdf"),
                                                         ("SVG files", "*.svg")])
        if filename:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight',
                          facecolor=COLORS['bg_light'])
            messagebox.showinfo("Success!", f"Image saved to {filename}")

    def draw_graph(self, highlight_nodes=None):
        """Draw the graph"""
        highlight_nodes = highlight_nodes or []
        self.ax.clear()
        self.ax.set_facecolor(COLORS['bg_light'])

        if len(self.rag.graph.nodes()) == 0:
            self.ax.text(0.5, 0.5, 'Ready to Build!\n\nAdd processes and resources',
                        ha='center', va='center', fontsize=14,
                        color=COLORS['text'], style='italic')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            self.canvas.draw()
            return

        # Calculate layout
        try:
            pos = nx.spring_layout(self.rag.graph, seed=42, k=3, iterations=100)
        except:
            pos = nx.circular_layout(self.rag.graph)

        # Separate nodes by type
        process_nodes = []
        resource_nodes = []
        process_colors = []
        resource_colors = []

        for node in self.rag.graph.nodes():
            if node in self.rag.processes:
                process_nodes.append(node)
                proc_name = self.rag.processes[node].name
                if proc_name in highlight_nodes or node in highlight_nodes:
                    process_colors.append(COLORS['process_deadlock'])
                else:
                    process_colors.append(COLORS['process'])
            elif node in self.rag.resources:
                resource_nodes.append(node)
                resource_colors.append(COLORS['resource'])

        # Draw edges
        request_edges = [(u, v) for u, v, d in self.rag.graph.edges(data=True)
                        if d.get('edge_type') == 'request']
        allocation_edges = [(u, v) for u, v, d in self.rag.graph.edges(data=True)
                           if d.get('edge_type') == 'allocation']

        # Draw allocation edges
        nx.draw_networkx_edges(self.rag.graph, pos, edgelist=allocation_edges,
                              edge_color=COLORS['allocation'],
                              arrows=True, arrowsize=25, width=3,
                              alpha=0.8, ax=self.ax)

        # Draw request edges
        nx.draw_networkx_edges(self.rag.graph, pos, edgelist=request_edges,
                              edge_color=COLORS['request'],
                              arrows=True, arrowsize=25, width=3,
                              style='--', alpha=0.9, ax=self.ax)

        # Draw process nodes
        if process_nodes:
            nx.draw_networkx_nodes(self.rag.graph, pos,
                                  nodelist=process_nodes,
                                  node_color=process_colors,
                                  node_shape='o',
                                  node_size=2500,
                                  edgecolors='white',
                                  linewidths=2,
                                  ax=self.ax)

        # Draw resource nodes
        if resource_nodes:
            nx.draw_networkx_nodes(self.rag.graph, pos,
                                  nodelist=resource_nodes,
                                  node_color=resource_colors,
                                  node_shape='s',
                                  node_size=2000,
                                  edgecolors='white',
                                  linewidths=2,
                                  ax=self.ax)

        # Draw labels with white text
        labels = {}
        for node in self.rag.graph.nodes():
            if node in self.rag.processes:
                labels[node] = self.rag.processes[node].name
            elif node in self.rag.resources:
                r = self.rag.resources[node]
                labels[node] = f"{r.name}\n({r.available_instances}/{r.total_instances})"

        nx.draw_networkx_labels(self.rag.graph, pos, labels,
                               font_size=11, font_weight='bold',
                               font_color='white', ax=self.ax)

        # Edge labels (counts)
        edge_labels = {}
        for u, v, d in self.rag.graph.edges(data=True):
            count = d.get('count', 1)
            if count > 1:
                edge_labels[(u, v)] = str(count)

        nx.draw_networkx_edge_labels(self.rag.graph, pos, edge_labels,
                                    font_size=10, font_color=COLORS['highlight'],
                                    font_weight='bold', ax=self.ax)

        # Title
        self.ax.set_title("Resource Allocation Graph\n"
                         "Blue circles = Processes, Green squares = Resources\n"
                         "Solid green = Allocation, Dashed orange = Request",
                         fontsize=11, color=COLORS['text'], pad=10)

        self.ax.set_axis_off()
        self.fig.tight_layout()
        self.canvas.draw()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = DeadlockGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

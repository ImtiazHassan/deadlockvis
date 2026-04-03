"""
Core data structures for Resource Allocation Graph (RAG)
"""

import networkx as nx
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional


class NodeType(Enum):
    PROCESS = "process"
    RESOURCE = "resource"


class Process:
    """Represents a process in the system"""

    def __init__(self, pid: str, name: str = None):
        self.pid = pid
        self.name = name or f"P{pid}"
        self.allocated_resources: Dict[str, int] = {}  # resource_id -> count
        self.requested_resources: Dict[str, int] = {}  # resource_id -> count
        self.is_deadlocked = False

    def __repr__(self):
        return f"Process({self.name})"


class Resource:
    """Represents a resource type with multiple instances"""

    def __init__(self, rid: str, total_instances: int = 1, name: str = None):
        self.rid = rid
        self.name = name or f"R{rid}"
        self.total_instances = total_instances
        self.available_instances = total_instances
        self.allocated_to: Dict[str, int] = {}  # process_id -> count

    @property
    def is_single_instance(self) -> bool:
        return self.total_instances == 1

    def allocate(self, process_id: str, count: int = 1) -> bool:
        """Allocate resource instances to a process"""
        if self.available_instances >= count:
            self.available_instances -= count
            self.allocated_to[process_id] = self.allocated_to.get(process_id, 0) + count
            return True
        return False

    def release(self, process_id: str, count: int = None) -> bool:
        """Release resource instances from a process"""
        if process_id not in self.allocated_to:
            return False

        allocated = self.allocated_to[process_id]
        release_count = count if count is not None else allocated

        if release_count > allocated:
            return False

        self.allocated_to[process_id] -= release_count
        self.available_instances += release_count

        if self.allocated_to[process_id] == 0:
            del self.allocated_to[process_id]

        return True

    def __repr__(self):
        return f"Resource({self.name}, {self.available_instances}/{self.total_instances})"


class ResourceAllocationGraph:
    """
    Resource Allocation Graph for deadlock detection
    Uses NetworkX for graph operations
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.processes: Dict[str, Process] = {}
        self.resources: Dict[str, Resource] = {}

    def add_process(self, pid: str, name: str = None) -> Process:
        """Add a process to the graph"""
        process = Process(pid, name)
        self.processes[pid] = process
        self.graph.add_node(pid, node_type=NodeType.PROCESS, object=process)
        return process

    def add_resource(self, rid: str, total_instances: int = 1, name: str = None) -> Resource:
        """Add a resource to the graph"""
        resource = Resource(rid, total_instances, name)
        self.resources[rid] = resource
        self.graph.add_node(rid, node_type=NodeType.RESOURCE, object=resource)
        return resource

    def request_resource(self, process_id: str, resource_id: str, count: int = 1) -> bool:
        """
        Process requests a resource.
        Returns True if granted immediately, False if request edge added.
        """
        if process_id not in self.processes or resource_id not in self.resources:
            return False

        process = self.processes[process_id]
        resource = self.resources[resource_id]

        # Try to allocate immediately if available
        if resource.allocate(process_id, count):
            # Add allocation edge (resource -> process)
            self.graph.add_edge(resource_id, process_id,
                              edge_type="allocation",
                              count=count)
            process.allocated_resources[resource_id] = count
            return True
        else:
            # Add request edge (process -> resource)
            self.graph.add_edge(process_id, resource_id,
                              edge_type="request",
                              count=count)
            process.requested_resources[resource_id] = count
            return False

    def release_resource(self, process_id: str, resource_id: str, count: int = None) -> bool:
        """Process releases a resource"""
        if process_id not in self.processes or resource_id not in self.resources:
            return False

        process = self.processes[process_id]
        resource = self.resources[resource_id]

        if resource.release(process_id, count):
            # Remove allocation edge
            if self.graph.has_edge(resource_id, process_id):
                self.graph.remove_edge(resource_id, process_id)

            if resource_id in process.allocated_resources:
                del process.allocated_resources[resource_id]

            return True
        return False

    def grant_pending_request(self, process_id: str, resource_id: str) -> bool:
        """Convert a request edge to an allocation edge"""
        if not self.graph.has_edge(process_id, resource_id):
            return False

        process = self.processes[process_id]
        resource = self.resources[resource_id]
        edge_data = self.graph.get_edge_data(process_id, resource_id)
        count = edge_data.get("count", 1)

        # Remove request edge
        self.graph.remove_edge(process_id, resource_id)
        if resource_id in process.requested_resources:
            del process.requested_resources[resource_id]

        # Try to allocate
        if resource.allocate(process_id, count):
            self.graph.add_edge(resource_id, process_id,
                              edge_type="allocation",
                              count=count)
            process.allocated_resources[resource_id] = count
            return True

        return False

    def remove_process(self, pid: str):
        """Remove a process and all its edges"""
        if pid in self.processes:
            process = self.processes[pid]

            # Release all allocated resources
            for rid in list(process.allocated_resources.keys()):
                self.release_resource(pid, rid)

            # Remove request edges
            for rid in list(process.requested_resources.keys()):
                if self.graph.has_edge(pid, rid):
                    self.graph.remove_edge(pid, rid)

            self.graph.remove_node(pid)
            del self.processes[pid]

    def remove_resource(self, rid: str):
        """Remove a resource and all its edges"""
        if rid in self.resources:
            # Release from all processes
            for pid in list(self.resources[rid].allocated_to.keys()):
                self.release_resource(pid, rid)

            self.graph.remove_node(rid)
            del self.resources[rid]

    def get_wait_for_graph(self) -> nx.DiGraph:
        """
        Convert RAG to Wait-For Graph (WFG) for deadlock detection.
        In WFG: edge Pi -> Pj means Pi is waiting for Pj to release a resource.
        """
        wfg = nx.DiGraph()

        # Add all processes as nodes
        for pid in self.processes:
            wfg.add_node(pid)

        # Add edges: for each request edge Pi -> R -> Pj, add Pi -> Pj
        for pid, process in self.processes.items():
            for rid in process.requested_resources:
                if rid in self.resources:
                    resource = self.resources[rid]
                    # Pi is waiting for all processes that hold instances of R
                    for holder_pid in resource.allocated_to:
                        if holder_pid != pid:
                            wfg.add_edge(pid, holder_pid, resource=rid)

        return wfg

    def detect_deadlock_single_instance(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Detect deadlock for single-instance resources using cycle detection.
        Returns: (is_deadlocked, cycle_nodes)
        """
        # For single-instance, we can check RAG directly
        try:
            cycle = nx.find_cycle(self.graph, orientation='original')
            # Extract unique nodes in the cycle
            nodes_in_cycle = set()
            for u, v, _ in cycle:
                nodes_in_cycle.add(u)
                nodes_in_cycle.add(v)
            return True, list(nodes_in_cycle)
        except nx.NetworkXNoCycle:
            return False, None

    def detect_deadlock_wait_for_graph(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Detect deadlock using Wait-For Graph (for multi-instance).
        Returns: (is_deadlocked, cycle_nodes)
        """
        wfg = self.get_wait_for_graph()

        try:
            cycle = nx.find_cycle(wfg, orientation='original')
            nodes_in_cycle = set()
            for u, v, _ in cycle:
                nodes_in_cycle.add(u)
                nodes_in_cycle.add(v)
            return True, list(nodes_in_cycle)
        except nx.NetworkXNoCycle:
            return False, None

    def bankers_algorithm(self, available: Dict[str, int] = None) -> Tuple[bool, Optional[List[str]]]:
        """
        Banker's Algorithm for deadlock avoidance.
        Returns: (is_safe, safe_sequence or None)
        """
        if available is None:
            available = {rid: r.available_instances for rid, r in self.resources.items()}

        # Build allocation and need matrices
        allocation = {}
        need = {}
        finished = set()
        safe_sequence = []

        for pid, process in self.processes.items():
            allocation[pid] = process.allocated_resources.copy()
            need[pid] = process.requested_resources.copy()

        work = available.copy()

        while len(finished) < len(self.processes):
            found = False
            for pid in self.processes:
                if pid in finished:
                    continue

                # Check if need <= work
                can_allocate = True
                for rid, amount in need[pid].items():
                    if work.get(rid, 0) < amount:
                        can_allocate = False
                        break

                if can_allocate:
                    # This process can complete
                    for rid, amount in allocation[pid].items():
                        work[rid] = work.get(rid, 0) + amount
                    finished.add(pid)
                    safe_sequence.append(pid)
                    found = True

            if not found:
                # Deadlock detected - remaining processes are deadlocked
                deadlocked = [pid for pid in self.processes if pid not in finished]
                return False, deadlocked

        return True, safe_sequence

    def is_deadlocked(self) -> Tuple[bool, Optional[List[str]], str]:
        """
        Check if system is in deadlock state.
        Returns: (is_deadlocked, involved_nodes, method_used)
        """
        # First try single-instance detection
        deadlocked, nodes = self.detect_deadlock_single_instance()
        if deadlocked:
            return True, nodes, "RAG Cycle Detection"

        # Try wait-for graph
        deadlocked, nodes = self.detect_deadlock_wait_for_graph()
        if deadlocked:
            return True, nodes, "Wait-For Graph Cycle Detection"

        # Try Banker's algorithm (this checks for safe state)
        is_safe, result = self.bankers_algorithm()
        if not is_safe:
            return True, result, "Banker's Algorithm (Unsafe State)"

        return False, None, ""

    def to_dict(self) -> dict:
        """Serialize graph to dictionary"""
        return {
            "processes": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "allocated": p.allocated_resources,
                    "requested": p.requested_resources
                }
                for p in self.processes.values()
            ],
            "resources": [
                {
                    "rid": r.rid,
                    "name": r.name,
                    "total": r.total_instances,
                    "available": r.available_instances
                }
                for r in self.resources.values()
            ],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "type": data.get("edge_type"),
                    "count": data.get("count", 1)
                }
                for u, v, data in self.graph.edges(data=True)
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ResourceAllocationGraph':
        """Deserialize graph from dictionary"""
        rag = cls()

        for p in data.get("processes", []):
            rag.add_process(p["pid"], p.get("name"))

        for r in data.get("resources", []):
            rag.add_resource(r["rid"], r.get("total", 1), r.get("name"))

        for e in data.get("edges", []):
            if e["type"] == "allocation":
                rag.request_resource(e["target"], e["source"], e.get("count", 1))
            elif e["type"] == "request":
                rag.request_resource(e["source"], e["target"], e.get("count", 1))

        return rag

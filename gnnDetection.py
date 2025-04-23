import torch
from torch_geometric.data import Data
from collections import defaultdict
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def parse_netlist(lines):
    gates = []
    connections = defaultdict(list)
    gate_types = set()  # Dynamically collect gate types

    for line in lines:
        # Trim and skip non-gate lines
        line = line.strip()
        if not line or '(' not in line or line.startswith("module") or line.startswith("endmodule"):
            continue

        # Updated regex to handle gate instantiations
        match = re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line)
        if not match:
            # Debugging: Log lines that do not match the regex
            print(f"Unmatched line: {line}")
            continue

        gate_type, gate_name, pin_block = match.groups()
        gate_types.add(gate_type)  # Add gate type to the set
        pin_pairs = re.findall(r"\.(\w+)\(([^)]+)\)", pin_block)
        pin_map = {pin: net for pin, net in pin_pairs}

        gates.append((gate_type, gate_name, pin_map))

        for pin, net in pin_map.items():
            connections[net].append((gate_name, pin))

    print(f"Detected gate types: {gate_types}")
    print(f"Number of gates: {len(gates)}")
    return gates, connections, sorted(gate_types)  # Return sorted gate types

def build_graph(gates, connections, gate_types):
    """
    Builds a graph representation of the circuit.

    Args:
        gates (list): List of gates with their types, names, and pin mappings.
        connections (dict): Dictionary mapping nets to connected gates and pins.
        gate_types (list): List of unique gate types.

    Returns:
        Data: A PyTorch Geometric Data object representing the graph.
    """
    # Map gate types and gate names to indices
    gate_type_to_idx = {gate_type: idx for idx, gate_type in enumerate(gate_types)}
    gate_name_to_idx = {gate_name: idx for idx, (_, gate_name, _) in enumerate(gates)}

    # Initialize feature matrix (one-hot encoding for gate types)
    num_gates = len(gates)
    num_gate_types = len(gate_types)
    x = np.zeros((num_gates, num_gate_types), dtype=np.float32)

    for idx, (gate_type, _, _) in enumerate(gates):
        if gate_type in gate_type_to_idx:
            x[idx, gate_type_to_idx[gate_type]] = 1

    # Initialize edge list
    edge_index = []

    # Define input and output pins
    output_pins = {'uart_XMIT_dataH', 'xmit_doneH', 'rec_readyH', 'test_so'}
    input_pins = {'sys_clk', 'sys_rst_l', 'xmitH', 'uart_REC_dataH', 'test_mode', 'test_se', 'test_si'}

    # Build edges based on connections
    for net, connected in connections.items():
        # Identify drivers (sources) and sinks (destinations)
        drivers = {gate_name for gate_name, pin in connected if pin in output_pins or pin in input_pins}
        sinks = {gate_name for gate_name, pin in connected if pin not in output_pins and pin not in input_pins}

        # Add edges from drivers to sinks
        for src in drivers:
            for dst in sinks:
                if src in gate_name_to_idx and dst in gate_name_to_idx:
                    edge_index.append((gate_name_to_idx[src], gate_name_to_idx[dst]))

    # Convert edge list to PyTorch tensor
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

    # Convert feature matrix to PyTorch tensor
    x = torch.tensor(x, dtype=torch.float)

    # Return the graph as a PyTorch Geometric Data object
    return Data(x=x, edge_index=edge_index)

def read_verilog_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    # Return all lines without filtering
    return [line.strip() for line in lines]

# Read and parse the Verilog file
verilog_file = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\uart_formatted.v"
verilog_lines = read_verilog_file(verilog_file)

# Parse the netlist and dynamically detect gate types
gates, connections, gate_types = parse_netlist(verilog_lines)

# Build the graph using dynamically detected gate types
graph = build_graph(gates, connections, gate_types)

print(graph)

G = nx.DiGraph()
G.add_edges_from(graph.edge_index.t().tolist())
nx.draw(G, with_labels=True)
plt.show()

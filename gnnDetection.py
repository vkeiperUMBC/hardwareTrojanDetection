import torch
from torch_geometric.data import Data
from collections import defaultdict
import re
import numpy as np

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
    gate_type_to_idx = {g: i for i, g in enumerate(gate_types)}  # Dynamic mapping
    gate_name_to_idx = {name: idx for idx, (_, name, _) in enumerate(gates)}
    num_gates = len(gates)

    # Create feature matrix
    x = np.zeros((num_gates, len(gate_types)), dtype=np.float32)
    for idx, (gate_type, _, _) in enumerate(gates):
        if gate_type in gate_type_to_idx:
            x[idx, gate_type_to_idx[gate_type]] = 1

    # Create edge index
    edge_index = []
    output_pins = {'Y', 'Z', 'OUT', 'F'}

    for net, connected in connections.items():
        drivers = {g for g, p in connected if p in output_pins}
        sinks = {g for g, p in connected if p not in output_pins}

        edge_index.extend(
            (gate_name_to_idx[src], gate_name_to_idx[dst])
            for src in drivers for dst in sinks
            if src in gate_name_to_idx and dst in gate_name_to_idx
        )

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    x = torch.tensor(x, dtype=torch.float)

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
print(f"Edge Index: {graph.edge_index.}")

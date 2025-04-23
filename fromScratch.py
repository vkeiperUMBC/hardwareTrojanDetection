import torch
from torch_geometric.data import Data
import networkx as nx
import matplotlib.pyplot as plt
import re

class node:
    def __init__(self, name, gate_type, conn_names):
        self.name = name
        self.gate_type = gate_type
        self.conn_names = conn_names
        self.conn_id = 0
        self.conn_Num = []

    def __repr__(self):
        return f"Node(name={self.name}, gate_type={self.gate_type})"


def pnl_gates(lines):
    nodes =[]

    for line in lines:
        # Trim and skip non-gate lines
        wireNum = 0
        line = line.strip()
        if line.startswith("wire"):
            # Increment wireNum for unique naming
            wireNum += 1
            # Modify the line to keep "wire" in front, add W(wireNum), and ensure the semicolon is at the end
            connections = line[5:].strip().rstrip(";")  # Remove "wire" and any trailing semicolon
            line = f"wire W{wireNum} ({connections});"  # Add the semicolon at the end
        elif not line or '(' not in line or line.startswith("module") or line.startswith("endmodule"):
            continue

        # Updated regex to handle gate instantiations
        match = re.match(r"(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;", line)         
        if not match:
            # Debugging: Log lines that do not match the regex
            print(f"Unmatched line: {line}")
            continue
        
        # Parse the match string to extract gate details
        gate_type, gate_name, pin_block = match.groups()

        # Extract conn_names from the pin block
        conn_names = [conn.strip() for conn in pin_block.split(",")]

        # Initialize a node object and add it to the nodes list
        new_node = node(name=gate_name, gate_type=gate_type, conn_names=conn_names)
        nodes.append(new_node)

    return nodes;

def pnl_IO(lines):
    """
    Parse the Verilog file to create nodes for inputs and outputs.

    Args:
        lines (list): List of lines from the Verilog file.

    Returns:
        list: List of input and output nodes.
    """
    IO_nodes = []

    # Parse the Verilog file line by line
    for line in lines:
        line = line.strip()

        # Detect module header and extract inputs/outputs
        if line.startswith("module"):
            # Extract the part inside parentheses
            match = re.search(r"\((.*)\)", line)
            if match:
                io_list = match.group(1).split(",")
                for io in io_list:
                    io = io.strip()
                    if io.startswith("input wire"):
                        signal = io.replace("input wire", "").strip()
                        new_node = node(name=signal, gate_type="input", conn_names=[])
                        IO_nodes.append(new_node)
                    elif io.startswith("output wire"):
                        signal = io.replace("output wire", "").strip()
                        new_node = node(name=signal, gate_type="output", conn_names=[])
                        IO_nodes.append(new_node)

        # Detect gate conn_names and add them to input/output nodes
        elif re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line):
            match = re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line)
            if match:
                gate_type, gate_name, pin_block = match.groups()
                conn_names = [conn.strip() for conn in pin_block.split(",")]

                # Add conn_names to input/output nodes
                for conn in conn_names[1:]:  # Skip the first connection (output of the gate)
                    for io_node in IO_nodes:
                        if io_node.name == conn:
                            io_node.conn_names.append(gate_name)

    return IO_nodes

def constructEdgeList(nodes, io_nodes):
    edges = ([],[])
    conn_id = 0
    for node in io_nodes:
        node.conn_id = conn_id
        conn_id += 1
    for node in nodes:
        node.conn_id = conn_id
        conn_id += 1
    assList = ([],[])
    wassList = ([],[])
    for node in io_nodes:
        assList[0].append(node.name)
        assList[1].append(node.conn_id)
    for node in nodes:
        assList[0].append(node.name)
        assList[1].append(node.conn_id)
    for node in nodes:
        if node.gate_type == "wire":
            


    for node in io_nodes:
        for conn in node.conn_names:
            if conn in assList[0]:
                edges[0].append(node.conn_id)
                edges[1].append(assList[1][assList[0].index(conn)])
    for node in nodes:
        for conn in node.conn_names:
            if conn in assList[0]:
                edges[0].append(node.conn_id)
                edges[1].append(assList[1][assList[0].index(conn)])
    return edges;




def read_verilog_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    # Return all lines without filtering
    return [line.strip() for line in lines]

# Read and parse the Verilog file
verilog_file = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test_formatted.v"
verilog_lines = read_verilog_file(verilog_file)
nodes = pnl_gates(verilog_lines)
io_nodes = pnl_IO(verilog_lines)
edges = constructEdgeList(nodes, io_nodes)
# Generate edge_index from nodes
edge_index = torch.tensor(edges, dtype=torch.long)
# Convert edge_index to a list of edges
edges = edge_index.t().tolist()

# Create a mapping of node IDs to their types for labeling
node_labels = {}

# Add input/output nodes to the label mapping
for node in io_nodes:
    node_labels[node.conn_id] = f"{node.gate_type}: {node.name}"

# Add gate nodes to the label mapping
for node in nodes:
    node_labels[node.conn_id] = f"{node.gate_type}: {node.name}"

# Create a NetworkX graph
G = nx.DiGraph()  # Use DiGraph for directed graphs
G.add_edges_from(edges)

# Create positions for the nodes
pos = {}
for node in io_nodes:
    if node.gate_type == "input":
        # Place inputs on the left
        pos[node.conn_id] = (-1, node.conn_id)
    elif node.gate_type == "output":
        # Place outputs on the right
        pos[node.conn_id] = (1, node.conn_id)

# Place gate nodes in the middle
for idx, node in enumerate(nodes):
    pos[node.conn_id] = (0, idx)

# Plot the graph with node labels and custom positions
nx.draw(G, pos, labels=node_labels, with_labels=True, node_color='lightblue', font_weight='bold')
plt.title("Graph Visualization with Inputs on the Left and Outputs on the Right")
plt.show()


print("Edge Index:")
print(edge_index)

import torch
from torch_geometric.data import Data
import networkx as nx
import matplotlib.pyplot as plt
import re

file_name = "uart"
verilog_file = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\"+file_name+"_formatted.v"


# Define a class to represent a node in the graph
class node:
    def __init__(self, name, gate_type, conn_names):
        self.name = name  # Name of the node (e.g., gate name or wire name)
        self.gate_type = gate_type  # Type of the node (e.g., "and", "or", "input", "output", "wire")
        self.conn_names = conn_names  # List of connections (e.g., wires or other gates)
        self.conn_id = 0  # Unique ID for the node
        self.conn_Num = []  # Additional connection information (not used in this code)
        self.alt_name = ""  # Alternative name for the node (not used in this code)
    def __repr__(self):
        return f"Node(name={self.name}, gate_type={self.gate_type})"

# Function to parse gates and wires from the Verilog file
def pnl_gates(lines):
    nodes = []  # List to store nodes
    wireNum = 0  # Counter for uniquely naming wires

    for line in lines:
        # Trim and skip non-gate lines
        line = line.strip()
        if not line or line.startswith("module") or line.startswith("endmodule"):
            continue


        # Regex to handle gate instantiations
        match = re.match(r"(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;", line)
        if not match:
            # Debugging: Log lines that do not match the regex
            print(f"Unmatched line: {line}")
            continue

        # Parse the match string to extract gate details
        gate_type, gate_name, pin_block = match.groups()

        # Extract connection names from the pin block
        conn_names = [conn.strip() for conn in pin_block.split(",")]

        # Initialize a node object and add it to the nodes list
        new_node = node(name=gate_name, gate_type=gate_type, conn_names=conn_names)
        nodes.append(new_node)

    return nodes

# Function to parse inputs and outputs from the Verilog file
def pnl_IO(lines):
    IO_nodes = []  # List to store input/output nodes

    # Parse the Verilog file line by line
    for line in lines:
        line = line.strip()

        # Detect module header and extract inputs/outputs
        if line.startswith("input"):
            match = re.match(r"input\s+wire\s+([\w,\s]+);", line)
            if match:
                inputs = [inp.strip() for inp in match.group(1).split(",")]
                for inp in inputs:
                    new_node = node(name=inp, gate_type="input", conn_names=[])
                    IO_nodes.append(new_node)
                    
        if line.startswith("output"):
            match = re.match(r"output\s+wire\s+([\w,\s]+);", line)
            if match:
                outputs = [outp.strip() for outp in match.group(1).split(",")]
                for outp in outputs:
                    new_node = node(name=outp, gate_type="output", conn_names=[])
                    IO_nodes.append(new_node)
                            
        # Detect gate connections and add them to input/output nodes
        elif re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line):
            match = re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line)
            if match:
                gate_type, gate_name, pin_block = match.groups()
                conn_names = [conn.strip() for conn in pin_block.split(",")]

                # Add connections to input/output nodes
                for conn in conn_names[1:]:  # Skip the first connection (output of the gate)
                    for io_node in IO_nodes:
                        if io_node.name == conn:
                            io_node.conn_names.append(gate_name)
        

    return IO_nodes

def assignHandle(lines):
    assNodes = []  # List to store assignment nodes
    for line in lines:
        if line.startswith("assign"):
            # Extract the left-hand side and right-hand side of the assignment
            match = re.match(r"assign\s+(\w+)\s*=\s*(.*);", line)
            if match:
                lhs, rhs = match.groups()
                # Create a new node for the assignment
                new_node = node(name=rhs, gate_type="assign", conn_names=[lhs.strip()])
                assNodes.append(new_node)
    return assNodes;


# Function to construct the edge list for the graph
def constructEdgeList(nodes, io_nodes):
    edges = ([], [])  # Tuple to store edges (source, destination)
    conn_id = 0  # Counter for assigning unique IDs to nodes

    # Assign unique IDs to input/output nodes
    for node in io_nodes:
        node.conn_id = conn_id
        conn_id += 1

    # Assign unique IDs to gate nodes
    for node in nodes:
        node.conn_id = conn_id
        conn_id += 1

    # Create a mapping of node names to IDs
    assList = ([], [])
    for node in io_nodes:
        assList[0].append(node.name)
        assList[1].append(node.conn_id)
    for node in nodes:
        assList[0].append(node.name)
        assList[1].append(node.conn_id)

    # Add edges for input/output nodes
    for node in io_nodes:
        for conn in node.conn_names:
            if conn in assList[0]:
                edges[0].append(node.conn_id)
                edges[1].append(assList[1][assList[0].index(conn)])

    # Add edges for gate nodes
    for node in nodes:
        for conn in node.conn_names:
            if conn in assList[0]:
                edges[0].append(node.conn_id)
                edges[1].append(assList[1][assList[0].index(conn)])

    return edges

# Function to read the Verilog file
def read_verilog_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    # Return all lines without filtering
    return [line.strip() for line in lines]

# Main script to parse the Verilog file and visualize the graph
verilog_lines = read_verilog_file(verilog_file)

# Parse gates and inputs/outputs
nodes = pnl_gates(verilog_lines)
io_nodes = pnl_IO(verilog_lines)
assNodes = assignHandle(verilog_lines)
nodes = nodes + assNodes 
# Construct the edge list
edges = constructEdgeList(nodes, io_nodes,)

# Generate edge_index from nodes
edge_index = torch.tensor(edges, dtype=torch.long)

# Convert edge_index to a list of edges
edges = edge_index.t().tolist()

# Create a mapping of node IDs to their types for labeling
node_labels = {}
for node in io_nodes:
    node_labels[node.conn_id] = f"{node.gate_type}: {node.name}"
for node in nodes:
    node_labels[node.conn_id] = f"{node.gate_type}: {node.name}"

print("Edge Index:")
print(edge_index)

import matplotlib.pyplot as plt
import networkx as nx

# Create a NetworkX graph
G = nx.DiGraph()
G.add_edges_from(edges)

# Adjust the figure size to handle around 400 nodes
plt.figure(figsize=(20, 20))  # Increase the figure size for better visualization

# Use a layout suitable for large graphs
# Options: spring_layout, circular_layout, shell_layout, kamada_kawai_layout
pos = nx.spring_layout(G, k=0.5, iterations=50)  # Spring layout with adjusted parameters

# Print nodes in G in order
print("Nodes in G (in order):", sorted(G.nodes))

# Print keys in pos in order
print("Keys in pos (in order):", sorted(pos.keys()))
print("Keys in node_labels:", node_labels.keys())
print("Edges:", edges)

disconnected_nodes = [node for node in G.nodes if G.degree[node] == 0]
print("Disconnected Nodes:", disconnected_nodes)

# Plot the graph
nx.draw(G,
        pos=pos,
        with_labels=True,
        labels=node_labels,
        node_color='lightblue',
        node_size=500,  # Adjust node size for better visibility
        font_size=6,    # Reduce font size to fit labels
        font_weight='bold',
        edge_color='gray',
        arrows=True,
        arrowsize=10)

# Add a title and remove axis
plt.title("Circuit Graph: Large Graph Visualization")
plt.axis('off')
plt.tight_layout()
plt.show()

# Print the edge index
print("Edge Index:")
print(edge_index)


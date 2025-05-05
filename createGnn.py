import torch
from torch_geometric.data import Data
import networkx as nx
import matplotlib.pyplot as plt
import re

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
            # print(f"Unmatched line: {line}")
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
                    
        elif line.startswith("output"):
            match = re.match(r"output\s+wire\s+([\w,\s]+);", line)
            if match:
                outputs = [outp.strip() for outp in match.group(1).split(",")]
                for outp in outputs:
                    new_node = node(name=outp, gate_type="output", conn_names=[])
                    IO_nodes.append(new_node)
                            
        # Detect gate connections and add them to input/output nodes
        match = re.match(r"(\w+)\s+(\w+)\s*\((.*)\)\s*;", line)
        if match:
            gate_type, gate_name, pin_block = match.groups()
            conn_names = [conn.strip() for conn in pin_block.split(",")]

            # Add connections to input/output nodes
            for conn in conn_names:  # Skip the first connection (output of the gate)
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
    # for line in lines:
    #     for node in assNodes:
    #         if line.contain
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

def makeGnn(file_name):
    verilog_file = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\"+file_name+"_formatted.v"

    # Main script to parse the Verilog file and visualize the graph
    verilog_lines = read_verilog_file(verilog_file)

    # Parse gates and inputs/outputs
    nodes = pnl_gates(verilog_lines)
    io_nodes = pnl_IO(verilog_lines)
    assNodes = assignHandle(verilog_lines)
    nodes = nodes + assNodes 
    # Construct the edge list
    edges = constructEdgeList(nodes, io_nodes)

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


    # Create a NetworkX graph
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Create custom positions for nodes
    pos = {}
    
    # Position input nodes on the left
    input_nodes = [node for node in io_nodes if node.gate_type == "input"]
    input_spacing = 2.0 / (len(input_nodes) + 1)
    for i, node in enumerate(input_nodes):
        pos[node.conn_id] = (-2.0, 1.0 - (i + 1) * input_spacing)

    # Position output nodes on the right
    output_nodes = [node for node in io_nodes if node.gate_type == "output"]
    output_spacing = 2.0 / (len(output_nodes) + 1)
    for i, node in enumerate(output_nodes):
        pos[node.conn_id] = (2.0, 1.0 - (i + 1) * output_spacing)

    # Calculate layers for other nodes based on connectivity
    layers = {}
    max_layers = 4  # Number of intermediate layers

    # Assign layers based on connection distance from inputs
    for node in nodes:
        # Calculate layer based on input and output connections
        input_connections = sum(1 for conn in node.conn_names if any(inp.name == conn for inp in input_nodes))
        output_connections = sum(1 for out in output_nodes if out.name in node.conn_names)
        
        if output_connections > 0:
            layer = max_layers - 1
        else:
            layer = min(max_layers - 1, input_connections)
        
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(node)

    # Position nodes in each layer
    for layer_num, layer_nodes in layers.items():
        x_pos = -1.5 + (3 * (layer_num + 1) / (max_layers + 1))
        spacing = 2.0 / (len(layer_nodes) + 1)
        
        for i, node in enumerate(layer_nodes):
            pos[node.conn_id] = (x_pos, 1.0 - (i + 1) * spacing)

    # Plot the graph with the custom layout
    plt.figure(figsize=(15, 10))
    nx.draw(G,
            pos=pos,
            with_labels=True,
            labels=node_labels,
            node_color='lightblue',
            node_size=2000,
            font_size=8,
            font_weight='bold',
            edge_color='gray',
            arrows=True,
            arrowsize=20)

    plt.title("Circuit Graph: Inputs → Gates → Outputs")
    plt.axis('off')
    plt.tight_layout()
    plt.draw()  # Use draw() instead of show()
    plt.pause(5)  # Add a small pause to ensure the plot appears

    # Print the edge index
    print("Edge Index:")
    print(edge_index)
    
    return edges, edge_index, io_nodes, nodes, node_labels

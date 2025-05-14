from formatfile import format_file
from createGnn import makeGnn, plot_clean_gnn
import torch
from torch_geometric.data import Data

def procVfl(file_name):
    # Takes in a Verilog file and formats it for proper gnn creation
    # outputs a gnn object
    try:
        print(f"Input file = {file_name}.v")
        
        print("Formatting file...")
        format_file(file_name)
        print(f"Formatting complete. Output saved to {file_name}_formatted.v")
        
        print("Creating GNN visualization...")
        
        edges, edge_index, io_nodes, nodes, node_labels = makeGnn(file_name)
        gnn = {
            'edges': edges,
            'edge_index': edge_index,
            'io_nodes': io_nodes,
            'nodes': nodes,
            'node_labels': node_labels
        }
        return gnn
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def findTj(circuit_gnn, trojan_gnn):
    """
    Finds potential trojans in the GNN circuit by taking in a gnn and a trojan gnn
    """
    matches = []
    
    # Get the nodes and edges for both GNNs
    circuit_nodes = circuit_gnn['nodes']
    trojan_nodes = trojan_gnn['nodes']
    
    # Search based on naming scheme
    trojan_pattern = []
    for node in trojan_nodes:
        # if node.name.startswith('t'): 
        trojan_pattern.append(node.gate_type)
    
    # create a moving window as large as the trojan pattern and interiate through the circuit
    # to find potential matches
    window = len(trojan_pattern)
    for i in range(len(circuit_nodes) - window + 1):
        potential_match = circuit_nodes[i:i+window]
        
        # Check if gate types match the trojan pattern
        if all(p.gate_type == t for p, t in zip(potential_match, trojan_pattern)):
            match_info = {
                'start_index': i,
                'nodes': potential_match,
                'confidence': calcConf(potential_match, trojan_pattern)
            }
            matches.append(match_info)
    
    return matches

def calcConf(circuit_nodes, trojan_pattern):
    # Calculate confidence score for a potential trojan match. 
    
    gate_match_score = sum(1 for n, t in zip(circuit_nodes, trojan_pattern) if n.gate_type == t)
    
    naming_score = sum(1 for n in circuit_nodes if n.name.startswith('t'))
    
    connectivity_score = sum(1 for n in circuit_nodes if len(n.conn_names) >= 2)
    
    total_score = (0.5 * gate_match_score/len(trojan_pattern) +
                  0.3 * naming_score/len(circuit_nodes) +
                  0.2 * connectivity_score/len(circuit_nodes))
    
    return total_score

def rmTj(circuit_gnn, matches):
    """
    Remove trojan nodes from the circuit GNN.
    
    Args:
        circuit_gnn (dict): GNN representation of the circuit
        matches (list): List of trojan matches from findTj
    
    Returns:
        dict: Clean GNN with trojans removed
    """
    if not matches:
        return circuit_gnn
        
    # Create a new GNN dictionary
    clean_gnn = circuit_gnn.copy()
    
    # Get all trojan nodes to remove
    trojan_nodes = set()
    for match in matches:
        trojan_nodes.update(match['nodes'])
    
    # Remove trojan nodes
    clean_nodes = [node for node in circuit_gnn['nodes'] 
                  if node not in trojan_nodes]
    
    # Remove edges connected to trojan nodes
    clean_edges = []
    trojan_node_ids = {node.conn_id for node in trojan_nodes}
    
    for edge in circuit_gnn['edges']:
        if edge[0] not in trojan_node_ids and edge[1] not in trojan_node_ids:
            clean_edges.append(edge)
    
    # Update the clean GNN
    clean_gnn['nodes'] = clean_nodes
    clean_gnn['edges'] = clean_edges
    clean_gnn['edge_index'] = torch.tensor(clean_edges, dtype=torch.long).t()
    
    # Update node labels
    clean_gnn['node_labels'] = {k: v for k, v in circuit_gnn['node_labels'].items() 
                               if k not in trojan_node_ids}
    
    return clean_gnn

def outputVfile(file_name, gnn):
    """
    Outputs the GNN to a valid Verilog file.
    
    Args:
        file_name (str): Name of the output file (without extension).
        gnn (dict): GNN representation of the circuit.
    """
    try:
        with open(f"{file_name}_clean.v", "w") as f:
            # Write the module header
            f.write("module cleaned_circuit (\n")
            io_nodes = [node for node in gnn['io_nodes'] if node.gate_type in ['input', 'output']]
            inputs = [node.name for node in io_nodes if node.gate_type == 'input']
            outputs = [node.name for node in io_nodes if node.gate_type == 'output']
            
            # Write inputs and outputs
            f.write(",".join(inputs + outputs))
            f.write("\n);\n\n")
            
            # Declare inputs and outputs
            for inp in inputs:
                f.write(f"  input {inp};\n")
            for out in outputs:
                f.write(f"  output {out};\n")
            
            f.write("\n")
            
            # Declare assigns
            
            # Declare wires
            internal_nodes = [node for node in gnn['nodes'] if node.gate_type not in ['input', 'output']]
            used_wires = set()
            for node in internal_nodes:
                used_wires.update(node.conn_names)
            
            for node in internal_nodes:
                if node.gate_type == 'assign':
                    f.write(f"  assign {node.conn_names[0]} = {node.name};\n")
                    used_wires.add(node.name)
            f.write("\n")
            
            # Write gate instantiations
            for node in internal_nodes:
                if node.gate_type != 'wire' and node.gate_type != 'assign':
                    connections = ", ".join(node.conn_names)
                    f.write(f"  {node.gate_type} {node.name} ({connections});\n")
            f.write("\n")
            
            f.write("endmodule\n")
        
        print(f"Cleaned GNN saved to {file_name}_clean.v")
    except Exception as e:
        print(f"Error writing file: {str(e)}")
        
def add_missing_wires(file_name):
    """
    Reads a Verilog file, identifies missing wire declarations, and adds them before the first assign statement.

    Args:
        file_name (str): Name of the Verilog file to process.
    """
    try:
        with open(file_name, "r") as f:
            lines = f.readlines()

        inputs_outputs_assigns = set()
        used_wires = set()
        updated_lines = []
        first_assign_index = -1

        for idx, line in enumerate(lines):
            stripped_line = line.strip()

            # Collect inputs, outputs, and assigns
            if stripped_line.startswith("input") or stripped_line.startswith("output"):
                inputs_outputs_assigns.add(stripped_line.split()[1].strip(";"))
            elif stripped_line.startswith("assign"):
                assign_target = stripped_line.split()[1]
                inputs_outputs_assigns.add(assign_target.strip(";"))
                if first_assign_index == -1:
                    first_assign_index = idx
            elif stripped_line.startswith("wire"):
                # Skip existing wire declarations
                continue
            elif "(" in stripped_line and ")" in stripped_line and "assign" not in stripped_line:
                # Collect used wires in gate instantiations
                connections = stripped_line.split("(")[1].split(")")[0]
                used_wires.update(conn.strip() for conn in connections.split(",") if conn.strip())

            updated_lines.append(line)

        # Identify missing wires
        missing_wires = used_wires - inputs_outputs_assigns

        # Add missing wire declarations before the first assign statement
        if missing_wires:
            new_wire_declarations = f"  wire {', '.join(missing_wires)};\n"
            if first_assign_index != -1:
                updated_lines.insert(first_assign_index, new_wire_declarations)
            else:
                updated_lines.insert(0, new_wire_declarations)

        # Write the updated file
        with open(f"{file_name}", "w") as f:
            f.writelines(updated_lines)

        print(f"Missing wires added and saved to {file_name}.v")

    except Exception as e:
        print(f"Error processing file: {str(e)}")


            
if __name__ == "__main__":
    # List of files to process
    file_w_tj = "s38584_scan"    
    
    trojans = "simple_trojan"
          
    gnn_w_tj = procVfl(file_w_tj)   
    gnn_tj = procVfl(trojans)
    
    # Search for trojan pattern
    potential_trojans = findTj(gnn_w_tj, gnn_tj)
    
    # Print results
    if potential_trojans:
        print("\nPotential trojans found:")
        for idx, match in enumerate(potential_trojans):
            print(f"\nMatch {idx + 1}:")
            print(f"Confidence: {match['confidence']:.2f}")
            print("Gates involved:")
            for node in match['nodes']:
                print(f"  {node.name} ({node.gate_type})")
                
        # Remove trojans and create clean GNN
        clean_gnn = rmTj(gnn_w_tj, potential_trojans)
        print("\nTrojan removed. Clean circuit contains:")
        print(f"Nodes: {len(clean_gnn['nodes'])}")
        print(f"Edges: {len(clean_gnn['edges'])}")
        
        # Plot the clean circuit
        print("\nGenerating clean circuit visualization...")
        plot_clean_gnn(clean_gnn, "Circuit Graph After Trojan Removal")
        outputVfile("output", clean_gnn)
        add_missing_wires("output_clean.v")
    else:
        print("\nNo trojan patterns detected.")



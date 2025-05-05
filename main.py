from formatfile import format_file
from createGnn import makeGnn

def process_verilog_file(file_name):
    """
    Process a Verilog file through formatting and GNN creation.
    
    Args:
        file_name (str): Name of the Verilog file (without extension)
    """
    try:
        print(f"Processing {file_name}.v...")
        
        # Step 1: Format the Verilog file
        print("Formatting file...")
        format_file(file_name)
        print(f"Formatting complete. Output saved to {file_name}_formatted.v")
        
        # Step 2: Create and visualize GNN
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

def find_trojan_pattern(circuit_gnn, trojan_gnn):
    """
    Search for trojan pattern in the circuit GNN.
    
    Args:
        circuit_gnn (dict): GNN representation of the circuit to analyze
        trojan_gnn (dict): GNN representation of the trojan pattern
    
    Returns:
        list: List of potential trojan matches (node sets that match the pattern)
    """
    matches = []
    
    # Get the nodes and edges for both GNNs
    circuit_nodes = circuit_gnn['nodes']
    trojan_nodes = trojan_gnn['nodes']
    
    # Get gate patterns from trojan
    trojan_pattern = []
    for node in trojan_nodes:
        if node.name.startswith('t'):  # Trojan gates typically start with 't'
            trojan_pattern.append(node.gate_type)
    
    # Search for matching patterns in circuit
    window = len(trojan_pattern)
    for i in range(len(circuit_nodes) - window + 1):
        potential_match = circuit_nodes[i:i+window]
        
        # Check if gate types match the trojan pattern
        if all(p.gate_type == t for p, t in zip(potential_match, trojan_pattern)):
            match_info = {
                'start_index': i,
                'nodes': potential_match,
                'confidence': calculate_match_confidence(potential_match, trojan_pattern)
            }
            matches.append(match_info)
    
    return matches

def calculate_match_confidence(circuit_nodes, trojan_pattern):
    """
    Calculate confidence score for a potential trojan match.
    
    Args:
        circuit_nodes (list): List of nodes from the circuit
        trojan_pattern (list): List of gate types from trojan template
    
    Returns:
        float: Confidence score between 0 and 1
    """
    # Basic confidence based on gate type matches
    gate_match_score = sum(1 for n, t in zip(circuit_nodes, trojan_pattern) if n.gate_type == t)
    
    # Additional checks that could indicate a trojan:
    # 1. Nodes named with 't' prefix
    naming_score = sum(1 for n in circuit_nodes if n.name.startswith('t'))
    
    # 2. Connectivity pattern similar to trojan
    connectivity_score = sum(1 for n in circuit_nodes if len(n.conn_names) >= 2)
    
    # Combine scores (weighted average)
    total_score = (0.5 * gate_match_score/len(trojan_pattern) +
                  0.3 * naming_score/len(circuit_nodes) +
                  0.2 * connectivity_score/len(circuit_nodes))
    
    return total_score

if __name__ == "__main__":
    # List of files to process
    file_w_tj = "simple_test_tj"    
    
    trojans = "simple_trojan"
          
    gnn_w_tj = process_verilog_file(file_w_tj)   
    gnn_tj = process_verilog_file(trojans)
    
    # Search for trojan pattern
    potential_trojans = find_trojan_pattern(gnn_w_tj, gnn_tj)
    
    # Print results
    if potential_trojans:
        print("\nPotential trojans found:")
        for idx, match in enumerate(potential_trojans):
            print(f"\nMatch {idx + 1}:")
            print(f"Confidence: {match['confidence']:.2f}")
            print("Gates involved:")
            for node in match['nodes']:
                print(f"  {node.name} ({node.gate_type})")
    else:
        print("\nNo trojan patterns detected.")



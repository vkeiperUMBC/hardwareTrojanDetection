import re

def convert_verilog(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Initialize storage
    inputs = []
    outputs = []
    gates = []
    wire_map = {}
    wire_counter = 4  # Start at u4 since u1-u3 are used for gates

    # Process each line
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            continue

        # Process input declarations
        if 'input wire' in line:
            new_inputs = [i.strip() for i in line.replace('input wire', '').replace(';', '').split(',')]
            inputs.extend(new_inputs)
            continue

        # Process output declarations
        if 'output wire' in line:
            new_outputs = [o.strip() for o in line.replace('output wire', '').replace(';', '').split(',')]
            outputs.extend(new_outputs)
            continue

        # Process gate declarations
        gate_match = re.match(r'(\w+)\s+(\w+)\s*\((.*?)\);', line)
        if gate_match:
            gate_type, gate_name, connections = gate_match.groups()
            connections = [c.strip() for c in connections.split(',')]
            
            # For intermediate signals, use the gate name as the wire name
            output_signal = connections[0]
            if output_signal not in inputs and output_signal not in outputs:
                wire_map[output_signal] = gate_name
            
            # Replace intermediate wires in connections
            new_connections = []
            for conn in connections:
                if conn in wire_map:
                    new_connections.append(wire_map[conn])
                else:
                    new_connections.append(conn)
            
            gates.append(f"{gate_type} {gate_name} ({', '.join(new_connections)});")

    # Generate output
    output_lines = []
    
    # Create module header with individual input/output declarations
    input_decls = [f"input wire {inp}" for inp in inputs]
    output_decls = [f"output wire {out}" for out in outputs]
    module_header = f"module simple_circuit ( {', '.join(input_decls + output_decls)} );"
    output_lines.append(module_header)
    output_lines.append("")  # Empty line after header

    # Add gates
    output_lines.extend(gates)
    output_lines.append("")  # Empty line before endmodule
    output_lines.append("endmodule")

    # Write output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))

# Test the conversion
if __name__ == "__main__":
    input_file = r"c:\Users\keipe\Documents\414\hardwareTrojanDetection\simple_test.v"
    output_file = r"c:\Users\keipe\Documents\414\hardwareTrojanDetection\simple_test_formatted.v"
    convert_verilog(input_file, output_file)
    print("Conversion complete!")
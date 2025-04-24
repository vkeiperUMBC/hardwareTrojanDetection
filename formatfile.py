import re

def final_format(input_filepath, output_filepath):
    with open(input_filepath, 'r') as infile:
        lines = infile.readlines()

    formatted_lines = []
    current_line = ""
    lines = lines[1:-1]  # Skip the first and last lines
    for line in lines:
        # Remove all starting tabs
        line = line.lstrip('\t')
        current_line += line.strip()
        if current_line.endswith(';'):
            formatted_lines.append(current_line)
            current_line = ""
    # Write the formatted lines to the output file
    with open(output_filepath, 'w') as outfile:
        for formatted_line in formatted_lines:
            outfile.write(formatted_line + '\n')
        


def rmNl(input_file_path, output_file_path):
    """
    Removes all comments and newlines between lines that end with a semicolon.
    
    Args:
        input_file_path (str): Path to the input file
        output_file_path (str): Path to save the processed output
    """
    try:
        # Read the input file
        with open(input_file_path, 'r') as file:
            content = file.read()
        
        # Remove multi-line comments first (/* ... */)
        import re
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Process the content line by line to handle single-line comments and semicolons
        lines = []
        for line in content.split('\n'):
            # Remove single-line comments
            comment_pos = line.find('//')
            if comment_pos != -1:
                # Keep only the code part
                line = line[:comment_pos]
            lines.append(line.strip())
        
        # Process lines to combine those without semicolons
        result = []
        current_parts = []
        current_indent = ""
        
        for i, line_content in enumerate(lines):
            # Skip empty lines
            if not line_content and not current_parts:
                continue
            
            # Capture indentation of the first line
            if not current_parts and line_content:
                original_line = content.split('\n')[i]
                leading_spaces = len(original_line) - len(original_line.lstrip())
                current_indent = original_line[:leading_spaces]
            
            # Add content to current statement
            if line_content:
                current_parts.append(line_content)
            
            # If line ends with semicolon, complete the statement
            if line_content.endswith(';'):
                # Combine all parts into one line
                combined_line = current_indent + ' '.join(current_parts)
                result.append(combined_line)
                
                # Reset for next statement
                current_parts = []
                current_indent = ""
        
        # Add any remaining parts that don't end with semicolon
        if current_parts:
            combined_line = current_indent + ' '.join(current_parts)
            result.append(combined_line)
        
        # Write to output file
        with open(output_file_path, 'w') as file:
            file.write('\n'.join(result))
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def wireHandle(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    wire_names = []
    wireLineNum = 0
    
    # Extract wire declarations
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('wire'):
            wireLineNum = lines.index(line)  # Get the line number of the wire declaration
            # Remove 'wire' and split by commas to get individual wire names
            wire_names = stripped_line[len('wire'):].strip().strip(';').split(',')
            wire_names = [name.strip() for name in wire_names]  # Remove extra spaces
    
    formatted_lines = []
    for wire in wire_names:
        connections = []
        for i in range(wireLineNum + 1, len(lines)):
            line = lines[i].strip()
            if wire in line:
                # Extract the second word of the line
                words = line.split()
                if len(words) > 1:
                    connections.append(words[1])
        if connections:
            formatted_lines.append(f"wire {wire} ({', '.join(connections)});")
    
    # Write formatted wire connections to the second to last line of the output file
    with open(output_file, 'w') as file:
        for i, line in enumerate(lines):
            if not line.strip().startswith('wire') or lines.index(line) != wireLineNum:
                file.write(line)
            # Write formatted lines before the last line
            if i == len(lines) - 2:
                for formatted_line in formatted_lines:
                    file.write(formatted_line + '\n')
        
        
    

# Input and output file paths
input_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test.v"
preForm_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test_preform.v"
wire_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test_wire.v"
output_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test_formatted.v"

# Format the Verilog file
file_wo_newline = rmNl(input_filepath, preForm_filepath)
wireHandle(preForm_filepath, wire_filepath)
final_format(wire_filepath, output_filepath)

# print(f"Formatted Verilog file saved to {output_filepath}")
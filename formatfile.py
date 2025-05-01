import re
import os

def final_format(input_filepath, output_filepath):
    with open(input_filepath, 'r') as infile:
        lines = infile.readlines()

    formatted_lines = []
    current_line = ""
    lines = lines[1:-1]  # Skip the first and last lines
    for line in lines:
        # Remove all starting tabs
        line = line.lstrip('\t')
        # Replace all '[' and ']' with '_'
        line = line.replace('[', '_').replace(']', '')
        # Remove bit declarations like 1'b0 and ensure proper comma handling
        line = re.sub(r'\b\d+\'b[01]+\b,?', '', line).strip(',')
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
    Removes all comments, newlines between lines that end with a semicolon, and all '/' and '\\' characters.
    
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
        
        # Remove all '/' and '\\' characters
        content = content.replace('/', '').replace('\\', '')
        
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
    
    for line in lines:
        s_line = line.strip()
        if (s_line.__contains__('[') or s_line.__contains__(']')) and (s_line.startswith('input') or s_line.startswith('output') or s_line.startswith('wire')):
            # Extract the type (input/output/wire), range, and variable name
            match = re.match(r'(\w+)\s*\[(\d+):(\d+)\]\s*(\w+);', s_line)
            if match:
                var_type, msb, lsb, var_name = match.groups()
                msb, lsb = int(msb), int(lsb)
                # Generate expanded variables
                expanded_vars = [f"{var_name}_{i}" for i in range(lsb, msb + 1)]
                # Create the new line
                new_line = f"{var_type} {', '.join(expanded_vars)};"
                lines[lines.index(line)] = new_line + '\n'
         
    input_lines = []
    output_lines = []
    wire_lines = []

    for line in lines:
        s_line = line.strip()
        if s_line.startswith('input'):
            input_lines.append(s_line.replace('input', '').strip(';').strip())
        elif s_line.startswith('output'):
            output_lines.append(s_line.replace('output', '').strip(';').strip())
        elif s_line.startswith('wire'):
            wire_lines.append(s_line.replace('wire', '').strip(';').strip())

    combined_lines = []
    if input_lines:
        combined_lines.append("input wire " + ", ".join(input_lines) + ";\n")
    if output_lines:
        combined_lines.append("output wire " + ", ".join(output_lines) + ";\n")
    if wire_lines:
        combined_lines.append("wire " + ", ".join(wire_lines) + ";\n")

    first_line = lines[0]
    lines = [first_line] + combined_lines + [line for line in lines[1:] if not (line.strip().startswith('input') or line.strip().startswith('output') or line.strip().startswith('wire'))]
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
        
        
def rmPortNames(input_file, output_file):
    """
    Removes port names from module declarations but keeps inputs and outputs intact.
    Additionally, modifies gate instances to remove port names and adjust formatting.
    
    Args:
        input_file (str): Path to the input Verilog file.
        output_file (str): Path to save the processed Verilog file.
    """
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    processed_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Check if the line contains a module declaration
        if stripped_line.startswith('module'):
            # Remove everything after the first parenthesis
            line = re.sub(r'\(.*\)', '()', line)
        # Check if the line contains a gate instance
        elif re.match(r'^\w+\s+\w+\s*\(.*\);', stripped_line):
            # Remove port names and adjust formatting
            line = re.sub(r'\.\w+\(([^)]+)\)', r'\1', line)  # Remove port names
            line = re.sub(r'\s*,\s*', ', ', line)  # Ensure proper spacing for commas
            line = re.sub(r'\(\s*', '(', line)  # Remove extra spaces after '('
            line = re.sub(r'\s*\)', ')', line)  # Remove extra spaces before ')'
            line = re.sub(r'\)\s*;', ');', line)  # Ensure proper closing
        processed_lines.append(line)
    
    # Write the processed lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(processed_lines)
    
def flip_assigns(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if line.__contains__('assign'):
            old_line = line.strip()
            lhs = old_line.split('=')[0].strip()
            rhs = old_line.split('=')[1].strip().rstrip(';')
            for line in lines:
                if line.__contains__(rhs) and (line.startswith('input') or line.startswith('output')):
                    new_line = f"assign {rhs} = {lhs};\n"
                    lines[lines.index(line)] = new_line
                    break                    
    with open(output_file, 'w') as file:
        file.writelines(lines)

def format_file(file_name):
    # Input and output file paths
    input_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\" +file_name+".v"
    rmNlCmnt_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\"+file_name+"_NlCmntRmed.v"
    rmPortNm_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\" +file_name+"_prtNmRmed.v"
    wire_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\" +file_name+"_wire.v"
    ass_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\" +file_name+"_ass.v"
    output_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\" +file_name+"_formatted.v"


    # Format the Verilog file
    rmNl(input_filepath, rmNlCmnt_filepath)
    rmPortNames(rmNlCmnt_filepath,rmPortNm_filepath)
    wireHandle(rmPortNm_filepath, wire_filepath)
    # flip_assigns(wire_filepath,ass_filepath)
    final_format(wire_filepath, output_filepath)
    for filepath in [rmNlCmnt_filepath, rmPortNm_filepath, wire_filepath, ass_filepath]:
        if os.path.exists(filepath):
            os.remove(filepath)


file_name = "uart"
format_file(file_name)
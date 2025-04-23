import re

def format_verilog_file(input_filepath, output_filepath):
    with open(input_filepath, 'r') as infile:
        lines = infile.readlines()

    formatted_lines = []
    current_line = ""

    for line in lines:
        stripped_line = line.strip()

        # Check if the line is part of a gate instantiation
        if re.match(r"^\w+\s+\w+\s*\(.*", stripped_line) and not stripped_line.endswith(";"):
            # Start of a multi-line gate instantiation
            current_line += " " + stripped_line
        elif current_line and not stripped_line.endswith(";"):
            # Continuation of a multi-line gate instantiation
            current_line += " " + stripped_line
        elif current_line and stripped_line.endswith(";"):
            # End of a multi-line gate instantiation
            current_line += " " + stripped_line
            formatted_lines.append(current_line.strip())
            current_line = ""
        else:
            # Regular line
            formatted_lines.append(stripped_line)

    # Write the formatted lines to the output file
    with open(output_filepath, 'w') as outfile:
        outfile.write("\n".join(formatted_lines) + "\n")

# Input and output file paths
input_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test.v"
output_filepath = "c:\\Users\\keipe\\Documents\\414\\hardwareTrojanDetection\\simple_test_formatted.v"

# Format the Verilog file
format_verilog_file(input_filepath, output_filepath)

print(f"Formatted Verilog file saved to {output_filepath}")
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
        makeGnn(file_name)
        print("GNN visualization complete.")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    # List of files to process
    files_to_process = [
        # "simple_test",
        "uart"
    ]
    
    # Process each file
    for file_name in files_to_process:
        print(f"\n{'='*50}")
        process_verilog_file(file_name)
        print(f"{'='*50}\n")
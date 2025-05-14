# Hardware Trojan Detection Tool

This tool can identify and remove hardware Trojans from Verilog circuit designs by analyzing their structure as graph neural networks (GNNs).

## Prerequisites

- Python 3.x
- PyTorch
- PyTorch Geometric
- NetworkX
- Matplotlib
- Re (Regular Expression)

## Installation

```bash
pip install torch torch_geometric networkx matplotlib
```

## File Structure

- `formatfile.py` - Formats Verilog files for processing
- `createGnn.py` - Creates graph neural network representations of circuits
- `main.py` - Main script for Trojan detection and removal

## Usage

1. Place your Verilog files in the same directory as the scripts
2. Update the file paths in the code if necessary
3. Run the main script:

```bash
python main.py
```

## Workflow

1. The tool formats the input Verilog file
2. It creates a GNN representation of the circuit
3. It searches for Trojan patterns
4. If Trojans are found, they are removed
5. A clean Verilog file is generated

## Customization

In `main.py`, you can modify:
- `file_w_tj` - The potentially infected Verilog file
- `trojans` - The Trojan pattern file to detect

## Output

- `*_circuit_graph.png` - Visual representation of the circuit
- `output_clean.v` - Cleaned Verilog file with Trojans removed
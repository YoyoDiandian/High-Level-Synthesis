# LLVM IR based High-Level Synthesis

A toolset for High-Level Synthesis (HLS) and register allocation optimization in digital integrated circuit design.

## Project Overview

High-Level Synthesis is a toolset that transforms high-level programming languages (C-like) into hardware description languages and optimizes register allocation to improve circuit performance and resource utilization.

The project implements a comprehensive workflow from LLVM IR to hardware description languages. It includes LLVM IR parsing, scheduling optimization, RTL code generation, Verilog testbench creation, and simulation. The `sampleOutput` directory contains complete workflow demonstrations for three example files, showcasing parsing results, scheduling outputs, generated RTL code, and simulation waveforms.

## Key Features

- **Scheduling Algorithms**: Implement various operation scheduling strategies for optimized parallelism
- **Register Allocation**: Efficient register allocation algorithms to minimize register usage
- **Automatic Code Generation**: Generate hardware description language code based on optimized scheduling and register allocation
- **Waveform Generation**: Compile the generated RTL code and generate waveform
- **Testbench Generation**: Generate Verilog testbench based on LLVM IR and input parameters files

## Examples and Robustness

Our project includes two sets of test files:

### Fully-Tested Examples
These fully-tested examples are placed in the `example/` directory, with their corresponding sample outputs in the `sampleOutput/` directory:
- `dotprod.ll`: Dot product calculation
- `gcd.ll`: Greatest common divisor
- `sum.ll`: Array sum
These examples come with complete simulation results and testbenches.

### Input-Only Examples
Additional test files located in the `example/unrun` directory include:
- `linearSearch.ll`: Linear search implementation
- `maxArray.ll`: Maximum value finder
- `sumArray.ll`: Array summation
These examples include LLVM IR and input files, ready for testing.

Our HLS tool demonstrates robust performance across various algorithms and data structures, handling different control flows and memory access patterns effectively.

## Requirements

- Python 3.6+
- NetworkX
- Graphviz (optional, for visualization) or gtkwave (VS Code extension)
- Icarus Verilog (for simulating generated Verilog code)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YoyoDiandian/High-Level-Synthesis.git
   ```

2. Install Python dependencies:
   ```bash
   pip install networkx
   ```

3. Install Icarus Verilog (iverilog) for Verilog simulation:
   
   Linux (Ubuntu/Debian):
   ```bash
   sudo apt-get install iverilog
   ```
   
   MacOS:
   ```bash
   brew install icarus-verilog
   ```
   
   Windows:
   - Download the installer from http://bleyer.org/icarus/
   - Follow installation instructions
   - Add iverilog to your system PATH

4. Install `gtkwave` extension in vscode.

## Usage

### Running Tests

Execute the test suite from the project root directory:
```bash
sh test.sh
```

This will run three fully-tested examples tests to verify the functionality of the HLS toolset. The output will under `testOutput/` directory.

Upon successful test completion, you will see the following output in your terminal:
```
=============================
✅ Testing completed successfully!
Output files are available in the testOutput directory.
```

### Basic Usage

1. Prepare your LLVM IR file (`.ll` format):
   - Place the `.ll` file in the `example` directory
   - For the provided example files (`dotprod.ll`, `gcd.ll`, `sum.ll`), testbenches are included
   - For custom LLVM IR files:
     - Generate testbench using the [testbench generator](#testbench-generation-instructions), or
     - Manually create:
       - Verilog testbench file in `example/testbench/<filename>_tb.v`
       - SRAM initialization files in `example/testbench/<filename>/variable_name.txt`
       
     Note: Using the testbench generator is recommended. If you need to write a custom testbench, 
     please follow the [Manual Step-by-Step Usage](#manual-step-by-step-usage) guide and write teshbench after the Verilog file generated.

2. Run the automated workflow:
   ```bash
   sh autorun.sh example/<filename>.ll [output_directory]
   ```
   Note: `output_directory` is optional (defaults to `output/`)

   The `output_directory` parameter is optional and defaults to `output/`. After successful synthesis and compilation, you will see output similar to:
   ```
   =============================
   All processes completed successfully!
   =============================
   Output files:
   1. Parse result: testOutput/parseResult/<filename>_parseResult.txt
   2. Output flow file: testOutput/<filename>_outputFlow.txt
   3. Verilog file: testOutput/verilog_code/<filename>.v
   4. Waveform file: testOutput/waveform/<filename>_wave.vcd
   =============================
   ```

3. Check results in the `output_directory/`

### Testbench Generation Instructions

To generate a Verilog testbench for your LLVM IR file:

1. Create an input file in the `example` directory with the following format:
   ```
   a 10           # Single integer variable 'a'
   b 1 2 3 4 5    # Array variable 'b'
   ```
   Note: Variable names must match those in your LLVM IR file. Name the file as `<filename>_input.txt`.

2. Generate the testbench:
   ```bash
   cd example
   python testbenchGenerator.py <filename>
   ```
   Note: Omit file extensions (`.txt` or `.ll`) in the command.

The generated testbench will be created at `example/testbench/<filename>.v`. For array variables, corresponding SRAM initialization files will be placed in `example/testbench/<filename>/` directory as `variable_name.txt`.

### Manual Step-by-Step Usage

*Note: While manual step-by-step usage is available, we strongly recommend using `autorun.sh` for optimal workflow efficiency. Only proceed with manual steps if troubleshooting `autorun.sh` issues.*

1. Prepare your LLVM IR file and input data:
   - Place the `.ll` file in the `example` directory
   - Create testbench file in `example/testbench/` directory following [testbench generation instructions](#testbench-generation-instructions)

2. Build the parser:
   ```bash
   cd parser
   make
   ```

3. Parse LLVM IR and run HLS workflow:
   ```bash
   ./hls ../example/<filename>.ll ../output_directory/parseResult/<filename>_parseResult.txt
   cd ..
   python main.py output_directory/parseResult/<filename>_parseResult.txt
   ```
   The HLS results will be in:
   - Schedule and allocation: `output_directory/outputFlow/<filename>.txt`
   - Generated RTL: `output_directory/verilog_code/<filename>.v`

6. Simulate generated Verilog:
   ```bash
   cd output_directory/verilog_code
   iverilog -o wave <filename>.v ../../example/testbench/<filename>_tb.v
   vvp -n wave
   ```
   The waveform will be available at `output_directory/waveform/<filename>.vcd`

### Additional Example Files

In the `example/unrun` directory, we provide additional LLVM IR files and input data files that do not have pre-generated testbenches:
- `linearSearch.ll` - Linear search algorithm implementation
- `maxArray.ll` - Find maximum value in an array
- `sumArray.ll` - Calculate sum of array elements

Note: These files are not included in the automated tests (`test.sh`) as they require testbench generation before running the HLS workflow.

To use these examples:

1. Copy the desired `.ll` file and corresponding `input.txt` file from `example/unrun/` to the `example/` directory

2. Generate the testbench:
   ```bash
   cd example
   python testbenchGenerator.py <filename>    # e.g., linearSearch, maxArray, or sumArray
   ```

3. Run the HLS workflow:
   ```bash
   sh autorun.sh example/<filename>.ll        # e.g., example/linearSearch.ll
   ```

The generated files will be placed in the `output/` directory, including parsing results, RTL code, and simulation waveforms.

## Project Structure

```
.
├── example/           # Example LLVM IR files and input files
│   ├── dotprod.ll     # Dot product example
│   ├── gcd.ll         # Greatest common divisor example
│   ├── sum.ll         # Sum array example
│   ├── dotprod_input.txt  # Input file for dotprod.ll, as an input file example
│   ├── testbenchGenerator.py  # Script to generate testbenches
│   ├── testbench/     # Generated testbench files
│   └── unrun/         # Directory containing untested LLVM IR files and their corresponding input files
├── parser/            # LLVM IR parser
│   ├── Makefile       # Build configuration
│   ├── main.cpp       # Parser entry point
│   └── src/           # Parser source files
├── hls/               # HLS core implementation
│   ├── resourceData/  # Resource constraints
│   ├── cdfgGenerator.py   # CDFG generator
│   ├── genFSM.py      # FSM generator
│   ├── scheduler.py   # Scheduling algorithms
│   └── registerAllocator.py # Register allocation
├── sampleOutput/      # Sample generated files directory
│   ├── parseResult/   # Parser output
│   ├── outputFlow/    # HLS results
│   ├── verilog_code/  # Generated RTL
│   └── waveform/      # Simulation waves
├── main.py            # Project entry point
├── autorun.sh         # Automation script
└── test.sh            # Test automation script
```

## Example Run

Here's an example of running the tool with the sample file `dotprod.ll`:

```bash
sh autorun.sh example/dotprod.ll output/
```

The output containing basic block information, scheduling results, and register allocation results can be viewed in `output/outputFlow/dotprod.txt`. The generated RTL code can be viewed in `output/verilog_code/dotprod.v`. The wave can be viewed in `output/waveform/dotprod.vcd`

## Example File: dotprod.ll

```
define int dotprod(int a[], int b[], int n)
    c = 0;

start:
    i = phi(0, 0, i_inc, calc);
    cl = phi(c, 0, cr, calc);
    cond = i >= n;
    br cond ret calc;

calc:
    ai = load(a, i);
    bi = load(b, i);
    ci = ai * bi;
    cr = cl + ci;
    i_inc = i + 1;
    br start;

ret:
    return cl;
```


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions, please contact the project maintainer.

---

*Note: This project is for Fudan University Digital Integrated Circuit Design Automation course and is intended for learning and research purposes only.*
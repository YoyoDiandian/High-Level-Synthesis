# LLVM IR based High-Level Synthesis

A toolset for High-Level Synthesis (HLS) and register allocation optimization in digital integrated circuit design.

## Project Overview

High-Level Synthesis is a toolset that transforms high-level programming languages (C-like) into hardware description languages and optimizes register allocation to improve circuit performance and resource utilization.

The project implements a complete workflow from LLVM IR to hardware description languages, including a sophisticated register allocation algorithm that ensures variable continuity across basic blocks. Sample outputs demonstrating the workflow, including scheduling results, generated RTL code, and simulation waveforms, are provided in the `sampleOutput` directory.

## Key Features

- **LLVM IR Parsing**: Parse computational data flow graphs from LLVM intermediate representation
- **Scheduling Algorithms**: Implement various operation scheduling strategies for optimized parallelism
- **Register Allocation**: Efficient register allocation algorithms to minimize register usage
- **Cross-Basic-Block Optimization**: Support variable continuity optimization across basic blocks
- **Output Visualization**: Visualize data flow and scheduling results
- **Automatic Code Generation**: Generate hardware description language code based on optimized scheduling and register allocation
- **Waveform Generation**: Compile the generated RTL code and generate waveform

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

## Usage

### Running Tests

Execute the test suite from the project root directory:
```bash
sh test.sh
```

This will run all automated tests to verify the functionality of the HLS toolset. The output will under `testOutput/` directory

### Basic Usage

1. Prepare your LLVM IR file (`.ll` format):
   - Place the `.ll` file in the `example` directory
   - Place your Verilog testbench file in `example/testbench/your_file_tb.v`

2. Run the automated workflow:
   ```bash
   sh autorun.sh example/your_file.ll [output_directory]
   ```
   Note: `output_directory` is optional (defaults to `output/`)

3. Check results in the output directory

### Manual Step-by-Step Usage

1. Prepare input files as described above

2. Build the parser:
   ```bash
   cd parser
   make
   ```

3. Parse LLVM IR:
   ```bash
   ./hls ../example/your_file.ll ../output_directory/parseResult/your_file_parseResult.txt
   ```

4. Run HLS:
   ```bash
   cd ..
   python main.py output_directory/parseResult/your_file_parseResult.txt
   ```
   Note: Results will be generated in the grandparent directory of the parse result file

5. Simulate generated Verilog:
   ```bash
   cd output_directory/verilog_code
   iverilog -o wave your_file.v ../../example/testbench/your_file_tb.v
   vvp -n wave
   ```
   The waveform will be available at `output_directory/verilog_code/your_file_wave.vcd`

## Project Structure

```
.
├── example/            # Example LLVM IR files and testbenches
│   ├── dotprod.ll     # Dot product example
│   ├── gcd.ll         # Greatest common divisor example
│   ├── sum.ll         # Sum array example
│   └── testbench/     # Verilog testbench files
├── hls/               # High-level synthesis core implementation
│   ├── resourceData/  # Resource constraints and storage definitions
│   ├── cdfgGenerator.py     # Control Data Flow Graph generator
│   ├── genFSM.py      # Finite State Machine generator
│   ├── scheduler.py    # Operation scheduling algorithms
│   ├── registerAllocator.py # Register allocation optimization
│   └── IO port.md     # IO port specifications
├── sampleOutput/      # Sample generated output files
│   ├── outputFlow/    # Scheduling and allocation results
│   ├── parseResult/   # LLVM IR parsing results
│   ├── verilog_code/  # Generated Verilog RTL code
│   └── waveform/      # Simulation waveforms (vcd files)
├── parser/            # LLVM IR parser implementation
│   ├── Makefile      # Parser build script
│   ├── main.cpp      # Parser main program
│   ├── hls           # Execution file
│   └── src/          # Parser source files
├── main.py           # Project main entry point
├── autorun.sh        # Automation script
└── README.md         # Project documentation
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
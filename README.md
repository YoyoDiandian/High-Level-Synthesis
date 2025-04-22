# LLVM IR based High-Level Synthesis

A toolset for High-Level Synthesis (HLS) and register allocation optimization in digital integrated circuit design.

## Project Overview

High-Level Synthesis is a toolset that transforms high-level programming languages (C-like) into hardware description languages and optimizes register allocation to improve circuit performance and resource utilization.

The project implements a complete workflow from LLVM IR to hardware description languages, including a sophisticated register allocation algorithm that ensures variable continuity across basic blocks.

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

### Basic Usage

1. Prepare your LLVM IR file (.ll format) and place it in the `example` directory

2. Run the autorun program:
   ```bash
   sh autorun.sh example/your_file.ll
   ```

3. View the results:
   ```bash
   cat output/parseResult/your_file_parseResult.txt
   cat output/outputFlow/your_file_outputFlow.txt
   open output/wave/your_file_wave.vcd
   ```

### Generate Usage

1. Prepare your LLVM IR file (.ll format) and place it in the `example` directory

2. Enter parser directory:
   ```bash
   make
   ```

3. Generate parsed file:
   ```bash
   ./hls ../example/your_file.ll ../output/parseResult/your_file_parseResult.txt
   ```

4. Run main python file:
    ```bash
    cd ..
    python main.py output/parseResult/your_file_parseResult.txt
    ```

5. Compile Verilog file:
    ```bash
    sh compiler.sh output/verilog_code/you_file.v
    ```

## Project Structure

```
.
├── example/            # Example LLVM IR files
│   ├── dotprod.ll
│   ├── gcd.ll
│   └── sum.ll
├── hls/                # High-level synthesis core code
│   ├── resourceData    # Resource and storage data
│   ├── cdfgGenerator.py     # CDFG generation module
│   ├── genFSM.py       # FSM generation module
│   ├── scheduler.py    # Operation scheduling module
│   ├── registerAllocator.py  # Register allocation module
│   └── IO port.md      # IO port information
├── output/             # Output directory
│   ├── outputFlow/     # Output flow information
│   ├── parseResult/    # Parse result information
│   └── verilog_code/   # Generated Verilog code
├── parser/             # Parser tool
│   ├── main.cpp        # Main parser file
│   └── ...
├── main.py             # Main program entry
├── autorun.sh          # General code runner
└── README.md           # Project documentation
```

## Example Run

Here's an example of running the tool with the sample file `dotprod.ll`:

```bash
sh autorun.sh example/dotprod.ll
```

The output containing basic block information, scheduling results, and register allocation results can be viewed in `output/outputFlow/dotprod.txt`. The generated RTL code can be viewed in `output/verilog_code/dotprod.v`. The wave can be viewed in `output/wave/dotprod.vcd`

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
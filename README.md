# LLVM IR based High-Level Synthesis

A toolset for High-Level Synthesis (HLS) and register allocation optimization in digital integrated circuit design.

## Project Overview

High-Level Synthesis is a toolset that transforms high-level programming languages (C-like) into hardware description languages and optimizes scheduling and register allocation to improve circuit performance and resource utilization.

The project implements a complete workflow from LLVM IR to hardware description language Verilog. It includes LLVM IR parsing, operation scheduling, RTL code generation, Verilog testbench generation, and simulation. The `sampleOutput` directory contains complete workflow demonstrations for three example files, showcasing parsing results, scheduling outputs, generated RTL code, and simulation waveforms.

## Key Features

- **Scheduling Algorithms**: Implement various operation scheduling strategies for optimized parallelism
- **Register Allocation**: Efficient register allocation algorithms to minimize register usage
- **RTL Generation**: Generate hardware description language code based on optimized scheduling and register allocation
- **Waveform Generation**: Compile the generated RTL code and generate waveform
- **Testbench Generation**: Generate Verilog testbench based on and input parameters files

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
- VSCode 1.60+
- WaveTrace (VS Code extension for waveform visualization) or GTKWave (standalone waveform viewer)
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

4. Install `WaveTrace` extension in vscode.

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
       - SRAM initialization files in `example/testbench/<filename>/<variable_name>.txt`
       
     Note: Using the testbench generator is recommended. If you need to write a custom testbench, 
     please follow the [Manual Step-by-Step Usage](#manual-step-by-step-usage) guide and write teshbench after the Verilog file generated.

2. Run the automated workflow:
   ```bash
   sh autorun.sh example/<filename>.ll [output_directory]
   ```

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

The generated testbench will be created at `example/testbench/<filename>_tb.v`. For array variables, corresponding SRAM initialization files will be placed in `example/testbench/<filename>/` directory as `<variable_name>.txt`.

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
   cd output_directory/waveform
   iverilog -o wave ../verilog_code<filename>.v ../../example/testbench/<filename>_tb.v
   vvp -n wave
   ```
   The waveform will be available at `output_directory/waveform/<filename>.vcd`

### Additional Example Files

In the `example/unrun` directory, we provide additional LLVM IR files and input data files that do not have pre-generated testbenches. These files are not included in the automated tests (`test.sh`) as they require testbench generation before running the HLS workflow.

To use these examples:

1. Copy the desired `.ll` file and corresponding `<filename>_input.txt` file from `example/unrun/` to the `example/` directory

2. Generate the testbench:
   ```bash
   cd example
   python testbenchGenerator.py <filename>    # e.g., linearSearch, maxArray, or sumArray
   ```

3. Run the HLS workflow:
   ```bash
   cd ..
   sh autorun.sh example/<filename>.ll        # e.g., example/linearSearch.ll
   ```

The generated files will be placed in the `output/` directory, including parsing results, RTL code, and simulation waveforms.

## Generated Verilog Interface Specification

For detailed information about the I/O ports of Verilog modules generated by this HLS tool, please refer to our [I/O Port Documentation](./IO%20port.md).

## Project Structure

```
.
├── example/           # Example LLVM IR files and input files
│   ├── dotprod.ll     # Dot product example
│   ├── gcd.ll         # Greatest common divisor example
│   ├── sum.ll         # Sum array example
│   ├── testbenchGenerator.py  # Tool to generate testbenches
│   ├── testbench/     # Generated testbench files
│   └── unrun/         # Directory containing untested LLVM IR files and their corresponding input files
├── parser/            # LLVM IR parser
│   ├── Makefile       # Build configuration
│   ├── main.cpp       # Parser entry point
│   └── src/           # Parser source files
├── hls/               # HLS core implementation
│   ├── resourceData.py    # Resource constraints
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

## Contributors

This project was developed by a team of three contributors:

### Zihan Chen (陈子涵)
- **Github Username**: [CreamPumpkinCat](https://github.com/CreamPumpkinCat)
- **Responsibilities**: 
   - Key algorithm and data structure design and implementation: 
      - Establishment of the workflow from **LLVM parsing** to **scheduling and register allocation result**, ready for mapping to RTL codes.
      - Input pre-processing into control data flow graph;
      - **Operation Scheduling Algorithm** with resource and latency constraints in consideration, optimized to handle branch operations efficiently;
      - **Register Allocation Algorithm** based on Left Algorithm, optimized to align between basic blocks, avoiding extra memory access.
   - Detailed explanation of key scheduling and allocation algorithms in the final report with pseudo-codes included. Expansion on optimization methodologies concerning register alignment and branch operation handling.
   - Debugging and improvement of FSM generation. Reconstruction and standardization of the RTL code frame to avoid data and control hazard.

### Yaojia Wang (王瑶珈)
- **Github Username**: [YoyoDiandian](https://github.com/YoyoDiandian)
- **Responsibilities**:
   - Architected the overall repository structure and workflow:
      - Developed automation scripts (`autorun.sh`, `test.sh`) for seamless end-to-end processing;
      - Organized example files and test cases (3 complete + 3 input-only tests);
      - Designed and implemented the complete workflow from LLVM IR parsing to waveform generation.
      - Managed project repository.
   - Core algorithm implementation and optimization:
      - Enhanced CDFG generation for better representation of control and data flow;
      - Optimized operation scheduling with resource constraints consideration;
      - Designed and implemented **register merging algorithm** for efficient resource utilization, optimized the structure of register allocation algorithm;
      - Created the automated **testbench generation tool** supporting both scalar and array inputs.
   - Documentation and project management:
      - Authored comprehensive `README.md` with detailed installation, usage, and example instructions;
      - Created I/O port specifications for generated Verilog modules;
      - Completed project report writing covering introduction, background, overall design, algorithm design, experiment and conclusion (excluding algorithm details for scheduling, left algorithm and register coloring, and FSM generation).


### Yanqiu Cao (曹言秋)
- **Github Username**: [ccccccccyq](https://github.com/ccccccccyq)
- **Responsibilities**:
  - Implememtation of **Control Logic Synthesis and Verilog Code Generation**:
    - Developed the Verilog code generation framework;
    - Generated IO definition, wire/register and parameter definition, all the timing and assign logic;
    - Implemented mapping of input and output variables to registers in various situations;
    - Improved the code style of genFSM.py, making the encapsulation of functions and classes more reasonable, providing better readability, reusability, and extensibility.
  - Implemented the testbench generator.
  - Established the simulation and vertification workflow.
  - Completed project report of relevant sections, providing detailed explanation and examples of how to map the existing data structures and results to Verilog code. 
  - Modified the code style of operation scheduling and register allocation; Modify the output format of register allocation in the output flow.
  - Modified resourceData; defined the mapping from numerical values to operation names.

Together, these contributors invested significant time, expertise, and dedication to create this comprehensive end-to-end HLS toolchain. Each member's specialized contributions and collaborative efforts were essential in developing a robust system that successfully transforms LLVM IR into optimized, synthesizable Verilog code with advanced scheduling and efficient register allocation. This project represents hundreds of hours of research, implementation, debugging, and refinement—all focused on creating a tool that combines powerful functionality with exceptional ease of use for the users.

## Contact

If you have any questions, please contact the project maintainers.

---

*Note: This project is for Fudan University Digital Integrated Circuit Design Automation course and is intended for learning and research purposes only.*
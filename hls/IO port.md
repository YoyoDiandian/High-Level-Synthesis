# IO Port Documentation

## Overview

This document describes the input and output relationships between the Python modules in our High-Level Synthesis (HLS) tool chain. These modules work together to transform LLVM IR into synthesizable Verilog code.

## Module IO Relationships

### 1. `cdfgGenerator.py`

**Outputs:**
- `HLS` object containing:
  - Basic blocks with operations and data flow graphs (DFGs)
  - Control flow graph (CFG)
  - Function signature information (parameters, return type)

**Receivers:**
- `registerAllocator.py` uses the `HLS` object for register allocation.
- `scheduler.py` uses the `HLS` object for operation scheduling.
- `genFSM.py` uses the `HLS` object (with register and schedule data) to generate Verilog code.

### 2. `registerAllocator.py`

**Inputs:**
- `HLS` object from `cdfgGenerator.py`

**Outputs:**
- Updated `HLS` object with:
  - Global variable identification
  - Local variable liveness analysis
  - Register allocation results (coloring and merged coloring)

**Receivers:**
- `genFSM.py` uses the register allocation results in the `HLS` object.

### 3. `scheduler.py`

**Inputs:**
- `HLS` object from `cdfgGenerator.py`

**Outputs:**
- Updated `HLS` object with:
  - Operation scheduling results for each basic block

**Receivers:**
- `genFSM.py` uses the scheduling results in the `HLS` object.

### 4. `genFSM.py`

**Inputs:**
- `HLS` object with integrated data from:
  - `cdfgGenerator.py` (basic blocks, CFG/DFG)
  - `registerAllocator.py` (register allocation)
  - `scheduler.py` (scheduling results)

**Outputs:**
- Verilog code as a string
- File writer functionality to save Verilog code to a file

### 5. `resourceData.py`

**Outputs:**
- Constants and mappings used across modules:
  - Operation types (`OP_ASSIGN`, `OP_ADD`, etc.)
  - Operation delay values
  - Operation type names mapping

**Receivers:**
- `scheduler.py` uses operation delays for scheduling.
- `genFSM.py` uses operation type names for code generation.

## Interface Details

### Between `cdfgGenerator.py` and Others

- The main output is the `HLS` object containing:
  - Basic block structure
  - Control and data flow graphs
  - Function signature information

### Between `registerAllocator.py` and `genFSM.py`

- The `HLS` object is updated with:
  - Global variable identification
  - Local variable liveness analysis
  - Register allocation results

### Between `scheduler.py` and `genFSM.py`

- The `HLS` object is updated with:
  - Operation scheduling results for each basic block

### Between `resourceData.py` and Others

- Provides constants and mappings:
  - Operation type enumeration
  - Operation delay values
  - Operation name mappings
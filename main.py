import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, schedulePrinter
from hls.cdfgGenerator import HLS, BasicBlock, cdfgPrinter
from hls.registerAllocator import addRegisterAllocation, registerAllocatorPrinter
from hls.genFSM import VerilogSyntax, VerilogGenerator, verilogPrinter

def main():
    """
    Main function: Parse LLVM IR, generate HLS, schedule operations, 
    and allocate registers with register merging optimization.
    """
    start = time.time()
    defaultPath = "dotprod_parseResult.txt"
    if len(sys.argv) > 3:
        print("Too many arguments, please specify only the input file and optional output path.")
        sys.exit(1)
    elif len(sys.argv) > 1:
        inputFile = sys.argv[1]
        if len(sys.argv) == 3:
            outputPath = sys.argv[2]
            print(f"Output path specified: {outputPath}")
        else: 
            outputPath = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1])))
    else:
        print("File path unspecified, using default path: sampleOutput/parseResult/" + defaultPath)
        outputPath = 'sampleOutput'
        inputFile = os.path.join(os.path.dirname(__file__), outputPath, 'parseResult', defaultPath)
    try:
        name = inputFile[inputFile.rindex('/')+1:inputFile.rindex('_')]
    except Exception as e:
        print(f"Input file name must be a parse result file")
        sys.exit(1)
    
    # Create output directories if they don't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), outputPath, 'outputFlow'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), outputPath, 'verilog_code'), exist_ok=True)
    outputFile = os.path.join(os.path.dirname(__file__), outputPath, 'outputFlow', name + '_outputFlow.txt')
    verilogFile = os.path.join(os.path.dirname(__file__), outputPath, 'verilog_code', name + '.v')

    # Create HLS object and parse LLVM IR
    hls = HLS()
    addScheduler(HLS)
    addRegisterAllocation(HLS, BasicBlock)

    hls.llvmParser(inputFile)
    hls.generateCFG()
    hls.generateDFGs()
    hls.scheduleASAP()
    hls.registerAllocation()
    # print(f"schedule results: {hls.schedule}")
    # print(f"========================================")
    # print(f"register allocation after merging: {hls.merged_coloring_result}")

    verilog_syntax = VerilogSyntax()
    verilog_generator = VerilogGenerator(hls, verilog_syntax)
    verilog_generator.gen_all_code()

    # Print both original and optimized results
    with open(outputFile, 'w') as f:
        cdfgPrinter(hls, f)
        schedulePrinter(hls, f)
        registerAllocatorPrinter(hls, f)

    with open(verilogFile, 'w') as vf:
        verilogPrinter(verilog_generator, vf)
    end = time.time()
    print(f"Total time taken: {end - start:.10f} seconds")

if __name__ == "__main__":
    main()
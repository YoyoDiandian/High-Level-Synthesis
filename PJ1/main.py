import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, schedulePrinter
from hls.cdfgGenerator import CDFG, BasicBlock, cdfgPrinter
from hls.registerAllocator import addRegisterAllocation, registerAllocatorPrinter

def main():
    """
    Main function: Parse LLVM IR, generate CDFG, schedule operations, 
    and allocate registers with register merging optimization.
    """
    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
    else:
        print("File path unspecified, using default path: output/parseResult/dotprod_parseResult.txt")
        inputFile = os.path.join(os.path.dirname(__file__), 'output', 'parseResult', 'dotprod_parseResult.txt')
    try:
        name = inputFile[inputFile.rindex('/')+1:inputFile.rindex('_')]
    except Exception as e:
        print(f"Input file name must be a parse result file")
        sys.exit(1)
    outputFile = os.path.join(os.path.dirname(__file__), 'output', name + '_outputFlow.txt')
    
    # Create CDFG object and parse LLVM IR
    cdfg = CDFG()
    addScheduler(CDFG)
    addRegisterAllocation(CDFG, BasicBlock)

    cdfg.llvmParser(inputFile)
    cdfg.generateCFG()
    cdfg.generateDFGs()
    cdfg.scheduleASAP()
    cdfg.registerAllocation()
        
    # Print both original and optimized results
    with open(outputFile, 'w') as f:
        cdfgPrinter(cdfg, f)
        schedulePrinter(cdfg, f)
        registerAllocatorPrinter(cdfg, f)
        
if __name__ == "__main__":
    main()
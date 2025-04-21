import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, schedulePrinter
from hls.cdfgGenerator import CDFG, BasicBlock, cdfgPrinter
from hls.registerAllocator import addRegisterAllocation, registerAllocatorPrinter
from hls.genFSM import VerilogSyntax, VerilogGenerator, verilogPrinter

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
    verilogFile = os.path.join(os.path.dirname(__file__), 'output', 'verilog_code', name + '.v')

    # Create CDFG object and parse LLVM IR
    cdfg = CDFG()
    addScheduler(CDFG)
    addRegisterAllocation(CDFG, BasicBlock)

    cdfg.llvmParser(inputFile)
    cdfg.generateCFG()
    cdfg.generateDFGs()
    cdfg.scheduleASAP()
    cdfg.registerAllocation()
    
    verilog_syntax = VerilogSyntax()
    verilog_generator = VerilogGenerator(cdfg, verilog_syntax)
    verilog_generator.gen_all_code()

    # Print both original and optimized results
    with open(outputFile, 'w') as f:
        cdfgPrinter(cdfg, f)
        schedulePrinter(cdfg, f)
        registerAllocatorPrinter(cdfg, f)

    with open(verilogFile, 'w') as vf:
        verilogPrinter(verilog_generator, vf)

if __name__ == "__main__":
    main()



#     content = """
# module count4 (
#     out,
#     reset,
#     clk
# );
#     output [3:0] out;
#     input reset, clk;
#     reg [3:0] out;

# always@(posedge clk) begin
#     if(reset)
#         out <= 0;
#     else
#         out <= out + 1;
# end

# endmodule
#     """
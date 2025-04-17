import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, schedulePrinter
from hls.cdfgGenerator import CDFG, cdfgPrinter
from hls.registerAllocator import addRegisterAllocator, registerAllocationPrinter

def main():
    """
    主函数：解析LLVM IR并生成CDFG，然后进行调度和寄存器分配。
    """
    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
    else:
        # 默认路径
        print("File path unspecified, using default path: output/parseResult.txt")
        inputFile = os.path.join(os.path.dirname(__file__), 'output', 'parseResult', 'dotprod_parseResult.txt')
    
    outputFile = os.path.join(os.path.dirname(__file__), 'output', 'outputFlow.txt')
    
    # 添加调度和寄存器分配功能到CDFG类
    addScheduler(CDFG)
    addRegisterAllocator(CDFG)
    
    cdfg = CDFG()
    
    # 解析LLVM IR并构建CDFG
    cdfg.llvmParser(inputFile)
    cdfg.generateCFG()
    cdfg.generateDFGs()
    
    # 调度
    cdfg.scheduleASAP() # type: ignore
    
    # 寄存器分配
    cdfg.allocate_registers(num_registers=8)  # type: ignore # 假设有8个通用寄存器
    
    # 输出结果
    with open(outputFile, 'w') as f:
        cdfgPrinter(cdfg, f)
        schedulePrinter(cdfg, f)
        registerAllocationPrinter(cdfg, f)
        
if __name__ == "__main__":
    main()
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, schedulePrinter, scheduleASAP
from hls.cdfgGenerator import CDFG, BasicBlock, cdfgPrinter
from hls.registerAllocator import *

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
    
    # 创建CDFG对象并解析LLVM IR
    cdfg = CDFG()
    cdfg.llvmParser(inputFile)

    # 生成CFG和DFGs
    cdfg.generateCFG()
    cdfg.generateDFGs()

    # 添加schedule属性和schedule_asap方法到CDFG类
    addScheduler(CDFG)

    # 采用ASAP算法对CDFG图进行调度
    cdfg.scheduleASAP()

    # 添加各类属性至CDFG类和BasicBlock类
    addRegisterAllocation(CDFG, BasicBlock)

    # 通过CDFG图得到输入、输出变量、全局变量、寄存器生存周期和染色结果等信息
    input_variables, output_variables = cdfg.get_input_output_variables()
    global_variable_set = cdfg.get_global_variables()
    live_local_variables = cdfg.get_local_variable_liveness()
    living_period = cdfg.get_living_period()
    coloring_result = cdfg.register_coloring()
    
    # 输出结果
    with open(outputFile, 'w') as f:
        cdfgPrinter(cdfg, f)
        schedulePrinter(cdfg, f)
        registerAllocatorPrinter(input_variables, output_variables, 
                                 global_variable_set, live_local_variables, 
                                 living_period, coloring_result, f)
        
if __name__ == "__main__":
    main()
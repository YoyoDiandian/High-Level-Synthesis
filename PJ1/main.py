import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))

from hls.scheduler import scheduleASAP, printSchedule, addScheduler
from hls.cdfgGenerator import BasicBlock, CDFG
from hls.registerAllocator import * 

def main():
    """
        Main Function:
        1. Using LLVM Parser on LLVM IR and generating CDFG object.
        2. Schedule CDFG object and Print Schedule Results.
        3. Using Register Allocator, Binding Registers and get Coloring Results.
        主函数：解析LLVM IR并生成CDFG，然后进行调度。
    """
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认路径
        print("File path unspecified, using default path: output/parseResult/dotprod_parseResult.txt")
        file_path = os.path.join(os.path.dirname(__file__), 'output', 'parseResult', 'dotprod_parseResult.txt')

    # 创建CDFG对象并解析LLVM IR
    cdfg = CDFG()
    cdfg.llvmParser(file_path)

    # 生成CFG和DFGs
    cdfg.generateCFG()
    cdfg.generateDFGs()

    # 添加schedule属性和schedule_asap方法到CDFG类
    addScheduler(CDFG)
    cdfg.scheduleASAP()
    
    # 打印调度结果
    printSchedule(cdfg.schedule)

    # 添加各类属性至CDFG类和BasicBlock类
    addRegisterAllocation(CDFG, BasicBlock)

    # 打印输入变量和输出变量的结果
    input_variables, output_variables = cdfg.get_input_output_variables()
    printInputVariables(input_variables=input_variables)
    printOutputVariables(output_variables=output_variables)

    global_variable_set = cdfg.get_global_variables()
    printGlobalVariables(global_variable_set=global_variable_set)

    live_local_variables = cdfg.get_local_variable_liveness()
    printLocalVariablesLivenessCycle(live_local_variables=live_local_variables)

    living_period = cdfg.get_living_period()
    printLocalVariablesLivenessVariable(living_period=living_period)
    
    coloring_result = cdfg.register_coloring()
    printRegisterColoring(coloring_result=coloring_result)

if __name__ == "__main__":
    main()
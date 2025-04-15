import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'hls'))
from hls.scheduler import addScheduler, printSchedule, scheduleASAP
from hls.cdfgGenerator import CDFG

def main():
    """
    主函数：解析LLVM IR并生成CDFG，然后进行调度。
    """
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认路径
        print("File path unspecified, using default path: output/parseResult.txt")
        file_path = os.path.join(os.path.dirname(__file__), 'output', 'parseResult.txt')
    # 添加schedule属性和schedule_asap方法到CDFG类
    addScheduler(CDFG)
    # setattr(CDFG, 'schedule', {})
    # setattr(CDFG, 'scheduleASAP', scheduleASAP)
    
    # 创建CDFG对象并解析LLVM IR
    cdfg = CDFG()
    
    cdfg.llvmParser(file_path)
    cdfg.generateCFG()
    cdfg.generateDFGs()
    cdfg.scheduleASAP()
    
    # 打印调度结果
    printSchedule(cdfg.schedule)

if __name__ == "__main__":
    main()
import os
import re
import networkx as nx
import sys

class BasicBlock:
    """表示控制流图中的一个基本块"""
    
    def __init__(self, label):
        """
        初始化基本块
        
        Args:
            label: 基本块的标签
        """
        self.label = label
        self.ops = []  # 操作列表
        self.dfg = nx.DiGraph()  # 使用NetworkX有向图表示数据流图
        self.next_bb = None  # 下一个基本块的标签

    def addOP(self, op):
        """添加操作到基本块"""
        self.ops.append(op)

    def generateDFG(self):
        """
        构建数据流图（DFG）
        每个节点是操作索引，边表示数据依赖关系
        """
        # 清空已有图
        self.dfg.clear()
        
        # 添加所有操作作为节点
        for i in range(len(self.ops)):
            self.dfg.add_node(i, operation=self.ops[i])
            
        # 遍历每个操作，建立数据依赖边
        for i, op in enumerate(self.ops):
            # 当前操作产生的值
            current_value = op[0]
            
            # 当前操作使用的操作数
            operands = op[2:]
            
            # 查找操作数的来源（向前搜索）
            for j in range(i):
                prev_op = self.ops[j]
                prev_value = prev_op[0]
                
                # 如果前面的操作产生了当前操作使用的值，添加边
                if prev_value in operands:
                    self.dfg.add_edge(j, i, value=prev_value)
        
        return self.dfg


class CDFG:
    """控制数据流图(CDFG)的表示"""
    
    def __init__(self):
        """初始化CDFG对象"""
        self.basicBlocks = {}  # 基本块字典，键为基本块标签
        self.retType = None    # 函数返回类型
        self.functionName = None  # 函数名
        self.params = []  # 函数参数列表
        self.cfg = nx.DiGraph()  # 使用NetworkX有向图表示控制流图
    
    def llvmParser(self, file_path):
        """
        解析LLVM格式的parse_result文件，构建CDFG结构
        
        Args:
            file_path: parse_result文件的路径
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误：找不到文件 {file_path}")
            return None
        
        # 解析返回类型
        ret_type_match = re.search(r'ret type: (\w+)', content)
        if ret_type_match:
            self.retType = ret_type_match.group(1)
        
        # 解析函数名
        func_name_match = re.search(r'function name (\w+)', content)
        if func_name_match:
            self.functionName = func_name_match.group(1)
        
        # 解析参数
        # params = []
        param_matches = re.finditer(r'(array|non-array)\s+(\w+)', content)
        for match in param_matches:
            param_type, param_name = match.groups()
            self.params.append((param_name, param_type))
        # self.params = params
        
        # 解析基本块
        basic_block_pattern = r'Basic Block label: (\w+)(.*?)(?=Basic Block label:|$)'
        basic_block_matches = re.finditer(basic_block_pattern, content, re.DOTALL)
        
        # 获取所有基本块标签
        bb_labels = []
        for match in basic_block_matches:
            label = match.group(1)
            bb_labels.append(label)
        
        # 重新开始匹配基本块
        basic_block_matches = re.finditer(basic_block_pattern, content, re.DOTALL)
        
        for i, match in enumerate(basic_block_matches):
            label = match.group(1)
            block_content = match.group(2).strip()
            
            # 创建基本块对象
            bb = BasicBlock(label)
            
            # 设置next_bb属性
            if i < len(bb_labels) - 1:
                bb.next_bb = bb_labels[i + 1]
            
            # 解析操作
            op_pattern = r'value (\w*)\s+OP TYPE:(\d+)(.*?)(?=value|$)'
            op_matches = re.finditer(op_pattern, block_content, re.DOTALL)
            
            for op_match in op_matches:
                value = op_match.group(1)
                op_type = int(op_match.group(2))
                operands_text = op_match.group(3).strip()
                
                # 解析操作数
                operands = []
                if operands_text:
                    operands = [op.strip() for op in operands_text.split() if op.strip()]
                
                # 将操作添加到基本块
                bb.addOP([value, op_type] + operands)
            
            # 将基本块添加到CDFG
            self.addBasicBlock(bb)

    def addBasicBlock(self, basic_block):
        """
        添加基本块到CDFG
        
        Args:
            basic_block: BasicBlock对象
        """
        self.basicBlocks[basic_block.label] = basic_block
        self.cfg.add_node(basic_block.label, block=basic_block)

    def generateCFG(self):
        """
        构建控制流图（CFG）
        使用NetworkX有向图表示，节点是基本块标签，边表示控制流转移
        """
        # 清除现有边（保留节点）
        self.cfg.clear_edges()
        
        # 遍历每个基本块，建立控制流边
        for label, bb in self.basicBlocks.items():
            # 如果基本块为空，跳过
            if not bb.ops:
                continue
                
            # 获取基本块中的最后一个操作
            last_op = bb.ops[-1]
            
            # 判断最后一个操作的类型
            if last_op[1] == 7:  # 分支指令 (OP TYPE:7)
                if len(last_op) > 3:  # 条件分支
                    cond_var = last_op[2]
                    true_target = last_op[3]
                    false_target = last_op[4]
                    
                    # 添加条件为真的分支
                    self.cfg.add_edge(label, true_target, condition=cond_var)
                    
                    # 添加条件为假的分支
                    self.cfg.add_edge(label, false_target, condition=f"not {cond_var}")
                    
                elif len(last_op) > 2:  # 无条件跳转
                    target = last_op[2]
                    self.cfg.add_edge(label, target, condition="true")
            else:
                # 非分支指令，顺序执行到下一个基本块
                if bb.next_bb:
                    self.cfg.add_edge(label, bb.next_bb, condition="true")
            
    def generateDFGs(self):
        """为所有基本块构建数据流图"""
        for _, bb in self.basicBlocks.items():
            bb.generateDFG()
        return self.basicBlocks


def printCDFG(cdfg, file=None):
    """打印CDFG的基本信息"""
    print("===== 函数基本信息 =====", file=file)
    print(f"函数名: {cdfg.functionName}", file=file)
    print(f"返回类型: {cdfg.retType}", file=file)
    print(f"参数: {cdfg.params}", file=file)
    print("========================\n", file=file)


def printBasicBlocks(cdfg, file=None):
    """打印所有基本块的信息"""
    print("===== 基本块信息 =====", file=file)
    for label, bb in cdfg.basicBlocks.items():
        print(f"基本块 {label}:", file=file)
        print(f"\t下一个基本块: {bb.next_bb}", file=file)
        
        print("\t操作列表:", file=file)
        for i, op in enumerate(bb.ops):
            print(f"\t\t[{i}] {op}", file=file)
    print("===================\n", file=file)


def printCFG(cdfg, file=None):
    """打印控制流图信息"""
    print("===== 控制流图 (CFG) =====", file=file)
    for u, v, data in cdfg.cfg.edges(data=True):
        print(f"\t{u} -> {v} [条件: {data['condition']}]", file=file)
    print("=======================\n", file=file)


def printDFG(cdfg, file=None):
    """打印所有基本块的数据流图信息"""
    print("===== 数据流图 (DFG) =====", file=file)
    for label, bb in cdfg.basicBlocks.items():
        if len(bb.dfg.edges()) > 0:
            print(f"\t基本块 {label} 的DFG:", file=file)
            for u, v, data in bb.dfg.edges(data=True):
                value = data.get('value', '')
                print(f"\t\t操作 {u} -> {v} [值: {value}]", file=file)
    print("=======================\n", file=file)

def cdfgPrinter(cdfg, file=None):
    """打印CDFG的基本信息"""
    printCDFG(cdfg, file)
    printBasicBlocks(cdfg, file)    
    printCFG(cdfg, file)
    printDFG(cdfg, file)


# def main():
#     """主函数：解析LLVM IR并生成CDFG"""
#     # 获取文件路径
#     # 获取命令行参数
#     if len(sys.argv) > 1:
#         file_path = sys.argv[1]
#     else:
#         # 默认路径
#         print("File path unspecified, using default path: parser/parseResult.txt")
#         file_path = os.path.join(os.path.dirname(__file__), 'parser', 'parseResult.txt')
    
#     cdfg = CDFG()

#     cdfg.llvmParser(file_path)
#     cdfg.generateCFG()
#     cdfg.generateDFGs()


#     if not cdfg:
#         return
#     # 打印CDFG基本信息
#     printCDFG(cdfg)
#     printBasicBlocks(cdfg)    
#     printCFG(cdfg)
#     printDFG(cdfg)



# if __name__ == "__main__":
#     main()
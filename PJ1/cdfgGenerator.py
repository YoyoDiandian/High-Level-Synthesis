import os
import re
import networkx as nx
import matplotlib.pyplot as plt
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

    def add_op(self, op):
        """添加操作到基本块"""
        self.ops.append(op)

    def build_dfg(self):
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
        self.basic_blocks = {}  # 基本块字典，键为基本块标签
        self.cfg = nx.DiGraph()  # 使用NetworkX有向图表示控制流图
        self.ret_type = None    # 函数返回类型
        self.function_name = None  # 函数名
        self.params = []  # 函数参数列表

    def add_basic_block(self, basic_block):
        """
        添加基本块到CDFG
        
        Args:
            basic_block: BasicBlock对象
        """
        self.basic_blocks[basic_block.label] = basic_block
        self.cfg.add_node(basic_block.label, block=basic_block)

    def get_basic_blocks(self):
        """返回所有基本块"""
        return self.basic_blocks

    def build_cfg(self):
        """
        构建控制流图（CFG）
        使用NetworkX有向图表示，节点是基本块标签，边表示控制流转移
        """
        # 清除现有边（保留节点）
        self.cfg.clear_edges()
        
        # 遍历每个基本块，建立控制流边
        for label, bb in self.basic_blocks.items():
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
            
    def build_all_dfgs(self):
        """为所有基本块构建数据流图"""
        for _, bb in self.basic_blocks.items():
            bb.build_dfg()
        return self.basic_blocks

def parse_llvm_to_cdfg(file_path, cdfg):
    """
    解析LLVM格式的parse_result文件，构建CDFG结构
    
    Args:
        file_path: parse_result文件的路径
        CDFG对象
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
        cdfg.ret_type = ret_type_match.group(1)
    
    # 解析函数名
    func_name_match = re.search(r'function name (\w+)', content)
    if func_name_match:
        cdfg.function_name = func_name_match.group(1)
    
    # 解析参数
    params = []
    param_matches = re.finditer(r'(array|non-array)\s+(\w+)', content)
    for match in param_matches:
        param_type, param_name = match.groups()
        params.append((param_name, param_type))
    cdfg.params = params
    
    # 解析基本块
    basic_block_pattern = r'Basic Block label: (\w+)(.*?)(?=Basic Block label:|$)'
    basic_block_matches = re.finditer(basic_block_pattern, content, re.DOTALL)
    
    # 获取所有基本块标签
    bb_labels = []
    for match in re.finditer(basic_block_pattern, content, re.DOTALL):
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
            bb.add_op([value, op_type] + operands)
        
        # 将基本块添加到CDFG
        cdfg.add_basic_block(bb)
    
    # return cdfg

def print_cdfg_info(cdfg):
    """打印CDFG的基本信息"""
    print("\n===== CDFG 基本信息 =====")
    print(f"函数名: {cdfg.function_name}")
    print(f"返回类型: {cdfg.ret_type}")
    print(f"参数: {cdfg.params}")
    print("========================\n")


def print_basic_blocks_info(cdfg):
    """打印所有基本块的信息"""
    print("\n===== 基本块信息 =====")
    for label, bb in cdfg.basic_blocks.items():
        print(f"基本块 {label}:")
        print(f"  下一个基本块: {bb.next_bb}")
        
        print("  操作列表:")
        for i, op in enumerate(bb.ops):
            print(f"    [{i}] {op}")
    print("===================\n")


def print_cfg_info(cdfg):
    """打印控制流图信息"""
    print("\n===== 控制流图 (CFG) =====")
    for u, v, data in cdfg.cfg.edges(data=True):
        print(f"  {u} -> {v} [条件: {data['condition']}]")
    print("=======================\n")


def print_dfg_info(cdfg):
    """打印所有基本块的数据流图信息"""
    print("\n===== 数据流图 (DFG) =====")
    for label, bb in cdfg.basic_blocks.items():
        if len(bb.dfg.edges()) > 0:
            print(f"  基本块 {label} 的DFG:")
            for u, v, data in bb.dfg.edges(data=True):
                value = data.get('value', '')
                print(f"    操作 {u} -> {v} [值: {value}]")
    print("=======================\n")


def main():
    """主函数：解析LLVM IR并生成CDFG"""
    # 获取文件路径
    # 获取命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认路径
        print("File path unspecified, using default path: parser/parseResult.txt")
        file_path = os.path.join(os.path.dirname(__file__), 'parser', 'parseResult.txt')
    
    # 解析LLVM IR并生成CDFG

    cdfg = CDFG()

    parse_llvm_to_cdfg(file_path, cdfg)
    cdfg.build_cfg()
    cdfg.build_all_dfgs()


    if not cdfg:
        return
    # 打印CDFG基本信息
    print_cdfg_info(cdfg)
    print_basic_blocks_info(cdfg)    
    print_cfg_info(cdfg)
    print_dfg_info(cdfg)



if __name__ == "__main__":
    main()
class basic_block:
    def __init__(self, label):
        self.label = label
        self.ops = []
        self.dfg = {}
        self.next_bb = None

    def add_op(self, op):
        self.ops.append(op)

    def add_data_edge(self, src, dst):
        self.dfg[src] = dst
        
    def build_dfg(self):
        """
        建立数据流图（DFG）
        以邻接表形式存储，格式为：dfg[src] = [dst1, dst2, ...]
        其中src和dst是操作在ops列表中的索引
        """
        # 初始化DFG邻接表
        self.dfg = {}
        
        # 遍历每个操作
        for i, op in enumerate(self.ops):
            self.dfg[i] = []
            
            # 获取当前操作的左值
            current_value = op[0]
            
            # 获取当前操作的操作数（从索引2开始）
            operands = op[2:]
            
            # 向前搜索数据依赖
            for j in range(i):
                prev_op = self.ops[j]
                prev_value = prev_op[0]
                
                # 检查当前操作的操作数中是否包含前面操作的左值
                if prev_value in operands:
                    # 添加数据依赖边
                    self.dfg[j].append(i)
        
        return self.dfg

class cdfg:
    def __init__(self):
        self.cfg = {}
        self.ret_type = None
        self.function_name = None
        self.params = []

    def add_basic_block(self, basic_block):
        self.cfg[basic_block.label] = basic_block

    def get_cfg(self):
        return self.cfg
    
    def build_cfg(self):
        """
        建立控制流图（CFG）
        使用邻接表形式存储，格式为：cfg[src] = [[end, cond], ...]
        其中src是源块label，end是目标块label，cond是跳转条件
        """
        # 初始化邻接表
        self.cfg_adj_list = {}
        
        # 遍历每个基本块
        for label, bb in self.cfg.items():
            self.cfg_adj_list[label] = []
            
            # 获取基本块中的操作
            if not bb.ops:
                continue
                
            # 获取最后一个操作
            last_op = bb.ops[-1]
            
            # 检查最后一个操作是否为分支指令（OP TYPE:7）
            if last_op[1] == 7:  # 分支指令
                # 获取目标块
                if len(last_op) > 3:  # 有条件跳转
                    cond_var = last_op[2]
                    true_target = last_op[3]
                    false_target = last_op[4]
                    # 添加两条有向边
                    self.cfg_adj_list[label].append([true_target, cond_var])  # 条件为真时的跳转
                    self.cfg_adj_list[label].append([false_target, f"not {cond_var}"])  # 条件为假时的跳转
                elif len(last_op) > 2:  # 无条件跳转
                    target = last_op[2]
                    self.cfg_adj_list[label].append([target, "true"])
            else:
                # 非分支指令，添加顺序执行边
                if bb.next_bb:
                    self.cfg_adj_list[label].append([bb.next_bb, "true"])
        
        return self.cfg_adj_list
    
    def build_dfg(self):
        """
        为所有基本块建立数据流图（DFG）
        """
        # 遍历每个基本块
        for label, bb in self.cfg.items():
            # 为基本块建立DFG
            bb.build_dfg()
        
        return self.cfg

class op:
    def __init__(self, value, op_type):
        self.value = value
        self.op_type = op_type
    
    

import re

def parse_llvm_to_cdfg(file_path):
    """
    解析LLVM格式的parse_result文件，构建CDFG结构
    
    Args:
        file_path: parse_result文件的路径
        
    Returns:
        cdfg对象
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 创建CDFG对象
    cdfg_obj = cdfg()
    
    # 解析返回类型
    ret_type_match = re.search(r'ret type: (\w+)', content)
    if ret_type_match:
        cdfg_obj.ret_type = ret_type_match.group(1)
    
    # 解析函数名
    func_name_match = re.search(r'function name (\w+)', content)
    if func_name_match:
        cdfg_obj.function_name = func_name_match.group(1)
    
    # 解析参数
    params = []
    param_matches = re.finditer(r'(array|non-array)\s+(\w+)', content)
    for match in param_matches:
        param_type, param_name = match.groups()
        params.append((param_name, param_type))
    cdfg_obj.params = params
    
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
        bb = basic_block(label)
        
        # 设置next_bb属性
        if i < len(bb_labels) - 1:
            bb.next_bb = bb_labels[i + 1]
        else:
            bb.next_bb = None
        
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
            
            # 创建操作对象
            op_obj = op(value, op_type)
            
            # 将操作添加到基本块
            bb.add_op([value, op_type] + operands)
        
        # 将基本块添加到CDFG
        cdfg_obj.add_basic_block(bb)
    
    return cdfg_obj

# 使用示例
if __name__ == "__main__":
    cdfg_obj = parse_llvm_to_cdfg("parse_result")
    print(f"函数名: {cdfg_obj.function_name}")
    print(f"返回类型: {cdfg_obj.ret_type}")
    print(f"参数: {cdfg_obj.params}")
    
    for label, bb in cdfg_obj.get_cfg().items():
        print(f"基本块 {label}:")
        print(f"  下一个基本块: {bb.next_bb}")
        for op in bb.ops:
            print(f"  操作: {op}")
    
    # 建立控制流图
    cfg = cdfg_obj.build_cfg()
    print("\n控制流图 (CFG):")
    for src, edges in cfg.items():
        print(f"  基本块 {src} 的边:")
        for edge in edges:
            print(f"    -> {edge[0]} (条件: {edge[1]})")
    
    # 建立数据流图
    cdfg_obj.build_dfg()
    print("\n数据流图 (DFG):")
    for label, bb in cdfg_obj.get_cfg().items():
        print(f"  基本块 {label} 的DFG:")
        for src, dsts in bb.dfg.items():
            if dsts:  # 只打印有出边的节点
                print(f"    操作 {src} -> {dsts}")
    
    

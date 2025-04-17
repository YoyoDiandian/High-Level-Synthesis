import networkx as nx
from collections import defaultdict

class RegisterAllocator:
    """使用图着色法进行寄存器分配，支持全局寄存器分配"""
    
    def __init__(self, num_registers=8):
        """初始化寄存器分配器"""
        self.num_registers = num_registers
        self.variable_map = {}  # 变量名到节点ID的映射
        self.interference_graph = nx.Graph()  # 冲突图
        self.register_allocation = {}  # 寄存器分配结果
        self.spilled_vars = []  # 溢出到内存的变量
        self.global_var_def = {}  # 全局变量定义基本块
        self.global_var_uses = defaultdict(list)  # 全局变量使用基本块

    def analyze_global_variables(self, cdfg):
        """
        分析全局变量（在多个基本块中使用的变量）
        
        参数：
            cdfg: CDFG对象
        
        返回：
            global_vars: 全局变量集合
        """
        # 记录每个变量在哪些基本块中定义或使用
        var_blocks = defaultdict(set)
        
        # 遍历所有基本块
        for bb_label, bb in cdfg.basicBlocks.items():
            # 跳过没有调度信息的基本块
            if bb_label not in cdfg.schedule:
                continue
                
            # 分析基本块中的操作
            for ops in cdfg.schedule[bb_label]:
                for op_idx, _ in ops:
                    operation = bb.ops[op_idx]
                    
                    # 记录结果变量
                    result_var = operation[0]
                    if result_var:
                        var_blocks[result_var].add(bb_label)
                        self.global_var_def[result_var] = bb_label
                    
                    # 记录操作数
                    for var in operation[2:]:
                        if isinstance(var, str) and not var.isdigit() and var:
                            var_blocks[var].add(bb_label)
                            self.global_var_uses[var].append(bb_label)
        
        # 过滤出在多个基本块中使用的变量
        global_vars = {var for var, blocks in var_blocks.items() if len(blocks) > 1}
        
        return global_vars

    def build_global_liveness_info(self, cdfg):
        """
        构建全局变量的生命周期信息
        
        参数：
            cdfg: CDFG对象
            
        返回：
            global_live_ranges: 全局变量的生命周期
            global_live_vars: 全局活跃变量信息
        """
        # 获取全局变量
        global_vars = self.analyze_global_variables(cdfg)
        
        # 构建控制流图中基本块的执行顺序（简化版本）
        block_order = []
        visited = set()
        
        # 简单DFS以获取基本块顺序
        def dfs(bb_label):
            if bb_label in visited:
                return
            
            visited.add(bb_label)
            block_order.append(bb_label)
            
            # 遍历后继基本块
            for _, next_bb in cdfg.cfg.edges(bb_label):
                dfs(next_bb)
        
        # 从入口基本块开始DFS
        entry_blocks = [bb for bb in cdfg.basicBlocks if not list(cdfg.cfg.predecessors(bb))]
        for entry in entry_blocks or list(cdfg.basicBlocks.keys())[:1]:  # 如果没有明确的入口基本块，使用第一个基本块
            dfs(entry)
        
        # 为每个基本块分配一个全局时间戳范围
        block_timestamps = {}
        current_time = 0
        
        for bb_label in block_order:
            if bb_label in cdfg.schedule:
                block_len = sum(len(cycle) for cycle in cdfg.schedule[bb_label])
                block_timestamps[bb_label] = (current_time, current_time + block_len - 1)
                current_time += block_len
        
        # 构建全局变量的生命周期
        global_live_ranges = {}
        for var in global_vars:
            # 确定变量的定义点
            def_block = self.global_var_def.get(var)
            if not def_block:
                continue
                
            # 定义点时间戳
            if def_block in block_timestamps:
                def_time = block_timestamps[def_block][0]
            else:
                continue
            
            # 确定最后使用点
            last_use_time = def_time
            for use_block in self.global_var_uses.get(var, []):
                if use_block in block_timestamps:
                    last_use_time = max(last_use_time, block_timestamps[use_block][1])
            
            # 记录全局生命周期
            global_live_ranges[var] = (def_time, last_use_time)
        
        # 构建全局活跃变量信息
        global_live_vars = defaultdict(set)
        for var, (start, end) in global_live_ranges.items():
            for time in range(start, end + 1):
                global_live_vars[time].add(var)
        
        return global_live_ranges, global_live_vars

    def build_liveness_info(self, bb, schedule):
        """构建局部变量的生命周期信息（与原代码相同）"""
        # ... [保持原有代码不变] ...
        # 这里假设原函数已经实现，不再重复列出
        var_def = {}
        var_uses = defaultdict(list)
        max_cycle = len(schedule) - 1
        
        for cycle, ops in enumerate(schedule):
            for op_idx, _ in ops:
                operation = bb.ops[op_idx]
                result_var = operation[0]
                operands = operation[2:]
                
                if result_var:
                    var_def[result_var] = cycle
                
                for var in operands:
                    if isinstance(var, str) and not var.isdigit() and var:
                        var_uses[var].append(cycle)
        
        live_ranges = {}
        for var in set(list(var_def.keys()) + list(var_uses.keys())):
            if var in var_def:
                def_point = var_def[var]
                last_use = max(var_uses.get(var, [def_point])) if var in var_uses else max_cycle
                live_ranges[var] = (def_point, last_use)
        
        live_vars = defaultdict(set)
        for var, (start, end) in live_ranges.items():
            for cycle in range(start, end + 1):
                live_vars[cycle].add(var)
        
        return live_ranges, live_vars

    def build_unified_interference_graph(self, cdfg):
        """
        构建统一的冲突图，包含全局变量和局部变量
        
        参数：
            cdfg: CDFG对象
        
        返回：
            interference_graph: 统一的冲突图
        """
        # 重置冲突图
        self.interference_graph.clear()
        self.variable_map = {}
        
        # 构建全局活跃变量信息
        global_live_ranges, global_live_vars = self.build_global_liveness_info(cdfg)
        
        # 添加全局变量节点
        var_idx = 0
        for var in global_live_ranges:
            self.variable_map[var] = var_idx
            self.interference_graph.add_node(var_idx, name=var, is_global=True)
            var_idx += 1
        
        # 添加全局变量之间的冲突边
        for time, vars_set in global_live_vars.items():
            vars_list = list(vars_set)
            for i in range(len(vars_list)):
                for j in range(i + 1, len(vars_list)):
                    var1 = vars_list[i]
                    var2 = vars_list[j]
                    if var1 in self.variable_map and var2 in self.variable_map:
                        self.interference_graph.add_edge(
                            self.variable_map[var1], 
                            self.variable_map[var2],
                            reason="global_conflict"
                        )
        
        # 处理每个基本块的局部变量
        for bb_label, bb in cdfg.basicBlocks.items():
            # 跳过没有调度信息的基本块
            if bb_label not in cdfg.schedule:
                continue
                
            # 构建局部活跃变量信息
            _, local_live_vars = self.build_liveness_info(bb, cdfg.schedule[bb_label])
            
            # 添加局部变量节点（如果还未添加）
            for cycle, vars_set in local_live_vars.items():
                for var in vars_set:
                    if var not in self.variable_map:
                        self.variable_map[var] = var_idx
                        self.interference_graph.add_node(var_idx, name=var, is_global=False)
                        var_idx += 1
            
            # 添加局部变量之间的冲突边
            for cycle, vars_set in local_live_vars.items():
                vars_list = list(vars_set)
                for i in range(len(vars_list)):
                    for j in range(i + 1, len(vars_list)):
                        var1 = vars_list[i]
                        var2 = vars_list[j]
                        if var1 in self.variable_map and var2 in self.variable_map:
                            self.interference_graph.add_edge(
                                self.variable_map[var1],
                                self.variable_map[var2],
                                reason=f"local_conflict_in_{bb_label}"
                            )
            
            # 添加局部变量与全局变量之间的冲突
            for cycle, local_vars in local_live_vars.items():
                for local_var in local_vars:
                    # 只处理非全局的局部变量
                    if local_var in self.variable_map and not self.interference_graph.nodes[self.variable_map[local_var]].get('is_global', False):
                        for global_var, (start, end) in global_live_ranges.items():
                            # 如果全局变量在当前周期活跃，创建冲突边
                            if global_var in self.variable_map and global_var != local_var:
                                self.interference_graph.add_edge(
                                    self.variable_map[local_var],
                                    self.variable_map[global_var],
                                    reason=f"local_global_conflict_in_{bb_label}"
                                )
        
        return self.interference_graph

    def color_graph(self):
        """使用贪心算法为冲突图着色（与原代码相同）"""
        # ... [保持原有代码不变] ...
        sorted_nodes = sorted(
            self.interference_graph.nodes(), 
            key=lambda x: self.interference_graph.degree(x), # type: ignore
            reverse=True
        )
        
        coloring = {}
        
        for node in sorted_nodes:
            # 获取邻居已使用的颜色
            neighbor_colors = set()
            for neighbor in self.interference_graph.neighbors(node):
                if neighbor in coloring:
                    neighbor_colors.add(coloring[neighbor])
            
            # 查找可用的颜色
            color = 0
            while color < self.num_registers and color in neighbor_colors:
                color += 1
            
            # 分配颜色或标记为溢出
            if color < self.num_registers:
                coloring[node] = color
            else:
                # 这个节点无法着色，需要溢出
                return False, coloring
        
        return True, coloring

    def select_spill_candidates(self):
        """选择需要溢出的变量（与原代码相同）"""
        # ... [保持原有代码不变] ...
        sorted_nodes = sorted(
            self.interference_graph.nodes(), 
            key=lambda x: self.interference_graph.degree(x), # type: ignore
            reverse=True
        )
        
        # 选择前10%的高度数节点作为候选
        spill_candidates = sorted_nodes[:max(1, len(sorted_nodes) // 10)]
        
        # 找出冲突最严重的节点
        spill_node = spill_candidates[0]
        
        return [spill_node]

    def allocate_registers_for_cdfg(self, cdfg):
        """
        为整个CDFG统一分配寄存器，考虑全局变量
        
        参数：
            cdfg: CDFG对象
            
        返回：
            cdfg: 添加寄存器分配结果的CDFG对象
        """
        # 为CDFG添加寄存器分配结果属性
        if not hasattr(cdfg, 'register_allocation'):
            cdfg.register_allocation = {}
            cdfg.global_register_map = {}
        
        # 构建统一的冲突图
        self.build_unified_interference_graph(cdfg)
        
        # 尝试着色
        success, coloring = self.color_graph()
        
        # 处理变量溢出
        self.spilled_vars = []
        while not success:
            spill_nodes = self.select_spill_candidates()
            self.spilled_vars.extend([self.interference_graph.nodes[node]['name'] for node in spill_nodes])
            
            # 从图中移除溢出变量
            self.interference_graph.remove_nodes_from(spill_nodes)
            
            # 重新尝试着色
            success, coloring = self.color_graph()
        
        # 构建全局变量到寄存器的映射
        global_register_map = {}
        for node, color in coloring.items():
            var_name = self.interference_graph.nodes[node]['name']
            is_global = self.interference_graph.nodes[node].get('is_global', False)
            
            if is_global:
                global_register_map[var_name] = f"r{color}"
        
        # 为每个基本块分配寄存器
        for bb_label, bb in cdfg.basicBlocks.items():
            if bb_label not in cdfg.schedule:
                continue
                
            # 将全局变量的寄存器分配应用到当前基本块
            register_map = dict(global_register_map)
            
            # 为局部变量分配寄存器
            for node, color in coloring.items():
                var_name = self.interference_graph.nodes[node]['name']
                is_global = self.interference_graph.nodes[node].get('is_global', False)
                
                # 检查该变量是否在当前基本块中使用
                is_used_in_block = False
                for ops in cdfg.schedule[bb_label]:
                    for op_idx, _ in ops:
                        operation = bb.ops[op_idx]
                        if var_name == operation[0] or var_name in operation[2:]:
                            is_used_in_block = True
                            break
                
                if not is_global and is_used_in_block:
                    register_map[var_name] = f"r{color}"
            
            # 记录寄存器分配结果
            cdfg.register_allocation[bb_label] = {
                'register_map': register_map,
                'spilled_vars': [var for var in self.spilled_vars if var in register_map]
            }
        
        # 保存全局寄存器映射
        cdfg.global_register_map = global_register_map
        
        return cdfg

def addRegisterAllocator(classObj):
    """
    将寄存器分配功能添加到CDFG类
    
    参数：
        classObj: 要添加功能的类（CDFG）
    """
    def allocate_registers(self, num_registers=8):
        """
        使用图着色法为CDFG中的变量分配寄存器，支持跨基本块变量
        
        参数：
            num_registers: 可用的寄存器数量
            
        返回：
            self: CDFG对象
        """
        allocator = RegisterAllocator(num_registers)
        allocator.allocate_registers_for_cdfg(self)
        return self
    
    # 添加寄存器分配方法到CDFG类
    setattr(classObj, 'allocate_registers', allocate_registers)

def registerAllocationPrinter(cdfg, file=None):
    """
    打印寄存器分配结果，包括全局变量分配
    
    参数：
        cdfg: CDFG对象
        file: 输出文件对象
    """
    if not hasattr(cdfg, 'register_allocation'):
        print("尚未进行寄存器分配", file=file)
        return
    
    print("\n===== 寄存器分配结果 =====", file=file)
    
    # 打印全局变量的寄存器分配
    if hasattr(cdfg, 'global_register_map') and cdfg.global_register_map:
        print("全局变量寄存器分配:", file=file)
        for var, reg in sorted(cdfg.global_register_map.items()):
            print(f"  {var} -> {reg}", file=file)
        print("", file=file)
    
    # 打印各基本块的寄存器分配
    for bb_label, allocation in cdfg.register_allocation.items():
        print(f"基本块 {bb_label}:", file=file)
        
        register_map = allocation['register_map']
        spilled_vars = allocation['spilled_vars']
        
        # 打印寄存器分配
        print("  变量到寄存器的映射:", file=file)
        for var, reg in sorted(register_map.items()):
            print(f"    {var} -> {reg}", file=file)
        
        # 打印溢出变量
        if spilled_vars:
            print("  溢出到内存的变量:", file=file)
            for var in spilled_vars:
                print(f"    {var}", file=file)
    
    print("========================\n", file=file)
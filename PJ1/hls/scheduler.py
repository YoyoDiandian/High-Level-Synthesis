from cdfgGenerator import CDFG

# 操作类型常量定义 - 与cdfgGenerator中保持一致
OP_ASSIGN = 0
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4
OP_LOAD = 5
OP_STORE = 6
OP_BR = 7
OP_LT = 8
OP_GT = 9
OP_LE = 10
OP_GE = 11
OP_EQ = 12
OP_PHI = 13
OP_RET = 14

# 定义计算资源
RESOURCE = [
    1, # OP_ASSIGN
    1, # OP_ADD
    1, # OP_SUB
    1, # OP_MUL
    1, # OP_DIV
    1, # OP_LOAD
    1, # OP_STORE
    1, # OP_BR
    1, # OP_LT
    1, # OP_GT
    1, # OP_LE
    1, # OP_GE
    1, # OP_EQ
    1, # OP_PHI
    1, # OP_RET
]

# 定义延迟
DELAY = [
    1, # OP_ASSIGN
    1, # OP_ADD
    1, # OP_SUB
    1, # OP_MUL
    1, # OP_DIV
    1, # OP_LOAD
    1, # OP_STORE
    1, # OP_BR
    1, # OP_LT
    1, # OP_GT
    1, # OP_LE
    1, # OP_GE
    1, # OP_EQ
    1, # OP_PHI
    1, # OP_RET
]

def initializeSchedulingData(bb):
    """
    初始化调度所需的数据结构。
    
    参数：
        bb: 基本块对象
    
    返回：
        in_degree: 每个操作的入度
        op_schedule: 操作的调度结果
        resource_remain: 各资源类型的剩余可用数量
    """
    # 使用NetworkX的in_degree方法直接获取所有节点的入度
    in_degree = dict(bb.dfg.in_degree())
    
    # 确保所有操作都有入度值（包括孤立节点）
    for i in range(len(bb.ops)):
        in_degree[i] = 0 if i not in in_degree else in_degree[i]
    
    # 初始化调度结果
    op_schedule = {i: -1 for i in range(len(bb.ops))}
    
    # 初始化资源状态
    resource_remain = {i: RESOURCE[i] for i in range(len(RESOURCE))}
    
    return in_degree, op_schedule, resource_remain

def scheduleOperations(bb, in_degree, op_schedule, resource_remain):
    """
    使用ASAP算法调度操作。
    
    参数：
        bb: 基本块对象
        in_degree: 每个操作的入度
        op_schedule: 操作的调度结果
        resource_remain: 各资源类型的剩余可用数量
    
    返回：
        op_schedule: 更新后的调度结果
    """
    current_cycle = 0
    while True:
        # 找出当前周期可以调度的操作（入度为0且未调度）
        ready_ops = []
        for i in range(len(bb.ops)):
            if in_degree[i] == 0 and op_schedule[i] == -1:
                ready_ops.append(i)
        
        if not ready_ops:
            break  # 没有可调度的操作，退出循环
        
        # 按资源类型分组
        resource_groups = {}
        for op_idx in ready_ops:
            op_type = bb.ops[op_idx][1]
            if op_type not in resource_groups:
                resource_groups[op_type] = []
            resource_groups[op_type].append(op_idx)
        
        # 考虑资源约束进行调度
        scheduled_this_cycle = []
        for op_type, ops in resource_groups.items():
            available_resources = resource_remain[op_type]
            num_to_schedule = min(available_resources, len(ops))
            
            for i in range(num_to_schedule):
                op_idx = ops[i]
                op_schedule[op_idx] = current_cycle
                scheduled_this_cycle.append(op_idx)
                
                # 更新依赖于当前操作的操作的入度 - 使用NetworkX的API
                for _, dst in bb.dfg.out_edges(op_idx):
                    in_degree[dst] -= 1
                
                # 更新资源状态
                resource_remain[op_type] -= 1
        
        if not scheduled_this_cycle:
            break  # 没有操作被调度，退出循环
        
        current_cycle += 1  # 进入下一个周期
        
        # 重置资源状态
        resource_remain = {op_type: RESOURCE[op_type] for op_type in range(len(RESOURCE))}
    
    return op_schedule

def processBranchInstructions(bb, op_schedule):
    """
    处理跳转指令（OP_BR），确保其在所有其他操作完成后执行。
    
    参数：
        bb: 基本块对象
        op_schedule: 操作的调度结果
    
    返回：
        op_schedule: 更新后的调度结果
    """
    for i, op in enumerate(bb.ops):
        if op[1] == OP_BR:
            max_other_finish = 0
            for j in range(len(bb.ops)):
                if j != i and op_schedule[j] != -1:
                    max_other_finish = max(max_other_finish, op_schedule[j] + DELAY[bb.ops[j][1]])
            op_schedule[i] = max(op_schedule[i], max_other_finish)
    
    return op_schedule

def convertCycleList(op_schedule):
    """
    将调度结果转换为周期列表格式。
    
    参数：
        op_schedule: 操作的调度结果
    
    返回：
        cycle_list: 周期列表
    """
    max_cycle = max(op_schedule.values()) if op_schedule else 0
    cycle_list = [[] for _ in range(max_cycle + 1)]
    
    for op_idx, cycle in op_schedule.items():
        if cycle != -1:
            cycle_list[cycle].append(op_idx)
    
    return cycle_list

def allocateResources(cycle_list, bb):
    """
    为每个操作分配资源。
    
    参数：
        cycle_list: 周期列表
        bb: 基本块对象
    
    返回：
        final_cycles: 分配资源后的周期列表
    """
    final_cycles = []
    for cycle in range(len(cycle_list)):
        final_cycles.append([])
    
        # 重置资源状态
        resource_remain = {op_type: RESOURCE[op_type] for op_type in range(len(RESOURCE))}
        
        for op_idx in cycle_list[cycle]:
            op_type = bb.ops[op_idx][1]
            # 计算设备索引：资源总数减去调度前的当前资源数
            device_idx = RESOURCE[op_type] - resource_remain[op_type]
            # 更新资源状态
            resource_remain[op_type] -= 1
            # 添加到最终调度结果
            final_cycles[cycle].append((op_idx, device_idx))
    
    return final_cycles

def scheduleASAP(self):
    """
    使用ASAP（尽可能早）算法对CDFG进行调度。
    
    返回：
        schedule_result: 调度结果
    """    
    # 按照控制流图的顺序处理每个基本块
    for bbLabel, bb in self.basicBlocks.items():
        # 初始化调度数据
        in_degree, op_schedule, resource_remain = initializeSchedulingData(bb)
        
        # 调度操作
        op_schedule = scheduleOperations(bb, in_degree, op_schedule, resource_remain)
        
        # 处理跳转指令
        op_schedule = processBranchInstructions(bb, op_schedule)
        
        # 转换为周期列表
        cycle_list = convertCycleList(op_schedule)
        
        # 分配资源
        final_cycles = allocateResources(cycle_list, bb)
        
        # 保存结果
        self.schedule[bbLabel] = final_cycles
    

def printSchedule(schedule):
    """
    Print schedule results.
    """
    print("Schedule results:")
    for bbLabel, cycles in schedule.items():
        print(f"Basic block {bbLabel}'s schedule results:")
        for cycle_idx, ops in enumerate(cycles):
            print(f"  cycle {cycle_idx}: ", end="")
            for op_idx, device_idx in ops:
                print(f"(operation {op_idx}, resource {device_idx}) ", end="")
            print()
    print(35 * "-")

def addScheduler(classObj):
    setattr(classObj, 'schedule', {})
    setattr(classObj, 'scheduleASAP', scheduleASAP)

# def main():
#     """
#     主函数：解析LLVM IR并生成CDFG，然后进行调度。
#     """
#     # 添加schedule属性和schedule_asap方法到CDFG类
#     addScheduler()
    
#     # 创建CDFG对象并解析LLVM IR
#     cdfg = CDFG()
#     # 使用与cdfgGenerator中相同的默认路径
#     file_path = "output/parseResult.txt"
#     cdfg.llvmParser(file_path)
    
#     # 生成CFG和DFG
#     cdfg.generateCFG()
#     cdfg.generateDFGs()
    
#     # 使用ASAP算法进行调度
#     cdfg.scheduleASAP()
    
#     # 打印调度结果
#     printSchedule(cdfg.schedule)
#     print(cdfg.schedule)
# if __name__ == "__main__":
#     main()
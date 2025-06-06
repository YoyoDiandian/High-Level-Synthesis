from resourceData import *

def initializeSchedulingResources(bb):
    """初始化调度所需的资源和数据结构"""
    # 计算操作入度
    in_degree = dict(bb.dfg.in_degree())
    
    # 确保所有操作都有入度值（包括孤立节点）
    # for i in range(len(bb.ops)):
    #     if i not in in_degree:
    #         in_degree[i] = 0
    in_degree = {i: in_degree.get(i, 0) for i in range(len(bb.ops))}
    
    # 初始化跟踪变量
    # time remain for certain resource on certain operation
    time_remain = [0] * len(bb.ops)
    # show certain operation is occupying device or not
    device_occupied = [-1] * len(bb.ops)
    # show all the occupation situation
    # 0 means not occupied; 1 means occupied
    occupation = [[0] * RESOURCE[i] for i in range(len(RESOURCE))]
    
    return in_degree, time_remain, device_occupied, occupation

def processRunningOperations(bb, time_remain, device_occupied, occupation, in_degree, unfinished):
    """处理当前正在执行的操作"""
    for i in range(len(bb.ops)):
        if time_remain[i] <= 0:
            continue
            
        # decrease the time remain
        time_remain[i] -= 1
        
        # 如果操作执行完毕
        if time_remain[i] == 0:
            # 释放计算资源
            op_type = bb.ops[i][1]
            occupation[op_type][device_occupied[i]] = 0
            device_occupied[i] = -1
            
            # 从未完成列表中移除
            unfinished.remove(i) if i in unfinished else None

            # 降低依赖该操作的后继操作的入度
            for _, dst in bb.dfg.out_edges(i):
                in_degree[dst] -= 1

def identifyReadyOperations(bb, in_degree, sent):
    """找出当前周期可以调度的操作"""
    ready = []
    for i in range(len(bb.ops)):
        if i not in sent and in_degree[i] == 0:
            ready.append(i)
            sent.append(i)
    return ready

def scheduleReadyOperations(bb, ready, time_remain, device_occupied, occupation):
    """尝试调度就绪队列中的操作"""
    cycle_schedule = []
    removal_list = []
    
    for op_idx in ready:
        op_type = bb.ops[op_idx][1]
        
        # 查找空闲资源
        for pos in range(RESOURCE[op_type]):
            if occupation[op_type][pos] == 0:
                # 分配资源
                cycle_schedule.append((op_idx, pos))
                occupation[op_type][pos] = 1
                device_occupied[op_idx] = pos
                time_remain[op_idx] = DELAY[op_type]
                removal_list.append(op_idx)
                break
    
    # 从就绪队列中移除已调度的操作
    for op_idx in removal_list:
        ready.remove(op_idx)
        
    return cycle_schedule

def handleDeadlock(bb, unfinished, ready, in_degree, sent):
    """处理可能的死锁情况"""
    if not unfinished or ready:
        return False
        
    # 强制处理一个操作
    force_op = unfinished[0]
    in_degree[force_op] = 0
    ready.append(force_op)
    sent.append(force_op)
    return True

def ensureBranchOrder(bb, bb_schedule):
    """确保跳转指令在所有其他操作完成后执行"""
    # 查找所有跳转指令
    branch_ops = [i for i, op in enumerate(bb.ops) if op[1] == OP_BR]
    
    if not branch_ops:
        return
    
    # 找到所有非分支指令的最后执行周期
    last_non_branch_cycle = -1
    for cycle_idx, ops in enumerate(bb_schedule):
        for op_idx, _ in ops:
            if op_idx not in branch_ops:
                op_end_cycle = cycle_idx + DELAY[bb.ops[op_idx][1]] - 1
                last_non_branch_cycle = max(last_non_branch_cycle, op_end_cycle)
    
    # 确保所有分支指令在非分支指令之后执行
    for branch_idx in branch_ops:
        # 查找当前分支指令的调度周期
        current_cycle = -1
        current_device = -1
        for cycle_idx, ops in enumerate(bb_schedule):
            for op_idx, device_idx in ops:
                if op_idx == branch_idx:
                    current_cycle = cycle_idx
                    current_device = device_idx
                    break
            if current_cycle != -1:
                break
        
        # 如果分支指令被调度的太早，移动它
        if current_cycle != -1 and current_cycle <= last_non_branch_cycle:
            # 从原位置移除
            bb_schedule[current_cycle] = [(op_idx, dev_idx) for op_idx, dev_idx in bb_schedule[current_cycle] 
                                         if op_idx != branch_idx]
            
            # 确保目标周期存在
            target_cycle = last_non_branch_cycle + 1
            while len(bb_schedule) <= target_cycle:
                bb_schedule.append([])
            
            # 在目标周期添加分支指令
            bb_schedule[target_cycle].append((branch_idx, current_device))

def scheduleASAP(self):
    """
    使用ASAP算法对CDFG进行调度，采用周期级模拟。
    返回：调度结果字典 {bb_label: [[(op_idx, device_idx), ...], ...]}
    """
    self.schedule = {}
    
    # 处理每个基本块
    for bbLabel, bb in self.basicBlocks.items():
        # 初始化基本块的调度结果
        bb_schedule = []
        # print(f"\nbasic block label: {bbLabel}\n")
        # 初始化调度所需的各种数据结构
        in_degree, time_remain, device_occupied, occupation = initializeSchedulingResources(bb)
        
        # 初始化跟踪变量
        unfinished = list(range(len(bb.ops)))
        sent = []
        ready = []
        
        # 调度循环
        while unfinished:
            # 处理正在执行的操作
            processRunningOperations(bb, time_remain, device_occupied, occupation, in_degree, unfinished)
            
            # 查找可以调度的新操作
            ready.extend(identifyReadyOperations(bb, in_degree, sent))
            
            # 调度就绪操作
            cycle_schedule = scheduleReadyOperations(bb, ready, time_remain, device_occupied, occupation)
            
            # 记录当前周期的调度结果
            bb_schedule.append(cycle_schedule)
            
            # 检测并处理死锁
            if not cycle_schedule and not any(time_remain):
                if handleDeadlock(bb, unfinished, ready, in_degree, sent):
                    continue
                break
            
            # print(f"unfinished: {unfinished}")
            # print(f"sent: {sent}")
            # print(f"ready: {ready}")

        # 处理分支指令的特殊要求
        # ensureBranchOrder(bb, bb_schedule)
        bb_schedule.pop()
        # 保存基本块的调度结果
        self.schedule[bbLabel] = bb_schedule

# def schedulePrinter(hls, file=None):
#     """打印调度结果"""
#     print("\n======= 调度结果 =======", file=file)
#     for bbLabel, cycles in hls.schedule.items():
#         print(f"基本块 {bbLabel} 的调度结果:", file=file)
#         for cycle_idx, ops in enumerate(cycles):
#             print(f"\t周期 {cycle_idx}: ", end="", file=file)
#             for op_idx, device_idx in ops:
#                 op = hls.basicBlocks[bbLabel].ops[op_idx]
#                 op_type_name = getOperationName(op[1])
#                 print(f"(操作 {op_idx}:{op_type_name}, 设备 {device_idx}) ", end="", file=file)
#             print(file=file)
#     print("=========================\n", file=file)

def schedulePrinter(hls, file=None):
    """
    Print schedule results.
    """
    print("===== Schedule Results =====", file=file)
    for bbLabel, cycles in hls.schedule.items():
        print(f"Basic block {bbLabel}'s schedule results:", file=file)
        for cycle_idx, ops in enumerate(cycles):
            print(f"  cycle {cycle_idx}: ", end="", file=file)
            for op_idx, device_idx in ops:
                print(f"(operation {op_idx}, resource {device_idx}) ", end="", file=file)
            print(file=file)
    print(35 * "=" + "\n", file=file)

def getOperationName(op_type):
    """获取操作类型的名称"""
    names = ["ASSIGN", "ADD", "SUB", "MUL", "DIV", "LOAD", "STORE", 
             "BR", "LT", "GT", "LE", "GE", "EQ", "PHI", "RET"]
    return names[op_type] if 0 <= op_type < len(names) else str(op_type)

def addScheduler(classObj):
    """将调度功能添加到CDFG类"""
    setattr(classObj, 'schedule', {})
    setattr(classObj, 'scheduleASAP', scheduleASAP)
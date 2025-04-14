from cdfg_generator import *

# 定义计算资源
resource = [
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
delay = [
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

def add_scheduling_to_cdfg(cdfg_class):
    """
    为cdfg类添加调度相关的方法
    """
    def schedule_asap(self):
        """
        使用ASAP（尽可能早）算法对CDFG进行调度
        返回：调度结果，格式为 {bb_label: [[(op_idx, device_idx), ...], ...]}
        其中每个内部列表表示一个周期中被调度的操作信息，每个操作信息包含：
        - op_idx: 操作在bb.ops中的索引
        - device_idx: 该操作类型的计算资源序号，等于资源总数减去调度前的当前资源数
        """
        schedule_result = {}
        
        # 按照控制流图的顺序处理每个基本块
        for bb_label, bb in self.cfg.items():
            # 计算每个操作的入度
            in_degree = {}
            for i in range(len(bb.ops)):
                in_degree[i] = 0
            
            # 遍历DFG计算入度
            for src, dsts in bb.dfg.items():
                for dst in dsts:
                    in_degree[dst] += 1
            
            # 初始化调度结果
            op_schedule = {}
            for i in range(len(bb.ops)):
                op_schedule[i] = -1  # 初始化为未调度
            
            # 初始化资源状态
            resource_remain = {}
            for op_type in range(len(resource)):
                resource_remain[op_type] = resource[op_type]  # 初始化为资源总数
            
            # 使用ASAP算法进行调度
            current_cycle = 0
            while True:
                # 找出当前周期可以调度的操作（入度为0且未调度）
                ready_ops = []
                for i in range(len(bb.ops)):
                    if in_degree[i] == 0 and op_schedule[i] == -1:
                        ready_ops.append(i)
                
                # 如果没有可调度的操作，退出循环
                if not ready_ops:
                    break
                
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
                    # 获取该资源类型的可用数量
                    available_resources = resource_remain[op_type]
                    # 最多调度available_resources个操作
                    for i in range(min(available_resources, len(ops))):
                        op_idx = ops[i]
                        op_schedule[op_idx] = current_cycle
                        scheduled_this_cycle.append(op_idx)
                        
                        # 更新依赖于当前操作的操作的入度
                        if op_idx in bb.dfg:
                            for dst in bb.dfg[op_idx]:
                                in_degree[dst] -= 1
                        
                        # 更新资源状态
                        resource_remain[op_type] -= 1
                
                # 如果没有操作被调度，退出循环
                if not scheduled_this_cycle:
                    break
                
                # 进入下一个周期
                current_cycle += 1
                
                # 重置资源状态
                for op_type in range(len(resource)):
                    resource_remain[op_type] = resource[op_type]
            
            # 处理跳转指令（OP_BR）
            for i, op in enumerate(bb.ops):
                if op[1] == 7:  # OP_BR
                    # 找到基本块中所有其他操作的最大完成时间
                    max_other_finish = 0
                    for j in range(len(bb.ops)):
                        if j != i and op_schedule[j] != -1:
                            max_other_finish = max(max_other_finish, op_schedule[j] + delay[bb.ops[j][1]])
                    
                    # 确保跳转指令在所有其他操作完成后执行
                    op_schedule[i] = max(op_schedule[i], max_other_finish)
            
            # 将调度结果转换为周期列表格式
            cycle_list = []
            max_cycle = max(op_schedule.values()) if op_schedule else 0
            
            # 初始化周期列表
            for _ in range(max_cycle + 1):
                cycle_list.append([])
            
            # 将操作分配到对应的周期
            for op_idx, cycle in op_schedule.items():
                if cycle != -1:
                    cycle_list[cycle].append(op_idx)
            
            # 为每个操作分配资源
            final_cycles = []
            for cycle in range(len(cycle_list)):
                final_cycles.append([])
                
                # 重置资源状态
                resource_remain = {}
                for op_type in range(len(resource)):
                    resource_remain[op_type] = resource[op_type]  # 初始化为资源总数
                
                # 为每个操作分配资源
                for op_idx in cycle_list[cycle]:
                    op_type = bb.ops[op_idx][1]
                    # 计算设备索引：资源总数减去调度前的当前资源数
                    device_idx = resource[op_type] - resource_remain[op_type]
                    # 更新资源状态
                    resource_remain[op_type] -= 1
                    # 添加到最终调度结果
                    final_cycles[cycle].append((op_idx, device_idx))
            
            schedule_result[bb_label] = final_cycles
        
        self.schedule = schedule_result
        return schedule_result
    
    # 将schedule_asap方法添加到cdfg类
    setattr(cdfg_class, 'schedule', {})
    setattr(cdfg_class, 'schedule_asap', schedule_asap)

# 将调度方法添加到cdfg类
add_scheduling_to_cdfg(cdfg)

if __name__ == "__main__":
    cdfg_obj = parse_llvm_to_cdfg("parse_result")
    cdfg_obj.build_cfg()
    cdfg_obj.build_dfg()
    schedule = cdfg_obj.schedule_asap()
    for label, bb_schedule in schedule.items():
        print(label," 块的调度结果：")
        for cycle, ops in enumerate(bb_schedule):
            print(f"周期 {cycle}: {ops}")

                        

                

        
        
        


            
            
            


    
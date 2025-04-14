import cdfg_generator

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





def schedule_asap(self, resource, delay):
    schedule = []
    resource_remain = resource[:]
    cfg = self.cfg
    for label, bb in cfg.items():
        bb_schedule = []
        in_degree = [0] * len(bb.ops)
        visited = [False] * len(bb.ops)
        for i in range(len(bb.ops)):
            for j in bb.dfg[i]:
                in_degree[j] += 1
        ready_ops = [i for i, d in enumerate(in_degree) if d == 0 and not visited[i]]
        time_remain = [0] * len(bb.ops)
        while ready_ops:
            cycle_schedule = []
            # 正在执行的进程向下推进，执行完成后释放资源
            for op in ready_ops:
                if time_remain[op] > 0:
                    time_remain[op] -= 1
                    if time_remain[op] == 0:
                        resource_remain[op] += 1
    
            # 选择可以执行的进程
            for op in ready_ops:
                if resource_remain[op] > 0:
                    cycle_schedule.append(op)
                    visited[op] = True
                    resource_remain[op] -= 1
                    time_remain[op] = delay[op]
                    for j in bb.dfg[op]:
                        in_degree[j] -= 1
                        if in_degree[j] == 0 and not visited[j]:
                            ready_ops.append(j)
            bb_schedule.append(cycle_schedule)
        schedule[label] = bb_schedule
    return schedule
            
            
            


    
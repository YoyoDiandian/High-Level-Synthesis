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
    2, # OP_PHI
    1, # OP_RET
]

# 定义延迟
delay = [
    1, # OP_ASSIGN
    1, # OP_ADD
    1, # OP_SUB
    1, # OP_MUL
    1, # OP_DIV
    2, # OP_LOAD
    1, # OP_STORE
    1, # OP_BR
    1, # OP_LT
    1, # OP_GT
    1, # OP_LE
    1, # OP_GE
    1, # OP_EQ
    2, # OP_PHI
    1, # OP_RET
]

def schedule_asap(self):
    schedule_result = {}
    # 按控制图顺序处理各基本块
    for bb_label, bb in self.cfg.items():
        bb_schedule = []
        #入度计算
        in_degree = {}
        for i in range(len(bb.ops)):
            in_degree[i] = 0

        for src, dsts in bb.dfg.items():
            for dst in dsts:
                in_degree[dst] += 1
        print(bb_label," : ",in_degree)
        # 每个指令的剩余时间
        time_remain = [0] * len(bb.ops)
        # 每个指令在占用的该类型计算单元索引
        device_occupied = [-1] * len(bb.ops)
        # 每个类型计算单元每个实例的占用情况
        occupation = [None] * len(resource)
        for i in range(len(resource)):
            occupation[i] = [0] * resource[i]
        # 尚未执行完毕的指令
        unfinished = list(range(len(bb.ops)))
        sent = []
        print("Unfinished:", unfinished)
        # 待调度的队列
        ready = []
        while unfinished:
            cycle_schedule = []
            for i in range(len(bb.ops)):
            # 处理正在执行的操作，若执行完毕，释放该类型指定索引的计算单元，降低后继节点的入度
                if time_remain[i] > 0:
                    # 计时器递减
                    time_remain[i] -= 1 
                    if time_remain[i] == 0:
                        # 释放资源
                        occupation[bb.ops[i][1]][device_occupied[i]] = 0
                        device_occupied[i] = -1
                        # 完成操作
                        print(unfinished,i)
                        unfinished.remove(i)
                        # 削减入度
                        dsts = bb.dfg[i]
                        for dst in dsts:
                            in_degree[dst] -= 1
            # 引入新的可以调度的操作
            for i in range(len(bb.ops)):
                if i not in sent and in_degree[i]==0:
                    ready.append(i)
                    sent.append(i)
            print("ready:",ready)
            removal_list = []
            for i in ready:
                print("trying to schedule:",i)
            # 检查该类型计算单元的每一个实例
                for pos in range(len(occupation[bb.ops[i][1]])):
                    if occupation[bb.ops[i][1]][pos] == 0:
                        print("successfully scheduling:",i)
                        # 若用空闲实例，则调度并占用资源
                        cycle_schedule.append((i,pos))
                        # 占用资源
                        occupation[bb.ops[i][1]][pos] = 1
                        device_occupied[i] = pos
                        # 从待调度队列中移除操作
                        removal_list.append(i)
                        # 设定计时器
                        time_remain[i] = delay[bb.ops[i][1]]
                        break
            print("time remaining", time_remain)
            for i in removal_list:
                ready.remove(i)
            bb_schedule.append(cycle_schedule)
        schedule_result[bb_label] = bb_schedule
    return schedule_result

cdfg.schedule_asap = schedule_asap

if __name__ == "__main__":
    cdfg_obj = parse_llvm_to_cdfg("parse_result")
    cdfg_obj.build_cfg()
    cdfg_obj.build_dfg()
    schedule = cdfg_obj.schedule_asap()
    for i in cdfg_obj.cfg:
        #print(cdfg_obj.cfg[i].dfg)
        print(i,schedule[i])

            


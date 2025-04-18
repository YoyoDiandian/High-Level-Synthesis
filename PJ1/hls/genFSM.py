from cdfgGenerator import BasicBlock
from cdfgGenerator import CDFG

from scheduler import * 

# 操作类型常量定义 - 与scheduler.py中保持一致
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

# 计算资源定义 - 与scheduler.py中保持一致
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

# 延迟定义 - 与scheduler.py中保持一致
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

op_type = None

class VerilogFSMGenerator:
    def __init__(self, schedule, register_allocation, cdfg):
        """
        初始化 Verilog FSM 生成器
        :param schedule: 调度结果，格式为 {time_step: [(operation, operands, destination)]}
        :param register_allocation: 寄存器分配结果，格式为 {variable: register}
        """
        self.schedule = schedule
        self.register_allocation = register_allocation
        self.cdfg = cdfg

    def gen_module_IO(self):
        pass
    
    def gen_always_logic(self):
        pass

    def gen_if_logic(self):
        pass
    
    def gen_else_if_logic(self):
        pass

    def gen_else_logic(self):
        pass

    def gen_begin_logic(self):
        pass

    def gen_end_logic(self):
        pass

    def op_translation(self):
        match op_type:
            case x if x == OP_ASSIGN:
                print("OP_ASSIGN")
            case x if x == OP_ADD:
                pass
            case x if x == OP_SUB:
                pass
            case x if x == OP_MUL:
                pass
            case x if x == OP_DIV:
                pass
            case x if x == OP_LOAD:
                pass
            case x if x == OP_STORE:
                pass
            case x if x == OP_BR:
                pass
            case x if x == OP_LT:
                pass
            case x if x == OP_GT:
                pass
            case x if x == OP_LE:
                pass                        
            case x if x == OP_GE:
                pass                
            case x if x == OP_EQ:
                pass
            case x if x == OP_PHI:
                pass
            case x if x == OP_RET:
                pass

    def gen_fsm(self):
        pass

    def gen_counter(self):
        pass

    def gen_per_period(self):
        pass

    def output_verilog(self):
        pass


# 示例输入
if __name__ == "__main__":
    # 调度结果示例
    schedule = {
        1: [("ADD", ["a", "b"], "t1"), ("MUL", ["c", "d"], "t2")],
        2: [("SUB", ["t1", "t2"], "t3")],
        3: [("DIV", ["t3", "e"], "result")],
        4: []
    }

    # 寄存器分配示例
    register_allocation = {
        "a": "R1",
        "b": "R2",
        "c": "R3",
        "d": "R4",
        "e": "R5",
        "t1": "R6",
        "t2": "R7",
        "t3": "R8",
        "result": "R9"
    }


    cdfg = CDFG()
    # 生成 Verilog 文件
    verilog_generator = VerilogFSMGenerator(schedule, register_allocation, cdfg)
    verilog_generator.output_verilog()
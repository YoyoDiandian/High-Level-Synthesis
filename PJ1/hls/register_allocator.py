from scheduler import *


def get_bb_operands(self):
    operands = set()
    for op in self.ops:
        if op[1] == 13:
            operands = operands | set(op[2::2])
        elif op[1] == 5 or op[1] == 6:
            operands = operands | set(op[3:])
        elif op[1] == 7:
            if len(op) > 3:
               operands.add(op[2])
        else:
            operands = operands | set(op[2:])
    return operands

def get_bb_left_values(self):
    left_values = set()
    for op in self.ops:
        if op[0]:
            left_values.add(op[0])

    return left_values

def get_input_output_variables(self):
    param_list = []
    for param in self.params:
        param_list.append(param[0])
    input_variables = {}
    output_variables = {}
    require_variables = {}
    visited = {}
    for bb in self.cfg:
        visited[bb] = 0
        input_variables[bb] = set()
        require_variables[bb] = self.cfg[bb].get_bb_operands()-self.cfg[bb].get_bb_left_values()
    bb_queue = ['0']
    visited['0'] = 1
    while bb_queue:
        bb = bb_queue.pop(0)
        output_variables[bb] = (input_variables[bb] | self.cfg[bb].get_bb_left_values())-self.cfg[bb].get_bb_operands()
        for edge in self.cfg_adj_list[bb]:
            next_bb = edge[0]
            input_variables[next_bb] = input_variables[next_bb]|output_variables[bb]
            if visited[next_bb] == 0:
                visited[next_bb] = 1
                bb_queue.append(next_bb)

    for label, variable_set in input_variables.items():
        removal_list = []
        for v in variable_set:
            if (v in param_list) or v.isdigit():
                removal_list.append(v)
        for v in removal_list:
            input_variables[label].remove(v)

    for label, variable_set in output_variables.items():
        removal_list = []
        for v in variable_set:
            if (v in param_list) or v.isdigit():
                removal_list.append(v)
        for v in removal_list:
            output_variables[label].remove(v)

    

    return input_variables, output_variables

def get_global_variables(self):
    global_variable_set = set()
    for param in self.params:
        if param[1] == 'non-array':
            global_variable_set.add(param[0])
    bb_operands_list = []
    for bb in self.cfg.values():
        bb_operands_list.append(bb.get_bb_operands())
    L = len(bb_operands_list)
    for i in range(L):
        for j in range(i+1,L):
            global_variable_set = global_variable_set | (bb_operands_list[i]&bb_operands_list[j])
    removal_list = []
    for v in global_variable_set:
        if v.isdigit():
            removal_list.append(v)
    for v in removal_list:
        global_variable_set.remove(v)
    return global_variable_set

    

basic_block.get_bb_operands = get_bb_operands
basic_block.get_bb_left_values = get_bb_left_values
cdfg.get_input_output_variables = get_input_output_variables
cdfg.get_global_variables = get_global_variables









if __name__ == "__main__":
    cdfg_obj = parse_llvm_to_cdfg("parse_result")
    cdfg_obj.build_cfg()
    cdfg_obj.build_dfg()
    schedule = cdfg_obj.schedule_asap()
    input_variables, output_variables = cdfg_obj.get_input_output_variables()
    print("Input variables:",input_variables)
    print("Output variables:",output_variables)
    global_variable_set = cdfg_obj.get_global_variables()
    print("Global Variables:", global_variable_set)
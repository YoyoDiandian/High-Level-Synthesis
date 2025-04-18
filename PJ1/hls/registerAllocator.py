from scheduler import scheduleASAP, printSchedule, addScheduler
from cdfgGenerator import BasicBlock, CDFG
import sys

def get_op_operands(op):
    op_type = op[1]
    if op_type == 13: # phi操作
        operands = set(op[2::2])
    elif op_type == 5 or op_type == 6: # 存取操作
        operands = set(op[3:])
    elif op_type == 7: # 跳转操作
        if len(op) > 3: # 有条件跳转
            operands = {op[2]}
        else:
            operands = set()
    else:
        operands = set(op[2:])
    return operands

def get_op_left_values(op):
    return op[0]

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
    param_list = [param[0] for param in self.params]
    # for param in self.params:
    #     param_list.append(param[0])
    input_variables = {}
    output_variables = {}
    require_variables = {}
    visited = {}

    for bb in self.basicBlocks:
        visited[bb] = 0
        input_variables[bb] = set()
        require_variables[bb] = self.basicBlocks[bb].get_bb_operands()-self.basicBlocks[bb].get_bb_left_values()
    bb_queue = ['0']
    visited['0'] = 1
    while bb_queue:
        bb = bb_queue.pop(0)
        output_variables[bb] = (input_variables[bb] | self.basicBlocks[bb].get_bb_left_values())-self.basicBlocks[bb].get_bb_operands()
        for edge in self.cfg.successors(bb):
            next_bb = edge
            input_variables[next_bb] = input_variables[next_bb] | output_variables[bb]
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
    for bb in self.basicBlocks.values():
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

def get_local_variable_liveness(self):
    # print("Getting Local Variable Liveness:")
    live_local_variables = {}

    input_variables, output_variables = self.get_input_output_variables()
    global_variable_set = self.get_global_variables()

    self.scheduleASAP()
    # if not self.schedule:
    #     raise ValueError("Schedule is not generated. Ensure that scheduleASAP() is called and works correctly.")
    
    for bb_label, bb in self.basicBlocks.items():
        bb_live_local_variables = []
        
        cycle_live_local_variables = input_variables.get(bb_label, set()) - global_variable_set
        bb_live_local_variables.append(cycle_live_local_variables)
        for cycle in range(len(self.schedule[bb_label])):
            ops = self.schedule[bb_label][cycle]
            cycle_operands = set()
            cycle_left_values = set()
            for op, _ in ops:
                operands = get_op_operands(bb.ops[op])
                if operands:
                    cycle_operands = cycle_operands | operands
                left_value = get_op_left_values(bb.ops[op])
                if left_value:
                    cycle_left_values = cycle_left_values | {left_value}
            if cycle_left_values:
                cycle_live_local_variables = (((cycle_live_local_variables - (cycle_operands-output_variables[bb_label])))|cycle_left_values) - global_variable_set
            else:
                cycle_live_local_variables = ((cycle_live_local_variables - (cycle_operands-output_variables[bb_label]))) - global_variable_set

            bb_live_local_variables.append(cycle_live_local_variables)
        live_local_variables[bb_label] = bb_live_local_variables
        # print(bb_label,":",bb_live_local_variables)

        # print(f"Basic block {bb_label}:")
    # print(35 * "-")
    # print(live_local_variables)
    return live_local_variables

def get_living_period(self):
    live_local_variables = self.get_local_variable_liveness()
    # print("Getting Living Period:")
    living_period = {}
    for bb_label, bb in self.basicBlocks.items():
        bb_live_local_variables = live_local_variables[bb_label]
        bb_live_period = {}
        for i, cycle in enumerate(bb_live_local_variables):
            for v in cycle:
                if v not in bb_live_period:
                    bb_live_period[v] = [i,i]
                else:
                    bb_live_period[v][1] = i
        living_period[bb_label]=bb_live_period
        # print(bb_label, ":", bb_live_period)
        # print(f"Basic block {bb_label}")
    # print(35 * "-")
    return living_period

def register_coloring(self):
    # 获取变量生存周期
    living_period = self.get_living_period()
    coloring_result = {}
    # print("Coloring Registers:")
    # print("Coloring Result BEFORE Aligning:")

    for bb_label, bb in self.basicBlocks.items():
        bb_coloring_result ={}
        # 将该块内局部变量初始化为未染色
        uncolored = list(living_period[bb_label].keys())
        uncolored.sort(key = lambda x:(living_period[bb_label][x][0],(living_period[bb_label][x][1]-living_period[bb_label][x][0]),x))

        color = 0
        while uncolored:
            colored_var_list = []
            right_edge = -1
            for v in uncolored:
                if living_period[bb_label][v][0] > right_edge:
                    # 在该颜色的列表中加上该变量及其存活周期
                    colored_var_list.append((v,living_period[bb_label][v]))
                    # 更新右边沿
                    right_edge = living_period[bb_label][v][1]
            bb_coloring_result[color] = colored_var_list
            color += 1
            for v,_ in colored_var_list:
                # 更新染色状态
                uncolored.remove(v)
        coloring_result[bb_label] = bb_coloring_result
        #print(bb_label,":",bb_coloring_result)

    min_register_required = 0
    for bb_label in self.cfg:
        min_register_required = max(len(coloring_result[bb_label]),min_register_required)
    for bb_label in self.cfg:
        if min_register_required > len(coloring_result[bb_label]):
            for reg in range(len(coloring_result[bb_label]),min_register_required):
                coloring_result[bb_label][reg] = []
    # for bb_label in self.cfg:
    #     print(bb_label,":",coloring_result[bb_label])
    # print(35 * "-")
    
    input_variables, output_variables = self.get_input_output_variables()
    global_variables = self.get_global_variables()
    # cfg_adj_list = self.cfg
    # for src_label in cfg_adj_list:
    #     for sink_label, _ in cfg_adj_list[src_label]:
    for src_label, sink_label, _ in self.cfg.edges(data=True):
        src_coloring = coloring_result[src_label]
        sink_coloring = coloring_result[sink_label]
        #print(src_label,sink_label,":")

        checklist = list((output_variables[src_label] & input_variables[sink_label]) - global_variables)
        var_check_liveness = {}
        for var_check in checklist:
            for reg in src_coloring.values():
                if reg:
                    if reg[-1][0] == var_check:
                        var_check_liveness[var_check] = reg[-1][-1][-1]-reg[-1][-1][0]
        checklist.sort(key=lambda x:(-var_check_liveness[x]))

        #print(checklist)
        src_reg = -1
        sink_reg = -1
        for var_check in checklist:
            flag = 0
            for reg, var_list in src_coloring.items():
                if var_list:
                    if var_list[-1][0] == var_check:
                        src_reg = reg
                        flag = 1
                        break
                if flag:
                    break
            flag = 0
            for reg, var_list in sink_coloring.items():
                if var_list:
                    if var_list[0][0] == var_check:
                        sink_reg = reg
                        flag = 1
                        break
                if flag:
                    break
            if src_reg == sink_reg:
                continue
            else:
                settled = 0
                src_var = src_coloring[src_reg][-1]
                if src_coloring[sink_reg]:
                    right_edge = src_coloring[sink_reg][-1][-1][-1]
                else:
                    right_edge = -1
                if src_var[-1][0] > right_edge:
                    src_coloring[sink_reg].append(src_var)
                    src_coloring[src_reg].pop()
                    settled = 1
                if not settled:
                    if (len(src_coloring[src_reg])>1):
                        src_right_edge = src_coloring[src_reg][-2][-1][-1]
                    else:
                        src_right_edge = -1
                    if (len(src_coloring[sink_reg])>1):
                        sink_right_edge = src_coloring[sink_reg][-2][-1][-1]
                    else:
                        sink_right_edge = -1
                    if src_coloring[sink_reg][-1][-1][0] > src_right_edge and src_var[-1][0] > sink_right_edge:
                        temp0 = src_coloring[src_reg].pop()
                        temp1 = src_coloring[sink_reg].pop()
                        src_coloring[src_reg].append(temp1)
                        src_coloring[sink_reg].append(temp0)
                        settled = 1

                if not settled:
                    sink_var = sink_coloring[sink_reg][0]
                    if sink_coloring[src_reg]:
                        left_edge = sink_coloring[src_reg][0][-1][0]
                    else:
                        left_edge = sys.maxsize
                    if sink_var[-1][1] < left_edge:
                        sink_coloring[src_reg].insert(0,sink_var)
                        settled = 1
                '''
                if not settled:
                    if (len(sink_coloring[sink_reg])>1):
                        sink_left_edge = sink_coloring[sink_reg][1][-1][0]
                    else:
                        sink_left_edge = sys.maxsize
                    if (len(sink_coloring[src_reg])>1):
                        src_left_edge = sink_coloring[src_reg][1][-1][0]
                    else:
                        src_left_edge = sys.maxsize
                    if sink_coloring[src_reg][0][-1][-1] < sink_left_edge and sink_var[-1][-1] < src_left_edge: # type: ignore
                        temp0 = sink_coloring[src_reg].pop(0)
                        temp1 = sink_coloring[sink_reg].pop(0)
                        sink_coloring[src_reg].insert(0,temp1)
                        sink_coloring[sink_reg].insert(0,temp0)
                        settled = 1
                '''

                if not settled:
                    sink_var = sink_coloring[sink_reg][0]
                    for i in range(0,min_register_required):
                        if src_coloring[i]:
                            src_right_edge = src_coloring[i][-1][-1][-1]
                        else:
                            src_right_edge = -1
                        if sink_coloring[i]:
                            sink_left_edge = sink_coloring[i][0][-1][0]
                        else:
                            sink_left_edge = sys.maxsize
                        if src_var[-1][0] > src_right_edge and sink_var[-1][-1] < sink_left_edge:
                            src_coloring[src_reg].pop()
                            sink_coloring[sink_reg].pop(0)
                        if src_var[-1][0] > src_right_edge and sink_var[-1][-1] < sink_left_edge: # type: ignore
                            src_coloring[i].append(src_var)
                            sink_coloring[i].insert(0,sink_var)

                            settled = 1
                    if not settled:
                        src_coloring[src_reg].pop()
                        sink_coloring[sink_reg].pop(0)
                        src_coloring[min_register_required]=[src_var]
                        sink_coloring[min_register_required]=[sink_var]
                        min_register_required += 1
                        for bb_label in self.cfg:
                            if min_register_required > len(coloring_result[bb_label]):
                                for reg in range(len(coloring_result[bb_label]),min_register_required):
                                    coloring_result[bb_label][reg] = []
    # print("Coloring Result AFTER Aligning")
    # for bb_label in self.cfg:
    #     print(bb_label,":",coloring_result[bb_label])    
    # print(35 * "-")     
    return coloring_result
    

def printInputVariables(input_variables, file=None):
    """
        Print input variables information.
    """
    # print(35 * "-")
    print("Input variables:", file=file)
    # print(input_variables)
    for block_label, variables in input_variables.items():
        print(f"Basic block {block_label}:", file=file)
        if not variables:
            print(f"No input variables in this block.", end="  ", file=file)
        else:
            for variable in variables:
                print(f"{variable}", end="  ", file=file)
        print(file=file)
    print(35 * "-", file=file)

def printOutputVariables(output_variables, file=None):
    """
        Print output variables information.
    """
    print("Output variables:", file=file)
    # print(output_variables)
    for block_label, variables in output_variables.items():
        print(f"Basic block {block_label}:", file=file)
        if not variables:
            print(f"No output variables in this block.", end="  ", file=file)
        else:
            for variable in variables:
                print(f"{variable}", end="  ", file=file)
        print(file=file)
    print(35 * "-", file=file)

def printGlobalVariables(global_variable_set, file=None):
    """
        Print global variables information.
    """
    print("Global Variables:", file=file)
    # print(global_variable_set)
    if global_variable_set:
        print("  ".join(global_variable_set), file=file)
    else:
        print("No global variables", file=file)
    print(35 * "-", file=file)

def printLocalVariablesLivenessCycle(live_local_variables, file=None):
    """
        Print local variable liveness, in cycle order.
    """
    print("Getting Local Variable Liveness:", file=file)
    # print(live_local_variables)
    for bb_label, bb_live_local_variables in live_local_variables.items():
        print(f"Basic block {bb_label}: ", file=file)
        # print(bb_live_local_variables, file=file)
        for cycle, variable in enumerate(bb_live_local_variables):
            result = ', '.join(variable)
            if not result:
                print(f"  cycle {cycle}, there's no variable living in this cycle.", file=file)
            else:
                print(f"  cycle {cycle}, variable\t{result}\tis living.", file=file)
    print(35 * "-", file=file)
    # print(live_local_variables, file=file)

def printLocalVariablesLivenessVariable(living_period, file=None):
    """
        Print local variable liveness, in variable order.
    """
    print("Getting Living Period for every local variable:", file=file)
    # print(living_period)
    for bb_label, bb_variable_liveness in living_period.items():
        print(f"Basic block {bb_label}: ", file=file)
        if not bb_variable_liveness:
            print(f"  No variable living in this basic block.")
        else:
            for variable, var_living_period in bb_variable_liveness.items():
                print(f"  Variable\t{variable}\tlives from cycle {var_living_period[0]} to cycle {var_living_period[1]}", file=file)
    print(35 * "-", file=file)

def printRegisterColoring(coloring_result, file=None):
    """
        Print register allocation result after aligning, using left-edge algorithm.    
    """
    print("Coloring Register by using Left-Edge Algorithm, after Aligning:", file=file)
    # print(coloring_result)
    for bb_label, bb_reg_dict in coloring_result.items():
        print(f"Basic block {bb_label}: ", file=file)
        for bb_reg_index, bb_reg_allocation in bb_reg_dict.items():
            print(f"  Register {bb_reg_index}:", file=file)
            for bb_reg_allocation_items in bb_reg_allocation:
                start_cycle = bb_reg_allocation_items[1][0]
                end_cycle = bb_reg_allocation_items[1][1]
                print(f"    stores variable\t{bb_reg_allocation_items[0]}\tfrom cycle {start_cycle} to cycle {end_cycle}", file=file)
    
    print(35 * "-", file=file)

def addRegisterAllocation(cdfg_obj, basic_block_obj):
    setattr(basic_block_obj, 'get_bb_operands', {})
    setattr(basic_block_obj, 'get_bb_operands', get_bb_operands)
    setattr(basic_block_obj, 'get_bb_left_values', {})
    setattr(basic_block_obj, 'get_bb_left_values', get_bb_left_values)
    setattr(cdfg_obj, 'get_input_output_variables', {})
    setattr(cdfg_obj, 'get_input_output_variables', get_input_output_variables)
    setattr(cdfg_obj, 'get_global_variables', {})
    setattr(cdfg_obj, 'get_global_variables', get_global_variables)
    setattr(cdfg_obj, 'get_local_variable_liveness', {})
    setattr(cdfg_obj, 'get_local_variable_liveness', get_local_variable_liveness)
    setattr(cdfg_obj, 'get_living_period', {})
    setattr(cdfg_obj, 'get_living_period', get_living_period)
    setattr(cdfg_obj, 'register_coloring', {})
    setattr(cdfg_obj, 'register_coloring', register_coloring)


if __name__ == "__main__":
    cdfg = CDFG()
    cdfg.llvmParser("parse_result")

    cdfg.generateCFG()
    cdfg.generateDFGs()

    addScheduler(CDFG)
    cdfg.scheduleASAP()
    printSchedule(cdfg.schedule)

    addRegisterAllocation(CDFG, BasicBlock)

    input_variables, output_variables = cdfg.get_input_output_variables()
    printInputVariables(input_variables=input_variables)
    printOutputVariables(output_variables=output_variables)
    
    global_variable_set = cdfg.get_global_variables()
    printGlobalVariables(global_variable_set=global_variable_set)

    live_local_variables = cdfg.get_local_variable_liveness()
    printLocalVariablesLivenessCycle(live_local_variables=live_local_variables)

    living_period = cdfg.get_living_period()
    printLocalVariablesLivenessVariable(living_period=living_period)
    
    coloring_result = cdfg.register_coloring()
    printRegisterColoring(coloring_result=coloring_result)
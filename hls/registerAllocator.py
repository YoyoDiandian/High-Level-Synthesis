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
    self.input_variables = {}
    self.output_variables = {}
    require_variables = {}
    visited = {}

    for bb in self.basicBlocks:
        visited[bb] = 0
        self.input_variables[bb] = set()
        require_variables[bb] = self.basicBlocks[bb].get_bb_operands()-self.basicBlocks[bb].get_bb_left_values()
    bb_queue = ['0']
    visited['0'] = 1
    while bb_queue:
        bb = bb_queue.pop(0)
        self.output_variables[bb] = (self.input_variables[bb] | self.basicBlocks[bb].get_bb_left_values())-self.basicBlocks[bb].get_bb_operands()
        for edge in self.cfg.successors(bb):
            next_bb = edge
            if self.cfg.successors(next_bb):
                self.input_variables[next_bb] = self.input_variables[next_bb] | self.output_variables[bb]
            else:
                self.input_variables[next_bb] = require_variables[next_bb]
            if visited[next_bb] == 0:
                visited[next_bb] = 1
                bb_queue.append(next_bb)

    for label, variable_set in self.input_variables.items():
        removal_list = []
        for v in variable_set:
            if (v in param_list) or v.isdigit():
                removal_list.append(v)
        for v in removal_list:
            self.input_variables[label].remove(v)

    for label, variable_set in self.output_variables.items():
        removal_list = []
        for v in variable_set:
            if (v in param_list) or v.isdigit():
                removal_list.append(v)
        for v in removal_list:
            self.output_variables[label].remove(v)

def get_global_variables(self):
    self.global_variable = set()
    bb_operands_list = []
    for bb in self.basicBlocks.values():
        bb_operands_list.append(bb.get_bb_operands())
    L = len(bb_operands_list)
    for i in range(L):
        for j in range(i+1,L):
            self.global_variable = self.global_variable | (bb_operands_list[i]&bb_operands_list[j])
    removal_list = []
    for v in self.global_variable:
        if v.isdigit():
            removal_list.append(v)
    for v in removal_list:
        self.global_variable.remove(v)
    for param in self.params:
        if param[1] == 'non-array':
            self.global_variable = self.global_variable - {param[0]}

def get_local_variable_liveness(self):
    self.live_local_variables = {}

    for bb_label, bb in self.basicBlocks.items():
        bb_live_local_variables = []
        cycle_live_local_variables = self.output_variables[bb_label] - self.global_variable
        bb_live_local_variables.insert(0, cycle_live_local_variables)

        for cycle in range(len(self.schedule[bb_label])-1, -1, -1):
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

            if cycle_operands:
                cycle_live_local_variables = (cycle_live_local_variables-cycle_left_values)|cycle_operands - self.global_variable
            else:
                cycle_live_local_variables = (cycle_live_local_variables-cycle_left_values) - self.global_variable

            removal_set = set()

            for v in cycle_live_local_variables:
                if v.isdigit():
                    removal_set.add(v)
            if removal_set:
                cycle_live_local_variables = cycle_live_local_variables - removal_set
            bb_live_local_variables.insert(0,cycle_live_local_variables)

        self.live_local_variables[bb_label] = bb_live_local_variables
        print(bb_label, ":", bb_live_local_variables)

def get_living_period(self):
    self.living_period = {}
    for bb_label, bb in self.basicBlocks.items():
        bb_live_local_variables = self.live_local_variables[bb_label]
        bb_live_period = {}
        for i, cycle in enumerate(bb_live_local_variables):
            for v in cycle:
                if v not in bb_live_period:
                    bb_live_period[v] = [i,i]
                else:
                    bb_live_period[v][1] = i
        self.living_period[bb_label]=bb_live_period

def get_block_length(self):
    self.block_length = {}
    for key in self.schedule:
        self.block_length[key] = len(self.schedule[key])

def register_coloring(self):
    self.coloring_result = {}

    for bb_label, bb in self.basicBlocks.items():
        bb_coloring_result ={}
        # 将该块内局部变量初始化为未染色
        uncolored = list(self.living_period[bb_label].keys())
        uncolored.sort(key = lambda x:(self.living_period[bb_label][x][0],(self.living_period[bb_label][x][1]-self.living_period[bb_label][x][0]),x))

        color = 0
        while uncolored:
            colored_var_list = []
            right_edge = -1
            for v in uncolored:
                if self.living_period[bb_label][v][0] > right_edge:
                    # 在该颜色的列表中加上该变量及其存活周期
                    colored_var_list.append((v,self.living_period[bb_label][v]))
                    # 更新右边沿
                    right_edge = self.living_period[bb_label][v][1]
            bb_coloring_result[color] = colored_var_list
            color += 1
            for v,_ in colored_var_list:
                # 更新染色状态
                uncolored.remove(v)
        self.coloring_result[bb_label] = bb_coloring_result
        #print(bb_label,":",bb_coloring_result)

    min_register_required = 0
    for bb_label in self.cfg:
        min_register_required = max(len(self.coloring_result[bb_label]),min_register_required)
    for bb_label in self.cfg:
        if min_register_required > len(self.coloring_result[bb_label]):
            for reg in range(len(self.coloring_result[bb_label]),min_register_required):
                self.coloring_result[bb_label][reg] = []

    for src_label, sink_label, _ in self.cfg.edges(data=True):
        src_coloring = self.coloring_result[src_label]
        sink_coloring = self.coloring_result[sink_label]

        checklist = list((self.output_variables[src_label] & self.input_variables[sink_label]) - self.global_variable)
        var_check_liveness = {}
        for var_check in checklist:
            for reg in src_coloring.values():
                if reg:
                    if reg[-1][0] == var_check:
                        var_check_liveness[var_check] = reg[-1][-1][-1]-reg[-1][-1][0]
        checklist.sort(key=lambda x:(-var_check_liveness[x]))

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
                        src_right_edge = 0
                    if (len(src_coloring[sink_reg])>1):
                        sink_right_edge = src_coloring[sink_reg][-2][-1][-1]
                    else:
                        sink_right_edge = 0
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
                        sink_coloring[sink_reg].pop(0)
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
                            if min_register_required > len(self.coloring_result[bb_label]):
                                for reg in range(len(self.coloring_result[bb_label]),min_register_required):
                                    self.coloring_result[bb_label][reg] = []
   
def merge_registers(self):
    """
    合并没有时间重叠的寄存器，将高序号寄存器合并到低序号寄存器中
    
    参数:
        coloring_result: 原始的寄存器分配结果
        
    返回:
        merged_coloring_result: 合并后的寄存器分配结果
    """
    self.merged_coloring_result = {bb_label: {} for bb_label in self.coloring_result}
    # 初始化合并后的结果
    for bb_label in self.coloring_result:
        self.merged_coloring_result[bb_label] = dict(self.coloring_result[bb_label])
    
    # 构建变量到寄存器的映射
    var_to_reg = {} # {变量: {基本块: 寄存器号}}
    vars_reg = {}
    for bb_label, bb_coloring in self.coloring_result.items():
        for reg, var_list in bb_coloring.items():
            for var, period in var_list:
                if var not in var_to_reg:
                    var_to_reg[var] = {}
                var_to_reg[var][bb_label] = (reg, period)
                vars_reg[var] = reg

    while True:
        merged_variable = set()
         # 遍历每个局部变量
        continueMerge = False  # 这个变量代表在此次遍历变量的过程中是否产生了寄存器merge，如果产生了则说明coloring result产生了变化，可能有这一轮没被merge的寄存器在变化后能够被merge，因此需要再merge一次
        for var in var_to_reg:
            # 获取该变量在各个基本块中的寄存器分配情况
            bb_assignments = var_to_reg[var]
            currentRegister = vars_reg[var] # 当前变量所在的寄存器
            # 如果本来就在寄存器0，或者是已经被merge过的variable，则跳过
            if currentRegister == 0 or var in merged_variable:
                continue
            
            mergeTowards = [i for i in range(0, currentRegister)] # 候选的寄存器

            # 遍历这个变量在各个基本块中的寄存器及周期
            for bb_label, (reg, period) in bb_assignments.items():
                # 遍历这个基本块中的各个寄存器
                for compared_reg in self.merged_coloring_result[bb_label]:
                    # 如果这个寄存器的序号大于当前变量的寄存器，或者这个寄存器不在候选列表中，则跳过
                    if compared_reg >= currentRegister or compared_reg not in mergeTowards:
                        continue
                    # 遍历这个基本块中这个寄存器存储的各个变量
                    for compared_var, compared_period in self.merged_coloring_result[bb_label][compared_reg]:
                        # 检查是否有时间重叠，有则从候选列表中移除这个寄存器
                        if var != compared_var and not (period[1] < compared_period[0] or compared_period[1] < period[0]):
                            # 合并寄存器
                            mergeTowards.remove(compared_reg)
                            break
            
            # 候选列表中还有存活的寄存器
            if mergeTowards:
                continueMerge = True
                mergeTowardReg = mergeTowards.pop(0)
                # Remove from old register and add to new register
                # Update the var_to_reg mapping
                vars_reg[var] = mergeTowardReg
                for bb_label in bb_assignments:
                    var_to_reg[var][bb_label] = (mergeTowardReg, var_to_reg[var][bb_label][1])
                    # Find the variable's data in old register
                    var_index = None
                    for i, (var_item, _) in enumerate(self.merged_coloring_result[bb_label][currentRegister]):
                        if var_item == var:
                            var_index = i
                            break
                    
                    if var_index is not None:
                        # Move data to new register
                        var_data = self.merged_coloring_result[bb_label][currentRegister].pop(var_index)
                        if mergeTowardReg not in self.merged_coloring_result[bb_label]:
                            self.merged_coloring_result[bb_label][mergeTowardReg] = []
                        self.merged_coloring_result[bb_label][mergeTowardReg].append(var_data)
                
                merged_variable.add(var)
                continue            
        if not continueMerge:
            break
    
    # Remove empty registers
    for bb_label in self.merged_coloring_result:
        # Create new dict without empty registers
        non_empty = {reg: vars for reg, vars in self.merged_coloring_result[bb_label].items() if vars}
        
        # Reassign register numbers sequentially
        new_coloring = {}
        for new_reg, (old_reg, vars) in enumerate(sorted(non_empty.items())):
            new_coloring[new_reg] = vars
            
        self.merged_coloring_result[bb_label] = new_coloring

    # Ensure all basic blocks have same number of registers
    max_regs = max(len(bb_coloring) for bb_coloring in self.merged_coloring_result.values())
    for bb_label in self.merged_coloring_result:
        for reg in range(len(self.merged_coloring_result[bb_label]), max_regs):
            self.merged_coloring_result[bb_label][reg] = []
                # 将该变量的寄存器合并到目标寄存器

def printInputVariables(self, file=None):
    """
        Print input variables information.
    """
    # print(35 * "-")
    print("Input variables:", file=file)
    # print(input_variables)
    for block_label, variables in self.input_variables.items():
        print(f"Basic block {block_label}:", file=file)
        if not variables:
            print(f"No input variables in this block.", end="  ", file=file)
        else:
            for variable in variables:
                print(f"{variable}", end="  ", file=file)
        print(file=file)
    print(35 * "-", file=file)

def printOutputVariables(self, file=None):
    """
        Print output variables information.
    """
    print("Output variables:", file=file)
    # print(output_variables)
    for block_label, variables in self.output_variables.items():
        print(f"Basic block {block_label}:", file=file)
        if not variables:
            print(f"No output variables in this block.", end="  ", file=file)
        else:
            for variable in variables:
                print(f"{variable}", end="  ", file=file)
        print(file=file)
    print(35 * "-", file=file)

def printGlobalVariables(self, file=None):
    """
        Print global variables information.
    """
    print("Global Variables:", file=file)
    # print(global_variable_set)
    if self.global_variable:
        print("  ".join(self.global_variable), file=file)
    else:
        print("No global variables", file=file)
    print(35 * "-", file=file)

def printLocalVariablesLivenessCycle(self, file=None):
    """
        Print local variable liveness, in cycle order.
    """
    print("Getting Local Variable Liveness:", file=file)
    # print(live_local_variables)
    for bb_label, bb_live_local_variables in self.live_local_variables.items():
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

def printLocalVariablesLivenessVariable(self, file=None):
    """
        Print local variable liveness, in variable order.
    """
    print("Getting Living Period for every local variable:", file=file)
    # print(living_period)
    for bb_label, bb_variable_liveness in self.living_period.items():
        print(f"Basic block {bb_label}: ", file=file)
        if not bb_variable_liveness:
            print(f"  No variable living in this basic block.", file=file)
        else:
            for variable, var_living_period in bb_variable_liveness.items():
                print(f"  Variable\t{variable}\tlives from cycle {var_living_period[0]} to cycle {var_living_period[1]}", file=file)
    print(35 * "-", file=file)

def printRegisterColoring(self, file=None):
    """
        Print register allocation result after aligning, using left-edge algorithm.    
    """
    print("Register Allocation:", file=file)
    # print(coloring_result)
    for bb_label, bb_reg_dict in self.coloring_result.items():
        print(f"Basic block {bb_label}: ", file=file)
        for bb_reg_index, bb_reg_allocation in bb_reg_dict.items():
            print(f"  Register {bb_reg_index}:", file=file)
            for bb_reg_allocation_items in bb_reg_allocation:
                start_cycle = bb_reg_allocation_items[1][0]
                end_cycle = bb_reg_allocation_items[1][1]
                print(f"    stores variable\t{bb_reg_allocation_items[0]}\tfrom cycle {start_cycle} to cycle {end_cycle}", file=file)
    
    print(35 * "-", file=file)

def printRegisterMerging(self, file=None):
    """
        Print register allocation result after merging, using left-edge algorithm.    
    """
    print("Register Allocation After Merging:", file=file)
    # print(coloring_result)
    for bb_label, bb_reg_dict in self.merged_coloring_result.items():
        print(f"Basic block {bb_label}: ", file=file)
        for bb_reg_index, bb_reg_allocation in bb_reg_dict.items():
            print(f"  Register {bb_reg_index}:", file=file)
            for bb_reg_allocation_items in bb_reg_allocation:
                start_cycle = bb_reg_allocation_items[1][0]
                end_cycle = bb_reg_allocation_items[1][1]
                print(f"    stores variable\t{bb_reg_allocation_items[0]}\tfrom cycle {start_cycle} to cycle {end_cycle}", file=file)
    
    print(35 * "-", file=file)

def registerAllocation(cdfg_obj):
    get_input_output_variables(cdfg_obj)
    get_global_variables(cdfg_obj)
    get_local_variable_liveness(cdfg_obj)
    get_living_period(cdfg_obj)
    register_coloring(cdfg_obj)
    merge_registers(cdfg_obj)

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
    setattr(cdfg_obj, 'merge_registers', {})
    setattr(cdfg_obj, 'merge_registers', merge_registers)
    setattr(cdfg_obj, 'registerAllocation', {})
    setattr(cdfg_obj, 'registerAllocation', registerAllocation)

def registerAllocatorPrinter(self, file=None):
    print("===== Initial Register Allocation =====", file=file)
    printInputVariables(self, file)
    printOutputVariables(self, file)
    printGlobalVariables(self, file)
    printLocalVariablesLivenessCycle(self, file)
    printLocalVariablesLivenessVariable(self, file)
    printRegisterColoring(self, file)
    printRegisterMerging(self, file)
    print("\nRegister Usage Statistics:", file=file)
    print(f"Total registers needed: {len(self.merged_coloring_result['0']) + len(self.global_variable)}", file=file)
    print(f"Global registers needed: {len(self.global_variable)}", file=file)
    print(f"Local registers needed: {len(self.merged_coloring_result['0'])}", file=file)
    print("=====================================\n", file=file)
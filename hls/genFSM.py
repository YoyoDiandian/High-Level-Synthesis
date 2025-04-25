import resourceData

class VerilogSyntax:
    def __init__(self):
        """
        初始化 Verilog 语法工具类
        """
        pass

    @staticmethod
    def always_ff(clk_signal="sys_clk", rst_signal="sys_rst_n", negedge_rst=True):
        """
        生成时序逻辑的 always 块
        """
        rst_edge = "negedge" if negedge_rst else "posedge"
        return f"always @(posedge {clk_signal} or {rst_edge} {rst_signal}) begin"

    @staticmethod
    def if_else(condition, true_block, false_block=None):
        """
        生成 if-else 语句
        """
        code = f"if ({condition}) begin\n"
        code += f"{true_block}\n"
        if false_block:
            code += f"end else begin\n{false_block}\n"
        code += "end\n"
        return code

    @staticmethod
    def outer_case(case_variable, case_items):
        """
        生成 case 语句
        :param case_variable: case 的变量
        :param case_items: 字典，键为 case 条件，值为对应的代码块
        """
        code = f"case ({case_variable})\n"
        for case, block in case_items.items():
            code += f"\t{case}: begin\n\t\t{block}\n\tend\n"
        code += "endcase"
        return code
    
    @staticmethod
    def inner_case(case_variable, case_items):
        code = f"case ({case_variable})\n"
        for case, block in case_items.items():
            code += f"\t\t\t{case}: begin\n\t\t\t\t{block}\n\t\t\tend\n"
        code += "\t\tendcase"
        return code

    @staticmethod
    def assign(lhs, rhs):
        """
        生成连续赋值语句
        """
        return f"assign {lhs} = {rhs};\n"

    @staticmethod
    def reg_declaration(name, width=32):
        """
        生成寄存器声明
        """
        return f"reg [{width-1}:0] {name};\n"

    @staticmethod
    def wire_declaration(name, width=32):
        """
        生成线网声明
        """
        return f"wire [{width-1}:0] {name};\n"

    @staticmethod
    def module_header(module_name, ports):
        """
        生成模块头部
        :param module_name: 模块名称
        :param ports: 端口列表
        """
        ports_str = ",\n".join(ports)
        return f"module {module_name} (\n{ports_str}\n);\n"

    @staticmethod
    def module_footer():
        """
        生成模块结束
        """
        return "endmodule\n"

class VerilogGenerator:
    def __init__(self, cdfg, verilog_syntax):
        """
        初始化 Verilog 生成器
        """
        self.cdfg = cdfg
        self.verilog_syntax = verilog_syntax
        
        self.global_reg_num = 0
        self.local_reg_num = 0
        self.global_reg = []
        # self.return_reg = []
        self.cond_all = []
        self.cond_block = []
        self.reg_counter = []

        self.content_IO = []
        self.content_registers = []
        self.content_wire = []
        self.content_parameters = []
        self.content_timing_logic = []
        self.content_br_counter = []
        self.content_control_logic = []
        self.content_assign_logic = []
        self.content_end = []

    def gen_module_IO(self):
        """
        生成模块的输入输出端口
        """
        # content = "module " + self.cdfg.functionName + "("
        # self.content_IO.append(content)
        # self.content_IO.append(f"`timescale 1ns / 1ps")
        self.content_IO.append(f"module {self.cdfg.functionName} (")

        for variables in self.cdfg.params:
            variable_name, variable_type = variables
            if variable_type == 'array':
                self.content_registers.append(f"\treg [31:0] {variable_name}_mem [0:255];")
                # self.content_IO.append(f"\tinput\t[31:0] {variable_name}_q0,")
                # self.content_IO.append(f"\toutput\treg [31:0] {variable_name}_address0,")
                # self.content_IO.append(f"\toutput\treg [31:0] {variable_name}_ad0,")
                # self.content_IO.append(f"\toutput\treg {variable_name}_ce0,")
                # self.content_IO.append(f"\toutput\treg {variable_name}_we0,")
            elif variable_type == 'non-array':
                self.content_IO.append(f"\tinput\t[31:0] {variable_name},")
                
            
        if self.cdfg.retType == 'int':
            self.content_IO.append(f"\toutput\t[31:0] return_val,")

        self.content_IO.append(f"\tinput\tsys_clk,")
        self.content_IO.append(f"\tinput\tsys_rst_n")
        # self.content_IO.append(f"\tinput\tstart,")
        # self.content_IO.append(f"\toutput\treg idle,")
        # self.content_IO.append(f"\toutput\treg done")
        self.content_IO.append(f");")

    def gen_global_register(self):
        """
        生成全局寄存器变量
        """
        self.global_reg_num = len(self.cdfg.global_variable)
        for item in self.cdfg.global_variable:
            self.content_registers.append(f"\treg [31:0] reg_{item};")
            self.global_reg.append(f"{item}")
        # self.content_registers.append(f"\t")

    def gen_local_register(self):
        """
        生成局部寄存器变量
        """
        # calculating the number of local register
        key_to_count = '0'
        num_local_reg = len(self.cdfg.merged_coloring_result[key_to_count])
        self.local_reg_num = num_local_reg
        # print(type(num_local_reg))
        for i in range(num_local_reg):
            self.content_registers.append(f"\treg [31:0] reg_{i};")
        # self.content_registers.append(f"\t")

    def gen_state_register(self):
        num_state = len(self.cdfg.basicBlocks.keys())
        # print(self.cdfg.basicBlocks.keys())
        self.content_registers.append(f"\treg [{num_state-1}:0] cur_state;")
        self.content_registers.append(f"\treg [{num_state-1}:0] last_state;")
        # self.content_registers.append(f"\t")

    def gen_bb_parameter(self):
        """
        生成 Verilog 参数定义，使用独热码表示状态
        """
        # 获取基本块的键列表
        bb_keys = list(self.cdfg.basicBlocks.keys())
        # print(bb_keys)
        num_states = len(bb_keys)  # 独热码的位数

        for i, state in enumerate(bb_keys):
            # 生成独热码，右移 i 位
            one_hot_code = f"{num_states}'b" + ''.join(['1' if j == i else '0' for j in range(num_states)])
            # 添加 Verilog 参数定义
            self.content_parameters.append(f"\tparameter state_{state} = {one_hot_code};")
        # self.content_parameters.append(f"\t")

    def gen_other_register(self):
        self.content_registers.append(f"\treg branch_ready;")
        self.content_registers.append(f"\treg [31:0] counter;")
        self.content_registers.append(f"\treg [31:0] ret;")
        # self.content_parameters.append(f"\t")

    def gen_wire(self):
        # self.content_wire.append(f"\twire cond;")
        # self.content_wire.append(f"\t")
        pass

    def gen_comb_logic(self):
        pass

    def gen_timing_logic(self):
        """
        生成时序逻辑
        """

        reg_init = []
        
        # 分配寄存器的初始化
        for i in range(self.local_reg_num):
            reg_init.append(f"\t\treg_{i} <= 32'bx;")
        
        # 全局寄存器的初始化
        for item in self.cdfg.global_variable:
            reg_init.append(f"\t\treg_{item} <= 32'bx;")

        # SRAM的初始化
        for variables in self.cdfg.params:
            variable_name, variable_type = variables
            if variable_type == 'array':
                reg_init.append(f'\t\t$readmemh("../../example/testbench/{self.cdfg.functionName}/{variable_name}.txt", {variable_name}_mem);')
            else:
                continue
        
        # reg ret 初始化
        reg_init.append(f"\t\tret <= 32'bz;")

        # reg counter 初始化
        reg_init.append(f"\t\tcounter <= 32'b0;")

        self.content_timing_logic.append(self.verilog_syntax.always_ff(clk_signal="sys_clk", rst_signal="sys_rst_n", negedge_rst=True))
        self.content_timing_logic.append(f"\tif (!sys_rst_n) begin")
        for reg_init_item in reg_init:
            self.content_timing_logic.append(reg_init_item)
        self.content_timing_logic.append(f"\t\tlast_state <= state_0;")
        self.content_timing_logic.append(f"\t\tcur_state <= state_0;")
        # self.content_timing_logic.append(f"\t\tdone <= 1'b0;")
        self.content_timing_logic.append(f"\tend")
        self.content_timing_logic.append(f"\telse begin")
        

        # self.content_timing_logic.append(f"// xxxxxxxxx")
        self.content_timing_logic.append(self.content_control_logic[0])

        first_condition = True  # 标记是否是第一个条件
        # cond_all = [] # 所有的条件变量
        for u, v, data in self.cdfg.cfg.edges(data=True):
            condition = data['condition']
            # print(f"condition before:{condition}")
            cond_wire = condition.split()[1] if len(condition.split()) >= 2 else condition
            if cond_wire != 'true' and cond_wire not in self.cond_all:
                self.content_wire.append(f"\twire {cond_wire};")
                self.cond_all.append(cond_wire)
                self.cond_block.append(u)
            # print(f"condition after:{condition}")
            if first_condition:
                if condition == "true":
                    self.content_timing_logic.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1) begin")
                else:
                    if len(condition.split()) >= 2:
                        condition = condition.split()[1]
                        self.content_timing_logic.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b0) begin")
                    else:
                        self.content_timing_logic.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b1) begin")
                first_condition = False

            else:
                if condition == "true":
                    self.content_timing_logic.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1) begin")
                else:
                    if len(condition.split()) >= 2:
                        condition = condition.split()[1]
                        self.content_timing_logic.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b0) begin")
                    else:
                        self.content_timing_logic.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b1) begin")
            
            self.content_timing_logic.append(f"\t\t\tlast_state <= cur_state;")
            self.content_timing_logic.append(f"\t\t\tcur_state <= state_{v};")
            self.content_timing_logic.append(f"\t\t\tbranch_ready <= 1'b0;")
            self.content_timing_logic.append(f"\t\t\tcounter <= 32'b0;")
            self.content_timing_logic.append(f"\t\tend")
        
        self.content_timing_logic.append(f"\t\telse begin")
        self.content_timing_logic.append(f"\t\t\tcounter <= counter + 1'b1;")
        self.content_timing_logic.append(f"\t\tend")
        self.content_timing_logic.append(f"\tend")
        self.content_timing_logic.append(f"end")
        # self.content_timing_logic.append(f"\t")

    # def gen_br_counter(self):
    #     """
    #     根据调度结果生成分支逻辑
    #     """
    #     # 添加 counter 寄存器
    #     self.content_registers.append("\treg [31:0] counter;")
        
    #     # 开始生成 always 块
    #     self.content_br_counter.append(self.verilog_syntax.always_ff(clk_signal="sys_clk", rst_signal="sys_rst_n", negedge_rst=True))
    #     self.content_br_counter.append("\tif (!sys_rst_n) begin")
    #     self.content_br_counter.append("\t\tcounter <= 0;")
    #     self.content_br_counter.append("\tend")
    #     self.content_br_counter.append("\telse begin")

    #     # 遍历调度结果，生成分支逻辑
    #     for bb_label, cycles in self.cdfg.schedule.items():
    #         cycle_count = len(cycles)  # 获取基本块运行的周期数
    #         if bb_label == "0":
    #             self.content_br_counter.append(f"\t\tif (cur_state == state_{bb_label} && counter == {cycle_count-1}) begin")
    #         else:
    #             self.content_br_counter.append(f"\t\telse if (cur_state == state_{bb_label} && counter == {cycle_count-1}) begin")
    #         self.content_br_counter.append("\t\t\tcounter <= 0;")
    #         self.content_br_counter.append("\t\tend")

    #     # 添加默认情况
    #     self.content_br_counter.append("\t\telse counter <= counter + 1;")
    #     self.content_br_counter.append("\tend")
    #     self.content_br_counter.append("end")

    def gen_control_logic(self):
        # self.content_control_logic.append(self.verilog_syntax.always_comb(sensitive_list="counter"))
        
        outer_case_items = {}
        for bb_label, schedule_results in self.cdfg.schedule.items():
            inner_case_items = {}
            for cycle_idx, ops in enumerate(schedule_results):
                check_last_cycle = (cycle_idx == len(schedule_results) - 1)
                # print(f"len_schedule_results of {bb_label}: {len(schedule_results)}")
                # print(f"cycle_idx {cycle_idx}")
                # print(check_last_cycle)

                cycle_logic = []
                for op_idx, device_idx in ops:
                    op = self.cdfg.basicBlocks[bb_label].ops[op_idx]
                    out_var = op[0]
                    op_type = op[1]
                    op_type_name = resourceData.OP_TYPE_MAP.get(op_type, "UNKNOWN_OP")
                    in_var = op[2:]
                    # in_var = in_var[0] if len(in_var) == 1 else in_var
                    # print(f"basic block {bb_label}:\t{out_var}\t{op_type_name}\t{in_var}")
                    
                    # 调用op_translation 并获取返回的操作逻辑
                    op_trans_output = self.op_translation(bb_label, cycle_idx, op_type_name, in_var, out_var)
                    cycle_logic.extend(op_trans_output)
                
                if (check_last_cycle):
                    cycle_logic.append("\tbranch_ready <= 1'b1;")
                
                # 处理 cycle_logic 的缩进
                if len(cycle_logic) > 1:
                    # 第一行保持原缩进，第二行及之后添加额外的缩进
                    formatted_logic = "\n".join(
                        f"{line}" if idx == 0 else f"\t\t\t\t{line}"
                        for idx, line in enumerate(cycle_logic)
                        if line.strip()
                    )
                else:
                    # 如果只有一行，保持原缩进
                    formatted_logic = "\n".join(f"{line}" for line in cycle_logic if line.strip())

                inner_case_items[f"32'd{cycle_idx}"] = formatted_logic
            
            inner_case_code = self.verilog_syntax.inner_case(case_variable="counter", case_items=inner_case_items)
            outer_case_items[f"state_{bb_label}"] = inner_case_code

        # 生成外层case语句
        outer_case_code = self.verilog_syntax.outer_case(case_variable="cur_state", case_items=outer_case_items)
        self.content_control_logic.append(outer_case_code)
        # self.content_control_logic.append("end")

    def in_var_to_register_mapping(self, bb_label, input_variable):
        if input_variable in self.global_reg:
            return f"reg_{input_variable}"
        elif self.check_int(input_variable):
            return int(input_variable)
        elif self.check_non_array_input(input_variable):
            return input_variable
        else:
            return f"reg_{self.get_register_for_variable(bb_label, input_variable)}"

    def out_var_to_register_mapping(self, bb_label, output_variable):
        if output_variable in self.global_reg:
            return f"reg_{output_variable}"
        else:
            return f"reg_{self.get_register_for_variable(bb_label, output_variable)}"

    def get_register_for_variable(self, block_name, variable_name):
        """
        根据基本块名称和变量名称，返回变量所在的寄存器编号。
        
        :param block_name: 基本块名称（如 'calc'）
        :param variable_name: 变量名称（如 'i_inc'）
        :return: 寄存器编号（如 2），如果未找到则返回 None
        """
        # 获取指定基本块的寄存器分配结果
        block_registers = self.cdfg.merged_coloring_result.get(block_name, {})
        
        # 遍历寄存器分配结果，查找变量所在的寄存器
        for reg, variables in block_registers.items():
            for var in variables:
                if var[0] == variable_name:
                    # print(f"reg matched, {variable_name} to {reg}")
                    return reg  # 返回寄存器编号
        
        # 如果未找到变量，返回 None
        return None

    def check_int(self, value):
        try:
            if isinstance(value, int):
                return True
            elif isinstance(value, str) and value.isdigit():
                return True
            else:
                return False
        except (ValueError, TypeError):
            return False
        
    def check_non_array_input(self, value):
        non_array_list = []
        for input_param in self.cdfg.params:
            if input_param[1] == 'non-array':
                non_array_list.append(input_param[0])
        
        if value in non_array_list:
            return True
        else:
            return False

    def op_translation(self, bb_label, cycle_idx, cur_op_type, in_var, out_var):
        # 需要把 in_var 和 out_var 转换成对应的 in_signal 和 out_signal
        # print(f"out var: {out_var}; in var: {in_var}.")
        in_signal = []

        op_trans_output = []
        # op_trans_output.append(f"32'd{cur_cycle} begin:\n")
        match cur_op_type:
            case "OP_ASSIGN":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                op_trans_output.append(f"\t{out_signal} <= {in_signal[0]};")

            case "OP_ADD":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in1, in2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {in1} + {in2};")

            case "OP_SUB":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in1, in2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {in1} - {in2};")

            case "OP_MUL":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in1, in2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {in1} * {in2};")

            case "OP_DIV":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in1, in2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {in1} / {in2};")

            case "OP_LOAD":
                # print(f"out var: {out_var}; in var: {in_var}.")
                # op_trans_output.append(f"\t{out_signal} <= a_q0;")
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                idx = self.in_var_to_register_mapping(bb_label, in_var[1])
                op_trans_output.append(f"\t{out_signal} <= {in_var[0]}_mem[{idx}];")
                
            case "OP_STORE":
                # print(f"out var: {out_var}; in var: {in_var}.")
                # out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                idx = self.in_var_to_register_mapping(bb_label, in_var[1])
                temp_reg = self.in_var_to_register_mapping(bb_label, in_var[2])
                op_trans_output.append(f"\t{in_var[0]}_mem[{idx}] <= {temp_reg};")

            case "OP_BR":
                # print(f"out var: {out_var}; in var: {in_var}.")
                # 分支操作不直接生成代码，通常由状态机控制
                pass

            case "OP_LT":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in_1, in_2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {{31'b0, ({in_1} < {in_2})}};")

            case "OP_GT":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in_1, in_2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {{31'b0, ({in_1} > {in_2})}};")

            case "OP_LE":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in_1, in_2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {{31'b0, ({in_1} <= {in_2})}};")

            case "OP_GE":
                # print(f"out var: {out_var}; in var: {in_var}.")
                # print(self.cdfg.params)
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                
                in_1, in_2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {{31'b0, ({in_1} >= {in_2})}};")

            case "OP_EQ":
                for var in in_var:
                    in_signal.append(self.in_var_to_register_mapping(bb_label, var))
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)
                in_1, in_2 = in_signal
                op_trans_output.append(f"\t{out_signal} <= {{31'b0, ({in_1} == {in_2})}};")

            case "OP_PHI":
                # print(f"out var: {out_var}; in var: {in_var}.")
                out_signal = self.out_var_to_register_mapping(bb_label, out_var)

                phi_results = []
                # phi 的输入应该是2n个，奇数项为basic_block_label，偶数项为value
                bb_labels = [x for i, x in enumerate(in_var) if i % 2 != 0]
                values = [x for i, x in enumerate(in_var) if i % 2 == 0]

                for idx, var in enumerate(values):
                    in_signal.append(self.in_var_to_register_mapping(bb_label=bb_labels[idx], input_variable=var))
                
                for i in range(len(values)):
                    if i == 0:
                        phi_results.append(f"\tif (last_state == state_{bb_labels[i]}) {out_signal} <= {in_signal[i]};")
                    else:
                        phi_results.append(f"\telse if (last_state == state_{bb_labels[i]}) {out_signal} <= {in_signal[i]};")
                op_trans_output.extend(phi_results)
                
            case "OP_RET":
                # print(f"out var: {out_var}; in var: {in_var}.")
                # for var in in_var:
                #     self.return_reg = self.in_var_to_register_mapping(bb_label, var)
                # print(self.return_reg)
                # return_val 是线网类型，所以在最后用assign赋值。
                in_signal.append(self.in_var_to_register_mapping(bb_label, in_var[0]))
                op_trans_output.append(f"\tret <= {in_signal[0]};")
        
        # if(check_last_cycle):
        #     op_trans_output.append("\tbranch_ready <= 1'b1;")
        # op_trans_output.append("end")
    
        return op_trans_output
        
    def gen_assign_logic(self):
        if self.cdfg.retType == 'int':
            self.content_assign_logic.append(f"assign return_val = ret;")

        for idx, cond_var in enumerate(self.cond_all):
            # print(self.cond_block)
            bb_label = self.cond_block[idx]
            cond_reg = self.in_var_to_register_mapping(bb_label, cond_var)
            self.content_assign_logic.append(f"assign {cond_var} = ((cur_state == state_{bb_label}) & {cond_reg}[0]);")
            # assign cond = ((CurrentState == state_start) & reg_3);

    def gen_endmodule(self):
        self.content_end.append("endmodule")

    def gen_all_code(self):
        self.gen_module_IO()
        self.gen_global_register()
        self.gen_local_register()
        self.gen_state_register()
        self.gen_bb_parameter()
        self.gen_other_register()
        self.gen_wire()
        self.gen_control_logic()
        self.gen_timing_logic()
        # self.gen_br_counter()
        self.gen_assign_logic()
        self.gen_endmodule()

def format_line(line, indent_level):
    return "\t" * indent_level + line.strip()

def verilogPrinter(verilog_generator, file=None):
    indent_level = 0
    for line in verilog_generator.content_IO:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_registers:
        print(line,file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_parameters:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_wire:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_timing_logic:
        print(line, file=file)
    print(f"\t", file=file)
    # for line in verilog_generator.content_br_counter:
    #     print(line, file=file)
    # print(f"\t", file=file)
    # for line in verilog_generator.content_control_logic:
    #     print(line, file=file)
    # print(f"\t", file=file)
    # for line in verilog_generator.content_control_logic:
    #     if "begin" in line:
    #         print(format_line(line, indent_level), file=file)
    #         indent_level += 1
    #     elif "end" in line:
    #         indent_level -= 1
    #         print(format_line(line, indent_level), file=file)
    #     else:
    #         print(format_line(line, indent_level), file=file)
    # print("", file=file)
    for line in verilog_generator.content_assign_logic:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_end:
        print(line, file=file)
    print(f"\t", file=file)
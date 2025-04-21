from typing import Counter


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
    def always_comb(sensitive_list="*"):
        """
        生成组合逻辑的 always 块
        """
        return f"always @({sensitive_list}) begin\n"

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
    def case(case_variable, case_items):
        """
        生成 case 语句
        :param case_variable: case 的变量
        :param case_items: 字典，键为 case 条件，值为对应的代码块
        """
        code = f"case ({case_variable})\n"
        for case, block in case_items.items():
            code += f"\t{case}: begin\n\t\t{block}\n\tend\n"
        code += "endcase\n"
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

        self.content_IO = []
        self.content_registers = []
        self.content_wire = []
        self.content_parameters = []
        self.content_state_update = []
        self.content_br_counter = []
        self.content_control_logic = []
        # self.content_timing = []
        # self.content_logic = []
        self.content_end = []

    def gen_module_IO(self):
        """
        生成模块的输入输出端口
        """
        # content = "module " + self.cdfg.functionName + "("
        # self.content_IO.append(content)
        self.content_IO.append(f"`timescale 1ns / 1ps")
        self.content_IO.append(f"module {self.cdfg.functionName} (")
        for variables in self.cdfg.params:
            variable_name, variable_type = variables
            if variable_type == 'array':
                self.content_IO.append(f"\tinput\t[31:0] {variable_name}_q0,")
                self.content_IO.append(f"\toutput\treg [31:0] {variable_name}_address0,")
                self.content_IO.append(f"\toutput\treg [31:0] {variable_name}_ad0,")
                self.content_IO.append(f"\toutput\treg {variable_name}_ce0,")
                self.content_IO.append(f"\toutput\treg {variable_name}_we0,")
            elif variable_type == 'non-array':
                self.content_IO.append(f"\tinput\t[31:0] {variable_name},")
            
        if self.cdfg.retType == 'int':
            self.content_IO.append(f"\toutput\t[31:0] return_val,")

        self.content_IO.append(f"\tinput\tsys_clk,")
        self.content_IO.append(f"\tinput\tsys_rst_n,")
        self.content_IO.append(f"\tinput\tstart,")
        self.content_IO.append(f"\toutput\treg idle,")
        self.content_IO.append(f"\toutput\treg done")
        self.content_IO.append(f");")

    def gen_global_register(self):
        """
        生成全局寄存器变量
        """
        for item in self.cdfg.global_variable:
            self.content_registers.append(f"\treg [31:0] reg_{item};")
        # self.content_registers.append(f"\t")

    def gen_local_register(self):
        """
        生成局部寄存器变量
        """
        # calculating the number of local register
        key_to_count = '0'
        num_local_reg = len(self.cdfg.merged_coloring_result[key_to_count])

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
        # self.content_parameters.append(f"\t")

    def gen_wire(self):
        # self.content_wire.append(f"\twire cond;")
        # self.content_wire.append(f"\t")
        pass

    def gen_state_update(self):
        """
        根据控制流图生成状态更新逻辑
        """
        self.content_state_update.append(self.verilog_syntax.always_ff(clk_signal="sys_clk", rst_signal="sys_rst_n", negedge_rst=True))
        self.content_state_update.append(f"\tif (!sys_rst_n) begin")
        self.content_state_update.append(f"\t\tlast_state <= state_0;")
        self.content_state_update.append(f"\t\tcur_state <= state_0;")
        self.content_state_update.append(f"\t\tdone <= 1'b0;")
        self.content_state_update.append(f"\tend")
        self.content_state_update.append(f"\telse begin")

        first_condition = True  # 标记是否是第一个条件
        cond_all = [] # 所有的条件变量
        for u, v, data in self.cdfg.cfg.edges(data=True):
            condition = data['condition']
            # print(f"condition before:{condition}")
            cond_wire = condition.split()[1] if len(condition.split()) >= 2 else condition
            if cond_wire != 'true' and cond_wire not in cond_all:
                self.content_wire.append(f"\twire {cond_wire};")
                cond_all.append(cond_wire)
            # print(f"condition after:{condition}")
            if first_condition:
                if condition == "true":
                    self.content_state_update.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1) begin")
                else:
                    if len(condition.split()) >= 2:
                        condition = condition.split()[1]
                        self.content_state_update.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b0) begin")
                    else:
                        self.content_state_update.append(f"\t\tif (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b1) begin")
                first_condition = False

            else:
                if condition == "true":
                    self.content_state_update.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1) begin")
                else:
                    if len(condition.split()) >= 2:
                        condition = condition.split()[1]
                        self.content_state_update.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b0) begin")
                    else:
                        self.content_state_update.append(f"\t\telse if (cur_state == state_{u} && branch_ready == 1'b1 && {condition} == 1'b1) begin")
                
            
            self.content_state_update.append(f"\t\t\tlast_state <= cur_state;")
            self.content_state_update.append(f"\t\t\tcur_state <= state_{v};")
            self.content_state_update.append(f"\t\t\tbranch_ready <= 1'b0;")
            self.content_state_update.append(f"\t\tend")

        self.content_state_update.append(f"\tend")
        self.content_state_update.append(f"end")
        # self.content_state_update.append(f"\t")

    def gen_br_counter(self):
        """
        根据调度结果生成分支逻辑
        """
        # 添加 counter 寄存器
        self.content_registers.append("\treg [31:0] counter;")
        
        # 开始生成 always 块
        self.content_br_counter.append(self.verilog_syntax.always_ff(clk_signal="sys_clk", rst_signal="sys_rst_n", negedge_rst=True))
        self.content_br_counter.append("\tif (!sys_rst_n) begin")
        self.content_br_counter.append("\t\tcounter <= 0;")
        self.content_br_counter.append("\tend")
        self.content_br_counter.append("\telse begin")

        # 遍历调度结果，生成分支逻辑
        for bb_label, cycles in self.cdfg.schedule.items():
            cycle_count = len(cycles)  # 获取基本块运行的周期数
            if bb_label == "0":
                self.content_br_counter.append(f"\t\tif (cur_state == state_{bb_label} && counter == {cycle_count}) begin")
            else:
                self.content_br_counter.append(f"\t\telse if (cur_state == state_{bb_label} && counter == {cycle_count}) begin")
            self.content_br_counter.append("\t\t\tcounter <= 0;")
            self.content_br_counter.append("\t\tend")

        # 添加默认情况
        self.content_br_counter.append("\t\telse counter <= counter + 1;")
        self.content_br_counter.append("\tend")
        self.content_br_counter.append("end")

    def gen_control_logic(self):
        outer_case_items = {}
        self.content_control_logic.append(self.verilog_syntax.always_comb(sensitive_list="counter"))
        self.content_control_logic.append(self.verilog_syntax.case(case_variable="cur_state", case_items=outer_case_items))
        self.content_control_logic.append("end")
        


    def op_translation(self):
        # match op_type:
        #     case x if x == OP_ASSIGN:
        #         print("OP_ASSIGN")
        #     case x if x == OP_ADD:
        #         pass
        #     case x if x == OP_SUB:
        #         pass
        #     case x if x == OP_MUL:
        #         pass
        #     case x if x == OP_DIV:
        #         pass
        #     case x if x == OP_LOAD:
        #         pass
        #     case x if x == OP_STORE:
        #         pass
        #     case x if x == OP_BR:
        #         pass
        #     case x if x == OP_LT:
        #         pass
        #     case x if x == OP_GT:
        #         pass
        #     case x if x == OP_LE:
        #         pass                        
        #     case x if x == OP_GE:
        #         pass                
        #     case x if x == OP_EQ:
        #         pass
        #     case x if x == OP_PHI:
        #         pass
        #     case x if x == OP_RET:
        #         pass
        pass
        
        
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
        self.gen_state_update()
        self.gen_br_counter()
        self.gen_control_logic()
        self.gen_endmodule()

def verilogPrinter(verilog_generator, file=None):
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
    for line in verilog_generator.content_state_update:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_br_counter:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_control_logic:
        print(line, file=file)
    print(f"\t", file=file)
    for line in verilog_generator.content_end:
        print(line, file=file)
    print(f"\t", file=file)
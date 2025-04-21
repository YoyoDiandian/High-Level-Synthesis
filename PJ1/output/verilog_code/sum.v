`timescale 1ns / 1ps
module Sum (
	input	[31:0] a_q0,
	output	reg [31:0] a_address0,
	output	reg [31:0] a_ad0,
	output	reg a_ce0,
	output	reg a_we0,
	input	[31:0] b_q0,
	output	reg [31:0] b_address0,
	output	reg [31:0] b_ad0,
	output	reg b_ce0,
	output	reg b_we0,
	input	[31:0] n,
	output	[31:0] return_val,
	input	sys_clk,
	input	sys_rst_n,
	input	start,
	output	reg idle,
	output	reg done
);
	
	reg [31:0] reg_n;
	reg [31:0] reg_i;
	reg [31:0] reg_temp;
	reg [31:0] reg_0;
	reg [31:0] reg_1;
	reg [31:0] reg_2;
	reg [3:0] cur_state;
	reg [3:0] last_state;
	reg branch_ready;
	reg [31:0] counter;
	
	parameter state_0 = 4'b1000;
	parameter state_start = 4'b0100;
	parameter state_calc = 4'b0010;
	parameter state_ret = 4'b0001;
	
	wire cond;
	
always @(posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		last_state <= state_0;
		cur_state <= state_0;
		done <= 1'b0;
	end
	else begin
		if (cur_state == state_0 && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && cond == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_ret;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && cond == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_calc;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_calc && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
		end
	end
end
	
always @(posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		counter <= 0;
	end
	else begin
		if (cur_state == state_0 && counter == 1) begin
			counter <= 0;
		end
		else if (cur_state == state_start && counter == 3) begin
			counter <= 0;
		end
		else if (cur_state == state_calc && counter == 5) begin
			counter <= 0;
		end
		else if (cur_state == state_ret && counter == 4) begin
			counter <= 0;
		end
		else counter <= counter + 1;
	end
end
	
endmodule
	

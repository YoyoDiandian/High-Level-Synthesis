`timescale 1ns / 1ps
module gcd (
	input	[31:0] a,
	input	[31:0] b,
	output	[31:0] return_val,
	input	sys_clk,
	input	sys_rst_n,
	input	start,
	output	reg idle,
	output	reg done
);
	
	reg [31:0] reg_b;
	reg [31:0] reg_b1;
	reg [31:0] reg_a1;
	reg [31:0] reg_remainder;
	reg [31:0] reg_divisor;
	reg [31:0] reg_a;
	reg [31:0] reg_0;
	reg [31:0] reg_1;
	reg [4:0] cur_state;
	reg [4:0] last_state;
	reg branch_ready;
	reg [31:0] counter;
	
	parameter state_0 = 5'b10000;
	parameter state_start = 5'b01000;
	parameter state_cal = 5'b00100;
	parameter state_exchange = 5'b00010;
	parameter state_ret = 5'b00001;
	
	wire a_LE_b;
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
		else if (cur_state == state_start && branch_ready == 1'b1 && a_LE_b == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_cal;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && a_LE_b == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_exchange;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_cal && branch_ready == 1'b1 && cond == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_ret;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_cal && branch_ready == 1'b1 && cond == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
		end
		else if (cur_state == state_exchange && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_cal;
			branch_ready <= 1'b0;
		end
	end
end
	
always @(posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		counter <= 0;
	end
	else begin
		if (cur_state == state_0 && counter == 2) begin
			counter <= 0;
		end
		else if (cur_state == state_start && counter == 4) begin
			counter <= 0;
		end
		else if (cur_state == state_cal && counter == 5) begin
			counter <= 0;
		end
		else if (cur_state == state_exchange && counter == 1) begin
			counter <= 0;
		end
		else if (cur_state == state_ret && counter == 1) begin
			counter <= 0;
		end
		else counter <= counter + 1;
	end
end
	
always @(counter) begin

case (cur_state)
	1: begin
		1
	end
	2: begin
		2
	end
	3: begin
		3
	end
endcase

end
	
endmodule
	

module sum (
	input	[31:0] n,
	output	[31:0] return_val,
	input	sys_clk,
	input	sys_rst_n
);
	
	reg [31:0] a_mem [0:255];
	reg [31:0] b_mem [0:255];
	reg [31:0] reg_temp;
	reg [31:0] reg_i;
	reg [31:0] reg_0;
	reg [31:0] reg_1;
	reg [31:0] reg_2;
	reg [31:0] reg_3;
	reg [3:0] cur_state;
	reg [3:0] last_state;
	reg branch_ready;
	reg [31:0] counter;
	reg [31:0] ret;
	
	parameter state_0 = 4'b1000;
	parameter state_start = 4'b0100;
	parameter state_calc = 4'b0010;
	parameter state_ret = 4'b0001;
	
	wire cond;
	
always @(posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		reg_0 <= 32'bx;
		reg_1 <= 32'bx;
		reg_2 <= 32'bx;
		reg_3 <= 32'bx;
		reg_temp <= 32'bx;
		reg_i <= 32'bx;
		$readmemh("../../example/testbench/sum/a.txt", a_mem);
		$readmemh("../../example/testbench/sum/b.txt", b_mem);
		ret <= 32'bz;
		counter <= 32'b0;
		last_state <= state_0;
		cur_state <= state_0;
	end
	else begin
case (cur_state)
	state_0: begin
		case (counter)
			32'd0: begin
					reg_0 <= 0;
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_start: begin
		case (counter)
			32'd0: begin
					if (last_state == state_0) reg_i <= 0;
					else if (last_state == state_calc) reg_i <= reg_2;
			end
			32'd1: begin
					if (last_state == state_0) reg_0 <= reg_0;
					else if (last_state == state_calc) reg_0 <= reg_temp;
					reg_1 <= {31'b0, (reg_i >= n)};
			end
			32'd2: begin
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_calc: begin
		case (counter)
			32'd0: begin
					reg_1 <= a_mem[reg_i];
					reg_2 <= reg_i + 1;
			end
			32'd1: begin
				
			end
			32'd2: begin
					reg_temp <= reg_0 + reg_1;
			end
			32'd3: begin
					b_mem[reg_i] <= reg_temp;
			end
			32'd4: begin
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_ret: begin
		case (counter)
			32'd0: begin
					reg_0 <= n - 1;
			end
			32'd1: begin
					reg_0 <= b_mem[reg_0];
			end
			32'd2: begin
				
			end
			32'd3: begin
					ret <= reg_0;
					branch_ready <= 1'b1;
			end
		endcase
	end
endcase
		if (cur_state == state_0 && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && cond == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_ret;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && cond == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_calc;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_calc && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else begin
			counter <= counter + 1'b1;
		end
	end
end
	
assign return_val = ret;
assign cond = ((cur_state == state_start) & reg_1[0]);
	
endmodule
	

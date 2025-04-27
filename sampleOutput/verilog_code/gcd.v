module gcd (
	input	[31:0] b,
	input	[31:0] a,
	output	[31:0] return_val,
	input	sys_clk,
	input	sys_rst_n
);
	
	reg [31:0] reg_a1;
	reg [31:0] reg_b1;
	reg [31:0] reg_divisor;
	reg [31:0] reg_remainder;
	reg [31:0] reg_0;
	reg [31:0] reg_1;
	reg [4:0] cur_state;
	reg [4:0] last_state;
	reg branch_ready;
	reg [31:0] counter;
	reg [31:0] ret;
	
	parameter state_0 = 5'b10000;
	parameter state_start = 5'b01000;
	parameter state_cal = 5'b00100;
	parameter state_exchange = 5'b00010;
	parameter state_ret = 5'b00001;
	
	wire a_LE_b;
	wire cond;
	
always @(posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		reg_0 <= 32'bx;
		reg_1 <= 32'bx;
		reg_a1 <= 32'bx;
		reg_b1 <= 32'bx;
		reg_divisor <= 32'bx;
		reg_remainder <= 32'bx;
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
					reg_0 <= a;
			end
			32'd1: begin
					reg_1 <= b;
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_start: begin
		case (counter)
			32'd0: begin
					if (last_state == state_0) reg_a1 <= reg_0;
					else if (last_state == state_cal) reg_a1 <= reg_divisor;
			end
			32'd1: begin
					if (last_state == state_0) reg_b1 <= reg_1;
					else if (last_state == state_cal) reg_b1 <= reg_remainder;
			end
			32'd2: begin
					reg_0 <= {31'b0, (reg_a1 >= reg_b1)};
			end
			32'd3: begin
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_cal: begin
		case (counter)
			32'd0: begin
					if (last_state == state_start) reg_divisor <= reg_b1;
					else if (last_state == state_exchange) reg_divisor <= reg_a1;
			end
			32'd1: begin
					if (last_state == state_start) reg_0 <= reg_a1;
					else if (last_state == state_exchange) reg_0 <= reg_b1;
			end
			32'd2: begin
					reg_remainder <= reg_0 - reg_divisor;
			end
			32'd3: begin
					reg_0 <= {31'b0, (reg_remainder == 0)};
			end
			32'd4: begin
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_exchange: begin
		case (counter)
			32'd0: begin
					branch_ready <= 1'b1;
			end
		endcase
	end
	state_ret: begin
		case (counter)
			32'd0: begin
					ret <= reg_divisor;
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
		else if (cur_state == state_start && branch_ready == 1'b1 && a_LE_b == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_cal;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_start && branch_ready == 1'b1 && a_LE_b == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_exchange;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_cal && branch_ready == 1'b1 && cond == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_ret;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_cal && branch_ready == 1'b1 && cond == 1'b0) begin
			last_state <= cur_state;
			cur_state <= state_start;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else if (cur_state == state_exchange && branch_ready == 1'b1) begin
			last_state <= cur_state;
			cur_state <= state_cal;
			branch_ready <= 1'b0;
			counter <= 32'b0;
		end
		else begin
			counter <= counter + 1'b1;
		end
	end
end
	
assign return_val = ret;
assign a_LE_b = ((cur_state == state_start) & reg_0[0]);
assign cond = ((cur_state == state_cal) & reg_0[0]);
	
endmodule
	

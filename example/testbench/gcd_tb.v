module gcd_tb;
	reg sys_clk;
	reg sys_rst_n;
	reg [31:0] a;
	reg [31:0] b;
	wire [31:0] return_val;

	initial begin
		$dumpfile("gcd_wave.vcd");
		$dumpvars(0, gcd_tb);

		sys_clk <= 1'b0;
		sys_rst_n <= 1'b1;
		#10 begin
			a <= 32'd28;
			b <= 32'd42;
		end
		#5 sys_rst_n <= 1'b0;
		#5 sys_rst_n <= 1'b1;
		#2000 $finish;
	end

	always #1 sys_clk = ~sys_clk;

	gcd uut (.sys_clk(sys_clk), .sys_rst_n(sys_rst_n), .return_val(return_val), .a(a), .b(b));

endmodule
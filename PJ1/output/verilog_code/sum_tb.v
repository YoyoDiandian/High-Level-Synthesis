module sum_tb();
reg sys_clk;
reg sys_rst_n;
reg [31:0] n;
wire [31:0] return_val;

initial begin
    $dumpfile("sum_wave.vcd");
    $dumpvars(0, sum_tb);

    sys_clk <= 1'b0;
    sys_rst_n <= 1'b1;
    # 10 n <= 32'd10;
    #5 sys_rst_n <= 1'b0;
    #5 sys_rst_n <= 1'b1;
    #5000 $finish;
end

always #1 sys_clk <= ~sys_clk;

Sum uut(.sys_clk(sys_clk), .sys_rst_n(sys_rst_n), .n(n), .return_val(return_val));
endmodule
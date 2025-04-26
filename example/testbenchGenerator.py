import os
import sys

def testbenchPrinter(inputParams, testbenchFile, moduleName):
    with open(testbenchFile, 'w') as f:
        f.write(f"module {moduleName}_tb;\n")
        f.write(f"\treg sys_clk;\n")
        f.write(f"\treg sys_rst_n;\n")
        for key in inputParams:
            if type(inputParams[key]) == int:
                f.write(f"\treg [31:0] {key};\n")
        f.write(f"\twire [31:0] return_val;\n")
        f.write("\n")
        f.write(f"\tinitial begin\n")
        f.write(f"\t\t$dumpfile(\"{moduleName}_wave.vcd\");\n")
        f.write(f"\t\t$dumpvars(0, {moduleName}_tb);\n")
        f.write("\n")
        f.write(f"\t\tsys_clk <= 1'b0;\n")
        f.write(f"\t\tsys_rst_n <= 1'b1;\n")
        f.write(f"\t\t#10 begin\n")
        for key in inputParams:
            if type(inputParams[key]) == int:
                f.write(f"\t\t\t{key} <= 32'd{inputParams[key]};\n")
        f.write(f"\t\tend\n")
        f.write(f"\t\t#5 sys_rst_n <= 1'b0;\n")
        f.write(f"\t\t#5 sys_rst_n <= 1'b1;\n")
        f.write(f"\t\t#2000 $finish;\n")
        f.write(f"\tend\n")
        f.write("\n")
        f.write(f"\talways #1 sys_clk = ~sys_clk;\n")
        f.write("\n")
        f.write(f"\t{moduleName} uut (.sys_clk(sys_clk), .sys_rst_n(sys_rst_n), .return_val(return_val)")
        for key in inputParams:
            if type(inputParams[key]) == int:
                f.write(f", .{key}({key})")
        f.write(");\n")
        f.write("\n")
        f.write(f"endmodule")

def inputParamsParser(file):
    with open (file, 'r') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip()]
        inputParams = {}
        for line in lines:
            parts = line.split()
            key = parts[0]
            if len(parts) == 2:
                inputParams[key] = int(parts[1])
            else:
                inputParams[key] = [int(x) for x in parts[1:]]
        return inputParams

def arrayGenerator(inputParams, directory):
    has = 0
    for key in inputParams:
        if type(inputParams[key]) == list:
            if not has:
                os.makedirs(outputDirectory, exist_ok=True)
                has = 1
            with open(os.path.join(directory, key + '.txt'), 'w') as f:
                for i in inputParams[key]:
                    f.write(f"{i:08x}\n")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) != 2:
        print("Error: Input arguments required")
        sys.exit(1)
    moduleName = sys.argv[1]
    inputFile = os.path.join(os.path.dirname(__file__), moduleName + '_input.txt')
    outputDirectory = os.path.join(os.path.dirname(__file__), 'testbench', moduleName)
    testbenchFile = os.path.join(os.path.dirname(__file__), 'testbench', moduleName + '_tb.v')

    inputParams = inputParamsParser(inputFile)
    arrayGenerator(inputParams, outputDirectory)
    testbenchPrinter(inputParams, testbenchFile, moduleName)
    print("Testbench generated successfully.")
import os
import sys
import shutil

def testbenchPrinter(inputParams, testbenchFile, moduleName):
    """Generate a Verilog testbench file for the given module."""
    try:
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
        return True
    except Exception as e:
        print(f"Error: Failed to generate testbench file - {e}")
        return False

def inputParamsParser(file):
    """Parse input parameters from a file."""
    try:
        if not os.path.exists(file):
            print(f"Error: Input file '{file}' does not exist")
            return None
            
        with open(file, 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                print(f"Error: Input file '{file}' is empty")
                return None
                
            inputParams = {}
            for line in lines:
                parts = line.split()
                if len(parts) < 2:
                    print(f"Error: Invalid line format in input file: '{line}'")
                    continue
                    
                key = parts[0]
                try:
                    if len(parts) == 2:
                        inputParams[key] = int(parts[1])
                    else:
                        inputParams[key] = [int(x) for x in parts[1:]]
                except ValueError:
                    print(f"Error: Non-integer value found in line: '{line}'")
                    return None
                    
            if not inputParams:
                print("Error: No valid parameters found in input file")
                return None
                
            return inputParams
    except Exception as e:
        print(f"Error: Failed to parse input file - {e}")
        return None

def arrayGenerator(inputParams, directory):
    """Generate array files for the testbench."""
    try:
        # Create directory if it doesn't exist
        created_dir = False
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            created_dir = True
            
        arrays_written = False
        for key in inputParams:
            if isinstance(inputParams[key], list):
                array_file = os.path.join(directory, key + '.txt')
                with open(array_file, 'w') as f:
                    for i in inputParams[key]:
                        f.write(f"{i:08x}\n")
                arrays_written = True
                print(f"Generated array file: {array_file}")
        
        if not arrays_written and created_dir:
            print("Warning: No arrays to write, but directory was created")
            
        return True
    except Exception as e:
        print(f"Error: Failed to generate array files - {e}")
        return False

def cleanup_directory(directory):
    """Delete a directory and all its contents."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Cleanup: Removed directory '{directory}'")
    except Exception as e:
        print(f"Warning: Failed to clean up directory '{directory}' - {e}")

def main():
    """Main function to process command line arguments and generate testbench."""
    if len(sys.argv) < 2:
        print("Usage: python testbenchGenerator.py <module_name> [input_file_path]")
        return 1
        
    moduleName = sys.argv[1]
    
    # Handle optional input file path argument
    if len(sys.argv) >= 3:
        inputFile = sys.argv[2]
    else:
        inputFile = os.path.join(os.path.dirname(__file__), moduleName + '_input.txt')
    
    print(f"Processing module: {moduleName}")
    print(f"Using input file: {inputFile}")
    
    # Define output directories and files
    outputDirectory = os.path.join(os.path.dirname(__file__), 'testbench', moduleName)
    testbenchFile = os.path.join(outputDirectory, moduleName + '_tb.v')
    
    print(f"Output directory: {outputDirectory}")
    print(f"Testbench file: {testbenchFile}")
    
    # Check if testbench directory already exists
    if os.path.exists(outputDirectory):
        response = input(f"Directory '{outputDirectory}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled by user")
            return 1
        
    # Parse input parameters
    inputParams = inputParamsParser(inputFile)
    if inputParams is None:
        return 1
    
    # Create output directory
    try:
        os.makedirs(os.path.dirname(testbenchFile), exist_ok=True)
    except Exception as e:
        print(f"Error: Failed to create output directory - {e}")
        return 1
    
    # Generate array files
    if not arrayGenerator(inputParams, outputDirectory):
        cleanup_directory(outputDirectory)
        return 1
    
    # Generate testbench file
    if not testbenchPrinter(inputParams, testbenchFile, moduleName):
        cleanup_directory(outputDirectory)
        return 1
    
    print(f"Successfully generated testbench in: {testbenchFile}")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
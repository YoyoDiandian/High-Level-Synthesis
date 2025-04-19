import os
import re
import networkx as nx
import sys

class BasicBlock:
    """a basic block within the CFG"""
    
    def __init__(self, label):
        """
        initialize basic block
        
        Args:
            label: the label of basic block
        """
        self.label = label
        self.ops = []  # Operation list
        self.dfg = nx.DiGraph()  # Use NetworkX directed graph to represent data flow graph
        self.next_bb = None  # Label of the next basic block

    def addOP(self, op):
        """add operation to basic block"""
        self.ops.append(op)

    def generateDFG(self):
        """
        build DFG
        Each node is operation index, edges represent data dependencies
        """
        # Clear existing graph
        self.dfg.clear()
        
        # Add all operations as nodes
        for i in range(len(self.ops)):
            self.dfg.add_node(i, operation=self.ops[i])
            
        # Traverse each operation to establish data dependency edges
        for i, op in enumerate(self.ops):
            # Value produced by the current operation
            current_value = op[0]
            
            # Operands used by the current operation
            operands = op[2:]
            
            # Find the source of operands (search forward)
            for j in range(i):
                prev_op = self.ops[j]
                prev_value = prev_op[0]
                
                # If the previous operation produces a value used by the current operation, add an edge
                if prev_value in operands:
                    self.dfg.add_edge(j, i, value=prev_value)
        
        return self.dfg


class CDFG:
    """Control Data Flow Graph (CDFG) representation"""
    
    def __init__(self):
        """Initialize CDFG object"""
        self.basicBlocks = {}  # Dictionary of basic blocks, key is the basic block label
        self.retType = None    # Function return type
        self.functionName = None  # Function name
        self.params = []  # Function parameter list
        self.cfg = nx.DiGraph()  # Use NetworkX directed graph to represent control flow graph
    
    def llvmParser(self, file_path):
        """
        Parse LLVM format parse_result file to build CDFG structure
        
        Args:
            file_path: Path to the parse_result file
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found {file_path}")
            return None
        
        # Parse return type
        ret_type_match = re.search(r'ret type: (\w+)', content)
        if ret_type_match:
            self.retType = ret_type_match.group(1)
        
        # Parse function name
        func_name_match = re.search(r'function name (\w+)', content)
        if func_name_match:
            self.functionName = func_name_match.group(1)
        
        # Parse parameters
        # params = []
        param_matches = re.finditer(r'(array|non-array)\s+(\w+)', content)
        for match in param_matches:
            param_type, param_name = match.groups()
            self.params.append((param_name, param_type))
        # self.params = params
        
        # Parse basic blocks
        basic_block_pattern = r'Basic Block label: (\w+)(.*?)(?=Basic Block label:|$)'
        basic_block_matches = re.finditer(basic_block_pattern, content, re.DOTALL)
        
        # Get all basic block labels
        bb_labels = []
        for match in basic_block_matches:
            label = match.group(1)
            bb_labels.append(label)
        
        # Restart matching basic blocks
        basic_block_matches = re.finditer(basic_block_pattern, content, re.DOTALL)
        
        for i, match in enumerate(basic_block_matches):
            label = match.group(1)
            block_content = match.group(2).strip()
            
            # Create basic block object
            bb = BasicBlock(label)
            
            # Set next_bb attribute
            if i < len(bb_labels) - 1:
                bb.next_bb = bb_labels[i + 1]
            
            # Parse operations
            op_pattern = r'value (\w*)\s+OP TYPE:(\d+)(.*?)(?=value|$)'
            op_matches = re.finditer(op_pattern, block_content, re.DOTALL)
            
            for op_match in op_matches:
                value = op_match.group(1)
                op_type = int(op_match.group(2))
                operands_text = op_match.group(3).strip()
                
                # Parse operands
                operands = []
                if operands_text:
                    operands = [op.strip() for op in operands_text.split() if op.strip()]
                
                # Add operation to basic block
                bb.addOP([value, op_type] + operands)
            
            # Add basic block to CDFG
            self.addBasicBlock(bb)

    def addBasicBlock(self, basic_block):
        """
        Add basic block to CDFG
        
        Args:
            basic_block: BasicBlock object
        """
        self.basicBlocks[basic_block.label] = basic_block
        self.cfg.add_node(basic_block.label, block=basic_block)

    def generateCFG(self):
        """
        Build Control Flow Graph (CFG)
        Use NetworkX directed graph, nodes are basic block labels, edges represent control flow transfers
        """
        # Clear existing edges (keep nodes)
        self.cfg.clear_edges()
        
        # Traverse each basic block to establish control flow edges
        for label, bb in self.basicBlocks.items():
            # Skip if basic block is empty
            if not bb.ops:
                continue
                
            # Get the last operation in the basic block
            last_op = bb.ops[-1]
            
            # Determine the type of the last operation
            if last_op[1] == 7:  # Branch instruction (OP TYPE:7)
                if len(last_op) > 3:  # Conditional branch
                    cond_var = last_op[2]
                    true_target = last_op[3]
                    false_target = last_op[4]
                    
                    # Add branch for true condition
                    self.cfg.add_edge(label, true_target, condition=cond_var)
                    
                    # Add branch for false condition
                    self.cfg.add_edge(label, false_target, condition=f"not {cond_var}")
                    
                elif len(last_op) > 2:  # Unconditional jump
                    target = last_op[2]
                    self.cfg.add_edge(label, target, condition="true")
            else:
                # Non-branch instruction, sequential execution to the next basic block
                if bb.next_bb:
                    self.cfg.add_edge(label, bb.next_bb, condition="true")
            
    def generateDFGs(self):
        """Build data flow graphs for all basic blocks"""
        for _, bb in self.basicBlocks.items():
            bb.generateDFG()
        return self.basicBlocks


def printCDFG(cdfg, file=None):
    """Print basic information of CDFG"""
    print("===== Function Basic Information =====", file=file)
    print(f"Function name: {cdfg.functionName}", file=file)
    print(f"Return type: {cdfg.retType}", file=file)
    print(f"Parameters: {cdfg.params}", file=file)
    print("========================\n", file=file)


def printBasicBlocks(cdfg, file=None):
    """Print information of all basic blocks"""
    print("===== Basic Block Information =====", file=file)
    for label, bb in cdfg.basicBlocks.items():
        print(f"Basic block {label}:", file=file)
        print(f"\tNext basic block: {bb.next_bb}", file=file)
        
        print("\tOperation list:", file=file)
        for i, op in enumerate(bb.ops):
            print(f"\t\t[{i}] {op}", file=file)
    print("===================\n", file=file)


def printCFG(cdfg, file=None):
    """Print control flow graph information"""
    print("===== Control Flow Graph (CFG) =====", file=file)
    for u, v, data in cdfg.cfg.edges(data=True):
        print(f"\t{u} -> {v} [Condition: {data['condition']}]", file=file)
    print("=======================\n", file=file)


def printDFG(cdfg, file=None):
    """Print data flow graph information for all basic blocks"""
    print("===== Data Flow Graph (DFG) =====", file=file)
    for label, bb in cdfg.basicBlocks.items():
        if len(bb.dfg.edges()) > 0:
            print(f"\tDFG of basic block {label}:", file=file)
            for u, v, data in bb.dfg.edges(data=True):
                value = data.get('value', '')
                print(f"\t\tOperation {u} -> {v} [Value: {value}]", file=file)
    print("=======================\n", file=file)

def cdfgPrinter(cdfg, file=None):
    """Print basic information of CDFG"""
    printCDFG(cdfg, file)
    printBasicBlocks(cdfg, file)    
    printCFG(cdfg, file)
    printDFG(cdfg, file)


# def main():
#     """Main function: Parse LLVM IR and generate CDFG"""
#     # Get file path
#     # Get command line arguments
#     if len(sys.argv) > 1:
#         file_path = sys.argv[1]
#     else:
#         # Default path
#         print("File path unspecified, using default path: parser/parseResult.txt")
#         file_path = os.path.join(os.path.dirname(__file__), 'parser', 'parseResult.txt')
    
#     cdfg = CDFG()

#     cdfg.llvmParser(file_path)
#     cdfg.generateCFG()
#     cdfg.generateDFGs()


#     if not cdfg:
#         return
#     # Print CDFG basic information
#     printCDFG(cdfg)
#     printBasicBlocks(cdfg)    
#     printCFG(cdfg)
#     printDFG(cdfg)



# if __name__ == "__main__":
#     main()
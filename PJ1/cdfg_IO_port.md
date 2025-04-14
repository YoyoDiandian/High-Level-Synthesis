# CDFG生成器接口文档

本文档描述了`cdfgGenerator.py`模块的接口，该模块用于从LLVM IR格式的文件中解析和构建控制数据流图(CDFG)。

## 1. 类

### 1.1 BasicBlock

表示控制流图中的一个基本块。

#### 构造函数

```python
BasicBlock(label)
```

**参数**:
- `label` (str): 基本块的唯一标识符

#### 属性

- `label` (str): 基本块的标签
- `ops` (list): 操作列表
- `dfg` (NetworkX.DiGraph): 数据流图
- `next_bb` (str): 下一个基本块的标签

#### 方法

- **add_op(op)**

  添加操作到基本块。

  **参数**:
  - `op` (list): 操作列表，格式为`[value, op_type, operands...]`
    - `value`: 操作产生的值
    - `op_type`: 操作类型编号
    - `operands`: 操作使用的操作数

- **build_dfg()**

  构建数据流图(DFG)。每个节点是操作索引，边表示数据依赖关系。

  **返回值**: NetworkX.DiGraph: 构建好的数据流图

### 1.2 CDFG

控制数据流图(CDFG)的表示。

#### 构造函数

```python
CDFG()
```

#### 属性

- `basic_blocks` (dict): 基本块字典，键为基本块标签
- `cfg` (NetworkX.DiGraph): 控制流图
- `ret_type` (str): 函数返回类型
- `function_name` (str): 函数名
- `params` (list): 函数参数列表，每个元素为(参数名, 参数类型)元组

#### 方法

- **add_basic_block(basic_block)**

  添加基本块到CDFG。

  **参数**:
  - `basic_block` (BasicBlock): 要添加的基本块对象

- **get_basic_blocks()**

  获取所有基本块。

  **返回值**: dict: 键为基本块标签，值为BasicBlock对象的字典

- **build_cfg()**

  构建控制流图(CFG)。分析基本块间的控制流关系，并在图中添加适当的边。

- **build_all_dfgs()**

  为所有基本块构建数据流图。

  **返回值**: dict: 包含所有基本块的字典

## 2. 函数

### 2.1 parse_llvm_to_cdfg(file_path, cdfg)

解析LLVM格式的parse_result文件，构建CDFG结构。

**参数**:
- `file_path` (str): parse_result文件的路径
- `cdfg` (CDFG): 将被填充的CDFG对象

### 2.2 print_cdfg_info(cdfg)

打印CDFG的基本信息。

**参数**:
- `cdfg` (CDFG): CDFG对象

### 2.3 print_basic_blocks_info(cdfg)

打印所有基本块的信息。

**参数**:
- `cdfg` (CDFG): CDFG对象

### 2.4 print_cfg_info(cdfg)

打印控制流图信息。

**参数**:
- `cdfg` (CDFG): CDFG对象

### 2.5 print_dfg_info(cdfg)

打印所有基本块的数据流图信息。

**参数**:
- `cdfg` (CDFG): CDFG对象

### 2.6 main()

主函数：解析LLVM IR并生成CDFG，然后打印相关信息。

## 3. 使用示例

```python
# 创建CDFG对象
cdfg = CDFG()

# 解析LLVM IR文件
file_path = 'parser/parseResult.txt'
parse_llvm_to_cdfg(file_path, cdfg)

# 构建控制流图和数据流图
cdfg.build_cfg()
cdfg.build_all_dfgs()

# 打印各种信息
print_cdfg_info(cdfg)
print_basic_blocks_info(cdfg)
print_cfg_info(cdfg)
print_dfg_info(cdfg)
```

# CDFG 生成器数据结构详解

## 1. BasicBlock 类详细数据结构

`BasicBlock` 类表示控制流图中的一个基本块（连续执行的指令序列），其详细数据结构如下：

### 1.1 主要属性

- **label** (str)
  - 基本块的唯一标识符
  - 通常是字符串形式，如 "entry"、"for.body"、"if.then" 等

- **ops** (list of lists)
  - 存储基本块中的所有操作指令
  - 每个操作是一个列表，结构为 `[value, op_type, operands...]`
  - 示例：`["a", 1, "b", "c"]` 表示将变量 b 和 c 进行操作，结果存储在 a 中，操作类型为 1
  
- **dfg** (NetworkX.DiGraph)
  - 数据流图的网络表示
  - **节点**：整数索引，对应操作在 ops 列表中的位置
    - 节点属性：`operation` - 指向 ops 列表中对应的操作
  - **边**：从生产者操作到使用者操作的有向边
    - 边属性：`value` - 表示数据依赖的变量名

- **next_bb** (str 或 None)
  - 程序顺序上的下一个基本块标签
  - 用于构建非分支转移的控制流边
  - 最后一个基本块该值为 None

### 1.2 内部结构示例

```
BasicBlock {
    label: "for.body",
    ops: [
        ['c', 0, '0'],             // 给c赋值
        ['ai', 5, 'a', 'i'],       // ai = a * i
        ['', 7, 'cond', 'ret', 'calc']  // 分支指令
    ],
    dfg: DiGraph {
        nodes: {
            0: {operation: ["i.0", 4, "i"]},
            1: {operation: ["mul", 2, "i.0", "2"]},
            2: {operation: ["", 7, "exitcond", "for.end", "for.body"]}
        },
        edges: {
            (0, 1): {value: "i.0"},
            (1, 2): {value: "bi"}
        }
    },
    next_bb: "for.end"
}
```

## 2. CDFG 类详细数据结构

`CDFG` 类表示整个控制数据流图，包含了函数的结构和流程信息：

### 2.1 主要属性

- **basic_blocks** (dict)
  - 键：基本块标签字符串
  - 值：对应的 `BasicBlock` 对象
  - 存储程序中所有基本块的完整集合

- **cfg** (NetworkX.DiGraph)
  - 控制流图的网络表示
  - **节点**：基本块标签字符串
    - 节点属性：`block` - 指向对应的 `BasicBlock` 对象
  - **边**：从一个基本块到其可能的后继基本块的有向边
    - 边属性：`condition` - 表示控制转移条件
      - 条件分支：变量名（真分支）或 `"not {变量名}"`（假分支）
      - 无条件转移：`"true"`

- **ret_type** (str)
  - 函数的返回类型，如 "int"、"void" 等

- **function_name** (str)
  - 解析的函数名称

- **params** (list of tuples)
  - 函数参数列表
  - 每个元素是 `(参数名, 参数类型)` 元组
  - 参数类型可以是 `"array"` 或 `"non-array"`

### 2.2 内部结构示例

```
CDFG {
    function_name: "sum",
    ret_type: "int",
    params: [("arr", "array"), ("n", "non-array")],
    
    basic_blocks: {
        "entry": BasicBlock { ... },
        "for.body": BasicBlock { ... },
        "for.end": BasicBlock { ... }
    },
    
    cfg: DiGraph {
        nodes: {
            "entry": {block: BasicBlock对象},
            "for.body": {block: BasicBlock对象},
            "for.end": {block: BasicBlock对象}
        },
        edges: {
            ("entry", "for.body"): {condition: "true"},
            ("for.body", "for.body"): {condition: "i.0"},
            ("for.body", "for.end"): {condition: "not i.0"}
        }
    }
}
```

## 3. 数据结构间的关系

- **基本块与操作**: 每个基本块包含多个操作，形成一对多关系
- **基本块与DFG**: 每个基本块有自己的数据流图，描述该块内部的数据依赖
- **基本块与CFG**: 所有基本块组成控制流图的节点，CFG的边描述它们之间的执行流关系
- **CDFG整合**: CDFG类将所有数据结构整合在一起，形成完整的程序表示

## 4. 操作类型表示

操作列表中的`op_type`对应不同的操作类型：
- `0`: assign =
- `1`: 加法运算
- `2`: 减法运算
- `3`: 乘法运算
- `4`: 除法运算
- `5`: 加载操作 load
- `6`: 存储操作 store
- `7`: 分支操作 br
- `8`: 比较 <
- `9`: 比较 >
- `10`: 比较 <=
- `11`: 比较 >=
- `12`: 比较 ==
- `13`: 条件判断 phi
- `14`: 返回 return
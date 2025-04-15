# 接口文档

## CDFG生成器

### BasicBlock
表示控制流图中的一个基本块

#### 构造函数

```python
BasicBlock(label)
```

**参数**: `label` (str): 基本块的唯一标识符

#### 属性

- `label` (str): 基本块的标签
- `ops` (list): 操作列表
- `dfg` (NetworkX.DiGraph): 数据流图
- `next_bb` (str): 下一个基本块的标签

#### 方法

- **addOP(op)**

  添加操作到基本块。

  **参数**:
  - `op` (list): 操作列表，格式为`[value, op_type, operands...]`
    - `value`: 操作产生的值
    - `op_type`: 操作类型编号
    - `operands`: 操作使用的操作数

- **generateDFG()**

  构建数据流图(DFG)。每个节点是操作索引，边表示数据依赖关系。

  **返回值**: NetworkX.DiGraph: 构建好的数据流图

#### 内部结构示例

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

### CDFG

控制数据流图(CDFG)的表示。

#### 构造函数

```python
CDFG()
```

#### 属性

- `basicBlocks` (dict): 基本块字典，键为基本块标签
- `cfg` (NetworkX.DiGraph): 控制流图
- `retType` (str): 函数返回类型
- `functionName` (str): 函数名
- `params` (list): 函数参数列表，每个元素为(参数名, 参数类型)元组

#### 方法

- **llvmParser(file_path)**

    解析LLVM格式的parse_result文件，构建CDFG结构。

    **参数**:
    - `file_path` (str): parse_result文件的路径
    - `cdfg` (CDFG): 将被填充的CDFG对象

- **addBasicBlock(basic_block)**

  添加基本块到CDFG。

  **参数**:
  - `basic_block` (BasicBlock): 要添加的基本块对象

- **generateCFG()**

  构建控制流图(CFG)。分析基本块间的控制流关系，并在图中添加适当的边。

- **generateDFGs()**

  为所有基本块构建数据流图。

  **返回值**: dict: 包含所有基本块的字典

#### 内部结构示例

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



## scheduler列表调度

scheduler.py 模块实现了针对控制数据流图(CDFG)的ASAP(尽可能早)调度算法，将操作分配到适当的时间周期并考虑资源约束。

### 常量

#### 操作类型常量

```python
OP_ASSIGN = 0  # 赋值操作
OP_ADD = 1     # 加法
OP_SUB = 2     # 减法
OP_MUL = 3     # 乘法
OP_DIV = 4     # 除法
OP_LOAD = 5    # 加载
OP_STORE = 6   # 存储
OP_BR = 7      # 分支跳转
OP_LT = 8      # 小于比较
OP_GT = 9      # 大于比较
OP_LE = 10     # 小于等于
OP_GE = 11     # 大于等于
OP_EQ = 12     # 等于比较
OP_PHI = 13    # φ函数
OP_RET = 14    # 返回
```

#### 资源与延迟定义

- `RESOURCE`: 每种操作类型可用的硬件资源数量
- `DELAY`: 每种操作类型的执行延迟（周期数）

### 函数

#### initializeSchedulingData(bb)

初始化调度所需的数据结构。

**参数**:
- `bb` (BasicBlock): 基本块对象

**返回**:
- `in_degree` (dict): 每个操作的入度
- `op_schedule` (dict): 操作的调度结果，键为操作索引，值为分配的周期
- `resource_remain` (dict): 各资源类型的剩余可用数量

#### scheduleOperations(bb, in_degree, op_schedule, resource_remain)

使用ASAP算法调度操作。

**参数**:
- `bb` (BasicBlock): 基本块对象
- `in_degree` (dict): 每个操作的入度
- `op_schedule` (dict): 操作的调度结果
- `resource_remain` (dict): 各资源类型的剩余可用数量

**返回**:
- `op_schedule` (dict): 更新后的调度结果

#### processBranchInstructions(bb, op_schedule)

处理跳转指令（OP_BR），确保其在所有其他操作完成后执行。

**参数**:
- `bb` (BasicBlock): 基本块对象
- `op_schedule` (dict): 操作的调度结果

**返回**:
- `op_schedule` (dict): 更新后的调度结果

#### convertCycleList(op_schedule)

将调度结果转换为周期列表格式。

**参数**:
- `op_schedule` (dict): 操作的调度结果，键为操作索引，值为分配的周期

**返回**:
- `cycle_list` (list): 周期列表，每个元素是一个周期中的操作索引列表

#### allocateResources(cycle_list, bb)

为每个操作分配资源。

**参数**:
- `cycle_list` (list): 周期列表
- `bb` (BasicBlock): 基本块对象

**返回**:
- `final_cycles` (list): 分配资源后的周期列表，格式为`[[(op_idx, device_idx), ...], ...]`

#### scheduleASAP(self)

使用ASAP算法对CDFG进行调度。这是添加到CDFG类的方法。

**返回**:
- 无明确返回值，但会设置`self.schedule`属性

#### addScheduler(classObj)

将调度功能添加到类对象（通常是CDFG类）。

**参数**:
- `classObj` (class): 要添加调度功能的类对象，通常是CDFG类

**返回**:
- 无

### 数据结构

调度结果格式
```
{
  "基本块标签1": [
    [(操作索引, 设备索引), ...],  # 周期0
    [(操作索引, 设备索引), ...],  # 周期1
    ...
  ],
  "基本块标签2": [ ... ],
  ...
}


# High Level Synthesis

## Log

### 4.13 7d0aa1e35c641c45da399ede003244ad610a8026
- 添加PJ1的作业描述
- 添加老师提供的hls文件夹及其内容
- 添加`autorun.sh`文件以运行hls目录下的文件

## 4.14 edb1c4dfac31561e9d0f2a11a7018eda6220cbfe
- 添加`cdfg_generator.py`生成cdfg内容
- 添加`scheduler.py`文件

## 4.14 4f84ac81755071321331e4650a366d2ba86ce010
- 将`hls`文件夹更名为`parser`
- 修改`autorun.sh`文件的内容，完善其内容的严谨性，可运行`parser`目录下的cpp文件，并运行`cdfgGenerator.py`的文件，输出相关内容
- 将`cdfg_generator.py`文件更名为`cdfgGenerator.py`，并完善其中的内容，使结构性更强
- 为`cdfgGenerator.py`文件撰写接口文档`cdfg_IO_port.md`
- 创建`log.md`
- 添加`readme.md`

## 4.15 20c863d9a83457209e3990b70c0dde619028a762
- czh补一下日志

## 4.15 014d450d6568e78a4d4c98efe0937f0e0f80a55c
- 添加`main.py`，运行python文件
- 整理`scheduler.py`列表调度算法的代码
- 将`scheduler.py`和`cdfgGenerator.py`中的所有函数改为驼峰命名法
- 修改接口文档，删除不必要的函数说明，增添列表调度算法说明。
- 修改`autorun.sh`，直接调用`main.py`
- 修改文件夹结构，`python`文件统一放在`/hls`目录下，`main.py`放在PJ1目录下

## 4.15 bff7cc1be066a1e7098f622812d18dfa1bcfc96c
- 在测试文件中增加`gcd.ll`及`sum.ll`
- 修改`autorun.sh`文件，使输出的parserResult文件名与输入的文件相关
- 在IO port的修改CDFG和BasicBlock的内部结构示例

## 4.16 324a523cccb5fd1a7629d30c8acc3b8bbdb5cf3d
- 将标准RTL输出放到`/output/RTL`下
- 添加verilog编译文件`output/RTL/compiler.sh`，并将标准RTL的波形图输出放在`/output/RTL/wave`下
- 将所有parseResult放在`output/parseResult`下

## 4.16 
- 增加`registerAllocator`功能
- 更改`cdfgGenerator`和`scheduler`的内容，将输出统一到`output/outputFlow.txt`下
- 更新`scheduler.py`，可以不在最后一个周期调度分支指令

## 4.17 ec9f37dad08e3115d83828b3c3e7642d54205f87
- 更改`cdfgGenerator.py`和`scheduler.py`中的一小部分代码表述

## 4.19 9e67cd1ff66209ccf464150356556e090359c636
- 微改`autorun.sh`，在终端中输出`main.py`运行成功的信息
- 更改`main.py`，import `registerAllocator.py`；通过运行`sh autorun.sh example/xxx.ll `
可以直接得到CDFG、调度结果、全局变量、寄存器生存周期和染色结果等信息。
- 更改`scheduler.py`中的`schedulePrinter`

## 4.20 f7265a1046df242d225cba8afc887fdaba3204fc
- 改了`cdfgGenerator.py`的注释和输出为英文
- 在`resourceAllocator.py`中增加对冗余寄存器的合并函数
- 对`resourceAllocator.py`中重复调用的函数进行删除。对于反复调用函数的问题进行了优化。所有的函数不再采用`return`结果的方法进行数据传递，而是将数据存储在`CDFG`类中。将所有函数整理到同一`registerAllocator`函数中，可以在`main.py`中统一调用。
- 对输出文件进行名字修改，输出文件名与输入文件相关
- 将Resource和Delay同一放到`resourceData.py`中

## 4.22 b65f4653db758a2d05a464e9ee081c3f339cd1ba
- 创建`genFSM.py`，用于从得到的CDFG、调度结果、全局变量、寄存器生存周期和染色结果等信息直接生成verilog代码。
- `genFSM.py`包含两个类：VerilogSyntax和VerilogGenerator。前者主要用于基本的Verilog语法生成，后者主要用于生成verilog代码。VerilogGenerator主要使用三段式FSM生成进行撰写，主要部分有生成端口变量、生成局部/全局寄存器、根据控制流图生成状态更新逻辑、根据调度结果生成分支逻辑以及生成控制逻辑等内容。
- `genFSM.py`中同时添加verilogPrinter()方法，用于最后打印verilog代码至指定文件。
- 修改`main.py`，导入genFSM模块并将VerilogSyntax和VerilogGenerator实例化，并最终在指定路径文件中输出verilog代码。
- 修改`registerAllocator.py`，添加了printRegisterMerging()方法，用于在`outputFlow.txt`中打印merge过后的寄存器分配情况。

## 4.22 5dae65de8bfeca9e9d5a4014b647efff854d4b78
- 修改`registerAllocator.py`中`merge_registers`函数，使其功能更加准确，解决在`sum.ll`实例中错误合并的问题
- 统一`outputFlow.txt`输出到`output/outputFlow/`文件夹下
- `main.py`中默认读入文件的改为由`defaultPath`设定，保证终端打印的读入文件和实际读入文件一致

## 4.22 e6cdbaa1c3532aac2823cdfd9fdb024446ccdb07
- 更新`README.md`

## 4.23 5504d4b253f2b1facc376f4fb2ccaa571289a8b9
- 实现`genFSM.py`的基础1.0版本，可以跑通，但是代码风格有待调整修改；三段式FSM主要面临组合逻辑和时序逻辑不对齐等重大问题，所以在最后的代码中直接使用一个always块生成所有的内容。
- 对`genFSM.py`中的相关函数进行重构和添加，将原来的三段式写法`gen_state_update`、`gen_br_counter`、`gen_control_logic`合并成`gen_timing_logic`，并在其中调用`gen_control_logic`以实现想要达成的目的。
- `genFSM.py`中的`op_translation`method补全，这个方法主要用于实现给定基本块、给定周期数，将特定的指令转换成verilog代码。
- `genFSM.py`添加`gen_assign_logic`method，主要用于对有`int`类型返回值的函数，对输出端口的return_val进行赋值；以及对在branch指令中的条件变量进行赋值。
- 修改`registerAllocator.py`中的`get_global_variables`method，将输出变量从全局寄存器中删去（否则在之后生成verilog代码中会在input wire和reg中重复生成该变量，导致问题）
- 在`resourceData.py`中定义数值到常量名称的映射。

## 4.23 00f2c657eae549887efc7cd7e4d69ada5f4be14d
- 整体进行微调

## 4.23 33f2aa459e0d7cb0d1c8ac64b37a16fade940c65
- 整体把所有文件提到根目录下，去除PJ1目录
- 微调`genFSM.py`，生成的Verilog文件从`example/testbench/`目录下读取SRAM
- 更新`autorun.sh`，可以一步到位生成波形文件，outputFlow、parseResult、verilog_code、waveform分别放在四个目录下，不含其他杂质。可以定义输出目录，默认为`output/`
- 删除现有`output`目录改为`sampleOutput`，存放三个文件的输出。
- 修改`main.py`，可以指定输出文件目录，当无指定的输出目录时，默认为输入文件的爷爷目录

## 4.23 f3aa0c462fc62e440ad82886f6d2219db07d3962
- 添加parser下的`./hls`，可以直接调用。如果`./hls`不存在再make。可以节省时间。删掉`make clean`，让`hls`可执行文件反复使用
- 在`main.py`中增加运行时间的输出
- 增加`test.sh`，自动运行三个测试文件，并将输出存储在`testOutput`目录下。在`README.md`中添加这一部分的描述。
- 修改`autorun.sh`中关于输出目录最后`/`符号的问题。

## 4.25
- polish一下`README.md`，添加了生成testbench的部分
- 把sum的函数名改为小写
- 撰写`testbenchGenerator.py`
- 将SRAM文件按照使用它们的函数放到了`testbench/`的不同文件夹下
- 修改`genFSM.py`，详细读入SRAM文件的地址。

## 4.25
-修改了prototype分支下的`register_allocator.py`，修改内容如下：
1. 发现`get_local_variable_liveness`存在漏洞，即从上向下计算生存周期，这可能使局部变量在还未完成使用时被错删，应当从下往上，更正后的方法`get_local_variable_liveness_ll`（见142行）
2. 发现`register_coloring`部分不够严谨，当跨块间无法通过挪动、交换位置来对齐寄存器时，需要新建一个寄存器，原先的代码仅处理正在校验的位置，（即仅将正在检验的两个块间的该变量挪至新寄存器），但严谨的做法是遍历所有基本块，将其中所有该变量挪动到新寄存器并从旧寄存器中删除（见366-374行）
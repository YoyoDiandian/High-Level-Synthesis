# 高层次综合

## 日志

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
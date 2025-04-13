# 高层次综合课程Project

可以从(一)或(二)中选择一个来实现，(一）的参考代码见文件->高层次综合project(一）附件。

## 一、基于LLVM语法的project

1. 语言输入
    - 变量：
    仅支持int变量，支持数组，定义与c语言类似。如int a, int a[]

    - 函数定义：
    define int foo(int a, int b);

    - 返回值可以是int和void。

    - 操作定义：
    
        load：从数组中加载一个数据，如b=load(a, 10)就是加载a[10]到b

        store: 将数据存储到数组：如store(a, 10, c)，将c存储到a[10]

    ```
    =：赋值
    +: c = a+b
    -: c = a-b;
    *: c = a*b;
    /: c = a/b;
    ==: cond = a==b;
    <: cond = a < b;
    >: cond = a> b;
    >=: cond = a>=b;
    <=: cond = a<=b;
    br:
        br label：无条件跳转
        br cond label1 label2：有条件跳转‘
    phi: 从不同模块中选择不同的变量值：phi(value1, block_label1, value2, block_label2, ...);
    函数入口的label默认为0。
    return：返回或返回值。
    ```
 

2. 语言实例
    ```
    define int dotprod(int a[], int b[], int n)
        c = 0;
    start:
        i = phi(0, 0, i_inc, calc);
        cl = phi(c, 0, cr, calc);
        cond = i >= n;
        br cond ret calc;

    calc:
        ai = load(a, i);
        bi = load(b, i);
        ci = ai * bi;
        cr = cl + ci;
        i_inc = i + 1;
        br start;

    ret:s
        return cl;
    ```

3. project要求
    - 以上述IR作为输入，我们提供基本的IR的parser
    - 根据上述IR，完成调度、寄存器及操作的绑定、控制逻辑综合，函数输入的数组综合为SRAM存储器，需要根据load/store指令来读写存储器数据。最终生成RTL代码。基本计算操作可以调用RTL计算模块，或直接使用原始操作符
    - 不超过3位同学为1组
    - 最终提交代码、技术报告(包括测试结果)，并注明每位同学贡献
    - 如有同学希望单独开发某个模块作为project，可单独与我联系。
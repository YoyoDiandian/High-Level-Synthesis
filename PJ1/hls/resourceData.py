OP_ASSIGN = 0
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4
OP_LOAD = 5
OP_STORE = 6
OP_BR = 7
OP_LT = 8
OP_GT = 9
OP_LE = 10
OP_GE = 11
OP_EQ = 12
OP_PHI = 13
OP_RET = 14

# 定义数值到常量名称的映射
OP_TYPE_MAP = {
    0: "OP_ASSIGN",
    1: "OP_ADD",
    2: "OP_SUB",
    3: "OP_MUL",
    4: "OP_DIV",
    5: "OP_LOAD",
    6: "OP_STORE",
    7: "OP_BR",
    8: "OP_LT",
    9: "OP_GT",
    10: "OP_LE",
    11: "OP_GE",
    12: "OP_EQ",
    13: "OP_PHI",
    14: "OP_RET"
}

# 定义计算资源
RESOURCE = [
    1, # OP_ASSIGN
    1, # OP_ADD
    1, # OP_SUB
    1, # OP_MUL
    1, # OP_DIV
    1, # OP_LOAD
    1, # OP_STORE
    1, # OP_BR
    1, # OP_LT
    1, # OP_GT
    1, # OP_LE
    1, # OP_GE
    1, # OP_EQ
    1, # OP_PHI
    1, # OP_RET
]

# 定义延迟
DELAY = [
    1, # OP_ASSIGN
    1, # OP_ADD
    1, # OP_SUB
    5, # OP_MUL
    10, # OP_DIV
    2, # OP_LOAD
    2, # OP_STORE
    1, # OP_BR
    1, # OP_LT
    1, # OP_GT
    1, # OP_LE
    1, # OP_GE
    1, # OP_EQ
    1, # OP_PHI
    1, # OP_RET
]
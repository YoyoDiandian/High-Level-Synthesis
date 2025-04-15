#!/bin/bash

echo "开始编译"
FILE="${1%.v}"
WAVE_PATH="wave"
iverilog -o $FILE ./"$FILE".v ./tb_"$FILE".v SRAM.v
echo "编译完成"

echo "生成波形文件"
vvp -n $FILE
cp "$WAVE_PATH/$FILE.vcd" $FILE.lxt

rm -f *.lxt $FILE

echo "打开波形文件"
# open wave.vcd
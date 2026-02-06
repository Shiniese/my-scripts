#!/bin/bash

# ==============================================================================
# 脚本名称：make_duplex_pdf.sh

# 功能描述：
#   该脚本将多个 PDF 文件按“双面打印”（Duplex Printing）要求进行处理：
#   - 所有页数为奇数的 PDF 文件，会与一个空白页（A4）合并，形成“单面+空白”结构；
#   - 所有页数为偶数的 PDF 文件保持原样；
#   - 最终将所有处理后的 PDF 文件按顺序合并为一个 PDF，适用于双面打印（如 A4 纸张）。
#   例如：一个 3 页的 PDF 会被补成 4 页（3页内容 + 1页空白），以便双面打印时“正反面”对齐。
#
# 使用场景：
#   - 打印报告、简历、合同等文档时，避免因页数奇偶不匹配导致打印错位。
#   - 适用于需要“双面打印”的办公场景，尤其在使用激光打印机或复印机时。
#
# 依赖项：
#   - ghostscript (gs): 用于生成空白 PDF 页（A4 大小，5950x8420 像素）。
#     安装命令（Ubuntu/Debian）: sudo apt install ghostscript
#   - pdfinfo: 用于获取 PDF 文件的页数。
#   - pdfunite: 用于合并多个 PDF 文件。
#     安装命令（Ubuntu/Debian）: sudo apt install poppler-utils
#
# 输入参数：
#   $@: 一个或多个 PDF 文件路径（如 file1.pdf file2.pdf ...）
#     示例：./make_duplex_pdf.sh report1.pdf cover.pdf data.pdf
#
# 输出文件：
#   final_merged_duplex.pdf
#     一个最终合并的 PDF，页数为偶数，适合双面打印。
#
# 执行流程：
#   1. 检查是否提供了输入文件，若无则提示用法并退出。
#   2. 使用 ghostscript 创建一个临时空白 A4 页面（/tmp/blank_page.pdf）。
#   3. 遍历每个输入文件：
#      - 通过 pdfinfo 获取页数。
#      - 若页数为奇数 → 与空白页合并（补一页）。
#      - 若页数为偶数 → 保持原文件不变。
#   4. 将所有处理后的文件（含补白）按顺序合并为最终输出文件。
#   5. 清理临时文件（临时目录和空白页）。
#
# 错误处理：
#   - 若未安装 ghostscript，会提示用户安装并退出。
#   - 若输入文件不存在或无法读取，脚本不会处理，但会因 pdfinfo 失败而报错（需用户自行检查）。
#   - 若文件路径错误或权限不足，脚本会因命令失败而中断。
#
# 注意事项：
#   - 该脚本假设所有 PDF 文件是 A4 尺寸，且内容布局合理。
#   - 补白页是“空白页”，不会影响内容，但会占用一张纸的反面。
#   - 该脚本不会修改原始文件，所有操作均在临时文件中完成。
#
# 示例运行：
#   $ ./make_duplex_pdf.sh contract.pdf proposal.pdf
#   输出：final_merged_duplex.pdf
#   提示：打印时选择“双面打印”模式，即可正确打印。
#
# 重要提示：
#   ✅ 本脚本是为“双面打印”设计，确保每张纸的正反面内容对齐。#
# ==============================================================================

# 输出文件名
OUTPUT_FILE="final_merged_duplex.pdf"

# 检查是否提供了输入文件
if [ "$#" -eq 0 ]; then
    echo "用法: $0 file1.pdf file2.pdf ..."
    exit 1
fi

# 1. 创建一个临时的空白 PDF (A4大小)
# 这里使用 ghostscript 创建一个空白页，如果没有 gs，也可以找一个现成的 blank.pdf
if command -v gs >/dev/null 2>&1; then
    gs -sDEVICE=pdfwrite -o /tmp/blank_page.pdf -g5950x8420 -c showpage
else
    echo "错误: 需要安装 ghostscript 来生成空白页 (sudo apt install ghostscript)"
    exit 1
fi

BLANK="/tmp/blank_page.pdf"
TEMP_DIR=$(mktemp -d)
MERGE_LIST=()

echo "正在分析并处理 PDF 文件..."

# 2. 循环处理每一个输入文件
count=1
for f in "$@"; do
    # 获取页数
    pages=$(pdfinfo "$f" | grep "Pages" | awk '{print $2}')
    
    # 计算是否为奇数
    if [ $((pages % 2)) -ne 0 ]; then
        echo "文件 [$f] 是奇数页 ($pages 页)，正在补齐..."
        
        # 将当前文件和空白页合并到一个临时文件
        temp_file="$TEMP_DIR/fixed_${count}.pdf"
        pdfunite "$f" "$BLANK" "$temp_file"
        
        # 将处理后的临时文件加入列表
        MERGE_LIST+=("$temp_file")
    else
        echo "文件 [$f] 是偶数页 ($pages 页)，保持不变。"
        MERGE_LIST+=("$f")
    fi
    ((count++))
done

# 3. 最终合并
echo "正在合并所有文件到 $OUTPUT_FILE ..."
pdfunite "${MERGE_LIST[@]}" "$OUTPUT_FILE"

# 4. 清理临时文件
rm -rf "$TEMP_DIR"
rm -f "$BLANK"

echo "完成！已生成适合双面打印的文件：$OUTPUT_FILE"
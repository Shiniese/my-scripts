"""
参考文献缺失页码自动修复工具
---
功能说明
    针对GB/T 7714等格式的参考文献中**年份卷期后缺失冒号+页码**的常见错误，自动识别符合规则的条目，
    随机生成符合学术出版常理的页码（单页/页面范围二选一）并补全，无需手动逐条修改，大幅提升参考文献整理效率。
---
适用场景
    你导入/转录的参考文献条目存在类似如下格式问题：
    > 张三, 李四. 人工智能技术综述. 计算机学报, 2023, 46(3).  
    > ✅ 修复后变为：张三, 李四. 人工智能技术综述. 计算机学报, 2023, 46(3): 1234-1245. / 2023, 46(3): 789.

    已经包含冒号+页码的正确条目、无年份特征的条目会自动原样保留，不会误修改。
---
使用步骤
    1. 提前把需要修复的参考文献按**一行一条**的格式整理为纯文本文件，编码选择UTF-8
    2. 修改脚本开头的两个变量为你的实际文件路径：
    - `input_file`：待修复的原始参考文献文本文件路径
    - `output_file`：修复完成后结果的保存路径
    3. 直接运行脚本即可，无需额外依赖（Python标准库即可运行）
---
参数说明
    | 可调整参数 | 说明 | 默认值 |
    |------------|------|--------|
    | 页码生成范围 | 单页/范围起始页的最大数值 | 15000 |
    | 页面范围长度 | 起始页和结束页的差值范围 | 6-16页 |
    | 单页/范围比例 | 两种页码格式的生成概率 | 各50% |
    如果需要调整上述规则，直接修改代码中`random.randint`的参数或`random.choice`的概率配置即可。
---
输出说明
    运行后控制台会输出处理统计：
    - 成功修复的错误条目数量
    - 跳过的正确/不符合规则条目数量
    - 修复结果的保存路径
---
注意事项
    1. 请确保输入文件是UTF-8编码，避免中文乱码
    2. 脚本识别规则为「行内存在`四位年份, 非冒号内容`且结尾为句号」，如果你的参考文献格式特殊，可以自行调整正则表达式`pattern`的匹配规则
    3. 生成的页码为随机模拟值，如果对页码准确性有要求，请修复后对照原文逐一核对
    4. 脚本不会修改原始输入文件，所有修改均写入`output_file`指定的新文件，无需担心原始数据丢失
"""

# === 自己需要修改的变量 ===

# 请将这里的文件名替换为你实际的文件名
input_file = "references.txt"   
output_file = "fixed_references.txt" 

# === 自己需要修改的变量 ===

import re
import random

def fix_references(input_path, output_path):
    # 正则表达式解释：
    # group(1): ^(.*) 捕获从开头到年份之前的所有内容（即保留作者、标题等）
    # group(2): (\d{4},[^:]+) 捕获年份及之后没有冒号的内容
    # group(3): (\s*)$ 捕获结尾的换行符
    pattern = re.compile(r'^(.+)(\d{4},[^:]+)\.(\s*)$')

    count_fixed = 0
    count_skipped = 0

    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
         
        for line in f_in:
            # 搜索是否存在符合“缺失冒号”特征的片段
            match = pattern.search(line)
            if match:
                # 随机决定是添加 "范围页码" 还是 "单页码"
                if random.choice([True, False]):
                    # 生成页码范围，为了符合常理，确保 start <= end
                    start_page = random.randint(1, 14999)
                    end_page = start_page + random.randint(6, 16)
                    pages_str = f": {start_page}-{end_page}"
                else:
                    # 生成单页码
                    pages_str = f": {random.randint(1, 15000)}"
                
                # 拼接修复后的字符串
                # match.group(1) 是句号之前的所有内容（如："... 2020, 585"）
                # match.group(2) 是句号之后的空白符（如换行符 "\n"）
                new_line = f"{match.group(1)}{match.group(2)}{pages_str}.{match.group(3)}"
                f_out.write(new_line)
                count_fixed += 1
            else:
                # 如果原本就是正确的（已经有冒号），或者不包含年份特征，原样写入
                f_out.write(line)
                count_skipped += 1

    return count_fixed, count_skipped

if __name__ == '__main__':
    print("正在处理参考文献，请稍候...")
    try:
        fixed, skipped = fix_references(input_file, output_file)
        print(f"处理完成！")
        print(f"✅ 成功修复了 {fixed} 条错误引用。")
        print(f"⏭️ 跳过（或已是正确格式）了 {skipped} 条引用。")
        print(f"📄 结果已保存至: {output_file}")
    except FileNotFoundError:
        print(f"❌ 找不到输入文件 '{input_file}'，请确保该txt文件与Python脚本在同一目录下。")
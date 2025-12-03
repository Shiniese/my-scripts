"""
XRD谱图可视化脚本

功能：读取多个XRD.txt文件，按2θ-强度绘制谱图，不同样品用不同颜色区分（处理/原始）。

配置：
- FILE_TO_LABEL_DICT：文件名 → 样品标签
- FILE_TO_PALETTE_DICT：文件名 → 颜色（深色为处理，浅色为原始）

流程：
1. 读取当前目录所有.txt文件，按文件名排序
2. 为每组样品添加垂直偏移，避免线条重叠
3. 用seaborn绘制带颜色标签的XRD曲线
4. 保留2θ轴标签，隐藏y轴刻度，自动生成图例
5. 保存为xrd_patterns.png，显示图像

输出：xrd_patterns.png（高分辨率，Times New Roman字体）

注意事项：
- 文件需为格式：2theta intenisty（空格分隔）
- 支持文件名匹配，确保字典完整性
""" 


# === 自己需要修改的变量 ===
# 为每个样品重命名标签
FILE_TO_LABEL_DICT = {
    'XRD-MZ-700.txt': 'MZ@700°C',
    'XRD-MZ-raw.txt': 'MZ@raw',
    'XRD-SD-700.txt': 'SD@700°C',
    'XRD-SD-raw.txt': 'SD@raw',
    'XRD-TJ-700.txt': 'TJ@700°C',
    'XRD-TJ-raw.txt': 'TJ@raw'
}
# 为每组样品定义颜色（同类颜色相近），处理过的样品为深色，raw为浅色
FILE_TO_PALETTE_DICT = {
    'XRD-MZ-700.txt': '#4a83c3',           # 深天蓝（保持原色，经典）
    'XRD-MZ-raw.txt': '#6b8ebe',           # 浅天蓝（与深蓝形成柔和过渡）
    'XRD-SD-700.txt': '#4b8a62',           # 深青绿（自然、专业）
    'XRD-SD-raw.txt': '#98d8b7',           # 浅青绿（清新，对比自然）
    'XRD-TJ-700.txt': '#e65100',           # 深橙红（温暖、有冲击力）
    'XRD-TJ-raw.txt': '#ff8c69',           # 浅橙红（柔和，带一点暖意）
}
# 每条曲线之间的垂直偏移量
OFFSET_STEP = 500  # 可调整，比如 300 或 800
# === 自己需要修改的变量 ===

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# 设置Seaborn风格
sns.set(style="whitegrid", font_scale=1.3)

# 设置默认字体
plt.rcParams['font.family'] = 'Times New Roman'

# 获取当前目录下的所有txt文件，并排序
files = sorted([f for f in os.listdir('.') if f.endswith('.txt')], reverse=True)

assert len(files) == len(FILE_TO_LABEL_DICT), (
    f"\n❌ 文件数量不匹配！\n"
    f"❌ 实际文件数: {len(files)}\n"
    f"❌ 字典中定义的文件数: {len(FILE_TO_LABEL_DICT)}\n"
    f"❌ 存在问题的文件名: {set(files) ^ set(FILE_TO_LABEL_DICT.keys())}"
)

# 创建画布
plt.figure(figsize=(10, 6))

# 绘制每个样品
for i, file in enumerate(files):
    # 读取文件
    data = pd.read_csv(file, sep=r'\s+', header=None, names=['2theta', 'intensity'])
    
    # 应用垂直偏移
    data['intensity_shifted'] = data['intensity'] - i * OFFSET_STEP
    
    # 绘制曲线（不显示具体数值，只看形状）
    sns.lineplot(
        x='2theta', y='intensity_shifted',
        data=data,
        color=FILE_TO_PALETTE_DICT[file],
        label=FILE_TO_LABEL_DICT[file],
        linewidth=1.5
    )

# 隐藏 y 轴的刻度
plt.yticks([])

# 图像美化
plt.xlabel("2θ (°)", fontweight='bold')
plt.ylabel("Intensity (a.u.)", fontweight='bold')

plt.legend()
plt.tight_layout()

# 保存与显示
plt.savefig("xrd_patterns.png", dpi=300)
plt.show()


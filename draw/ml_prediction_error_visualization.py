"""
本脚本用于可视化机器学习模型的预测结果与真实值的对比，并同时展示对应的误差百分比。

功能说明：
    1. 输入数据包含样本名称（Sample）、真实值（True）和预测值（Pre）；
    2. 自动计算每个样本的绝对误差百分比：|True - Pre| / True * 100%；
    3. 使用双Y轴图表进行可视化：
        - 左Y轴：柱状图显示真实值（蓝色），并在相同位置用红色五角星标记预测值；
        - 右Y轴：绿色柱状图显示对应样本的误差百分比；
    4. 图表美化包括：
        - Times New Roman 字体；
        - 网格线、去顶边框（despine）；
        - 合并左右图例，清晰标注；
        - 自动调整布局与坐标轴范围，确保可读性。

使用方法：
    - 修改顶部 `data` 字典中的 'Sample'、'True' 和 'Pre' 列表，填入自己的数据；
    - 直接运行本脚本即可生成结果图。

依赖库：
    - matplotlib
    - seaborn
    - pandas
    - numpy
"""

# === 自己需要修改的变量 ===
# 1. 准备数据
data = {
    'Sample': ['TJ-700', 'MZ-700', 'SD-700'],
    'True': [26.47, 7.86, 19.27],
    'Pre': [31.496091, 7.654549, 15.388377]
}
# === 自己需要修改的变量 ===

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


df = pd.DataFrame(data)
# 计算误差百分比
df['Error%'] = np.abs(df['True'] - df['Pre']) / df['True'] * 100

# 2. 设置绘图风格
sns.set_theme(style="ticks")
plt.rcParams['font.family'] = 'Times New Roman'
fig, ax1 = plt.subplots(figsize=(10, 6), dpi=120)

# 设置柱状图的宽度和位置
x = np.arange(len(df['Sample']))
width = 0.35 

# 3. 绘制左轴 (ax1): 真实值与预测值对比
# 绘制真实值的柱状图
bar1 = ax1.bar(x - width/2, df['True'], width, label='True Value', 
               color=sns.color_palette("Blues_d")[1], edgecolor='black', alpha=0.8)

# 在对应的位置打上五角星（预测值）
star = ax1.scatter(x - width/2, df['Pre'], marker='*', s=200, 
                   color='#D62728', label='Predicted Value', zorder=3, edgecolors='black')

# 4. 绘制右轴 (ax2): Error %
ax2 = ax1.twinx()
bar2 = ax2.bar(x + width/2, df['Error%'], width, label='Error', 
               color=sns.color_palette("Greens_d")[1], edgecolor='black', alpha=0.7)

# 5. 细节美化
# 设置坐标轴标签
ax1.set_xlabel('Sample Name', fontsize=12, fontweight='bold')
ax1.set_ylabel('Value (True/Pre)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Error Percentage (%)', fontsize=12, fontweight='bold', color='green')

# 设置 X 轴刻度
ax1.set_xticks(x)
ax1.set_xticklabels(df['Sample'])

# 设置 Y 轴范围（让图表看起来更疏朗）
ax1.set_ylim(0, max(df['True'].max(), df['Pre'].max()) * 1.5)
ax2.set_ylim(0, df['Error%'].max() * 1.5)

# 合并图例
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left', frameon=True)

# 辅助线
ax1.grid(axis='y', linestyle='--', alpha=0.6)
sns.despine(top=True, right=False)

plt.title('Machine Learning Prediction Results and Error Analysis', fontsize=14, pad=20)
plt.tight_layout()

# 保存与显示
plt.savefig("ml_prediction_error_visualization.png", dpi=300)
plt.show()
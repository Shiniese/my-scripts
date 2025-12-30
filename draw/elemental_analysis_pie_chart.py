"""
================================================================================
🎯 自定义元素分析数据可视化脚本（单文件执行版）

📌 功能说明：
    - 输入原始元素质量百分比数据（如 C, H, S, O, N）
    - 自动对“平行样”进行平均处理
    - 将各元素比例归一化为总和为 100%
    - 绘制美观的“甜甜圈饼图”（Donut Chart）展示每个样品的元素分布
    - 支持中英文双语注释，便于阅读与维护

✅ 使用场景：
    - 化学、材料、地质等领域的样品元素分析结果展示
    - 科研报告、论文图表快速生成

🔧 依赖库：
    - pandas：用于数据处理
    - matplotlib：用于绘图

📌 说明：
    - 本脚本为“单文件可执行”脚本，无需额外配置，直接运行即可。
    - 所有变量和逻辑均可根据实际数据修改。
    - 输出文件：elemental_analysis_pie_chart.png（保存在当前目录）

💡 提示：
    - 若需调整样式（如字体、颜色、标题），可修改对应参数。
================================================================================
"""

# === 自己需要修改的变量 ===

# 1. 准备数据
data = {
    'Samples': ['MZ', 'MZ', 'TJ', 'TJ'],
    'N(%)': [0.82, 0.86, 0.78, 0.82],
    'C(%)': [59.34, 59.69, 56.40, 56.69],
    'H(%)': [1.01, 0.95, 0.85, 0.82],
    'S(%)': [0.31, 0.29, 0.41, 0.45],
    'O(%)': [11.01, 11.04, 9.59, 9.72]
}

# === 自己需要修改的变量 ===

import pandas as pd
import matplotlib.pyplot as plt


df = pd.DataFrame(data)

# 2. 对平行样取平均
df_mean = df.groupby('Samples').mean().reindex(df['Samples'].unique())
print("--- 平行样平均值 (原始比例) ---")
print(df_mean)

# 3. 按比例扩充到总和为 100% (归一化)
# 计算每行的当前总和
row_sums = df_mean.sum(axis=1)
# 除以总和并乘以 100
df_normalized = df_mean.div(row_sums, axis=0) * 100
print("\n--- 归一化后数据 (总和 100%) ---")
print(df_normalized)

# 4. 绘制美观的饼图
plt.rcParams['font.sans-serif'] = ['Times New Roman']  
plt.rcParams['axes.unicode_minus'] = False 

# 定义一套舒适的配色 (莫兰迪色系风格)
colors = ['#FFBE7A', '#8ECFC9', '#FA7F6F', '#82B0D2', '#BEB8DC']
elements = df_normalized.columns

# 创建画布
fig, axes = plt.subplots(1, len(df_normalized), figsize=(15, 6))
# fig.suptitle('Normalized Distribution Plot of Elemental Analysis for Each Sample', fontsize=16, y=1.05)

for i, (idx, row) in enumerate(df_normalized.iterrows()):
    ax = axes[i]
    
    # 可选择过滤掉数值为0的部分，避免标签重叠
    valid_values = row[row >= 0]
    valid_labels = valid_values.index
    
    # 绘制饼图 (使用甜甜圈样式，看起来更现代)
    wedges, texts, autotexts = ax.pie(
        valid_values, 
        labels=valid_labels,
        autopct='%1.1f%%', 
        startangle=90,
        colors=colors,
        pctdistance=0.85, # 百分比距离圆心的距离
        textprops={'fontsize': 11}
    )
    
    # 添加中间的白色圆圈，做成甜甜圈效果
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    ax.set_title(f'{idx}', fontsize=14, fontweight='bold')
    
    # 优化字体颜色
    for text in texts:
        text.set_color('#333333')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

plt.tight_layout()
plt.savefig('elemental_analysis_pie_chart.png', dpi=300, bbox_inches='tight')
plt.show()

"""
========================================
特征重要性按类别分类可视化脚本
========================================

功能说明：
    本脚本用于可视化“特征重要性”在不同类别中的分布情况。
    通过横向条形图展示各特征的重要性百分比，右侧下角嵌入一个扇形图，展示各类别的总重要性占比。

依赖库：
    - pandas：数据处理
    - matplotlib：绘图
    - mpl_toolkits.axes_grid1.inset_locator：插入子图（用于扇形图）

运行方式：
    将本脚本保存为 .py 文件，运行即可生成图片文件：
        Feature_Importance_By_Category.png

输出结果：
    - 一张包含横向条形图与右下角扇形图的 PNG 图像文件
    - 图中使用 Times New Roman 字体，风格专业、美观

注意事项：
    - 所有特征重要性值必须为正数（本脚本已过滤掉0值）
    - 类别映射关系需与数据一致，确保分类准确
    - 若需修改特征或类别，请在代码开头“需要修改的变量”部分进行调整
    
========================================
"""

# === 自己需要修改的变量 ===

# 1. 准备数据
data = {
    'Feature Id': [
        'O(%)/Oxygen content(%)', 'VP(cm3/g)', 'SBET(m2/g)', 'Adsorbent Loading(mg)',
        'Vmicrop(cm3/g)', 'N(%)/Nitrogen content(%)', 'Vmesop(cm3/g)', 'C(%)/Carbon content(%)',
        'pKa', 'H(%)/Hydrogen content(%)', 'Adsorbent Loading(g/L)', 'Adsorbent Pyrolysis Temperature(°C)',
        'Experiment Initial Organic Compound Concentration(mg/L)', 'DP(nm)', 'MW', 'TPSA',
        'HBD', 'Vm', 'HBA', 'logKow',
        'Adsorbent Pyrolysis Time(min)', 'Experiment Initial pH', 'Experiment Temperature(°C)', 'Nrings'
    ],
    'Importances': [
        14.851427, 10.401077, 9.857117, 9.246028,
        9.169193, 8.416188, 6.894493, 5.837758,
        4.874536, 4.052943, 3.014343, 2.779677,
        2.337460, 2.097947, 1.650998, 1.441430,
        1.052939, 0.931850, 0.659770, 0.432826,
        0.000000, 0.000000, 0.000000, 0.000000
    ]
}

category_mapping = {
    'Adsorbent Pyrolysis Time(min)': 'Biochar Physical Properties',
    'Adsorbent Pyrolysis Temperature(°C)': 'Biochar Physical Properties',
    'SBET(m2/g)': 'Biochar Physical Properties',
    'DP(nm)': 'Biochar Physical Properties',
    'VP(cm3/g)': 'Biochar Physical Properties',
    'Vmicrop(cm3/g)': 'Biochar Physical Properties',
    'Vmesop(cm3/g)': 'Biochar Physical Properties',
    'C(%)/Carbon content(%)': 'Biochar Chemical Properties',
    'H(%)/Hydrogen content(%)': 'Biochar Chemical Properties',
    'N(%)/Nitrogen content(%)': 'Biochar Chemical Properties',
    'O(%)/Oxygen content(%)': 'Biochar Chemical Properties',
    'Adsorbent Loading(mg)': 'Experimental Conditions',
    'Adsorbent Loading(g/L)': 'Experimental Conditions',
    'Experiment Initial Organic Compound Concentration(mg/L)': 'Experimental Conditions',
    'Experiment Initial pH': 'Experimental Conditions',
    'Experiment Temperature(°C)': 'Experimental Conditions',
    'logKow': 'Pollutant Properties',
    'pKa': 'Pollutant Properties',
    'MW': 'Pollutant Properties',
    'Vm': 'Pollutant Properties',
    'Nrings': 'Pollutant Properties',
    'HBD': 'Pollutant Properties',
    'HBA': 'Pollutant Properties',
    'TPSA': 'Pollutant Properties'
}

# === 自己需要修改的变量 ===

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# 设置字体为 Times New Roman
plt.rcParams['font.family'] = 'Times New Roman'

# 创建 DataFrame 并映射类别
df = pd.DataFrame(data)
df['Category'] = df['Feature Id'].map(category_mapping)

# 为了绘图美观，将数据按 Importances 升序排列（这样在 barh 中最大的会在最上面）
df = df.sort_values(by='Importances', ascending=True)

# 2. 定义颜色方案 (参考图中的粉、青、绿风格，并增加一种颜色)
colors_map = {
    'Biochar Physical Properties': '#5FBDBF',   # 青色 (参考 Proximate Composition)
    'Biochar Chemical Properties': '#84B090',   # 绿色 (参考 Ultimate Composition)
    'Experimental Conditions': '#E87A90',       # 粉色 (参考 Pyrolysis Conditions)
    'Pollutant Properties': '#F2C46D'           # 黄橙色 (新增类别)
}
df['Color'] = df['Category'].map(colors_map)
df = df[df['Importances'] > 0]

# 3. 开始绘图
fig, ax = plt.subplots(figsize=(12, 8))

# 绘制主条形图
bars = ax.barh(df['Feature Id'], df['Importances'], color=df['Color'], height=0.6)

# 添加数值标签 (在柱子右侧)
for bar in bars:
    width = bar.get_width()
    if width > 0: # 只有大于0的值才显示
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}%', 
                va='center', fontsize=10, color='black')

# 设置轴标签和样式
ax.set_xlabel('Feature Importance (%)', fontsize=14, fontweight='bold')
ax.set_xlim(0, max(df['Importances']) * 1.3) # 留出右侧空间给扇形图
ax.tick_params(axis='y', labelsize=10)

# 创建自定义图例
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=colors_map[cat], label=cat) for cat in colors_map]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.85), fontsize=14, frameon=False)

# 4. 绘制右下角的扇形图 (Inset Pie Chart)
# 计算各类别的总 Importance
category_sums = df.groupby('Category')['Importances'].sum()

# 准备扇形图数据
pie_labels = category_sums.index
pie_sizes = category_sums.values
pie_colors = [colors_map[l] for l in pie_labels]

# 在右下角创建插入轴 (x, y, width, height) 坐标是相对于父轴的
ax_inset = inset_axes(ax, width="70%", height="70%", loc='lower right', 
                      bbox_to_anchor=(0.05, 0.05, 0.9, 0.5), bbox_transform=ax.transAxes)

# 绘制扇形图
wedges, texts, autotexts = ax_inset.pie(pie_sizes, colors=pie_colors, autopct='%1.2f%%', 
                                        startangle=140, pctdistance=0.7,
                                        explode=[0.05]*len(pie_sizes), # 轻微炸开效果
                                        shadow=True)

# 调整扇形图字体样式
for text in texts:
    text.set_color('grey')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(12)
    autotext.set_weight('bold')

# 调整整体布局
plt.tight_layout()
plt.savefig("Feature_Importance_By_Category.png", dpi=300)
plt.show()

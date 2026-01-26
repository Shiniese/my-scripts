"""
=======================================
HPLC原始数据处理与吸附等温线拟合脚本
=======================================
📌 功能说明：
    本脚本用于处理HPLC原始吸附实验数据，自动完成：
    1. 数据读取与清洗（含初始浓度、峰面积等）
    2. 吸附量（Qe）与平衡浓度（Ce）计算
    3. Langmuir与Freundlich模型拟合
    4. 拟合参数输出与R²、RMSE、MAE评估
    5. 生成高质量“Qe-Ce”吸附等温线图表（支持LaTeX公式渲染）

📌 使用场景：
    适用于吸附质对吸附剂的吸附实验数据处理。

📌 输入文件格式示例：
    | initial_conc(mM) | initial_peak_area | after_peak_area |
    |------------------|-------------------|-----------------|
    | 0.1              | 1234567           | 1234            |
    | 0.2              | 1345678           | 1567            |

📌 输出内容：
    1. 新CSV文件（含计算字段）：xxx-caculated.csv
    2. 图像文件（含双模型拟合曲线）：xxx-Adsorption Isotherms.png
    3. 控制台输出：拟合参数与误差指标

📌 注意事项：
    - 请确保路径正确，文件存在且格式无误。
    - 所有变量可在顶部修改以适配不同实验。
    - 建议在Jupyter Notebook或Python环境（如Anaconda）中运行。
=======================================
"""

# === 自己需要修改的变量 ===

csv_file_path = 'TJ700-ACP-raw.csv'

BIOCHAR_TYPE = "TJ700"
POLLUTANT_NAME = "ACP"
MW = 151.16
adsorbent_conc_g_L = 5

initial_peak_area_name = "initial_peak_area"
after_peak_area_name = "after_peak_area"
initial_conc_name = "initial_conc(mM)"

# csv 文件数据形式
# | initial_conc(mM) | initial_peak_area | after_peak_area |
# |------------------|-------------------|-----------------|
# | 0.1              | 1234567           | 1234            |
# | 0.2              | 1345678           | 1567            |
# | 0.3              | 1456789           | 3456            |
# | 0.4              | 1567890           | 12345           |
# | 0.5              | 1678901           | 98765           |

# === 自己需要修改的变量 ===

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from matplotlib import rcParams


# 启用 LaTeX 渲染
rcParams['text.usetex'] = True  # 启用 LaTeX 支持
rcParams['font.size'] = 14      # 设置字体大小
# 设置图表风格
sns.set_theme(style="darkgrid")
sns.set_context("talk")

data = pd.read_csv(csv_file_path)
data['Removal Ratio'] = 1 - data[after_peak_area_name] / data[initial_peak_area_name]
data['Ce(mg/L)'] = (1 - data['Removal Ratio']) * data[initial_conc_name] * MW
data['Qe(mg/g)'] = data[initial_conc_name] * data['Removal Ratio'] * MW / adsorbent_conc_g_L
Qe = data['Qe(mg/g)']
Ce = data['Ce(mg/L)']
data.to_csv(f'{csv_file_path}-caculated.csv', index=False, encoding='utf-8')

# 定义模型函数
def langmuir_model(Ce, Qmax, b):
    return (Qmax * b * Ce) / (1 + b * Ce)

def freundlich_model(Ce, Kf, n):
    return Kf * Ce**(1/n)

# 进行Langmuir拟合
initial_guess_langmuir = [max(Qe), 1]  # 初始猜测：[Qmax, b]
params_langmuir, covariance_langmuir = curve_fit(langmuir_model, Ce, Qe, p0=initial_guess_langmuir)
Qmax_fit, b_fit = params_langmuir

# 进行Freundlich拟合
initial_guess_freundlich = [np.mean(Qe), 1]  # 初始猜测：[Kf, n]
params_freundlich, covariance_freundlich = curve_fit(freundlich_model, Ce, Qe, p0=initial_guess_freundlich)
Kf_fit, n_fit = params_freundlich

# 生成拟合曲线数据
Ce_fit = np.linspace(0, max(Ce), 100)
Qe_langmuir_fit = langmuir_model(Ce_fit, *params_langmuir)
Qe_freundlich_fit = freundlich_model(Ce_fit, *params_freundlich)

Qe_langmuir_predict = langmuir_model(Ce, *params_langmuir)
Qe_freundlich_predict = freundlich_model(Ce, *params_freundlich)
# 计算 R²
r2_langmuir = r2_score(Qe, Qe_langmuir_predict)
r2_freundlich = r2_score(Qe, Qe_freundlich_predict)
# 计算 RMSE（均方根误差）
rmse_langmuir = np.sqrt(mean_squared_error(Qe, Qe_langmuir_predict))
rmse_freundlich = np.sqrt(mean_squared_error(Qe, Qe_freundlich_predict))
# 计算 MAE（平均绝对误差）
mae_langmuir = mean_absolute_error(Qe, Qe_langmuir_predict)
mae_freundlich = mean_absolute_error(Qe, Qe_freundlich_predict)

# 输出结果
print(f"Langmuir 拟合参数:")
print(f"Qmax = {Qmax_fit:.2f} mg/g")
print(f"b = {b_fit:.4f} L/mg")
print(f"R² = {r2_langmuir:.4f}\n")

print(f"Freundlich 拟合参数:")
print(f"Kf = {Kf_fit:.2f} (mg/g)^1/n")
print(f"n = {n_fit:.2f}")
print(f"R² = {r2_freundlich:.4f}")


# draw "Qe-Ce" figure
plt.figure(figsize=(10,6))
plt.errorbar(Ce, Qe, fmt='o', ecolor='red', capsize=5, 
                color='black', label='Experimental Data')


# 绘制 Langmuir 拟合曲线
plt.plot(
    Ce_fit, Qe_langmuir_fit, 'r-', 
    label=(r'Langmuir Fit: $Q_e = \frac{Q_{\mathrm{max}} \cdot b \cdot C_e}{1 + b \cdot C_e}$'
           f'\n$Q_{{\mathrm{{max}}}}={Qmax_fit:.2f}, b={b_fit:.2f}$'
           f'\n$R^2={r2_langmuir:.3f}, RMSE={rmse_langmuir:.3f}, MAE={mae_langmuir:.3f}$')
)
# 绘制 Freundlich 拟合曲线
plt.plot(
    Ce_fit, Qe_freundlich_fit, 'b--', 
    label=(r'Freundlich Fit: $Q_e = K_f \cdot C_e^{1/n}$'
           f'\n$K_f={Kf_fit:.2f}, n={n_fit:.2f}$'
           f'\n$R^2={r2_freundlich:.3f}, RMSE={rmse_freundlich:.3f}, MAE={mae_freundlich:.3f}$')
)


plt.xlabel('Ce (mg/L)')
plt.ylabel('Qe (mg/g)')
plt.title(f'{BIOCHAR_TYPE}-{adsorbent_conc_g_L}g/L-{POLLUTANT_NAME}-Adsorption Isotherms')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f'{csv_file_path}-Adsorption Isotherms.png', dpi=500, facecolor='white')
plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. 加载数据
df = pd.read_csv('nbaplayersdraft.csv')

# 2. 数据转换：计算“年均胜场贡献”
# 我们过滤掉只打了不到1年的边缘球员，避免分母为0或异常值
df = df[df['years_active'] >= 1]
df = df[df['year'] >= 2011]
df = df[df['overall_pick'] <= 14]

# 计算单赛季平均 Win Shares (这直接对应了胜场提升量)
df['avg_annual_ws'] = df['win_shares'] / df['years_active']

# 3. 数据清洗与分组
# 限制在首轮和二轮区间，剔除缺失值
clean_data = df[df['overall_pick'].between(1, 20)].dropna(subset=['avg_annual_ws'])

# 锚定点计算：依然采用你设定的“状元中表现前9名的平均值”
all_no1_picks = clean_data[clean_data['overall_pick'] == 1]['avg_annual_ws']
top_anchor = all_no1_picks.nlargest(9).mean()
print(f">>> 锚定点确定：状元潜力天花板为 {top_anchor:.2f} 胜")

# --- 关键修改：直接使用所有球员个体点作为训练数据 ---
X_train = clean_data['overall_pick'].values
y_train = clean_data['avg_annual_ws'].values

# 4. 拟合函数定义 (保持 top_anchor 锁定)
def model_func(r, lmbda, C):
    # A 保持由锚定点决定，模型学习如何从这个点衰减
    A = top_anchor - C
    return A * np.exp(-lmbda * (r - 1)) + C

# 执行拟合
# 增加 bounds 限制 C 不会过高（例如限制在 0.5 胜以内）
popt, pcov = curve_fit(model_func, X_train, y_train, p0=[0.1, 0.2], bounds=([0, 0], [2.0, 0.5]))
lmbda, C = popt
A = top_anchor - C

print(f"拟合参数 (个体点维度)：")
print(f"A (锚定增益): {A:.2f} 胜")
print(f"λ (衰减率): {lmbda:.3f}")
print(f"C (前20顺位底噪): {C:.2f} 胜")

# --- 5. 可视化修改 ---
plt.figure(figsize=(10, 6))
# 绘制所有球员的个体散点（用小点和低透明度）
plt.scatter(X_train, y_train, color='blue', s=10, alpha=0.2, label='Individual Player WS')
# 绘制拟合曲线
X_plot = np.linspace(1, 20, 100)
plt.plot(X_plot, model_func(X_plot, *popt), 'r-', linewidth=3, label='Fitted Expectation')

plt.title("Expected Win Increment (Top 20 Picks - Individual Analysis)")
plt.xlabel("Draft Pick (r)")
plt.ylabel("Win Increment")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

import numpy as np


# 1. 之前拟合出的球员单赛季胜场贡献函数 (K_t)
def V_pick(r):
    """输入顺位 r，返回该顺位新秀两年后的单赛季期望胜场贡献"""
    return A * np.exp(-lmbda * (r - 1)) + C


# 2. 构造乐透概率字典 (基于你提供的图片数据)
# 键为倒数排名(Seed)，值为一个列表，表示抽中第 1, 2, 3, 4 ... 14 顺位的百分比概率
# 这里补充了图片中前 4 位之后的“最差保底顺位”逻辑
lottery_matrix = {
    # Seed: {顺位: 概率}
    1: {1: 14.0, 2: 13.4, 3: 12.7, 4: 12.0, 5: 47.9},
    2: {1: 14.0, 2: 13.4, 3: 12.7, 4: 12.0, 5: 27.8, 6: 20.0},
    3: {1: 14.0, 2: 13.4, 3: 12.7, 4: 12.0, 5: 14.8, 6: 26.0, 7: 7.0},
    4: {1: 12.5, 2: 12.2, 3: 11.9, 4: 11.5, 5: 7.2, 6: 25.7, 7: 16.7, 8: 2.2},
    5: {1: 10.5, 2: 10.5, 3: 10.6, 4: 10.5, 5: 2.2, 6: 19.6, 7: 26.7, 8: 8.7, 9: 0.6},
    6: {1: 9.0, 2: 9.2, 3: 9.4, 4: 9.6, 6: 8.6, 7: 29.8, 8: 20.5, 9: 3.7, 10: 0.1},
    7: {1: 7.5, 2: 7.8, 3: 8.1, 4: 8.5, 7: 19.7, 8: 34.1, 9: 12.9, 10: 1.3},
    8: {1: 6.0, 2: 6.3, 3: 6.7, 4: 7.2, 8: 34.5, 9: 32.1, 10: 6.7, 11: 0.4},
    9: {1: 4.5, 2: 4.8, 3: 5.2, 4: 5.7, 9: 50.7, 10: 25.9, 11: 3.0, 12: 0.1},
    10: {1: 3.0, 2: 3.3, 3: 3.6, 4: 4.0, 10: 65.9, 11: 19.0, 12: 1.2},
    11: {1: 2.0, 2: 2.2, 3: 2.4, 4: 2.8, 11: 77.6, 12: 12.6, 13: 0.4},
    12: {1: 1.5, 2: 1.7, 3: 1.9, 4: 2.1, 12: 86.1, 13: 6.7, 14: 0.1},
    13: {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.4, 13: 92.9, 14: 2.3},
    14: {1: 0.5, 2: 0.6, 3: 0.6, 4: 0.7, 14: 97.6}
}


# 3. 核心计算函数
def get_tanking_expectation(seed):
    """
    输入：球队上赛季排名(1-14，1代表倒数第一)
    输出：两年后战力的期望提升值 (胜场数)
    """
    if seed not in lottery_matrix:
        return 0.0

    odds = lottery_matrix[seed]
    expected_gain = 0.0

    # 遍历该排名下所有可能的顺位及其概率
    for pick, prob in odds.items():
        value = V_pick(pick)  # 该顺位的战力价值
        expected_gain += (prob / 100.0) * value

    return expected_gain


# --- 测试用例 ---
s = int(input('请输入倒数名次：'))
print(f"如果你是倒数第 {s} 名，两年后预期的战力提升为: {get_tanking_expectation(s):.2f} 胜")

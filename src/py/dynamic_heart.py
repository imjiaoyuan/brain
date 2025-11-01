import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib as mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['mathtext.fontset'] = 'cm'

def LoveFunc(x, alpha):
    term1 = np.cbrt(x**2)
    
    val_in_sqrt = 3.3 - x**2
    valid_mask = val_in_sqrt >= 0
    
    term2_component = np.full_like(x, np.nan, dtype=float) 
    term2_component[valid_mask] = np.sqrt(val_in_sqrt[valid_mask]) * np.sin(alpha * np.pi * x[valid_mask])
    
    result = term1 + 0.9 * term2_component
    
    return result

fig, ax = plt.subplots(figsize=(10, 7))
ax.grid(True)
ax.set_xlim(-3, 3)
ax.set_ylim(-2, 4)

x_vals = np.arange(-1.8, 1.805, 0.005)

func_text = ax.text(0, 3.3, r'$f(x)=x^{2/3}+0.9(3.3-x^2)^{1/2}\sin(\alpha\pi x)$',
                    fontsize=48, ha='center', va='bottom')

# ax.text(0, -2.5, 'lyy I love you', fontsize=30, color='black', ha='center', va='center')

alpha_text = ax.text(-0.35, 2.9, '', fontsize=52, ha='left', va='center')

line, = ax.plot([], [], lw=2.5, color='red')

def init():
    line.set_data([], [])
    alpha_text.set_text('')
    return line, alpha_text

alpha_current_value = 1.0

def update(frame):
    global alpha_current_value
    
    alpha_current_value += 0.01

    y_vals = LoveFunc(x_vals, alpha_current_value)
    
    color_start = np.array([1.0, 0.8, 0.8])
    color_end = np.array([0.8, 0.0, 0.0])
    
    normalized_alpha = min(1.0, (alpha_current_value - 1) / (20 - 1))
    current_color = color_start + (color_end - color_start) * normalized_alpha
    
    line.set_data(x_vals, y_vals)
    line.set_color(current_color)

    alpha_string = r'$\alpha=' + f'{alpha_current_value:.2f}' + r'$' 
    alpha_text.set_text(alpha_string)

    return line, alpha_text

ani = FuncAnimation(fig, update, frames=None,
                    init_func=init, blit=True, interval=3)

plt.show()
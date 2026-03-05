#!/usr/bin/env python3
"""
行波 sin(ωt - kx) 动图 - 动画3
演示：行波 = 时间视角(ω) + 空间视角(k) 的结合
波相位 = k·x - ω·t，随时间传播
重点：高亮小球平滑移动展示传播

用法：
  python traveling_wave.py

输出：output/traveling_wave.gif
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io, os, argparse
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============ 默认参数 ============
DEFAULTS = {
    'frames': 120,
    'fps': 24,
    'pendulum_length': 1.0,
    'amplitude': 0.8,
    'pivot_height': 1.5,
    'wave_length': 2 * np.pi,
    'fig_size': (13, 7),
    'dpi': 100,
    'view_elev': 25,
    'view_azim': -60,
}

MAIN_COLOR = '#FF5722'
MAIN_EDGE = '#D84315'
GHOST_COLOR = '#CCCCCC'
TRACE_COLOR = '#2196F3'
AXIS_GREEN = '#4CAF50'
CREST_COLOR = '#E91E63'  # 高亮小球颜色
# ==================================


def parse_args():
    parser = argparse.ArgumentParser(description='行波 sin(ωt-kx) 动图')
    parser.add_argument('--frames', type=int, default=DEFAULTS['frames'])
    parser.add_argument('--fps', type=int, default=DEFAULTS['fps'])
    parser.add_argument('--output', type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    n_frames = args.frames
    fps = args.fps
    L = DEFAULTS['pendulum_length']
    A = DEFAULTS['amplitude']
    H = DEFAULTS['pivot_height']
    wl = DEFAULTS['wave_length']

    k = 2 * np.pi / wl
    omega = 2 * np.pi / 3.0
    x_span = 3 * wl

    # 固定单摆（半波长一个，显示空间分布）
    x_positions = np.arange(0, x_span + 0.1, wl / 2)
    x_curve = np.linspace(0, x_span, 300)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    out_path = args.output or os.path.join(output_dir, 'traveling_wave.gif')

    frames_images = []

    for frame in range(n_frames):
        fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
        ax = fig.add_subplot(111, projection='3d')

        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.xaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
        ax.yaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
        ax.zaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)

        t = frame / fps
        phase = omega * t

        # ★ 高亮点位置：在波峰附近平滑移动
        # 波峰位置 = (ωt + π/2) / k，取模实现循环
        x_highlight = ((phase + np.pi / 2) / k) % x_span

        # 底面行波曲线
        y_curve = A * np.sin(k * x_curve - phase)
        ax.plot(x_curve, y_curve, np.zeros_like(x_curve),
                color=TRACE_COLOR, linewidth=2.5, zorder=3)

        # 底面中心线
        ax.plot([0, x_span], [0, 0], [0, 0],
                color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)

        # 悬挂横梁
        ax.plot([0, x_span], [0, 0], [H, H],
                color='#888888', linewidth=2.5, alpha=0.4)

        # ★ 画高亮点轨迹（淡色，显示运动路径）
        # 从起点到当前位置的轨迹
        trail_start = (x_highlight - 1.5 * wl) % x_span
        trail_x = np.linspace(trail_start, x_highlight, 50)
        # 处理跨周期的情况
        trail_x_adj = []
        trail_y_adj = []
        for tx in trail_x:
            if tx < trail_start:
                tx += x_span
            if tx <= x_highlight:
                trail_x_adj.append(tx % x_span)
                trail_y_adj.append(A * np.sin(k * tx - phase))
        if trail_x_adj:
            ax.plot(trail_x_adj, trail_y_adj, np.zeros_like(trail_x_adj),
                    color=CREST_COLOR, linewidth=1.5, alpha=0.25, zorder=2)

        # ★ 画固定单摆（淡淡的，显示空间分布）
        for i, xp in enumerate(x_positions):
            swing = A * np.sin(k * xp - phase)
            ball_z = H - np.sqrt(max(L ** 2 - swing ** 2, 0.01))

            # 摆杆（非常淡）
            ax.plot([xp, xp], [0, swing], [H, ball_z],
                    color=GHOST_COLOR, linewidth=0.6, alpha=0.2, zorder=4)
            ax.scatter([xp], [swing], [ball_z], color=GHOST_COLOR, s=30,
                       alpha=0.2, zorder=5)
            ax.scatter([xp], [swing], [0], color=GHOST_COLOR, s=10,
                       alpha=0.15, zorder=4)

        # ★ 高亮小球（核心！平滑移动的大红球）
        y_highlight = A * np.sin(k * x_highlight - phase)
        z_highlight = H - np.sqrt(max(L ** 2 - y_highlight ** 2, 0.01))
        
        # 高亮小球
        ax.scatter([x_highlight], [y_highlight], [z_highlight], 
                   color=CREST_COLOR, s=350, zorder=10,
                   edgecolors='#AD1457', linewidths=2)
        
        # 高亮小球到底面的投影
        ax.plot([x_highlight, x_highlight], [y_highlight, y_highlight], [z_highlight, 0],
                color=CREST_COLOR, linewidth=1.5, linestyle=':', alpha=0.6, zorder=9)
        ax.scatter([x_highlight], [y_highlight], [0], 
                   color=CREST_COLOR, s=100, zorder=9, marker='^')

        # 波传播方向箭头（跟随高亮点）
        if x_highlight < x_span - 0.8:
            ax.quiver(x_highlight + 0.4, y_highlight + 0.3, 0, 
                      1.0, 0, 0, color=CREST_COLOR, 
                      arrow_length_ratio=0.35, linewidth=2.5, zorder=11)

        # 标注
        ax.text(x_highlight, y_highlight + 0.5, 0, 
                '高亮点', fontsize=11, color=CREST_COLOR, 
                ha='center', fontweight='bold', zorder=12)

        # 公式标注
        ax.text(x_span / 2, -A - 0.6, 0,
                '行波：sin(kx - ωt)　　k作用在x上，ω作用在t上',
                fontsize=11, color=TRACE_COLOR, ha='center', fontweight='bold')
        ax.text(x_span / 2, -A - 1.0, 0,
                '红色高亮点沿正弦轨迹平滑移动，展示波在传播',
                fontsize=10, color='#888888', ha='center')

        # 波长标注
        ax.text(wl / 2, -A - 0.2, 0, 'λ',
                fontsize=12, color='#9C27B0', ha='center', fontweight='bold')

        # 重力箭头
        ax.quiver(0, -1.0, H, 0, 0, -0.5, color='#BBBBBB',
                  arrow_length_ratio=0.3, linewidth=1.2)
        ax.text(0, -1.0, H - 0.7, 'g', fontsize=10, color='#BBBBBB',
                ha='center', fontweight='bold')

        # 标准视角
        ax.view_init(elev=DEFAULTS['view_elev'], azim=DEFAULTS['view_azim'])
        ax.set_xlim(-0.5, x_span + 0.5)
        ax.set_ylim(-A - 1.3, A + 0.8)
        ax.set_zlim(0, H + 0.3)

        ax.set_xlabel('位置 x →', fontsize=10, color=AXIS_GREEN,
                      fontweight='bold', labelpad=5)
        ax.set_ylabel('摆动 ←→', fontsize=10, color=MAIN_COLOR,
                      fontweight='bold', labelpad=5)
        ax.set_zlabel('↑ 高度', fontsize=10, color='#888888',
                      fontweight='bold', labelpad=5)
        ax.set_title('行波 sin(kx - ωt)：高亮点沿正弦轨迹平滑移动，展示波在传播',
                     fontsize=13, fontweight='bold', pad=12)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        frames_images.append(Image.open(buf).copy().convert('RGB'))
        buf.close()
        plt.close(fig)

        if (frame + 1) % 30 == 0:
            print(f'  渲染: {frame + 1}/{n_frames}')

    w = min(f.width for f in frames_images)
    h = min(f.height for f in frames_images)
    p_frames = [img.resize((w, h), Image.LANCZOS)
                   .convert('P', palette=Image.ADAPTIVE, colors=256)
                for img in frames_images]

    p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:],
                      duration=int(1000 / fps), loop=0, optimize=False, disposal=2)
    print(f'✅ 动图已保存: {out_path}')


if __name__ == '__main__':
    main()

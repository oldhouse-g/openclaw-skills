#!/usr/bin/env python3
"""
行波 sin(ωt - kx) 动图 - 动画3
演示：行波 = 时间视角(ω) + 空间视角(k) 的结合
波相位 = k·x - ω·t，随时间传播

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
    'wave_length': 2 * np.pi,  # 空间波长 λ = 2π/k
    'period': 4.0,             # 时间周期 T = 2π/ω
    'fig_size': (12, 7),
    'dpi': 100,
    # 标准3D视角
    'view_elev': 25,
    'view_azim': -60,
}

# 标准配色
MAIN_COLOR = '#FF5722'
MAIN_EDGE = '#D84315'
GHOST_COLOR = '#CCCCCC'
TRACE_COLOR = '#2196F3'
AXIS_GREEN = '#4CAF50'
# ==================================


def parse_args():
    parser = argparse.ArgumentParser(description='行波 sin(ωt-kx) 动图')
    parser.add_argument('--frames', type=int, default=DEFAULTS['frames'])
    parser.add_argument('--fps', type=int, default=DEFAULTS['fps'])
    parser.add_argument('--output', type=str, default=None)
    return parser.parse_args()


def render_frame(fig, ax, frame, n_frames, L, A, H, wl, T, x_positions, x_curve):
    ax.cla()

    # 坐标面板白色/透明
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.xaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
    ax.yaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
    ax.zaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)

    k = 2 * np.pi / wl
    omega = 2 * np.pi / T
    t = frame / DEFAULTS['fps']
    phase = omega * t  # 时间带来的相位

    # 底面行波曲线 sin(kx - ωt)
    y_curve = A * np.sin(k * x_curve - phase)
    ax.plot(x_curve, y_curve, np.zeros_like(x_curve),
            color=TRACE_COLOR, linewidth=2.5, zorder=3)

    # 底面中心线
    ax.plot([0, 2 * wl], [0, 0], [0, 0],
            color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)

    # 悬挂横梁（沿x方向）
    ax.plot([0, 2 * wl], [0, 0], [H, H],
            color='#888888', linewidth=2.5, alpha=0.5)

    # 画每个单摆
    for i, xp in enumerate(x_positions):
        # 行波：相位 = kx - ωt
        swing = A * np.sin(k * xp - phase)
        ball_z = H - np.sqrt(max(L ** 2 - swing ** 2, 0.01))
        
        is_main = (i == len(x_positions) - 1)

        if is_main:
            rc, rw, ra = '#555555', 2.5, 1.0
            bc, bs, bec, bew, ba = MAIN_COLOR, 250, MAIN_EDGE, 1.5, 1.0
            pa, pds = 0.5, 80
        else:
            rc, rw, ra = GHOST_COLOR, 1.0, 0.3
            bc, bs, bec, bew, ba = GHOST_COLOR, 80, '#BBBBBB', 0.5, 0.35
            pa, pds = 0.15, 25

        # 摆杆
        ax.plot([xp, xp], [0, swing], [H, ball_z],
                color=rc, linewidth=rw, alpha=ra, zorder=4)
        # 悬挂点
        ax.scatter([xp], [0], [H], color='#888888',
                   s=15 if not is_main else 40, marker='s', zorder=5, alpha=ra)
        # 小球
        ax.scatter([xp], [swing], [ball_z], color=bc, s=bs,
                   zorder=6, edgecolors=bec, linewidths=bew, alpha=ba)
        # 投影虚线
        ax.plot([xp, xp], [swing, swing], [ball_z, 0],
                color=rc, linewidth=0.6 if not is_main else 1,
                linestyle=':', alpha=pa)
        # 底面投影点
        ax.scatter([xp], [swing], [0], color=TRACE_COLOR, s=pds,
                   zorder=5, alpha=0.7 if is_main else 0.2)

    # 波长标注
    ax.text(wl / 2, -A - 0.5, 0, 'λ = 2π/k',
            fontsize=11, color='#9C27B0', ha='center', fontweight='bold')
    
    # 周期标注
    ax.text(0, A + 0.5, 0, 'T = 2π/ω',
            fontsize=11, color='#FF9800', ha='center', fontweight='bold')

    # 相位公式标注
    ax.text(1.5 * wl, -A - 0.9, 0, '相位 = k·x - ω·t',
            fontsize=12, color=TRACE_COLOR, ha='center', fontweight='bold')
    ax.text(1.5 * wl, -A - 1.3, 0, '（波随时间向 +x 方向传播）',
            fontsize=10, color='#888888', ha='center')

    # 波传播方向箭头
    ax.quiver(2 * wl + 0.3, 0, 0, 1.0, 0, 0,
              color='#4CAF50', arrow_length_ratio=0.4, linewidth=2)
    ax.text(2 * wl + 0.8, 0, 0, '波传播方向',
            fontsize=9, color=AXIS_GREEN, ha='left')

    # 重力箭头
    ax.quiver(0, -1.2, H, 0, 0, -0.6, color='#BBBBBB',
              arrow_length_ratio=0.3, linewidth=1.5)
    ax.text(0, -1.2, H - 0.8, 'g', fontsize=11, color='#BBBBBB',
            ha='center', fontweight='bold')

    # 标准视角
    ax.view_init(elev=DEFAULTS['view_elev'], azim=DEFAULTS['view_azim'])
    ax.set_xlim(-0.5, 2 * wl + 1.5)
    ax.set_ylim(-A - 1.6, A + 0.8)
    ax.set_zlim(0, H + 0.3)

    ax.set_xlabel('位置 x →', fontsize=10, color=AXIS_GREEN,
                  fontweight='bold', labelpad=5)
    ax.set_ylabel('摆动 ←→', fontsize=10, color=MAIN_COLOR,
                  fontweight='bold', labelpad=5)
    ax.set_zlabel('↑ 高度', fontsize=10, color='#888888',
                  fontweight='bold', labelpad=5)
    ax.set_title('行波 sin(ωt - kx)：ω作用在t上 + k作用在x上 = 传播的波',
                 fontsize=13, fontweight='bold', pad=12)


def main():
    args = parse_args()
    n_frames = args.frames
    fps = args.fps
    L = DEFAULTS['pendulum_length']
    A = DEFAULTS['amplitude']
    H = DEFAULTS['pivot_height']
    wl = DEFAULTS['wave_length']
    T = DEFAULTS['period']

    # 半波长一个单摆，2个波长
    x_positions = np.arange(0, 2 * wl + 0.1, wl / 2)
    x_curve = np.linspace(0, 2 * wl, 200)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    out_path = args.output or os.path.join(output_dir, 'traveling_wave.gif')

    frames_images = []
    for frame in range(n_frames):
        fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
        ax = fig.add_subplot(111, projection='3d')
        render_frame(fig, ax, frame, n_frames, L, A, H, wl, T, x_positions, x_curve)

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

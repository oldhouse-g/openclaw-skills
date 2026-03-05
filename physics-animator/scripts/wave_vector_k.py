#!/usr/bin/env python3
"""
波矢k空间正弦波动图 - 一个单摆在不同位置的相位痕迹
演示：同一时刻、不同空间位置的单摆相位分布 → 空间正弦波
与 oscillator.py（频率ω/时间视角）配对使用

用法：
  python wave_vector_k.py                  # 默认
  python wave_vector_k.py --frames 60      # 调整帧数

输出：output/wave_vector_k.gif
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
    'fig_size': (12, 7),
    'dpi': 100,
    # ★ 标准3D视角（全局统一）
    'view_elev': 25,
    'view_azim': -60,
}

# ★ 标准颜色定义（全局统一）
MAIN_COLOR = '#FF5722'       # 主角球颜色
MAIN_EDGE = '#D84315'        # 主角球边框
GHOST_COLOR = '#CCCCCC'      # 幻影颜色
TRACE_COLOR = '#2196F3'      # 轨迹颜色
AXIS_GREEN = '#4CAF50'       # 空间轴标注
# ==================================


def parse_args():
    parser = argparse.ArgumentParser(description='波矢k空间正弦波动图')
    parser.add_argument('--frames', type=int, default=DEFAULTS['frames'])
    parser.add_argument('--fps', type=int, default=DEFAULTS['fps'])
    parser.add_argument('--output', type=str, default=None)
    return parser.parse_args()


def render_frame(fig, ax, frame, n_frames, L, A, H, wl, x_positions, x_curve):
    ax.cla()

    # 白色背景面板
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.xaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
    ax.yaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
    ax.zaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)

    k = 2 * np.pi / wl
    fps = DEFAULTS['fps']
    omega = 2 * np.pi / (n_frames / fps)
    phase_t = omega * (frame / fps)
    n_pend = len(x_positions)

    # 底面正弦曲线
    y_curve = A * np.sin(k * x_curve - phase_t)
    ax.plot(x_curve, y_curve, np.zeros_like(x_curve),
            color=TRACE_COLOR, linewidth=2.5, zorder=3)

    # 底面中心线
    ax.plot([0, 2 * wl], [0, 0], [0, 0],
            color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)

    # 悬挂横梁
    ax.plot([0, 2 * wl], [0, 0], [H, H],
            color='#888888', linewidth=2.5, alpha=0.5)

    for i, xp in enumerate(x_positions):
        swing = A * np.sin(k * xp - phase_t)
        ball_z = H - np.sqrt(max(L ** 2 - swing ** 2, 0.01))
        is_main = (i == n_pend - 1)

        if is_main:
            rc, rw, ra = '#555555', 2.5, 1.0
            bc, bs, bec, bew, ba = MAIN_COLOR, 250, MAIN_EDGE, 1.5, 1.0
            pa, pds = 0.5, 80
        else:
            rc, rw, ra = GHOST_COLOR, 1.0, 0.3
            bc, bs, bec, bew, ba = GHOST_COLOR, 80, '#BBBBBB', 0.5, 0.35
            pa, pds = 0.15, 25

        ax.plot([xp, xp], [0, swing], [H, ball_z],
                color=rc, linewidth=rw, alpha=ra, zorder=4)
        ax.scatter([xp], [0], [H], color='#888888',
                   s=15 if not is_main else 40, marker='s', zorder=5, alpha=ra)
        ax.scatter([xp], [swing], [ball_z], color=bc, s=bs,
                   zorder=6, edgecolors=bec, linewidths=bew, alpha=ba)
        ax.plot([xp, xp], [swing, swing], [ball_z, 0],
                color=rc, linewidth=0.6 if not is_main else 1,
                linestyle=':', alpha=pa)
        ax.scatter([xp], [swing], [0], color=TRACE_COLOR, s=pds,
                   zorder=5, alpha=0.7 if is_main else 0.2)

    # 标注（颜色与球一致）
    ax.text(x_positions[-1], A + 0.4, 0, '当前位置',
            fontsize=11, color=MAIN_COLOR, ha='center', fontweight='bold')
    ax.text(x_positions[1], A + 0.4, 0, '曾经的位置',
            fontsize=10, color=GHOST_COLOR, ha='center', fontweight='bold')
    ax.text(wl / 2, -A - 0.5, 0, 'λ = 2π/k',
            fontsize=11, color='#9C27B0', ha='center', fontweight='bold')
    ax.text(wl, -A - 0.9, 0, '相位 = k · x（不同位置 → 不同相位）',
            fontsize=12, color=TRACE_COLOR, ha='center', fontweight='bold')

    # 重力箭头
    ax.quiver(-0.5, 0, H, 0, 0, -0.6, color='#BBBBBB',
              arrow_length_ratio=0.3, linewidth=1.5)
    ax.text(-0.5, 0, H - 0.8, 'g', fontsize=11, color='#BBBBBB',
            ha='center', fontweight='bold')

    # ★ 标准视角
    ax.view_init(elev=DEFAULTS['view_elev'], azim=DEFAULTS['view_azim'])
    ax.set_xlim(-1, 2 * wl + 1.5)
    ax.set_ylim(-A - 1.2, A + 0.8)
    ax.set_zlim(0, H + 0.3)

    ax.set_xlabel('位置 x →', fontsize=10, color=AXIS_GREEN,
                  fontweight='bold', labelpad=5)
    ax.set_ylabel('摆动 ←→', fontsize=10, color=MAIN_COLOR,
                  fontweight='bold', labelpad=5)
    ax.set_zlabel('↑ 高度', fontsize=10, color='#888888',
                  fontweight='bold', labelpad=5)
    ax.set_title('波矢 k：一个单摆在不同位置的相位痕迹 → 空间正弦波',
                 fontsize=13, fontweight='bold', pad=12)


def main():
    args = parse_args()
    n_frames = args.frames
    fps = args.fps
    L = DEFAULTS['pendulum_length']
    A = DEFAULTS['amplitude']
    H = DEFAULTS['pivot_height']
    wl = DEFAULTS['wave_length']

    x_positions = np.arange(0, 2 * wl + 0.1, wl / 2)
    x_curve = np.linspace(0, 2 * wl, 200)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    out_path = args.output or os.path.join(output_dir, 'wave_vector_k.gif')

    frames_images = []
    for frame in range(n_frames):
        fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
        ax = fig.add_subplot(111, projection='3d')
        render_frame(fig, ax, frame, n_frames, L, A, H, wl, x_positions, x_curve)

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

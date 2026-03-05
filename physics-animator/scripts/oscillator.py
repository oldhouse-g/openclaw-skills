#!/usr/bin/env python3
"""
单摆正弦曲线动图 - 纸带式
演示：单摆固定左右荡，纸带匀速后退，小球在纸带上画出正弦曲线

用法：
  python oscillator.py                     # 默认：位置轴
  python oscillator.py --axis-label 时间    # 时间轴版本
  python oscillator.py --frames 60 --fps 12 # 调整帧数和帧率

输出：output/oscillator.gif
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io
import os
import argparse
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
    'trail_length': 4 * np.pi,
    'fig_size': (11, 7),
    'dpi': 100,
    'axis_label': '位置',
}
# ==================================


def parse_args():
    parser = argparse.ArgumentParser(description='单摆正弦曲线动图生成器')
    parser.add_argument('--frames', type=int, default=DEFAULTS['frames'], help='总帧数')
    parser.add_argument('--fps', type=int, default=DEFAULTS['fps'], help='帧率')
    parser.add_argument('--amplitude', type=float, default=DEFAULTS['amplitude'], help='摆动振幅')
    parser.add_argument('--length', type=float, default=DEFAULTS['pendulum_length'], help='摆长')
    parser.add_argument('--axis-label', type=str, default=DEFAULTS['axis_label'],
                        choices=['位置', '时间'], help='纸带轴标签（位置/时间）')
    parser.add_argument('--output', type=str, default=None, help='输出文件路径')
    return parser.parse_args()


def render_frame(fig, ax, frame, n_frames, L, A, H, trail_len, axis_label):
    """渲染单帧"""
    ax.cla()

    progress = (frame / n_frames) * 4 * np.pi
    t = np.linspace(0, progress, max(int(progress * 30), 2))

    swing_vals = A * np.sin(t)
    y_screen = t - progress  # 纸带后退

    # 可见范围内的轨迹
    visible = y_screen >= -trail_len
    if np.any(visible):
        ax.plot(swing_vals[visible], y_screen[visible], np.zeros(np.sum(visible)),
                color='#2196F3', linewidth=2.5, zorder=3)

    # 纸带网格线
    for grid_y in np.arange(0, progress + np.pi, np.pi):
        gy_screen = grid_y - progress
        if -trail_len <= gy_screen <= 0.5:
            ax.plot([-1.3, 1.3], [gy_screen, gy_screen], [0, 0],
                    color='#E0E0E0', linewidth=0.5, alpha=0.4)

    # 底面中心线
    ax.plot([0, 0], [-trail_len, 0.5], [0, 0],
            color='#CCCCCC', linewidth=1, linestyle='--', alpha=0.5)

    # 纸带方向箭头
    ax.quiver(1.2, -trail_len + 1, 0, 0, -1.5, 0,
              color='#4CAF50', arrow_length_ratio=0.3, linewidth=2)
    ax.text(1.2, -trail_len + 0.3, 0, axis_label, fontsize=10,
            color='#4CAF50', ha='center', fontweight='bold')

    # 单摆（固定在y=0）
    current_swing = A * np.sin(progress)
    ball_z = H - np.sqrt(max(L ** 2 - current_swing ** 2, 0.01))

    # 支架
    ax.plot([-0.3, 0.3], [0, 0], [H, H], color='#666666', linewidth=4, alpha=0.8)
    ax.plot([0, 0], [0, 0], [H, H + 0.15], color='#666666', linewidth=3, alpha=0.6)

    # 摆杆
    ax.plot([0, current_swing], [0, 0], [H, ball_z],
            color='#555555', linewidth=2.5, zorder=4)
    ax.scatter([0], [0], [H], color='#333333', s=50, marker='s', zorder=5)

    # 小球
    ax.scatter([current_swing], [0], [ball_z], color='#FF5722', s=280, zorder=6,
               edgecolors='#D84315', linewidths=1.5)

    # 投影虚线
    ax.plot([current_swing, current_swing], [0, 0], [ball_z, 0],
            color='#FF5722', linewidth=1, linestyle=':', alpha=0.5)
    ax.scatter([current_swing], [0], [0], color='#2196F3', s=80, zorder=5, alpha=0.8)

    # 历史幻影
    n_ghosts = min(8, int(progress / (np.pi / 2)))
    for i in range(n_ghosts):
        tp = i * (np.pi / 2)
        if tp <= progress - 0.8:
            gy = tp - progress
            if gy >= -trail_len:
                gs = A * np.sin(tp)
                gz = H - np.sqrt(max(L ** 2 - gs ** 2, 0.01))
                ax.plot([0, gs], [gy, gy], [H, gz],
                        color='#AAAAAA', linewidth=0.6, alpha=0.15)
                ax.scatter([gs], [gy], [gz],
                           color='#FF5722', s=40, alpha=0.12, zorder=4)
                ax.plot([gs, gs], [gy, gy], [gz, 0],
                        color='#AAAAAA', linewidth=0.4, linestyle=':', alpha=0.1)

    # 重力箭头
    ax.quiver(-1.2, 0, H, 0, 0, -0.6, color='#999999', arrow_length_ratio=0.3, linewidth=1.5)
    ax.text(-1.2, 0, H - 0.8, 'g', fontsize=12, color='#999999', ha='center', fontweight='bold')

    ax.view_init(elev=25, azim=-55)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-trail_len, 1.0)
    ax.set_zlim(0, H + 0.3)

    ax.set_xlabel('摆动 ←→', fontsize=10, color='#FF5722', fontweight='bold', labelpad=5)
    ax.set_ylabel(f'← {axis_label}（纸带方向）', fontsize=10, color='#4CAF50', fontweight='bold', labelpad=5)
    ax.set_zlabel('↑ 高度', fontsize=10, color='#666666', fontweight='bold', labelpad=5)
    ax.set_title(f'单摆摆动 → 纸带记录的{axis_label}轨迹 = 正弦曲线',
                 fontsize=14, fontweight='bold', pad=12)


def main():
    args = parse_args()

    n_frames = args.frames
    fps = args.fps
    L = args.length
    A = args.amplitude
    H = DEFAULTS['pivot_height']
    trail_len = DEFAULTS['trail_length']
    axis_label = args.axis_label

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    out_path = args.output or os.path.join(output_dir, 'oscillator.gif')

    fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
    ax = fig.add_subplot(111, projection='3d')

    frames_images = []
    for frame in range(n_frames):
        render_frame(fig, ax, frame, n_frames, L, A, H, trail_len, axis_label)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
        buf.seek(0)
        frames_images.append(Image.open(buf).copy().convert('RGB'))
        buf.close()
        plt.close(fig)

        fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
        ax = fig.add_subplot(111, projection='3d')

        if (frame + 1) % 30 == 0:
            print(f'  渲染: {frame + 1}/{n_frames}')

    plt.close(fig)

    # 统一尺寸
    w = min(f.width for f in frames_images)
    h = min(f.height for f in frames_images)
    p_frames = [img.resize((w, h), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=256)
                for img in frames_images]

    p_frames[0].save(out_path, save_all=True, append_images=p_frames[1:],
                      duration=int(1000 / fps), loop=0, optimize=False, disposal=2)
    print(f'✅ 动图已保存: {out_path}')


if __name__ == '__main__':
    main()

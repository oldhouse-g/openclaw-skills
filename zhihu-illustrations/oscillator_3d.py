#!/usr/bin/env python3
"""
单摆正弦曲线动图生成器
用途：知乎文章配图 - 演示"单摆左右荡 + 匀速前进 = 正弦曲线轨迹"
作者：蟹大爷 & 阿肝
日期：2026-03-05

依赖：pip install numpy matplotlib Pillow
用法：python oscillator_3d.py
输出：oscillator_3d.gif + oscillator_3d.mp4
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
import io
import subprocess
import os
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============ 参数配置 ============
N_FRAMES = 120        # 总帧数
FPS = 24              # 帧率
L = 1.0               # 摆长
A = 0.8               # 摆动振幅（水平）
H = 1.5               # 悬挂点高度
FIG_SIZE = (11, 7)    # 图片尺寸
DPI = 100             # 分辨率
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
# ==================================


def render_frame(fig, ax, frame):
    """渲染单帧"""
    ax.cla()

    progress = (frame / N_FRAMES) * 4 * np.pi
    t = np.linspace(0, progress, max(int(progress * 30), 2))

    swing_vals = A * np.sin(t)
    x_traj = swing_vals       # 水平摆动
    y_traj = t                # 前进方向

    # 轨迹只画在底面(z=0)——正弦曲线投影
    ax.plot(x_traj, y_traj, np.zeros_like(x_traj),
            color='#2196F3', linewidth=2.5, zorder=3)

    # 悬挂横梁
    ax.plot([0, 0], [0, 4 * np.pi], [H, H],
            color='#666666', linewidth=2.5, alpha=0.6)

    # 底面中心线
    ax.plot([0, 0], [0, 4 * np.pi], [0, 0],
            color='#CCCCCC', linewidth=1, linestyle='--', alpha=0.5)

    # 当前单摆
    current_swing = A * np.sin(progress)
    ball_z = H - np.sqrt(max(L ** 2 - current_swing ** 2, 0.01))

    # 摆杆
    ax.plot([0, current_swing], [progress, progress], [H, ball_z],
            color='#555555', linewidth=2.5, zorder=4)
    # 悬挂点
    ax.scatter([0], [progress], [H],
               color='#333333', s=40, marker='s', zorder=5)
    # 小球
    ax.scatter([current_swing], [progress], [ball_z],
               color='#FF5722', s=250, zorder=6,
               edgecolors='#D84315', linewidths=1.5)

    # 投影虚线（小球到底面）
    ax.plot([current_swing, current_swing], [progress, progress], [ball_z, 0],
            color='#FF5722', linewidth=1, linestyle=':', alpha=0.5)
    # 底面投影点
    ax.scatter([current_swing], [progress], [0],
               color='#2196F3', s=60, zorder=5, alpha=0.7)

    # 历史幻影单摆
    n_ghosts = min(10, int(progress / (np.pi / 2)))
    for i in range(n_ghosts):
        tp = i * (np.pi / 2)
        if tp <= progress - 0.8:
            gs = A * np.sin(tp)
            gz = H - np.sqrt(max(L ** 2 - gs ** 2, 0.01))
            ax.plot([0, gs], [tp, tp], [H, gz],
                    color='#AAAAAA', linewidth=0.8, alpha=0.2)
            ax.scatter([gs], [tp], [gz],
                       color='#FF5722', s=50, alpha=0.15, zorder=4)
            ax.plot([gs, gs], [tp, tp], [gz, 0],
                    color='#AAAAAA', linewidth=0.5, linestyle=':', alpha=0.15)

    # 重力箭头
    ax.quiver(1.3, 1.0, H, 0, 0, -0.6,
              color='#999999', arrow_length_ratio=0.3, linewidth=1.5)
    ax.text(1.3, 1.0, H - 0.8, 'g', fontsize=12,
            color='#999999', ha='center', fontweight='bold')

    # 视角（缓慢旋转）
    ax.view_init(elev=22, azim=-60 + frame * 0.3)

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(0, 4 * np.pi)
    ax.set_zlim(0, H + 0.3)

    ax.set_xlabel('摆动 ←→', fontsize=10, color='#FF5722',
                  fontweight='bold', labelpad=5)
    ax.set_ylabel('前进 →', fontsize=10, color='#4CAF50',
                  fontweight='bold', labelpad=5)
    ax.set_zlabel('↑ 高度', fontsize=10, color='#666666',
                  fontweight='bold', labelpad=5)
    ax.set_title('单摆左右荡 + 匀速前进 → 底面轨迹 = 正弦曲线',
                 fontsize=14, fontweight='bold', pad=12)


def main():
    fig = plt.figure(figsize=FIG_SIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection='3d')

    frames_images = []
    for frame in range(N_FRAMES):
        render_frame(fig, ax, frame)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
        buf.seek(0)
        frames_images.append(Image.open(buf).copy())
        buf.close()
        if (frame + 1) % 20 == 0:
            print(f'  渲染进度: {frame + 1}/{N_FRAMES}')

    plt.close()

    # 保存 GIF
    out_gif = os.path.join(OUTPUT_DIR, 'oscillator_3d.gif')
    frames_images[0].save(out_gif, save_all=True,
                          append_images=frames_images[1:],
                          duration=int(1000 / FPS), loop=0, optimize=True)
    print(f'GIF saved: {out_gif}')

    # 转 MP4（需要 ffmpeg）
    out_mp4 = os.path.join(OUTPUT_DIR, 'oscillator_3d.mp4')
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', out_gif,
            '-movflags', 'faststart', '-pix_fmt', 'yuv420p',
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
            out_mp4
        ], capture_output=True, check=True)
        print(f'MP4 saved: {out_mp4}')
    except (FileNotFoundError, subprocess.CalledProcessError):
        print('MP4 转换跳过（需要安装 ffmpeg）')

    print('Done!')


if __name__ == '__main__':
    main()

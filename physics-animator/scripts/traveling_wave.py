#!/usr/bin/env python3
"""
行波 sin(ωt - kx) 动图 - 动画3
演示：行波 = 时间视角(ω) + 空间视角(k) 的结合
波相位 = k·x - ω·t，随时间传播
重点：波峰标记跟踪，清晰展示"波在传播"

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
CREST_COLOR = '#E91E63'  # 波峰标记颜色（品红，醒目）
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
    omega = 2 * np.pi / 3.0  # 3秒一个周期，让传播看得清楚
    x_span = 3 * wl  # 显示3个波长的范围

    # 更多单摆，让波形更清楚
    x_positions = np.arange(0, x_span + 0.1, wl / 4)  # 四分之一波长一个
    x_curve = np.linspace(0, x_span, 300)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    out_path = args.output or os.path.join(output_dir, 'traveling_wave.gif')

    frames_images = []

    for frame in range(n_frames):
        fig = plt.figure(figsize=DEFAULTS['fig_size'], dpi=DEFAULTS['dpi'])
        ax = fig.add_subplot(111, projection='3d')

        # 坐标面板白色/透明
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.xaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
        ax.yaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)
        ax.zaxis._axinfo['grid']['color'] = (0.9, 0.9, 0.9, 0.3)

        t = frame / fps
        phase = omega * t

        # ★ 波峰位置：kx - ωt = π/2 时 sin=1（峰值）
        # x_crest = (ωt + π/2) / k，对 x_span 取模实现循环
        x_crest = ((phase + np.pi / 2) / k) % x_span

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

        # ★ 波峰位置标记竖线（品红色，从底面到横梁，非常醒目）
        ax.plot([x_crest, x_crest], [A, A], [0, H * 0.3],
                color=CREST_COLOR, linewidth=2, alpha=0.6, zorder=7)
        # 波峰底面三角标记
        ax.scatter([x_crest], [A], [0], color=CREST_COLOR, s=120,
                   marker='^', zorder=8)

        # 画每个单摆
        for i, xp in enumerate(x_positions):
            swing = A * np.sin(k * xp - phase)
            ball_z = H - np.sqrt(max(L ** 2 - swing ** 2, 0.01))

            # 判断是否是波峰附近的单摆（距离波峰最近的那个高亮）
            dist_to_crest = min(abs(xp - x_crest), x_span - abs(xp - x_crest))
            is_near_crest = dist_to_crest < wl / 6

            if is_near_crest:
                rc, rw, ra = '#555555', 2.0, 0.9
                bc = CREST_COLOR
                bs, bec, bew, ba = 200, '#C2185B', 1.5, 1.0
                pa, pds = 0.5, 60
            else:
                rc, rw, ra = GHOST_COLOR, 0.8, 0.25
                bc, bs, bec, bew, ba = GHOST_COLOR, 50, '#BBBBBB', 0.5, 0.3
                pa, pds = 0.1, 15

            # 摆杆
            ax.plot([xp, xp], [0, swing], [H, ball_z],
                    color=rc, linewidth=rw, alpha=ra, zorder=4)
            # 悬挂点
            ax.scatter([xp], [0], [H], color='#888888', s=10,
                       marker='s', zorder=5, alpha=ra)
            # 小球
            ax.scatter([xp], [swing], [ball_z], color=bc, s=bs,
                       zorder=6, edgecolors=bec, linewidths=bew, alpha=ba)
            # 投影虚线
            ax.plot([xp, xp], [swing, swing], [ball_z, 0],
                    color=rc, linewidth=0.5, linestyle=':', alpha=pa)
            # 底面投影点
            ax.scatter([xp], [swing], [0], color=TRACE_COLOR, s=pds,
                       zorder=5, alpha=0.6 if is_near_crest else 0.15)

        # ★ 波传播方向大箭头（跟着波峰走）
        arrow_x = x_crest + 0.3
        if arrow_x < x_span - 0.5:
            ax.quiver(arrow_x, A + 0.25, 0, 1.2, 0, 0,
                      color=CREST_COLOR, arrow_length_ratio=0.35, linewidth=2.5)

        # 标注
        ax.text(x_crest, A + 0.55, 0, '波峰',
                fontsize=11, color=CREST_COLOR, ha='center', fontweight='bold')

        # 公式标注（固定位置）
        ax.text(x_span / 2, -A - 0.6, 0,
                '行波：sin(kx - ωt)　　k作用在x上，ω作用在t上',
                fontsize=11, color=TRACE_COLOR, ha='center', fontweight='bold')
        ax.text(x_span / 2, -A - 1.0, 0,
                '波峰向 +x 方向传播，速度 v = ω/k',
                fontsize=10, color='#888888', ha='center')

        # 波长标注
        x_mark = x_crest
        x_mark2 = x_mark + wl
        if x_mark2 <= x_span:
            ax.text((x_mark + x_mark2) / 2, -A - 0.2, 0, 'λ',
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
        ax.set_title('行波 sin(kx - ωt)：波峰随时间向右传播',
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

---
name: physics-animator
description: 物理科学动图生成器。用于生成知乎等平台的物理/数学科普配图（3D动图、波形、场线等）。当用户说"画一个XX动图"、"生成物理示意图"、"知乎配图"时激活。
allowed-tools:
  - Bash(python:*)
  - Read
---

# Physics Animator - 物理科学动图生成器

为知乎等平台的科普文章生成高质量3D动图。

## 使用方式

用户说"画一个XX"时，先检查 `scripts/` 下是否有现成脚本，有则直接调用，没有则新建。

### 现有动图脚本

| 脚本名 | 描述 | 调用示例 |
|--------|------|---------|
| `oscillator.py` | 单摆正弦曲线·时间视角ω（纸带式） | `python scripts/oscillator.py` |
| `wave_vector_k.py` | 波矢k·空间视角（一排单摆相位分布） | `python scripts/wave_vector_k.py` |
| `traveling_wave.py` | 行波 sin(ωt-kx) · 时空结合（波传播） | `python scripts/traveling_wave.py` |

### 调用方法

```bash
# 激活虚拟环境
source /Users/xie/.openclaw/workspace/.venv/bin/activate

# 运行脚本（输出到 output/ 目录）
cd <skill_dir>
python scripts/oscillator.py [--axis-label 位置|时间] [--frames 120] [--fps 24]
```

### 输出
- 统一输出 **GIF 动图**（知乎可直接上传）
- 文件保存在 `output/` 目录下

### ⚠️ 关键：GIF格式要点（飞书/微信播放）

保存GIF时必须设置 `disposal=2`，否则会出现：
- 重影、拖尾
- 动画只显示第一帧
- 微信/飞书无法播放

```python
# 正确写法
gif.save(out_path, save_all=True, append_images=frames,
         duration=42, loop=0, disposal=2)
```

原因：`disposal=2` 表示每帧画之前先清空背景，确保每帧独立。

### 新建动图脚本规范

1. 放在 `scripts/` 目录下
2. 输出到 `output/` 目录
3. 默认输出 GIF 格式
4. 顶部写参数配置区域，方便调整
5. 每帧独立渲染（避免重影）
6. 中文标注用 `Arial Unicode MS` / `PingFang SC` 字体
7. 支持命令行参数覆盖默认配置
8. 完成后更新本文件的脚本列表

### 依赖

```
numpy
matplotlib
Pillow
```

虚拟环境：`/Users/xie/.openclaw/workspace/.venv/`

### 标准3D视角（全局统一）

所有3D动图默认使用以下视角，保持蟹大爷输出内容的一致性：
- `view_init(elev=25, azim=-60)`
- 坐标面板颜色：白色/透明（淡化背景）
- 网格线：极淡灰 `(0.9, 0.9, 0.9, 0.3)`

### 标准配色（全局统一）

| 元素 | 颜色 | 色值 |
|------|------|------|
| 主角球/运动体 | 橙红 | `#FF5722` |
| 主角球边框 | 深橙 | `#D84315` |
| 幻影/历史痕迹 | 淡灰 | `#CCCCCC` |
| 轨迹曲线 | 蓝色 | `#2196F3` |
| 空间轴标注 | 绿色 | `#4CAF50` |
| 标注文字颜色与对应元素颜色一致 | — | — |

### 设计原则

- 科普为主，直观优先
- 3D视角，物理符合直觉（重力朝下等）
- 关键位置留幻影，帮助读者理解运动过程
- 标注简洁，中文为主
- 标注颜色与对应元素颜色一致（主角标注=主角色，幻影标注=幻影色）
- 坐标面板白色/透明，淡化背景对主要元素的干扰

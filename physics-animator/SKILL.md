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
| `oscillator.py` | 单摆正弦曲线（纸带式） | `python scripts/oscillator.py` |

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

### 设计原则

- 科普为主，直观优先
- 3D视角，物理符合直觉（重力朝下等）
- 关键位置留幻影，帮助读者理解运动过程
- 标注简洁，中文为主
- 配色：蓝色轨迹、橙红色运动体、灰色辅助线

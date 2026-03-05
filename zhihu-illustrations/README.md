# 知乎文章配图工具

为蟹大爷的知乎技术文章生成示意图和动图。

## oscillator_3d.py - 单摆正弦曲线动图

演示"单摆左右荡 + 匀速前进 = 正弦曲线轨迹"的3D动图。

### 依赖

```bash
pip install numpy matplotlib Pillow
# MP4 转换需要 ffmpeg
brew install ffmpeg
```

### 运行

```bash
python oscillator_3d.py
```

### 输出
- `oscillator_3d.gif` — 动图版（知乎上传用）
- `oscillator_3d.mp4` — 视频版（预览用）

### 参数调整
修改脚本顶部的参数配置区域即可：
- `N_FRAMES` — 帧数（越多越流畅，文件越大）
- `FPS` — 帧率
- `A` — 摆动振幅
- `L` — 摆长
- `H` — 悬挂高度

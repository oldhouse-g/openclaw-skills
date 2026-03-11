# 冷记忆参考（从 MEMORY.md 迁出，2026-03-11）

## 阿肝与小芒的分工协作
- 小芒是蟹大爷的另一个机器人助理（芒格同学）
- **GitHub写操作统一由阿肝负责**，小芒不直接写GitHub
- 小芒有技能要备份到GitHub时 → 在群里@阿肝，把文件内容发给我，我来操作
- 小芒可以通过公开链接读取GitHub仓库中的技能
- 公开读取地址：https://raw.githubusercontent.com/oldhouse-g/openclaw-skills/main/{技能目录}/{文件名}
- 协作原则：分工明确，避免冲突

## 技能目录
- SKILLS-CATALOG.md = 蟹大爷的技能速查表（自然语言说明，不用记命令）
- 每次新增技能，阿肝自动更新这个文件
- 另一个机器人也参考同一份目录

## 工作偏好
- 把聪明写进代码，保证什么水平的模型都能跑出一样质量
- 简化依赖，追求独立可运行（如去掉tushare包依赖改用HTTP直调）
- 能代码化的尽可能代码化

## "把工作结果存下来"的默认动作
蟹大爷说"把这个工作结果存下来"时，依次执行：
1. 把代码整理成独立脚本，存到对应 skill 的 `scripts/` 目录
2. 更新 skill 的 `SKILL.md` 脚本列表
3. 更新 `SKILLS-CATALOG.md` 技能目录（加入新条目+自然语言调用说明）
4. 同步到 GitHub 仓库（oldhouse-g/openclaw-skills）
5. 更新 `MEMORY.md` 如有必要

## 3D动图标准规范
- 标准视角：elev=25, azim=-60（所有3D动图统一）
- 坐标面板：白色/透明
- 配色：主角=#FF5722, 幻影=#CCCCCC, 轨迹=#2196F3, 空间轴=#4CAF50
- 标注颜色与对应元素颜色一致
- GIF保存必须 disposal=2

## 飞书文档
- 蟹大爷说"存到飞书"时，**默认写入知识库中的"信息汇总"文档**（不要新建独立文档）
  - wiki链接：https://waveview.feishu.cn/wiki/ShcPwkbf7iGb7Fke02Wckytdnhg
  - doc_token：SDQHdOTRSoQTFZx7IimcX47Pnsd
  - space_id：7611028270892453065
- 文档目录结构：行业信息 / 投资分析 / 技术笔记 / 要闻摘要 / 其他
- 写入时根据内容类型追加到对应分类下，保持目录整洁

## 认知学习系统（2026-03-06建立）
- 三层架构：L1事实（USER.md）→ L2方法论 → L3元认知（COGNITION.md）
- 置信度驱动更新，不按时间
- 待确认发现池：memory/insights/pending.md
- 不可变原则锁定在 SOUL.md
- 主动发现+主动反馈+敢于指出认知需完善之处

## GitHub
- 账号：oldhouse-g
- 已登录 gh CLI（keyring 方式，token scopes: gist, read:org, repo, workflow）
- 主仓库：oldhouse-g/openclaw-skills（公开）
  - 统一由阿肝负责所有 GitHub 写操作
  - 其他机器人只读取 skills，不写入，避免冲突
  - tavily-search/、tushare-finance/、valuation/、physics-animator/
- 本地路径：/Users/xie/.openclaw/workspace/openclaw-skills/
- 远程：https://github.com/oldhouse-g/openclaw-skills.git（main分支）

## 已安装的技能
- tavily-search（Python 脚本，手动安装在 skills/tavily-search/）
- tushare-finance（通过 clawhub 安装）
- toutiao-news-trends（通过 clawhub 安装，抓取今日头条热榜）

## API Keys（已配置到 ~/.zshrc）
- TAVILY_API_KEY：已配置
- TUSHARE_TOKEN：已配置

## 教训
- 说了"写入中"但没真写 → 不做的事不承诺！
- heredoc/base64 在飞书传输中会损坏 → 用 echo 逐行写入更靠谱
- 指导蟹大爷操作要具体到"复制粘贴按回车"
- **群聊讨论隐私话题时，不能举真实例子说明存了什么信息，这本身就是泄露！**

## 冷记忆索引
> 详细日记存放在 memory/ 目录
> 按日期检索：memory/2026-03-04.md ~ memory/2026-03-07.md
> 知识体系：memory/knowledge/*.md（18个文件）
> 待确认发现池：memory/insights/pending.md

## 恢复记录
- 2026-03-09：从 agbackup-20260308-082803.tar.gz 恢复记忆和身份文件（不含模型配置）

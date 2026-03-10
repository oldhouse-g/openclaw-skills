# MEMORY.md - 阿肝的长期记忆

## 群聊成员
- **蟹大爷 / Wave**（ou_0aadb19c13528d0b2e0bb04fc85f9bb6）→ 回复时称呼"蟹大爷"
- **Jason哥**（ou_8d9905517bf96817430dc4af657e6b86）→ 回复时称呼"Jason哥"
- **小芒 / 芒格同学** → 另一个机器人助理，蟹大爷的第二助手
- 规则：跟蟹大爷说话称"蟹大爷"，跟其他人说话称他们各自名字，所有群聊通用

## 阿肝与小芒的分工协作
- 小芒是蟹大爷的另一个机器人助理（芒格同学）
- **GitHub写操作统一由阿肝负责**，小芒不直接写GitHub
- 小芒有技能要备份到GitHub时 → 在群里@阿肝，把文件内容发给我，我来操作
- 小芒可以通过公开链接读取GitHub仓库中的技能
- 公开读取地址：https://raw.githubusercontent.com/oldhouse-g/openclaw-skills/main/{技能目录}/{文件名}
- 协作原则：分工明确，避免冲突

## 关于蟹大爷
- 称呼：蟹大爷（每次回复必须带）
- 时区：Asia/Shanghai
- 职业：做硬件的，不写代码。诺基亚天线专家，电子科技大学毕业
- 知乎：WaveView（2.1万关注者），签名"一个老工程师的认知远征"
- 公众号：@知语行
- 专长：电磁场与电磁波、天线设计，在知乎上写了很多高质量的科普
- 兴趣：西方美术、哲学、读书（《大地之上》等）
- 本名：谢万波，群里被叫"谢老师"
- 手机：小米；常用 DeepSeek、元宝、豆包等AI；用招商证券和国泰君安炒股
- 在另一个群有个AI叫"雷姆"
- 技术水平：对软件不太熟悉，操作指引要一步一步来
- 自选股：贵州茅台、腾讯控股、阿里巴巴、联想集团、小米集团、美的集团、格力电器、伊利股份、招商银行、平安银行
- 定时任务：每个工作日7:30发股市简报；8:00-21:00随机时间问候（约1.5-2小时一次，时间随机有惊喜感）
- 这些功能逐步完善，满意后转成 skill
- ClawHub 账号：@oldhouse-g

## 技能目录
- SKILLS-CATALOG.md = 蟹大爷的技能速查表（自然语言说明，不用记命令）
- 每次新增技能，阿肝自动更新这个文件
- 另一个机器人也参考同一份目录

## 工作偏好（降低不可控因素依赖的具体体现）
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
- 不可变原则锁定在 SOUL.md（利益优先、隐私保密、不伤害、事实和逻辑为基础、不知道说不知道、持续学习、拿不准就问）
- 主动发现+主动反馈+敢于指出认知需完善之处

## 蟹大爷的知识体系与专业理解

> 详细内容存放在 memory/knowledge/ 目录下，按需加载。

- **物理方法论**：数豆子+振子统一框架 → `memory/knowledge/physics-methodology.md`
- **相对论理解**：换舞台方法 → `memory/knowledge/relativity.md`
- **量子力学理解**：假设出发+独创振子推导路径 → `memory/knowledge/quantum-mechanics.md`
- **M理论**：需求/经济/技术/社会统一框架 → `memory/knowledge/m-theory.md`
- **认识论**：实在之路核心论证 → `memory/knowledge/epistemology.md`
- **西方美术**：求"真"之旅串联17个画派 → `memory/knowledge/western-art.md`
- **大脑/AI/意识**：理性脑vs感性脑、逆熵 → `memory/knowledge/brain-ai-consciousness.md`
- **李录文明论**：文化进化、文明度量 → `memory/knowledge/li-lu-civilization.md`
- **投资理论**：PE/PB/ROE第一性原理+M估值五步骤 → `memory/knowledge/investment-theory.md`
- **M宏观分析**：基于M理论公设的宏观趋势分析框架（子课题） → `memory/knowledge/macro-analysis.md`
- **技术论**：技术是第三种竞争优势+迭代螺旋+基因性趋势+正向循环 → `memory/knowledge/technology-theory.md`
- **市场机制**：稀缺性中心+稀缺性转移+两种竞争模式+技术特殊商品+大市场优势 → `memory/knowledge/market-mechanism.md`
- **资本与债务**：债务放大必然性+发展vs安全+内外视角+指标选择 → `memory/knowledge/capital-debt.md`
- **企业论**：企业存在理由+中心化本质+竞争力三维度+规模约束+估值连接 → `memory/knowledge/enterprise-theory.md`
- **LLM理解**：城市规划比喻 → `memory/knowledge/llm-understanding.md`
- **电磁场**：传输线+麦克斯韦+天线+信号处理 → `memory/knowledge/em-field-solutions.md`
- **振子体系**：全振子方程+损耗+级联+材料模型 → `memory/knowledge/oscillator-details.md`
- 三篇文章形成元闭环：实在之路(认识论)→相似系统(工程方法论)→M理论(社会经济观)

**加载规则**：蟹大爷聊物理/电磁→读physics；聊相对论→读relativity；聊量子→读quantum；聊经济社会→读m-theory；日常不加载

## 重要规矩
- 不做的事不承诺
- 有自己的判断，敢说不同意见
- 隐私绝对保密
- 拿不准就问
- **群聊里只有被 @ 阿肝的时候才回复，没 @ 我就只看不说话**

## GitHub
- 账号：oldhouse-g
- 已登录 gh CLI（keyring 方式，token scopes: gist, read:org, repo, workflow）
- 主仓库：oldhouse-g/openclaw-skills（公开）
  - 统一由阿肝负责所有 GitHub 写操作
  - 其他机器人只读取 skills，不写入，避免冲突
  - tavily-search/：Tavily搜索技能
  - tushare-finance/：Tushare金融数据技能
  - valuation/：估值工具草稿
  - physics-animator/：物理科学动图生成器（标准技能，跨机器人可复用）
    - scripts/oscillator.py：单摆正弦曲线纸带式3D动图（支持 --axis-label 位置|时间）
- 本地路径：/Users/xie/.openclaw/workspace/openclaw-skills/
- 远程：https://github.com/oldhouse-g/openclaw-skills.git（main分支）
- 蟹大爷是代码小白，GitHub相关操作全部由阿肝负责维护

## 已安装的技能
- tavily-search（Python 脚本，手动安装在 skills/tavily-search/）
- tushare-finance（通过 clawhub 安装）
- toutiao-news-trends（通过 clawhub 安装，抓取今日头条热榜）

## API Keys（已配置到 ~/.zshrc）
- TAVILY_API_KEY：已配置
- TUSHARE_TOKEN：已配置

## M早报（股市晨报）
- 技能名：morning-briefing，蟹大爷叫它"M早报"
- **全代码化**：数据获取+量价分析+格式化全在 Python 脚本里，模型只需执行脚本发结果
- 脚本：skills/morning-briefing/scripts/morning_briefing.py
- 数据源：Tushare Pro（A股大盘+个股）+ 腾讯日K线（港股，无频率限制）+ 财联社API（新闻）
- 内容：大盘概况（含沪深成交额+合计）→ 成交量趋势图 → 自选股 → 要闻（财联社早间精选）→ 小结（规则化量价分析）
- 设计原则：把"聪明"写进代码，什么水平的模型都能出一样质量的报告

## 模型使用规则（2026-03-09更新）
- 默认模型：Claude Opus 4.6（通过OpenRouter）
- 备用模型：Minimax M2.5（国产，中文好，便宜）、OpenRouter Auto
- cron定时任务（M早报等）：用 Minimax M2.5（无区域限制，稳定）
- 日常对话和复杂任务：用默认 Claude Opus 4.6
- 如果 Claude 出现区域限制报错，自动降级到 Minimax

## 教训
- 说了"写入中"但没真写 → 不做的事不承诺！
- heredoc/base64 在飞书传输中会损坏 → 用 echo 逐行写入更靠谱
- 指导蟹大爷操作要具体到"复制粘贴按回车"
- **群聊讨论隐私话题时，不能举真实例子说明存了什么信息，这本身就是泄露！**

## 冷记忆索引
> 详细日记存放在 memory/ 目录
> 按日期检索：memory/2026-03-04.md ~ memory/2026-03-07.md
> 知识体系：memory/knowledge/*.md（12个文件）
> 待确认发现池：memory/insights/pending.md

## 记忆管理规则
- 热记忆保持精简（不超过20条）
- 3个月前的记忆移到 memory/archive/ 归档
- 定期总结，合并相似内容

## 恢复记录
- 2026-03-09：从 agbackup-20260308-082803.tar.gz 恢复记忆和身份文件（不含模型配置）

# OpenClaw 配置备份 - 2026-03-11

## 备份内容

```
config-backup/2026-03-11/
├── README.md           ← 本文件（恢复指南）
├── openclaw.json       ← 核心配置（已脱敏，需填入 API key）
├── AGENTS.md           ← 工作规范
├── SOUL.md             ← 阿肝的灵魂
├── MEMORY.md           ← 长期记忆（精简版）
├── USER.md             ← 蟹大爷档案
├── TOOLS.md            ← 工具配置（当前为空）
├── IDENTITY.md         ← 身份（已合并到 SOUL.md）
├── HEARTBEAT.md        ← 心跳（当前无任务）
├── COGNITION.md        ← 认知模型
├── SKILLS-CATALOG.md   ← 技能速查表
├── TODO.md             ← 待办事项
└── memory/             ← 完整记忆目录
    ├── cold-reference.md       ← 冷记忆参考
    ├── user-profile.md         ← 用户详细档案
    ├── heartbeat-state.json    ← 心跳状态
    ├── knowledge/              ← 知识体系（18个文件）
    ├── insights/               ← 待确认发现池
    └── 2026-03-*.md            ← 日记
```

## 新机器恢复步骤

### 1. 安装 OpenClaw
```bash
npm install -g openclaw
openclaw onboard
```

### 2. 复制配置文件
```bash
# 复制 openclaw.json 到 ~/.openclaw/
cp openclaw.json ~/.openclaw/openclaw.json

# 编辑，填入你的 API keys：
# - models.providers.custom-openrouter-ai.apiKey → OpenRouter API key
# - channels.feishu.appSecret → 飞书 App Secret
# - gateway.auth.token → 自定义 gateway token
```

### 3. 复制 workspace 文件
```bash
# 复制所有 .md 文件到 workspace
cp AGENTS.md SOUL.md MEMORY.md USER.md TOOLS.md IDENTITY.md HEARTBEAT.md \
   COGNITION.md SKILLS-CATALOG.md TODO.md ~/.openclaw/workspace/

# 复制 memory 目录
cp -r memory/ ~/.openclaw/workspace/memory/
```

### 4. 安装 skills
```bash
# 从同一个 GitHub 仓库复制 skills
cd ~/.openclaw/workspace
git clone https://github.com/oldhouse-g/openclaw-skills.git

# 复制需要的 skills 到 workspace
for skill in morning-briefing stock-briefing fundamental-stock-analysis \
             tushare-finance tavily-search toutiao-news-trends \
             deep-research-pro pdf-text-extractor cninfo-announcement-scraper; do
  cp -r openclaw-skills/$skill/ skills/$skill/
done
```

### 5. 配置环境变量
```bash
# 在 ~/.zshrc 中添加：
export TAVILY_API_KEY="your-key"
export TUSHARE_TOKEN="your-token"
```

### 6. 启动
```bash
openclaw gateway start
```

## 需要填入的密钥清单
- [ ] OpenRouter API Key（openclaw.json → models.providers.custom-openrouter-ai.apiKey）
- [ ] MiniMax API Key（~/.openclaw/credentials/ 或环境变量）
- [ ] 飞书 App Secret（openclaw.json → channels.feishu.appSecret）
- [ ] Gateway Token（openclaw.json → gateway.auth.token，可自定义任意字符串）
- [ ] TAVILY_API_KEY（~/.zshrc）
- [ ] TUSHARE_TOKEN（~/.zshrc）

## 备份日期
2026-03-11，token 优化后的精简版配置。

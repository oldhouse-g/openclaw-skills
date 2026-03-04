# OpenClaw Skills 代码库

蟹大爷的个人 skill 库。任何新的 OpenClaw 实例 + 任何模型，一条命令装好所有 skill。

## 一键安装

```bash
curl -sL https://raw.githubusercontent.com/oldhouse-g/openclaw-skills/main/install.sh | bash
```

或者手动：

```bash
git clone https://github.com/oldhouse-g/openclaw-skills.git
cd openclaw-skills
bash install.sh
```

## 安装后需要配置的 API Keys

安装脚本会自动把 skill 复制到正确位置，但 API keys 需要手动配置：

```bash
# Tavily 搜索（网页搜索）
export TAVILY_API_KEY="你的key"

# Tushare 金融数据
export TUSHARE_TOKEN="你的token"
```

建议写入 `~/.zshrc` 永久生效：

```bash
echo 'export TAVILY_API_KEY="你的key"' >> ~/.zshrc
echo 'export TUSHARE_TOKEN="你的token"' >> ~/.zshrc
source ~/.zshrc
```

## 包含的 Skills

| Skill | 功能 | 依赖 |
|-------|------|------|
| tavily-search | AI 网页搜索 | Python3, TAVILY_API_KEY |
| tushare-finance | 中国金融市场数据（A股/港股/美股/基金/宏观） | Python3, tushare, pandas, TUSHARE_TOKEN |

## 给新助手的说明

如果你是一个新的 OpenClaw 助手，请：

1. 运行 `install.sh` 安装所有 skill
2. 让用户配置 API keys
3. 重启 OpenClaw：`openclaw gateway restart`
4. 测试：
   - 搜索：`python3 ~/.openclaw/workspace/skills/tavily-search/scripts/search.py "测试"`
   - 金融：`python3 -c "import tushare as ts; pro=ts.pro_api(); print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,name').head())"`

## 设计原则

- **代码做事，模型只管调用** — 保证跨模型结果一致
- **密钥不入库** — API keys 只存本地环境变量
- **一键安装** — 用户不需要懂代码

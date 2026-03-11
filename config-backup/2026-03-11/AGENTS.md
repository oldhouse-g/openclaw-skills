# AGENTS.md - 阿肝的工作规范

## 自动注入的文件（不需要手动 read）
以下文件已通过 OpenClaw workspace 机制自动注入到每轮上下文中：
- SOUL.md、USER.md、MEMORY.md、TOOLS.md、HEARTBEAT.md
- **不要再手动 read 这些文件，避免重复消耗 token**

## 按需加载（根据场景判断，用 memory_search 检索）
- COGNITION.md — 当需要深度理解蟹大爷时
- memory/user-profile.md — 蟹大爷详细背景
- memory/cold-reference.md — 工作偏好、GitHub、飞书、技能目录、教训等
- memory/knowledge/*.md — 蟹大爷的知识体系（物理、经济、哲学等）
- memory/*.md — 具体日期的日记

## 群聊规则
- 只有被 @ 才回复

## 记忆原则
- 重要事项写入 MEMORY.md 或 memory/ 文件
- 写文件比记脑子更可靠

## exec 输出控制
- 命令输出要精确控制长度：加 `| head` / `| tail` / `| grep` 过滤
- 避免无用信息涌入上下文消耗 token
- 这是默认工作习惯，每次 exec 都要注意

## 记忆管理
- MEMORY.md 保持精简（核心信息 + 索引）
- 冷信息放 memory/ 子文件，通过 memory_search 按需检索
- 3个月前的内容移到 memory/archive/ 归档

# GitHub 发布验收清单

- [x] 仓库为 Public。
- [x] README 第一屏能看懂项目目标、范围和关键结果。
- [x] 没有 API Key、密码、Token 或真实客户数据。
- [x] 有业务问题和用户场景。
- [x] 有系统架构图。
- [ ] 有脱敏的 Agent Desk RAG 运行截图。
- [x] 有可复现的离线 RAG 引用与评测成功证据图。
- [x] 有工具调用/任务路由证据。
- [ ] 有 Agent Desk 转人工流程截图。
- [x] 有脱敏的 Agent Desk 工单截图。
- [x] 有 80 条评测数据。
- [x] 有第一轮真实离线指标。
- [x] 有 Bad Case 分类。
- [x] 有 Prompt/知识库迭代记录。
- [x] 有第二轮复测。
- [x] 有迭代前后指标对比。
- [x] 有清晰的开源项目引用与许可证说明。
- [ ] 至少使用一个 Branch 和一个远程 PR。
- [x] Commit 信息体现开发过程。
- [x] 截图完成最终密钥/真实客户数据复核。

当前阻塞说明：Agent Desk 的本地 Ollama embedding 端点拒绝连接，Gemini 历史调用为 503/超时，因此不把失败页面包装成 RAG 成功截图。远程 Branch/PR 状态以 GitHub 为准，不能用模拟截图代替真实 Agent Desk 现场证据。

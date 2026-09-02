# Agent Desk 现场证据

## 已验证

2026-09-02 对本机 Agent Desk SQLite 进行只读、脱敏导出：

- Agent：`电商售后客服`，2 个发布修订；
- 知识库：`电商售后知识库`，4 份文档；
- 运行记录：7 次 Agent Run、15 个 Step；
- RAG：退货问题多次返回 `retrieved context items: 2`；
- 工具/工单：导出时均为 0 条。

## 历史失败分类

| 分类 | 次数 | 说明 |
| --- | ---: | --- |
| Provider 函数名校验 | 2 | Gemini OpenAI 兼容接口不接受带 `/` 的工具函数名 |
| Provider 503 高负载 | 4 | 模型端临时不可用 |
| Provider 超时 | 1 | 120 秒后仍未返回 |

本机 Agent Desk 源码中存在未提交的 provider-safe 工具别名修复；作品集没有把这项本地修改冒充上游贡献。完整脱敏数据见 `reports/live_agent_desk_evidence.json`。

## 证据边界

- 可证明：Agent 和知识库已配置；RAG 检索步骤实际执行并命中。
- 暂不可证明：Gemini 在线回复成功、Agent Desk 内真实工具调用成功、真实工单创建成功。
- 离线工具与风险指标来自本仓库的确定性 Harness，不能替代上述现场证据。


# 线上观测与反馈闭环

当前仓库以本地 CSV/JSON 为事实来源；没有声称已部署 Langfuse。

## 建议映射

| 本项目字段 | Langfuse/等价平台对象 |
| --- | --- |
| case_id / conversation_id | session |
| 一次 Agent 回答 | trace |
| 路由、检索、模型、工具 | span/generation |
| intent、risk_level、handoff | metadata |
| 正确/完整/安全 | score |
| 人工备注 | feedback/comment |

## 生产闭环

1. 记录 Trace、模型版本、Prompt 版本和知识库版本。
2. 对低分、用户点踩、人工接管和工具失败建立 Bad Case 数据集。
3. 完成隐私脱敏和人工标注。
4. 用 Promptfoo 或等价系统做固定回归。
5. 达到门槛后灰度发布，并比较线上 CSAT、转人工率和一次解决率。


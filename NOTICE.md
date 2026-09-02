# NOTICE — 开源参考与来源说明

核对日期：2026-09-02。

本仓库的评测数据、Prompt、知识文档、Python Harness 和说明文档为作品集原创内容。参考项目仅用于产品形态、架构和评测方法研究，没有把第三方源码复制进本仓库。

## 参考项目

- Agent Desk — https://github.com/huabeitech/agent-desk — Apache License 2.0。
- Arklex Agent-First Organization — https://github.com/arklexai/Agent-First-Organization — MIT License。
- Tau2 Bench — https://github.com/sierra-research/tau2-bench — MIT License。
- Langfuse — https://github.com/langfuse/langfuse — 核心目录 MIT Expat；企业目录使用仓库中单独许可证。
- Promptfoo — https://github.com/promptfoo/promptfoo — MIT License。

## 使用边界

- Agent Desk 在本机独立目录运行；本仓库仅保存脱敏配置摘要与运行证据。
- 80 条测试是为本电商售后场景从零编写，只借鉴 Tau2 的任务式结构。
- Promptfoo 配置依据其官方 Python Provider 接口编写。
- Langfuse 仅作为后续线上 Trace/反馈闭环参考，当前未部署、未产生云端数据。


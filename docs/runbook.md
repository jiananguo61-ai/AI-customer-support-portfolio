# 运行手册

## 离线评测

```powershell
.\run.ps1
```

成功条件：生成 80 条测试、输出 V1/V2 指标，5 个单元测试全部通过。

## Promptfoo（可选）

Node.js 22.22+ 环境中执行：

```bash
npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache
npx promptfoo@latest view
```

配置使用 Promptfoo 官方支持的 Python Provider 形式，不调用外部模型。

## 导出本机 Agent Desk 脱敏证据

```powershell
python scripts/export_agent_desk_evidence.py --db "<agent-desk目录>\data\app.db"
```

脚本不选择 API Key、登录 Token、手机号、邮箱等字段，只输出结构、计数和错误类别。

## Agent Desk 本机入口

- 管理后台：`http://127.0.0.1:8083/dashboard`
- 客服工作台：`http://127.0.0.1:8083/dashboard/conversations`
- 客户演示：`http://127.0.0.1:8083/support/demo`
- 客户聊天：`http://127.0.0.1:8083/support/chat`

不要在公开仓库记录后台密码、API Key、浏览器会话或真实客户数据。


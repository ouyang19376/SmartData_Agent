# SmartData Agent V1.0

银行数据智能问数 Agent：自然语言 -> 规划 -> 工具执行 -> 校验/重规划 -> 答案。

## 技术栈
Python 3.11 / LangGraph / LangChain / FastAPI / PostgreSQL / SQLAlchemy / Pydantic / pytest

## 启动（环境配置完成后）
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# 编辑 .env 后
uvicorn app.main:app --reload
```

## 里程碑
- M0 环境与骨架
- M1 PostgreSQL 元数据/演示数据
- M2 Planner（结构化计划 + 校验）
- M3 Executor（工具注册、依赖调度、状态）
- M4 Replanner（异常/缺数反馈）
- M5 LangGraph 工作流
- M6 FastAPI + 可观测性 + 测试
- M7 银行问数场景端到端

当前仓库为项目骨架，LLM 和数据库连接由使用者配置。

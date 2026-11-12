
import os

import pytest

from app.agent.llm_factory import create_llm
from app.agent.planner import Planner
from app.agent.plan_schema import AgentPlan


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LLM_INTEGRATION") != "1",
    reason="真实 LLM 集成测试默认关闭",
)


def test_real_llm_planner():
    """
    真实模型集成测试。

    验证：
    1. 模型 API 可以正常调用
    2. 模型能够生成 AgentPlan
    3. 结构化输出能够被 Pydantic 解析
    4. 计划能够通过 PlanValidator
    """

    llm = create_llm()
    planner = Planner(llm=llm)

    context_text = """
    指标：
    LOAN_BALANCE
    中文名称：贷款余额
    业务定义：统计贷款账户当前未偿还本金余额。

    数据模型：
    dwd_loan_account

    已知字段：
    account_id：贷款账户编号
    branch_code：机构编号
    loan_balance：贷款余额
    snapshot_date：数据日期

    注意：
    以上元数据仅用于演示。
    不得编造其他字段。
    """

    result = planner.plan(
        question="查询广州机构的贷款余额",
        context_text=context_text,
    )

    assert isinstance(result, AgentPlan)

    assert result.goal
    assert isinstance(result.steps, list)

    if result.requires_clarification:
        assert result.clarification_question
    else:
        assert len(result.steps) > 0

    print("\n真实 LLM Planner 输出：")
    print(result.model_dump_json(indent=2))


from unittest.mock import Mock

import pytest

from app.agent.plan_schema import AgentPlan
from app.agent.planner import Planner, PlannerError


class FakeStructuredLLM:
    """模拟支持 Structured Output 的 LLM。"""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.invoke_count = 0

    def with_structured_output(self, schema):
        assert schema is AgentPlan
        return self

    def invoke(self, messages):
        self.invoke_count += 1

        assert len(messages) == 2

        if self.error:
            raise self.error

        return self.result


def build_valid_plan():
    return AgentPlan(
        goal="查询广州机构贷款余额",
        reasoning_summary="使用贷款余额指标和贷款账户模型",
        requires_clarification=False,
        clarification_question=None,
        steps=[
            {
                "step_id": "step_1",
                "tool_name": "generate_sql",
                "description": "生成广州机构贷款余额查询 SQL",
                "dependencies": [],
                "inputs": {},
            },
            {
                "step_id": "step_2",
                "tool_name": "validate_sql",
                "description": "校验 SQL",
                "dependencies": ["step_1"],
                "inputs": {},
            },
            {
                "step_id": "step_3",
                "tool_name": "execute_sql",
                "description": "执行 SQL",
                "dependencies": ["step_2"],
                "inputs": {},
            },
            {
                "step_id": "step_4",
                "tool_name": "analyze_result",
                "description": "分析贷款余额结果",
                "dependencies": ["step_3"],
                "inputs": {},
            },
        ],
    )


def test_planner_success():
    llm = FakeStructuredLLM(result=build_valid_plan())

    planner = Planner(llm=llm)

    result = planner.plan(
        question="查询广州机构贷款余额",
        context_text="LOAN_BALANCE: 贷款余额",
    )

    assert isinstance(result, AgentPlan)
    assert result.goal == "查询广州机构贷款余额"
    assert len(result.steps) == 4
    assert llm.invoke_count == 1


def test_planner_empty_question():
    llm = FakeStructuredLLM(result=build_valid_plan())
    planner = Planner(llm=llm)

    with pytest.raises(ValueError):
        planner.plan(
            question="",
            context_text="",
        )


def test_planner_llm_error():
    llm = FakeStructuredLLM(
        error=RuntimeError("模拟 API 异常")
    )

    planner = Planner(llm=llm)

    with pytest.raises(PlannerError):
        planner.plan(
            question="查询贷款余额",
            context_text="",
        )


def test_planner_clarification():
    clarification_plan = AgentPlan(
        goal="查询贷款余额",
        reasoning_summary="缺少统计时间范围",
        requires_clarification=True,
        clarification_question="请问查询哪个月份的贷款余额？",
        steps=[],
    )

    llm = FakeStructuredLLM(result=clarification_plan)

    planner = Planner(llm=llm)

    result = planner.plan(
        question="查询贷款余额",
        context_text="LOAN_BALANCE",
    )

    assert result.requires_clarification is True
    assert result.clarification_question == (
        "请问查询哪个月份的贷款余额？"
    )

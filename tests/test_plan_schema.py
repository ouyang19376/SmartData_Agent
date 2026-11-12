
import pytest
from pydantic import ValidationError

from app.agent.plan_schema import AgentPlan


def test_valid_agent_plan():
    """正常计划应该通过校验。"""

    plan = AgentPlan(
        goal="统计2026年广东各分行贷款余额",
        reasoning_summary="需要生成SQL、校验SQL并执行查询",
        steps=[
            {
                "step_id": "step_1",
                "tool_name": "generate_sql",
                "description": "生成贷款余额查询SQL",
                "dependencies": [],
                "inputs": {
                    "metric_code": "LOAN_BALANCE",
                    "year": 2026,
                    "province": "广东"
                }
            },
            {
                "step_id": "step_2",
                "tool_name": "validate_sql",
                "description": "校验SQL",
                "dependencies": ["step_1"],
                "inputs": {}
            },
            {
                "step_id": "step_3",
                "tool_name": "execute_sql",
                "description": "执行SQL",
                "dependencies": ["step_2"],
                "inputs": {}
            }
        ]
    )

    assert len(plan.steps) == 3
    assert plan.steps[0].tool_name == "generate_sql"


def test_duplicate_step_id():
    """重复步骤ID应该校验失败。"""

    with pytest.raises(ValidationError):
        AgentPlan(
            goal="测试任务",
            reasoning_summary="测试重复ID",
            steps=[
                {
                    "step_id": "step_1",
                    "tool_name": "generate_sql",
                    "description": "步骤一"
                },
                {
                    "step_id": "step_1",
                    "tool_name": "execute_sql",
                    "description": "步骤二"
                }
            ]
        )


def test_invalid_dependency():
    """依赖不存在的步骤应该校验失败。"""

    with pytest.raises(ValidationError):
        AgentPlan(
            goal="测试任务",
            reasoning_summary="测试依赖",
            steps=[
                {
                    "step_id": "step_1",
                    "tool_name": "execute_sql",
                    "description": "执行SQL",
                    "dependencies": ["step_999"]
                }
            ]
        )


def test_clarification_plan():
    """需要澄清的计划允许暂时没有执行步骤。"""

    plan = AgentPlan(
        goal="查询贷款余额",
        reasoning_summary="统计时间范围不明确",
        requires_clarification=True,
        clarification_question="请问需要查询哪个日期或时间范围？",
        steps=[]
    )

    assert plan.requires_clarification is True

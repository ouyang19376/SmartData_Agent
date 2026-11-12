
import pytest

from app.agent.plan_schema import AgentPlan
from app.agent.validator import (
    PlanValidator,
    PlanValidationError,
)


def make_plan(steps):
    return AgentPlan(
        goal="测试任务",
        reasoning_summary="测试计划校验",
        steps=steps,
    )


def test_valid_plan():
    """正常的线性依赖计划应该通过。"""

    plan = make_plan([
        {
            "step_id": "step_1",
            "tool_name": "generate_sql",
            "description": "生成SQL",
            "dependencies": [],
        },
        {
            "step_id": "step_2",
            "tool_name": "validate_sql",
            "description": "校验SQL",
            "dependencies": ["step_1"],
        },
        {
            "step_id": "step_3",
            "tool_name": "execute_sql",
            "description": "执行SQL",
            "dependencies": ["step_2"],
        },
    ])

    validator = PlanValidator()

    result = validator.validate(plan)

    assert result == ["step_1", "step_2", "step_3"]


def test_topological_sort():
    """即使步骤声明顺序不同，也应得到合法执行顺序。"""

    plan = make_plan([
        {
            "step_id": "step_3",
            "tool_name": "execute_sql",
            "description": "执行SQL",
            "dependencies": ["step_2"],
        },
        {
            "step_id": "step_1",
            "tool_name": "generate_sql",
            "description": "生成SQL",
            "dependencies": [],
        },
        {
            "step_id": "step_2",
            "tool_name": "validate_sql",
            "description": "校验SQL",
            "dependencies": ["step_1"],
        },
    ])

    result = PlanValidator().validate(plan)

    assert result.index("step_1") < result.index("step_2")
    assert result.index("step_2") < result.index("step_3")


def test_cycle_dependency():
    """循环依赖应该被拒绝。"""

    plan = make_plan([
        {
            "step_id": "step_1",
            "tool_name": "generate_sql",
            "description": "生成SQL",
            "dependencies": ["step_3"],
        },
        {
            "step_id": "step_2",
            "tool_name": "validate_sql",
            "description": "校验SQL",
            "dependencies": ["step_1"],
        },
        {
            "step_id": "step_3",
            "tool_name": "execute_sql",
            "description": "执行SQL",
            "dependencies": ["step_2"],
        },
    ])

    with pytest.raises(PlanValidationError, match="循环依赖"):
        PlanValidator().validate(plan)


def test_unknown_tool():
    """不在工具白名单中的工具应该被拒绝。"""

    plan = make_plan([
        {
            "step_id": "step_1",
            "tool_name": "generate_sql",
            "description": "生成SQL",
        }
    ])

    validator = PlanValidator(
        allowed_tools={"execute_sql"}
    )

    with pytest.raises(PlanValidationError, match="不允许调用工具"):
        validator.validate(plan)


def test_max_steps():
    """步骤数量不能超过配置上限。"""

    plan = make_plan([
        {
            "step_id": "step_1",
            "tool_name": "generate_sql",
            "description": "生成SQL",
        },
        {
            "step_id": "step_2",
            "tool_name": "validate_sql",
            "description": "校验SQL",
        },
    ])

    validator = PlanValidator(max_steps=1)

    with pytest.raises(PlanValidationError, match="超过限制"):
        validator.validate(plan)


def test_clarification_plan():
    """澄清计划不需要进入执行调度。"""

    plan = AgentPlan(
        goal="查询贷款余额",
        reasoning_summary="统计日期不明确",
        requires_clarification=True,
        clarification_question="请问查询哪个日期？",
        steps=[],
    )

    assert PlanValidator().validate(plan) == []

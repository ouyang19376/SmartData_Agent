
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# 当前阶段预定义的工具名称。
# 后续 M3 Executor 会为这些工具注册实际执行函数。
ToolName = Literal[
    "generate_sql",
    "validate_sql",
    "execute_sql",
    "analyze_result",
    "answer_question",
]


class PlanStep(BaseModel):
    """Agent 执行计划中的一个步骤。"""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(
        description="步骤唯一标识，例如 step_1"
    )

    tool_name: ToolName = Field(
        description="该步骤需要调用的工具名称"
    )

    description: str = Field(
        description="步骤的具体任务描述"
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="当前步骤依赖的其他步骤ID"
    )

    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="调用工具所需的输入参数"
    )


class AgentPlan(BaseModel):
    """Planner 输出的完整任务计划。"""

    model_config = ConfigDict(extra="forbid")

    goal: str = Field(
        description="对用户目标的简洁描述"
    )

    reasoning_summary: str = Field(
        description="简要说明任务拆解依据，不要求输出详细内部推理"
    )

    requires_clarification: bool = Field(
        default=False,
        description="当前信息不足以制定可靠计划时设为True"
    )

    clarification_question: str | None = Field(
        default=None,
        description="需要用户补充的信息"
    )

    steps: list[PlanStep] = Field(
        default_factory=list,
        description="按照执行依赖组织的任务步骤"
    )

    @model_validator(mode="after")
    def validate_plan_structure(self):
        """检查计划内部的基础结构。"""

        if self.requires_clarification:
            if not self.clarification_question:
                raise ValueError(
                    "需要用户澄清时，必须提供 clarification_question"
                )
            return self

        if not self.steps:
            raise ValueError("正常执行计划至少需要一个步骤")

        step_ids = [step.step_id for step in self.steps]

        if len(step_ids) != len(set(step_ids)):
            raise ValueError("step_id 不能重复")

        known_ids = set(step_ids)

        for step in self.steps:
            for dependency in step.dependencies:
                if dependency not in known_ids:
                    raise ValueError(
                        f"{step.step_id} 依赖了不存在的步骤：{dependency}"
                    )

                if dependency == step.step_id:
                    raise ValueError(
                        f"{step.step_id} 不能依赖自己"
                    )

        return self

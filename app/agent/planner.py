
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.plan_schema import AgentPlan
from app.agent.prompts import PLANNER_SYSTEM_PROMPT
from app.agent.validator import PlanValidator


class PlannerError(Exception):
    """Planner 执行异常。"""


class Planner:
    """
    SmartData Agent Planner。

    职责：
    1. 接收用户问题和数据上下文
    2. 调用 LLM 生成 AgentPlan
    3. 使用 PlanValidator 校验计划
    4. 返回合法的 AgentPlan
    """

    def __init__(
        self,
        llm: Any,
        validator: PlanValidator | None = None,
    ):
        self.llm = llm
        self.validator = validator or PlanValidator()

        # 使用 LangChain Structured Output
        self.structured_llm = self.llm.with_structured_output(
            AgentPlan
        )

    def plan(
        self,
        question: str,
        context_text: str,
    ) -> AgentPlan:
        """
        根据用户问题和数据上下文生成执行计划。
        """

        if not question or not question.strip():
            raise ValueError("用户问题不能为空")

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(
                content=f"""
用户问题：
{question}

数据仓库元数据：
{context_text}

请根据上述信息生成 AgentPlan。
"""
            ),
        ]

        try:
            # 调用 LLM，返回 Pydantic AgentPlan 对象
            result = self.structured_llm.invoke(messages)

        except Exception as exc:
            raise PlannerError(
                f"LLM Planner 调用失败：{exc}"
            ) from exc

        if not isinstance(result, AgentPlan):
            raise PlannerError(
                "LLM 返回结果不是有效的 AgentPlan"
            )

        # 使用现有 PlanValidator 进行校验
        try:
            execution_order = self.validator.validate(result)

        except Exception as exc:
            raise PlannerError(
                f"AgentPlan 校验失败：{exc}"
            ) from exc

        # 返回经过校验的计划
        return result

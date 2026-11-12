
from collections import deque

from app.agent.plan_schema import AgentPlan


class PlanValidationError(Exception):
    """Agent 执行计划校验异常。"""


class PlanValidator:
    """
    AgentPlan 工程级校验器。

    当前负责：
    1. 检查步骤数量
    2. 检查工具白名单
    3. 检查依赖关系
    4. 检查 DAG 循环依赖
    5. 计算拓扑执行顺序
    """

    DEFAULT_ALLOWED_TOOLS = {
        "generate_sql",
        "validate_sql",
        "execute_sql",
        "analyze_result",
        "answer_question",
    }

    def __init__(
        self,
        allowed_tools: set[str] | None = None,
        max_steps: int = 10,
    ):
        self.allowed_tools = (
            allowed_tools
            if allowed_tools is not None
            else self.DEFAULT_ALLOWED_TOOLS
        )
        self.max_steps = max_steps

    def validate(self, plan: AgentPlan) -> list[str]:
        """
        校验计划并返回合法的拓扑执行顺序。

        返回示例：
        ["step_1", "step_2", "step_3"]

        校验失败时抛出 PlanValidationError。
        """

        if plan.requires_clarification:
            if not plan.clarification_question:
                raise PlanValidationError(
                    "澄清计划缺少 clarification_question"
                )
            return []

        steps = plan.steps

        if not steps:
            raise PlanValidationError("计划中没有执行步骤")

        if len(steps) > self.max_steps:
            raise PlanValidationError(
                f"步骤数量超过限制：{len(steps)} > {self.max_steps}"
            )

        step_map = {
            step.step_id: step
            for step in steps
        }

        # 1. 工具白名单检查
        for step in steps:
            if step.tool_name not in self.allowed_tools:
                raise PlanValidationError(
                    f"不允许调用工具：{step.tool_name}"
                )

        # 2. 依赖合法性检查
        for step in steps:
            for dependency in step.dependencies:
                if dependency not in step_map:
                    raise PlanValidationError(
                        f"{step.step_id} 依赖不存在的步骤：{dependency}"
                    )

                if dependency == step.step_id:
                    raise PlanValidationError(
                        f"{step.step_id} 不能依赖自己"
                    )

        # 3. 构建 DAG 入度表和邻接表
        in_degree = {
            step.step_id: 0
            for step in steps
        }

        graph = {
            step.step_id: []
            for step in steps
        }

        for step in steps:
            for dependency in step.dependencies:
                # dependency -> 当前 step
                graph[dependency].append(step.step_id)
                in_degree[step.step_id] += 1

        # 4. Kahn 拓扑排序
        queue = deque(
            step.step_id
            for step in steps
            if in_degree[step.step_id] == 0
        )

        execution_order = []

        while queue:
            current = queue.popleft()
            execution_order.append(current)

            for next_step in graph[current]:
                in_degree[next_step] -= 1

                if in_degree[next_step] == 0:
                    queue.append(next_step)

        # 5. 如果排序结果数量不足，说明存在循环依赖
        if len(execution_order) != len(steps):
            cycle_steps = [
                step_id
                for step_id, degree in in_degree.items()
                if degree > 0
            ]

            raise PlanValidationError(
                f"计划存在循环依赖，涉及步骤：{cycle_steps}"
            )

        return execution_order

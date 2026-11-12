
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.session import engine


class ContextBuilder:
    """
    为 Planner 构建银行数仓业务上下文。

    当前版本：
    1. 查询指标定义
    2. 查询模型定义
    3. 根据关键词进行简单过滤
    4. 生成 Planner 可使用的上下文文本
    """

    def __init__(self, db_engine: Any = engine):
        self.engine = db_engine

    def get_metrics(self) -> list[dict]:
        """读取所有启用的指标定义。"""
        sql = text("""
            SELECT
                metric_code,
                metric_name,
                business_definition,
                calculation_rule,
                source_tables,
                dimensions
            FROM agent_meta.metric_definition
            WHERE status = 'ACTIVE'
            ORDER BY metric_code
        """)

        with self.engine.connect() as conn:
            rows = conn.execute(sql).mappings().all()

        return [dict(row) for row in rows]

    def get_models(self) -> list[dict]:
        """读取所有启用的数据模型定义。"""
        sql = text("""
            SELECT
                model_name,
                schema_name,
                table_name,
                model_layer,
                business_description,
                columns_json,
                tags
            FROM agent_meta.model_definition
            WHERE status = 'ACTIVE'
            ORDER BY model_name
        """)

        with self.engine.connect() as conn:
            rows = conn.execute(sql).mappings().all()

        return [dict(row) for row in rows]

    @staticmethod
    def _match_keyword(text_value: str, keywords: list[str]) -> bool:
        """判断文本是否包含任意关键词。"""
        text_value = (text_value or "").lower()
        return any(keyword.lower() in text_value for keyword in keywords)

    def search_metrics(
        self,
        question: str,
        metrics: list[dict] | None = None,
    ) -> list[dict]:
        """根据用户问题筛选指标。"""
        metrics = metrics if metrics is not None else self.get_metrics()

        keywords = ["贷款", "余额", "客户", "loan", "balance"]

        matched = []
        for metric in metrics:
            content = (
                metric.get("metric_name", "")
                + " "
                + metric.get("metric_code", "")
                + " "
                + metric.get("business_definition", "")
            )

            if self._match_keyword(content, keywords):
                matched.append(metric)

        # 暂时没有语义检索能力时，返回全部指标作为兜底
        return matched or metrics

    def search_models(
        self,
        question: str,
        models: list[dict] | None = None,
    ) -> list[dict]:
        """根据用户问题筛选模型。"""
        models = models if models is not None else self.get_models()

        keywords = ["贷款", "余额", "客户", "loan", "account"]

        matched = []
        for model in models:
            content = (
                model.get("model_name", "")
                + " "
                + model.get("business_description", "")
                + " "
                + " ".join(model.get("tags") or [])
            )

            if self._match_keyword(content, keywords):
                matched.append(model)

        return matched or models

    def build_context(self, question: str) -> dict:
        """构建 Planner 所需完整上下文。"""
        metrics = self.search_metrics(question)
        models = self.search_models(question)

        return {
            "user_question": question,
            "metrics": metrics,
            "models": models,
            "context_text": self.format_context(metrics, models),
        }

    @staticmethod
    def format_context(
        metrics: list[dict],
        models: list[dict],
    ) -> str:
        """将元数据格式化为适合 LLM 阅读的文本。"""
        sections = []

        sections.append("## 可用业务指标")
        for metric in metrics:
            sections.append(
                f"""
指标名称：{metric.get('metric_name')}
指标编码：{metric.get('metric_code')}
业务定义：{metric.get('business_definition')}
计算规则：{metric.get('calculation_rule')}
来源表：{metric.get('source_tables')}
可用维度：{metric.get('dimensions')}
"""
            )

        sections.append("\n## 可用数据模型")
        for model in models:
            sections.append(
                f"""
模型名称：{model.get('model_name')}
物理表：{model.get('schema_name')}.{model.get('table_name')}
模型层级：{model.get('model_layer')}
业务描述：{model.get('business_description')}
字段定义：{model.get('columns_json')}
标签：{model.get('tags')}
"""
            )

        return "\n".join(sections)


if __name__ == "__main__":
    builder = ContextBuilder()

    question = "统计2026年广东各分行贷款余额"
    context = builder.build_context(question)

    print("=" * 60)
    print("用户问题：", context["user_question"])
    print("=" * 60)
    print(context["context_text"])


from app.agent.context_builder import ContextBuilder


def test_format_context():
    metrics = [
        {
            "metric_code": "LOAN_BALANCE",
            "metric_name": "贷款余额",
            "business_definition": "贷款账户未偿还余额合计",
            "calculation_rule": "SUM(outstanding_amount)",
            "source_tables": ["bank_demo.dwd_loan_account"],
            "dimensions": ["branch_id"],
        }
    ]

    models = [
        {
            "model_name": "dwd_loan_account",
            "schema_name": "bank_demo",
            "table_name": "dwd_loan_account",
            "model_layer": "DWD",
            "business_description": "贷款账户明细事实表",
            "columns_json": [],
            "tags": ["loan"],
        }
    ]

    result = ContextBuilder.format_context(metrics, models)

    assert "LOAN_BALANCE" in result
    assert "SUM(outstanding_amount)" in result
    assert "bank_demo.dwd_loan_account" in result

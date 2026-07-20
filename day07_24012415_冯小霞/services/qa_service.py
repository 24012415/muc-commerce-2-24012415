from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"
    # 4-1：补充“流失率”“偏好品类”“生命周期风险”和“订单”四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。

    elif any(word in normalized for word in ["流失率", "流失", "流失人数"]):
        loss_people = int(metrics["流失人数"])
        loss_ratio = metrics["流失率"]
        return f"平台总流失用户{loss_people:,}人，流失率为{loss_ratio:.1%}。"

    elif any(word in normalized for word in ["品类", "偏好", "哪个品类用户最多"]):
        category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
        category_df.columns = category_df.columns.str.strip()
        top_data = category_df.loc[category_df["用户数"].idxmax()]
        top_category = top_data["PreferedOrderCat"]
        top_user_count = int(top_data["用户数"])
        return f"{top_category}是用户数量最多的偏好品类，该品类共有{top_user_count:,}名用户。"


    elif any(word in normalized for word in ["生命周期", "风险", "哪个阶段风险最高"]):
        segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
        segment_df.columns = segment_df.columns.str.strip()
        max_loss_line = segment_df.loc[segment_df["流失率"].idxmax()]
        risk_group = max_loss_line["TenureGroup"]
        risk_rate = max_loss_line["流失率"]
        return f"{risk_group}分组流失风险最高，该分组流失率为{risk_rate:.1%}。"

    elif any(word in normalized for word in ["订单", "平均订单", "订单中位数"]):
        avg_order = metrics["平均订单数"]
        median_order = metrics["订单中位数"]
        return f"平台用户平均订单数为{avg_order:.2f}单，订单数量中位数为{median_order:.2f}单。"

    return (
        "基础问答尚未完成。目前只能回答总用户数；请继续完成TODO 4-1。"
        "请换一种更具体的问法。"
    )

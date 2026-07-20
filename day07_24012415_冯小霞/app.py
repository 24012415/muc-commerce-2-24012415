from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, Response, send_file
from services.data_service import load_dashboard_data
from services.qa_service import answer_question

import io
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"
'''@app.route("/")
def index():
    return 'Hello Flask!'
app.run(debug=True)'''


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})

@app.route("/download")
def download_csv():
    # 读取前端传递的品类参数，默认全部
    category_raw= request.args.get("category", "全部")
    selected_cat = category_raw.strip()
    # 调用数据加载函数，自动完成品类筛选
    dashboard_data = load_dashboard_data(BASE_DIR, category_raw)
    df_list = dashboard_data["category_rows"]
    # 调试打印：先确认后端有没有拿到筛选数据
    print("前端传递原始品类：", repr(category_raw))
    print("当前选中品类：", category_raw)
    print("导出列表长度：", len(df_list))
    print("列表内容：", df_list)

    # 列表为空直接返回提示，避免空csv
    if not df_list:
        return "当前筛选条件下无数据，无法导出"
    # 转DataFrame
    export_df = pd.DataFrame(df_list)

    # 内存生成csv，不落地本地文件
    output = io.StringIO()
    export_df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)

    # 转二进制流
    buffer = io.BytesIO(output.getvalue().encode("utf-8-sig"))

    # 拼接文件名：品类_用户分析表.csv
    file_name = f"{category_raw}_用户品类分析表.csv"

    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=file_name
    )

@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, port=5000)

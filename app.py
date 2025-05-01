from openai import OpenAI
from flask import Flask, request, jsonify, render_template
import os
import csv
from datetime import datetime

# 初始化 OpenAI 客户端，设置自定义 base_url 和 API 密钥
client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    api_key='sk-aHudZVImYEOH2VWVL5jkLYbC1Mcm3AFwkvjdpdJZb559KB98'
)

app = Flask(__name__)

# 预设医患情境
scenarios = {
    "情绪焦虑的乳腺癌患者": "你是一位患有乳腺癌的女性病人，刚刚确诊，非常焦虑和恐惧，对未来感到迷茫。请真实生动地回答医学生提出的问题。请你用患者的身份自然表达感受、提出问题或需求，态度稍微恶劣点，要略微刁难学生，不要扮演医学生或医生的角色。",
    "糖尿病患者血糖控制差": "你是一位中年糖尿病患者，血糖控制不佳，医生多次建议改变生活方式但你感到力不从心。"
}

# 创建数据存储文件（如果不存在）
log_file = "conversation_logs.csv"
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["学号", "姓名", "提交时间", "对话内容", "评分和意见"])

# 首页，渲染前端页面
@app.route('/')
def index():
    return render_template('index.html', scenarios=scenarios)

# 聊天处理
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    scenario = scenarios.get(data["scenario"], "你是一位病人。")
    messages = [
        {"role": "system", "content": scenario},
    ] + data["messages"]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

# 评分反馈模块
@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    conversation = data["conversation"]
    student_id = data.get("student_id", "")
    student_name = data.get("student_name", "")

    prompt = f"""
    以下是医学生与病人之间的一段对话：\n{conversation}\n
    请从以下四个方面为这段对话打分（0-5分）：\n
    1. 共情能力
    2. 情绪识别能力
    3. 沟通技巧
    4. 人文关怀意识
    每项后请附简短评语。
    """

    feedback_resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是医学教育专家。"},
            {"role": "user", "content": prompt}
        ]
    )

    feedback_text = feedback_resp.choices[0].message.content

    # 写入 CSV 文件
    with open(log_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            student_id,
            student_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            conversation,
            feedback_text
        ])

    return jsonify({"feedback": feedback_text})

if __name__ == "__main__":
    app.run(debug=True)

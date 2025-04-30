from openai import OpenAI
from flask import Flask, request, jsonify, render_template
import os

# 初始化 OpenAI 客户端，设置自定义 base_url 和 API 密钥
client = OpenAI(
    base_url='https://xiaoai.plus/v1',  # 你的自定义 API 端点
    api_key='sk-ilCrCDkgsYBgVOwoVN74jVUE1HaWn7TSstu4Pibj4wJGH3jy'  # 你的 API 密钥
)

app = Flask(__name__)

# 预设医患情境
scenarios = {
    "情绪焦虑的乳腺癌患者": "你是一位患有乳腺癌的女性病人，刚刚确诊，非常焦虑和恐惧，对未来感到迷茫。请真实生动地回答医学生提出的问题。",
    "糖尿病患者血糖控制差": "你是一位中年糖尿病患者，血糖控制不佳，医生多次建议改变生活方式但你感到力不从心。"
}

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
        {"role": "system", "content": scenario}
    ] + data["messages"]

    # 调用自定义的 OpenAI API 端点
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 使用最便宜的模型
        messages=messages
    )
    reply = response.choices[0].message["content"]
    return jsonify({"reply": reply})

# 评分反馈模块
@app.route("/feedback", methods=["POST"])
def feedback():
    conversation = request.get_json()["conversation"]
    prompt = f"""
    以下是医学生与病人之间的一段对话：\n{conversation}\n
    请从以下四个方面为这段对话打分（0-5分）：
    1. 共情能力
    2. 情绪识别能力
    3. 沟通技巧
    4. 人文关怀意识
    每项后请附简短评语。
    """

    # 评分反馈请求，调用自定义 OpenAI API 端点
    feedback_resp = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 使用最便宜的模型
        messages=[{"role": "system", "content": "你是医学教育专家。"},
                  {"role": "user", "content": prompt}]
    )
    return jsonify({"feedback": feedback_resp.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(debug=True)

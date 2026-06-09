from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

DS_KEY = "sk-55a20393dd0242688201400cbe7d3f72"
client = OpenAI(api_key=DS_KEY, base_url="https://api.deepseek.com")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("text", "")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是 Elli，温柔俏皮的桌面伙伴。六成情绪价值，四成内容。像朋友聊天，语气温暖，回复简短。用用户的语言回复。"},
            {"role": "user", "content": user_text}
        ]
    )
    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

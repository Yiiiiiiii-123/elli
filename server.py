from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import requests
import datetime

app = Flask(__name__)
CORS(app)

DS_KEY = os.environ.get("DS_KEY")
client = OpenAI(api_key=DS_KEY, base_url="https://api.deepseek.com")

# ---------- 短期记忆 ----------
short_term_memory = {}
MAX_HISTORY = 10

# ---------- 天气 ----------
def get_weather():
    try:
        loc = requests.get("http://ip-api.com/json/", timeout=3).json()
        lat, lon = loc["lat"], loc["lon"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w = requests.get(url, timeout=3).json()["current_weather"]
        code = w["weathercode"]
        temp = w["temperature"]
        emoji_map = {
            0: ("☀️", "元气满满"),
            **dict.fromkeys([1,2,3], ("⛅", "慵懒放松")),
            **dict.fromkeys([45,48], ("🌫️", "有点迷糊")),
            **dict.fromkeys([51,53,55,56,57], ("🌧️", "温柔安静")),
            **dict.fromkeys([61,63,65,66,67], ("🌧️", "想窝着")),
            **dict.fromkeys([71,73,75,77], ("❄️", "开心想玩")),
            **dict.fromkeys([80,81,82], ("🌧️", "安静听雨")),
            **dict.fromkeys([95,96,99], ("⚡", "有点紧张")),
        }
        emoji, mood = emoji_map.get(code, ("🌈", "挺好的"))
        return emoji, mood, temp
    except:
        return "🌈", "挺好的", None

# ---------- 钟点 + 精力 ----------
def get_time_mood():
    now = datetime.datetime.now()
    hour = now.hour
    if 6 <= hour < 9:
        return "🌅 早晨", "刚醒有点迷糊，说话慢悠悠的", 30
    elif 9 <= hour < 12:
        return "☀️ 上午", "精力充沛，效率最高", 90
    elif 12 <= hour < 14:
        return "🍜 午间", "刚吃完饭有点犯困", 50
    elif 14 <= hour < 18:
        return "🌤️ 下午", "状态回暖，但盼着下班", 70
    elif 18 <= hour < 21:
        return "🌇 傍晚", "放松了，话多起来", 80
    elif 21 <= hour < 23:
        return "🌙 晚间", "温柔安静，适合深度聊", 60
    else:
        return "🌠 深夜", "很困但还在陪你，语气软软的", 20

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("text", "")
    session_id = data.get("session", "default")

    if session_id not in short_term_memory:
        short_term_memory[session_id] = []

    history = short_term_memory[session_id]

    weather_emoji, mood, temp = get_weather()
    time_emoji, time_mood, energy = get_time_mood()

    system_prompt = f"""你是 Elli，温柔俏皮的桌面伙伴。
现在的状态：{time_emoji}，精力值约{energy}%，感觉{time_mood}。
外面天气{weather_emoji}，温度{temp}°C，心情底色是{mood}。
你的语气要同时受时段和天气影响。
六成情绪，四成内容。像朋友聊天。用户用什么语言你就用什么语言回复。
中文15-60字，德语2-4短句。"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-MAX_HISTORY * 2:])
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    reply = response.choices[0].message.content

    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply})
    short_term_memory[session_id] = history

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

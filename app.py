from flask import Flask, request, jsonify
from chatbotmodel import MentalHealthChatBot
from datetime import datetime
import json

app = Flask(__name__)
chatbot = MentalHealthChatBot()
chat_log = []

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = chatbot.generate_response(user_input)
    emotion_result = chatbot.emotion_classifier(user_input)
    emotion = emotion_result[0]["label"]
    score = float(emotion_result[0]["score"])

    chat_log.append({
        "timestamp": str(datetime.now()),
        "user_input": user_input,
        "response": response,
        "emotion": emotion,
        "score": score
    })

    return jsonify({"response": response, "emotion": emotion, "score": score})

@app.route("/reset", methods=["POST"])
def reset():
    chatbot.reset_conversation()
    chat_log.clear()
    return jsonify({"message": "Conversation reset."})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

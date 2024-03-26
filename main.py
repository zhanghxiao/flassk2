import logging
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
# 初始化 Flask 应用程序
app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)

# 设置 openai 的 api_key 和 base_url
openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.base_url = os.environ.get('OPENAI_BASE_URL')


def chat_with_gpt(model, messages):
    try:
        completion = openai.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        return response
    except Exception as e:
        # 记录错误信息
        app.logger.error('Error in chat_with_gpt: %s', str(e))
        raise


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['userMessage']
    selected_models = data['selectedModels']  # 使用前端发送的模型列表

    initial_messages = [
        {"role": "system", "content": "You are a helpful assistant."}]
    user_message_dict = {"role": "user", "content": user_message}
    messages = initial_messages + [user_message_dict]

    responses = []
    for model in selected_models:
        response = chat_with_gpt(model, messages)
        responses.append(response)

    return jsonify({'responses': responses})

# 定义一个视图函数，用于显示前端页面


@app.route("/")
def index():
    # 返回 html 文件
    return app.send_static_file("index.html")


if __name__ == '__main__':
    app.run(debug=True)

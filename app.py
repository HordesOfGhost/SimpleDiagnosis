from flask import Flask, request, jsonify, render_template
from utils.get_index import *
from utils.prompt_func import *
from utils.generation import *

from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.core import Settings

import os
os.environ['CURL_CA_BUNDLE'] = ''

from dotenv import load_dotenv
load_dotenv()

token = os.getenv('HUGGINGFACEHUB_API_TOKEN')

Settings.llm = HuggingFaceInferenceAPI(
    model_name="mistralai/Mistral-7B-Instruct-v0.3",
    token=token,
    context_window=3900,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    device_map="auto",
)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_bot():
    data = request.json
    user_input = data.get('query')

    if not user_input:
        return jsonify({'error': 'Query is missing'}), 400

    response, query = final_result(user_input)
    response_block, source_block = format_output(response, query)

    return jsonify({
        'response': response_block,
        'sources': source_block
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

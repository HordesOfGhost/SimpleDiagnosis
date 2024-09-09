from flask import Flask, request, jsonify, render_template
from utils.get_index import *
from utils.prompt_func import *

from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.core import Settings

import os
os.environ['CURL_CA_BUNDLE'] = ''

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

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

print("Setting up the QA bot...🤖")
index = create_index()

def final_result(query):
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response, query

def format_output(answer, query):
    # Main answer response
    response_block = f"{answer.response}\n\n"

    # Source information block
    source_block = ""
    if answer.source_nodes:
        source_block += "You can read more of it at: \n"
        for node in answer.source_nodes:
            # Extracting metadata
            metadata = node.node.metadata
            page = metadata.get('page_label', 'N/A')
            source = metadata.get('file_name', 'N/A')

            # Formatting the source information
            source_block += f"- Page {page} from {source}\n"
        source_block += "\n"
    
    return response_block, source_block


# Flask app setup
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

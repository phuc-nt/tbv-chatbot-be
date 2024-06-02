from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Load environment variables from .env file
load_dotenv()

# Define constants
QDRANT_DOMAIN = "https://5d9b085c-df8b-4f83-81f2-82d006da134a.us-east4-0.gcp.cloud.qdrant.io"
# QDRANT_DOMAIN = "http://localhost"
QDRANT_PORT = 6333
QDRANT_URL = f"{QDRANT_DOMAIN}:{QDRANT_PORT}"
COLLECTION_NAME = 'tbv_facebook_post_400_and_homepage_200'
MODEL_NAME = "text-embedding-3-large"
GPT_MODEL_NAME = "gpt-4o"
SYSTEM_MESSAGE_FILE = 'messages/system_message.txt'

# Get API keys from environments
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Qdrant client
client_qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Initialize OpenAI client
client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Phúc Đẹp Trai"

def get_embedding(text, model=MODEL_NAME):
    text = str(text).replace("\n", " ")  # Loại bỏ xuống dòng
    response = client_openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding, response.usage.total_tokens

def search_similar_sentences(query_embedding, collection_name=COLLECTION_NAME):
    return client_qdrant.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=3  # Lấy 3 kết quả hàng đầu
    )

def format_response(query, results):
    response = f"Truy vấn: {query}\n"
    for i, result in enumerate(results, start=1):
        snippet = result.payload['text']
        post_url = result.payload['post_url']
        posted_on = result.payload['posted_on']
        post_id = result.payload['post_id']
        response += f"\nKết quả {i}: {snippet}\nURL: {post_url}\nĐăng ngày: {posted_on}\nID: {post_id}\n"
    return response

def get_system_message():
    with open(SYSTEM_MESSAGE_FILE, 'r') as file:
        return file.read()

def ask_gpt(query, context, model=GPT_MODEL_NAME):
    system_message = get_system_message()
    completion = client_openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message + context},
            {"role": "user", "content": query}
        ],
        stream=True  # Enable streaming responses
    )
    return completion

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data['messages']

    user_message = messages[-1]['content']
    last_message_embedding, _ = get_embedding(user_message)
    search_result = search_similar_sentences(last_message_embedding)
    formatted_context = format_response(user_message, search_result)

    bot_response = ask_gpt(user_message, formatted_context)
    
    def generate():
        for chunk in bot_response:
            content = chunk.choices[0].delta.content  # This extracts the incremental content from the stream
            if content is not None:
                yield content.encode('utf-8')

    return Response(generate(), mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

app = Flask(__name__)
CORS(app)

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

embedder = SentenceTransformer("all-MiniLM-L6-v2")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("prompt", "")
    models = data.get("models", [])
    print(models)

    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400
    if not models:
        return jsonify({"error": "No models selected"}), 400

    results = {}
    for model in models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ],
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            results[model] = response.json()
        except Exception as e:
            results[model] = {"error": str(e)}
    
    model_responses = {}
    for model, resp in results.items():
        text = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        model_responses[model] = text or "No response"
    print(model_responses)

    texts = list(model_responses.values())
    embeddings = embedder.encode(texts)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=0.25,
        metric="cosine",
        linkage="average"
    )

    labels = clustering.fit_predict(embeddings)

    groups = {}
    for model, label in zip(model_responses.keys(), labels):
        label = int(label)
        groups.setdefault(label, []).append({
            "model": model,
            "answer": model_responses[model]
        })


    print(groups)

    return jsonify({
        "groups": groups,
        "raw": model_responses
    })

if __name__ == "__main__":
    app.run(debug=True)

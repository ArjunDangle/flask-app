from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
import ast

app = Flask(__name__)

# Load metadata and embeddings
product_df = pd.read_csv("product_metadata.csv")
text_embeddings = np.load("final_text_embeddings.npy")

# Load model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Convert embeddings to tensor
text_embeddings_tensor = torch.tensor(text_embeddings, dtype=torch.float32)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Generate embedding for input query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute similarity scores
    scores = util.pytorch_cos_sim(query_embedding, text_embeddings_tensor)[0]

    # Get top 5 matches
    top_results = torch.topk(scores, k=5)

    recommendations = []
    for score, idx in zip(top_results.values, top_results.indices):
        product = product_df.iloc[idx.item()]
        image_name = str(product.get("images", "")).strip()
        
        # Safely parse the image list (it's stored as a stringified list in the CSV)
        image_list_raw = product.get("images", "[]")
        try:
            image_list = ast.literal_eval(image_list_raw)
        except:
            image_list = []

        # Use the first image for display (or return the full list if needed)
        main_image_url = image_list[0] if image_list else ""

        recommendations.append({
            "name": product.get("name", ""),
            "brand": product.get("brand", ""),
            "price": product.get("price", ""),
            "currency": product.get("currency", "USD"),
            "description": product.get("description", ""),
            "url": product.get("url", ""),
            "image": f"/static/images/zara/{image_name}"  # served via Flask's static folder
        })

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)

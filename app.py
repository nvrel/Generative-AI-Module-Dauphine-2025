from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rag_system import RAGSystem
import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
from logger import app_logger

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize RAG system for tweet generation
data_path = os.path.join('data', 'twitter_data_clean_sample.csv')
rag_system = RAGSystem(data_path)

# Initialize RAG system for evaluation
eval_data_path = os.path.join('data', 'twitter_data_clean_eval.csv')
eval_data = pd.read_csv(eval_data_path)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index.html")
def index_html():
    return render_template("index.html")

@app.route("/evaluate")
def evaluate():
    return render_template("evaluate.html")

@app.route("/api/run_evaluation", methods=["POST"])
def run_evaluation():
    app_logger.log_backend_call("/api/run_evaluation", "POST")
    total_queries = len(eval_data)
    similarity_scores = []
    evaluation_results = []
    
    for idx, row in eval_data.iterrows():
        query = row['customer_tweet']
        actual_response = row['company_tweet']
        company = row['company']
        
        # Generate a response using RAG + GPT-4o-mini
        result = rag_system.generate_tweet(query, company)
        
        if result:
            similarity_scores.append(result['similarity_score'])
            evaluation_results.append({
                'query': query,
                'actual_response': actual_response,
                'generated_response': result['tweet'],
                'reference_tweet': result['original_tweet'],
                'similarity_score': float(result['similarity_score'])
            })
    
    # Calculate metrics
    avg_similarity = float(np.mean(similarity_scores)) * 100 if similarity_scores else 0
    
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_queries': total_queries,
        'average_similarity': avg_similarity,
        'evaluation_results': evaluation_results[:10]  # Send only first 10 detailed results
    }
    
    # Save results to file
    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    return jsonify(results)

@app.route("/api/generate_tweet", methods=["POST"])
def generate_tweet():
    data = request.json
    prompt = data.get("prompt", "")
    company = data.get("company", "")
    
    app_logger.log_backend_call("/api/generate_tweet", "POST", {"prompt": prompt, "company": company})
    
    # Generate a tweet using RAG system and GPT-4o-mini
    response = rag_system.generate_tweet(prompt, company)
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True) 
# import necessary libraries
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import Flask, request, jsonify, render_template
from recommender.logic import hybrid_recommendation

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

print("Flask app started...")

@app.route("/recommend", methods=["GET"])
def recommend():
    try:
        customer_id = int(request.args.get("customer_id"))
        top_n = int(request.args.get("top_n", 10))
        print(f"[DEBUG] Fetching recommendations for customer {customer_id}")

        recommendations = hybrid_recommendation(customer_id, top_n=top_n)
        
        if recommendations.empty:
            return jsonify({"message": "No recommendations found.", "recommendations": []})

        result = recommendations[['product_id', 'brand', 'category','price']].to_dict(orient='records')
        return jsonify({"customer_id": customer_id, "recommendations": result})

    except Exception as e:
        return jsonify({"error": str(e), "recommendations": []}), 400

if __name__ == "__main__":
    app.run(debug=True)

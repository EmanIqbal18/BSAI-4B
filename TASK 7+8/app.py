from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    ingredient = request.json["ingredient"]
    
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url).json()
    
    return jsonify(response)

@app.route("/recipe/<meal_id>")
def recipe_detail(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url).json()
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
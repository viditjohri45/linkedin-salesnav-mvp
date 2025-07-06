from flask import Flask, render_template, request
from scraper import run_sales_nav_search

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    criteria = {
        "title": request.form["title"],
        "location": request.form["location"],
        "company_size": request.form["company_size"],
        "industry": request.form["industry"],
    }
    result = run_sales_nav_search(criteria)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

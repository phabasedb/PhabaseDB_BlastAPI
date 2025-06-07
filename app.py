from flask import Flask, request
from blast import run_blast

app = Flask(__name__)

@app.route("/blastn", methods=["POST"])
def blastn():
    data = request.get_json() or {}
    return run_blast("blastn", data.get("sequence", ""), data.get("db", []), data.get("params", ""))

@app.route("/blastp", methods=["POST"])
def blastp():
    data = request.get_json() or {}
    return run_blast("blastp", data.get("sequence", ""), data.get("db", []), data.get("params", ""))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001)
from flask import Flask, request, Response
import subprocess
import tempfile
import os

app = Flask(__name__)

def run_blast(blast_type: str, sequence: str, dbs: list, params: str):
    if not sequence:
        return "Required parameter 'sequence' was not provided.", 400
    if not dbs:
        return "Required parameter 'db' was not provided. No databases were selected.", 400

    with tempfile.TemporaryDirectory() as tmpdir:

        query_path = os.path.join(tmpdir, "query.fa")
        out_path   = os.path.join(tmpdir, "result.html")
        
        with open(query_path, "w") as f:
            f.write(sequence)

        if dbs:
            db_string = " ".join(f"/blast/blastdb/{d}" for d in dbs)
            db_args = ["-db", db_string]
        else:
            db_args = []

        cmd = [
            blast_type,
            "-html",
            "-query", query_path,
            *db_args,
        ]

        if blast_type.lower() == "blastn":
            cmd += [
                "-reward",   "2",
                "-penalty",  "-3",
                "-gapopen",   "5",
                "-gapextend", "2",
            ]

        if params:
            cmd += params.split()

        cmd += ["-out", out_path]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            return f"{blast_type} failed: {e}", 500

        with open(out_path, "r") as hf:
            return Response(hf.read(), mimetype="text/html")

@app.route("/blastn", methods=["POST"])
def blastn():
    data = request.get_json() or {}
    return run_blast(
        "blastn",
        data.get("sequence", ""),
        data.get("db", []),
        data.get("params", "")
    )

@app.route("/blastp", methods=["POST"])
def blastp():
    data = request.get_json() or {}
    return run_blast(
        "blastp",
        data.get("sequence", ""),
        data.get("db", []),
        data.get("params", "")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001)
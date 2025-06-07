import subprocess
import tempfile
import os
from flask import jsonify, Response
from constants import VALID_PARAMS
from utils import normalize_fasta

def run_blast(blast_type: str, sequence: str, dbs: list, params: str):
    if not sequence.strip():
        return jsonify({"status":"error", "message": "It looks like the sequence was not provided. Please check and try again."}), 400
    
    if not isinstance(sequence, str):
        return jsonify({"status": "error", "message": "Sequence must be a string. Please check the input."}), 400
    
    if len(sequence) > 1_000_000:
        return jsonify({"status": "error", "message": "Sequence is too large. Maximum allowed size is 1,000,000 characters."}), 400

    try:
        sequence = normalize_fasta(sequence)
    except Exception as e:
        return jsonify({"status": "error", "message": "Error normalizating the sequence. Please check the input and try again."}), 500

    if not dbs:
        return jsonify({"status":"error", "message":"Missing database input. One or more databases must be included to run the analysis."}), 400
    
    missing_dbs = []
    for db in dbs:
        ruta = f"/blast/blastdb/{db}"
        if not (os.path.exists(ruta + ".nin") or os.path.exists(ruta + ".pin")):
            missing_dbs.append(db)
    
    if missing_dbs:
        if len(missing_dbs) == 1:
            message = f"Database '{missing_dbs[0]}' not found. Please verify the database name and try again."
        else:
            message = f"The following databases were not found: {', '.join(missing_dbs)}. Please verify the database names and try again."
        return jsonify({"status": "error", "message": message}), 400

    if params:
        for token in params.split():
            if token.startswith("-") and token not in VALID_PARAMS:
                return jsonify({"status":"error", "message": f"Unrecognized BLAST parameter: '{token}'."}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        query_path = os.path.join(tmpdir, "query.fa")
        try:
            with open(query_path, "w") as f:
                f.write(sequence)
        except OSError:
            return jsonify({"status":"error", "message": "Unable to process the sequence temporarily. Please try again."}), 500

        db_string = " ".join(f"/blast/blastdb/{db}" for db in dbs)
        #cmd = [blast_type, "-outfmt", "5", "-query", query_path, "-db", db_string]
        cmd = [blast_type, "-html", "-query", query_path, "-db", db_string]
        if blast_type.lower() == "blastn":
            cmd.extend(["-reward", "2", "-penalty", "-3", "-gapopen", "5", "-gapextend", "2"])
        if params:
            cmd.extend(params.split())

        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
            )
        except FileNotFoundError:
            return jsonify({"status":"error", "message": "The BLAST engine is currently unavailable. Please try again later."}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"status":"error", "message": "The analysis took too long. Please try again."}), 500
        except OSError:
            return jsonify({"status":"error", "message": "There was a problem running BLAST. Please try again."}), 500

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            return jsonify({"status":"error", "message": f"BLAST failure: {error_msg}"}), 500

        html_output = result.stdout
        #return Response(html_output, status=200, mimetype="text/xml")
        return Response(html_output, status=200, mimetype="text/html")
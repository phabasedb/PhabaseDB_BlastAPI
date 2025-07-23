# BLAST API

A lightweight Flask‐based web service that exposes BLAST functionality (nucleotide and protein) over HTTP. Simply POST your sequence and database names, and receive formatted BLAST results.

---

## Overview

This project wraps NCBI’s BLAST+ command‑line tools (`blastn` and `blastp`) behind two HTTP endpoints. It normalizes incoming FASTA, validates inputs, locates the requested BLAST databases on disk, runs the search, and returns the HTML output directly in the response (default).

---

## Prerequisites

1. **Python 3.8+**
2. **Flask**
3. **Gunicorn**
4. **NCBI BLAST+** installed and available in your `PATH` (`blastn`, `blastp`, etc.)

## Project Structure & Data Organization

```bash
project-root/
├── app.py # Defines /blastn and /blastp endpoints
├── blast.py # Core BLAST logic: validation, DB lookup, subprocess invocation
├── constants.py # Valid BLAST parameters and other constants
├── utils.py # FASTA normalization and helper functions
└── README.md # Project documentation
```

## Features

- **Two endpoints**:
  - `POST /blastn` for nucleotide BLAST
  - `POST /blastp` for protein BLAST
- **Input validation**:
  - Ensures sequence is provided, under size limit, and in proper FASTA format
  - Verifies that named databases exist on disk (`.nin` or `.pin` files)
  - Rejects unrecognized BLAST parameters
- **Automatic FASTA normalization**:
  - Inserts or cleans headers so every query has a unique identifier (`Query_N`)
- **Timeout and error handling**:
  - Fails gracefully if the BLAST binary is missing, times out, or returns an error
- **Response output**
  - By default it returns HTML, but you can set the output to XML, JSON, etc.

> **Tip**: If your DB directory is in a different location, edit the path in `constants.py` (the `BASE_DIR` variable).

```bash
BASE_DIR = '/blast/blastdb/'
```

## Configuration Notes

- Database directory

  Edit the ruta variable in `constants.py` or define your own `BASE_DIR` environment variable.

- Timeout and parameters

  - Default timeout is 60 s (`subprocess.run(timeout=60)`).

  - Allowed BLAST flags listed in `constants.VALID_PARAMS`.

- Port

  - By default it is on port 4001, but you can set it to the port of your choice.

    ```bash
    app.run(host="0.0.0.0", port=####)
    ```

## Run the Flask app

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=4001
```

or simply:

```bash
python app.py
```

The service will listen on 0.0.0.0:4001.

## API Endpoints

`POST /blastn`

- Description: Run a nucleotide BLAST search.

  Request JSON body:

```json
{
  "sequence": ">query1\nATGCATGC...",
  "db": ["nt", "my_custom_db"],
  "params": "-evalue 1e-5 -max_target_seqs 5"
}
```

- Responses:

  - 200 OK → HTML BLAST report (Content-Type: text/html)(default output or you can change the output)

  - 4xx/5xx → JSON { status: "error", message: "..." }

`POST /blastp`

- Description: Run a protein BLAST search.

- Request schema: same as /blastn, but runs blastp.

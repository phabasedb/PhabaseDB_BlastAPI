import re

def normalize_fasta(text: str) -> str:
    """
    Normalize a FASTA-formatted string by ensuring each sequence has a valid and unique header.

    This function processes the input text line by line. It assigns unique headers in the format
    'Query_N' for any sequence lines that do not already have a valid header. Existing headers matching
    the pattern 'Query_N' are tracked to avoid duplication.

    Steps:
    1. Split the input text into individual lines.
    2. Scan for existing headers starting with '>' and collect numeric suffixes from any 'Query_N' IDs.
    3. Define an internal helper to generate the next available 'Query_N' ID, skipping reserved or already assigned numbers.
    4. Iterate through each line:
       - If the line is a header ('>' prefix):
           a. If it has content after '>', preserve it; otherwise, assign a new 'Query_N' header.
       - If the line is a sequence (no '>' prefix) and the previous line was not a header, insert a new 'Query_N' header for it.
    5. Join and return the modified lines as a single string.

    Args:
        text (str): The raw FASTA-formatted string to normalize.

    Returns:
        str: A normalized FASTA string with unique, valid sequence headers.
    """
    lines = text.splitlines()
    result = []
    reserved_numbers = set()
    assigned_numbers = set()

    # Identify existing 'Query_N' IDs
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            content = stripped[1:].strip()
            if content:
                possible_id = content.split()[0]
                match = re.match(r"^Query_(\d+)$", possible_id)
                if match:
                    reserved_numbers.add(int(match.group(1)))

    def get_next_query() -> str:
        """Generate the next available Query_N identifier."""
        n = 1
        while n in reserved_numbers or n in assigned_numbers:
            n += 1
        assigned_numbers.add(n)
        return f"Query_{n}"

    prev_was_header = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(">"):
            content = stripped[1:].strip()
            header = content if content else get_next_query()
            result.append(f">{header}")
            prev_was_header = True
        else:
            # If sequence line appears without a preceding header, insert one
            if not prev_was_header:
                result.append(f">{get_next_query()}")
            result.append(stripped)
            prev_was_header = False

    return "\n".join(result)

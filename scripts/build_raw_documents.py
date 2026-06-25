import json

raw_documents = []

with open(
    "data/raw/isro/structured_missions.json",
    "r",
    encoding="utf-8"
) as f:
    isro_docs = json.load(f)

    raw_documents.extend(isro_docs)

with open(
    "data/raw/pdfs/pdf_documents.json",
    "r",
    encoding="utf-8"
) as f:
    
    pdf_docs = json.load(f)

    raw_documents.extend(pdf_docs)

with open(
    "data/raw/raw_documents.json",
    "w",
    encoding="utf-8"
) as f:
    
    json.dump(
        raw_documents,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    "Total Documents:",
    len(raw_documents)
)
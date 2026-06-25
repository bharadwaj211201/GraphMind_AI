import os
import json
import fitz

pdf_folder = "data/pdfs"

pdf_records = []

for file in os.listdir(pdf_folder):
    if not file.endswith(".pdf"):
        continue
    path = os.path.join(pdf_folder, file)

    doc = fitz.open(path)

    text = ""

    for page in doc:
        text += page.get_text()

    pdf_records.append({
        "title": file,
        "content": text,
        "source": "PDF"
    })
with open(
    "data/raw/pdfs/pdf_documents.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        pdf_records,
        f,
        indent=4,
        ensure_ascii=False
    )

print("PDFs Processed:", len(pdf_records))
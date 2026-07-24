"""
==========================================================
PDF Knowledge Extractor V2
==========================================================

Purpose
-------
Extract structured knowledge from ISRO PDFs.

Supported Documents
-------------------
1. Mission Brochures
2. Launch Vehicle Brochures
3. Annual Reports
4. Technical Reports

Pipeline
--------
PDF

↓

Metadata

↓

Page Extraction

↓

Cleaning

↓

Document Classification

↓

Structured Output
"""

import re
import fitz
from pathlib import Path
from collections import defaultdict

# ==========================================================
# Configuration
# ==========================================================

MIN_LINE_LENGTH = 3

REMOVE_PAGE_NUMBERS = True

REMOVE_EMPTY_LINES = True

MERGE_BROKEN_LINES = True

PRINT_STATISTICS = True


# ==========================================================
# Statistics
# ==========================================================

class PDFStatistics:

    def __init__(self):

        self.documents = 0
        self.pages = 0
        self.characters = 0

    def print_summary(self):

        if not PRINT_STATISTICS:
            return

        print("\n" + "=" * 70)
        print("PDF EXTRACTION STATISTICS")
        print("=" * 70)

        print(f"Documents Processed : {self.documents}")
        print(f"Pages Processed     : {self.pages}")
        print(f"Characters Extracted: {self.characters}")

        print("=" * 70)


pdf_stats = PDFStatistics()


# ==========================================================
# PDF Loader
# ==========================================================

def load_pdf(pdf_path):
    """
    Open PDF safely.
    """

    return fitz.open(pdf_path)


# ==========================================================
# Metadata Extraction
# ==========================================================

def extract_metadata(doc, pdf_path):

    metadata = doc.metadata

    return {

        "file_name": Path(pdf_path).stem,

        "title":
            metadata.get("title")
            or Path(pdf_path).stem,

        "author":
            metadata.get("author", ""),

        "subject":
            metadata.get("subject", ""),

        "creator":
            metadata.get("creator", ""),

        "producer":
            metadata.get("producer", ""),

        "page_count":
            len(doc)

    }


# ==========================================================
# Page Extraction
# ==========================================================

def extract_pages(doc):

    pages = []

    for page_number, page in enumerate(doc, start=1):

        pdf_stats.pages += 1

        text = page.get_text("text")

        pages.append({

            "page": page_number,

            "text": text

        })

    return pages


# ==========================================================
# Text Cleaning
# ==========================================================

def clean_text(text):

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if REMOVE_EMPTY_LINES and not line:
            continue

        if len(line) < MIN_LINE_LENGTH:
            continue

        if REMOVE_PAGE_NUMBERS:

            if re.fullmatch(r"\d+", line):
                continue

        cleaned.append(line)

    if MERGE_BROKEN_LINES:

        text = " ".join(cleaned)

    else:

        text = "\n".join(cleaned)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# Document Classification
# ==========================================================

MISSION_KEYWORDS = [

    "mission",

    "payload",

    "spacecraft",

    "launch profile",

    "scientific objectives"
]

VEHICLE_KEYWORDS = [

    "vehicle characteristics",

    "lift off mass",

    "stage",

    "propellant",

    "payload fairing"
]

ANNUAL_REPORT_KEYWORDS = [

    "annual report",

    "major activities",

    "budget",

    "organisation chart"
]


def classify_document(text):

    content = text.lower()

    mission_score = sum(
        keyword in content
        for keyword in MISSION_KEYWORDS
    )

    vehicle_score = sum(
        keyword in content
        for keyword in VEHICLE_KEYWORDS
    )

    report_score = sum(
        keyword in content
        for keyword in ANNUAL_REPORT_KEYWORDS
    )

    scores = {

        "MISSION_BROCHURE": mission_score,

        "LAUNCH_VEHICLE": vehicle_score,

        "ANNUAL_REPORT": report_score

    }

    return max(scores, key=scores.get)


# ==========================================================
# Extract Document
# ==========================================================

def extract_pdf(pdf_path):

    pdf_stats.documents += 1

    doc = load_pdf(pdf_path)

    metadata = extract_metadata(doc, pdf_path)

    pages = extract_pages(doc)

    raw_text = "\n".join(

        page["text"]

        for page in pages

    )

    cleaned_text = clean_text(raw_text)

    pdf_stats.characters += len(cleaned_text)

    metadata["document_type"] = classify_document(

        cleaned_text

    )

    return {

        "metadata": metadata,

        "pages": pages,

        "raw_text": raw_text,

        "clean_text": cleaned_text

    }


# ==========================================================
# Batch Extraction
# ==========================================================

def extract_pdf_folder(folder):

    documents = []

    folder = Path(folder)

    for pdf_file in sorted(folder.glob("*.pdf")):

        print(f"Processing {pdf_file.name}")

        documents.append(

            extract_pdf(pdf_file)

        )

    pdf_stats.print_summary()

    return documents

# ==========================================================
# Section Detection
# ==========================================================

SECTION_PATTERNS = [

    "Mission Objectives",

    "Mission Objective",

    "Mission Profile",

    "Mission Specifications",

    "Launch Vehicle",

    "Vehicle Characteristics",

    "Payload",

    "Payloads",

    "Scientific Objectives",

    "Mission Timeline",

    "Mission Sequence",

    "Mission Events",

    "Spacecraft",

    "Orbit",

    "Trajectory",

    "Configuration",

    "Applications",

    "Results",

    "Conclusion",

    "Introduction"
]


def detect_sections(clean_text):
    """
    Detect document sections.

    Returns
    -------
    [
        {
            "title": "...",
            "content":"..."
        }
    ]
    """

    lines = clean_text.split()

    sections = []

    current_title = "DOCUMENT"

    current_content = []

    for line in clean_text.split("\n"):

        line = line.strip()

        if not line:

            continue

        matched = False

        for pattern in SECTION_PATTERNS:

            if pattern.lower() == line.lower():

                sections.append({

                    "title": current_title,

                    "content": "\n".join(current_content).strip()

                })

                current_title = pattern

                current_content = []

                matched = True

                break

        if matched:

            continue

        current_content.append(line)

    sections.append({

        "title": current_title,

        "content": "\n".join(current_content).strip()

    })

    return sections


# ==========================================================
# Figure Detection
# ==========================================================

FIGURE_PATTERN = re.compile(

    r"(Figure\s*\d+.*)",

    re.IGNORECASE

)


def extract_figures(text):
    """
    Extract figure captions.
    """

    figures = []

    for line in text.splitlines():

        line = line.strip()

        match = FIGURE_PATTERN.search(line)

        if match:

            figures.append({

                "caption": match.group(1)

            })

    return figures


# ==========================================================
# Table Detection
# ==========================================================

TABLE_KEYWORDS = [

    "Table",

    "Characteristics",

    "Specifications",

    "Instrument",

    "Purpose",

    "Mass",

    "Height",

    "Propellant",

    "Payload"

]


def detect_tables(text):
    """
    Detect possible tables.

    NOTE:
    Actual parsing will be added in Part 3.
    """

    tables = []

    lines = text.splitlines()

    current_table = []

    inside_table = False

    for line in lines:

        line = line.strip()

        if any(

            keyword.lower() in line.lower()

            for keyword in TABLE_KEYWORDS

        ):

            inside_table = True

            current_table.append(line)

            continue

        if inside_table:

            if not line:

                if current_table:

                    tables.append(current_table)

                current_table = []

                inside_table = False

            else:

                current_table.append(line)

    if current_table:

        tables.append(current_table)

    return tables


# ==========================================================
# Timeline Detection
# ==========================================================

TIMELINE_PATTERN = re.compile(

    r"(T\+?\s*\d+|Time\s*\(s\)|\d+\.\d+\s*s)",

    re.IGNORECASE

)


def extract_timeline(text):
    """
    Extract launch timeline.

    Example

    T+0

    PS1 Ignition
    """

    timeline = []

    lines = text.splitlines()

    for i in range(len(lines)):

        line = lines[i].strip()

        if TIMELINE_PATTERN.search(line):

            event = ""

            if i + 1 < len(lines):

                event = lines[i + 1].strip()

            timeline.append({

                "time": line,

                "event": event

            })

    return timeline


# ==========================================================
# Specification Detection
# ==========================================================

SPECIFICATION_KEYWORDS = [

    "Height",

    "Lift off Mass",

    "Launch Pad",

    "Diameter",

    "Mass",

    "Propellant",

    "Orbit",

    "Inclination",

    "Apogee",

    "Perigee",

    "Velocity"
]


def extract_specifications(text):
    """
    Extract key-value specifications.
    """

    specifications = {}

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        for keyword in SPECIFICATION_KEYWORDS:

            if keyword.lower() in line.lower():

                specifications[keyword] = line

    return specifications


# ==========================================================
# Build Knowledge Document
# ==========================================================

def build_pdf_document(document):
    """
    Enrich extracted PDF with
    sections,
    figures,
    tables,
    timeline,
    specifications.
    """

    text = document["clean_text"]

    document["sections"] = detect_sections(text)

    document["tables"] = detect_tables(text)

    document["figures"] = extract_figures(text)

    document["timeline"] = extract_timeline(text)

    document["specifications"] = extract_specifications(text)

    return document

# ==========================================================
# Layout Extraction
# ==========================================================

def extract_layout(doc):
    """
    Extract complete page layout using PyMuPDF.

    Returns
    -------
    [
        {
            page,
            blocks
        }
    ]
    """

    pages = []

    for page_number, page in enumerate(doc, start=1):

        page_dict = page.get_text("dict")

        page_blocks = []

        for block in page_dict["blocks"]:

            if block["type"] != 0:

                continue

            block_data = {

                "bbox": block["bbox"],

                "lines":[]
            }

            for line in block["lines"]:

                line_text = ""

                spans = []

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:

                        continue

                    spans.append({

                        "text":text,

                        "font":span["font"],

                        "size":span["size"],

                        "flags":span["flags"],

                        "bbox":span["bbox"]

                    })

                    line_text += text + " "

                if line_text.strip():

                    block_data["lines"].append({

                        "text":line_text.strip(),

                        "spans":spans
                    })

            if block_data["lines"]:

                page_blocks.append(block_data)

        pages.append({

            "page":page_number,

            "blocks":page_blocks

        })

    return pages


# ==========================================================
# Heading Detection
# ==========================================================

HEADING_SIZE = 14


def detect_headings(layout):

    headings = []

    for page in layout:

        for block in page["blocks"]:

            for line in block["lines"]:

                if not line["spans"]:

                    continue

                largest = max(

                    span["size"]

                    for span in line["spans"]

                )

                if largest >= HEADING_SIZE:

                    headings.append({

                        "page":page["page"],

                        "heading":line["text"]

                    })

    return headings


# ==========================================================
# Key Value Extraction
# ==========================================================

KEYWORDS = [

    "Height",

    "Mass",

    "Launch Pad",

    "Diameter",

    "Propellant",

    "Orbit",

    "Apogee",

    "Perigee",

    "Inclination",

    "Velocity"

]


def extract_key_values(layout):

    values = {}

    for page in layout:

        for block in page["blocks"]:

            lines = block["lines"]

            for i in range(len(lines)-1):

                key = lines[i]["text"]

                value = lines[i+1]["text"]

                for keyword in KEYWORDS:

                    if keyword.lower() in key.lower():

                        values[keyword] = value

    return values


# ==========================================================
# Payload Detection
# ==========================================================

PAYLOAD_NAMES = [

    "VELC",

    "SUIT",

    "ASPEX",

    "SoLEXS",

    "HEL1OS",

    "PAPA",

    "MAG",

    "SWIS",

    "STEPS"
]


def extract_payloads(layout):

    payloads = []

    for page in layout:

        for block in page["blocks"]:

            for line in block["lines"]:

                text = line["text"]

                for payload in PAYLOAD_NAMES:

                    if payload.lower() in text.lower():

                        payloads.append(text)

    return sorted(

        set(payloads)

    )


# ==========================================================
# Build Layout Knowledge
# ==========================================================

def enrich_layout(document, doc):

    layout = extract_layout(doc)

    document["layout"] = layout

    document["headings"] = detect_headings(layout)

    document["payloads"] = extract_payloads(layout)

    document["key_values"] = extract_key_values(layout)

    return document

# ==========================================================
# Mission Brochure Parser
# ==========================================================

def parse_mission_brochure(document):

    document["knowledge"] = {

        "mission": document["metadata"]["title"],

        "payloads": document.get("payloads", []),

        "timeline": document.get("timeline", []),

        "specifications": document.get("key_values", {}),

        "sections": document.get("sections", [])

    }

    return document


# ==========================================================
# Launch Vehicle Parser
# ==========================================================

def parse_launch_vehicle(document):

    specs = document.get("key_values", {})

    document["knowledge"] = {

        "vehicle": document["metadata"]["title"],

        "height":

            specs.get("Height"),

        "diameter":

            specs.get("Diameter"),

        "propellant":

            specs.get("Propellant"),

        "lift_off_mass":

            specs.get("Mass"),

        "timeline":

            document.get("timeline", [])

    }

    return document


# ==========================================================
# Annual Report Parser
# ==========================================================

MISSION_NAMES = [

    "Chandrayaan",

    "Aditya",

    "Gaganyaan",

    "AstroSat",

    "Mangalyaan",

    "SSLV",

    "PSLV",

    "LVM3",

    "NISAR",

    "RISAT",

    "EOS"

]


def parse_annual_report(document):

    missions = []

    text = document["clean_text"]

    for mission in MISSION_NAMES:

        if mission.lower() in text.lower():

            missions.append(mission)

    document["knowledge"] = {

        "missions":

            sorted(set(missions)),

        "headings":

            document.get("headings", []),

        "sections":

            document.get("sections", [])

    }

    return document


# ==========================================================
# Generic Parser
# ==========================================================

def parse_document(document):

    doc_type = document["metadata"]["document_type"]

    if doc_type == "MISSION_BROCHURE":

        return parse_mission_brochure(document)

    elif doc_type == "LAUNCH_VEHICLE":

        return parse_launch_vehicle(document)

    elif doc_type == "ANNUAL_REPORT":

        return parse_annual_report(document)

    return document


# ==========================================================
# Batch Parser
# ==========================================================

def build_pdf_knowledge(documents):

    output = []

    for document in documents:

        output.append(

            parse_document(document)

        )

    return output

# ==========================================================
# Table Row Builder
# ==========================================================

def build_table_rows(layout):
    """
    Build table rows from page layout.

    Rows are created by grouping text
    appearing on nearly the same Y coordinate.
    """

    tables = []

    for page in layout:

        rows = defaultdict(list)

        for block in page["blocks"]:

            for line in block["lines"]:

                if not line["spans"]:
                    continue

                y = round(
                    line["spans"][0]["bbox"][1],
                    1
                )

                rows[y].append(line)

        page_rows = []

        for y in sorted(rows):

            columns = []

            for line in sorted(
                rows[y],
                key=lambda x: x["spans"][0]["bbox"][0]
            ):

                columns.append(
                    line["text"]
                )

            if len(columns) >= 2:

                page_rows.append(columns)

        if page_rows:

            tables.append({

                "page": page["page"],

                "rows": page_rows

            })

    return tables


# ==========================================================
# Key Value Table Parser
# ==========================================================

def parse_key_value_tables(tables):
    """
    Parse

    Height      44.4 m

    into

    Height -> 44.4 m
    """

    specifications = {}

    for table in tables:

        for row in table["rows"]:

            if len(row) != 2:
                continue

            key = row[0].strip()

            value = row[1].strip()

            specifications[key] = value

    return specifications


# ==========================================================
# Instrument Table Parser
# ==========================================================

INSTRUMENT_NAMES = [

    "VELC",

    "SUIT",

    "SoLEXS",

    "HEL1OS",

    "PAPA",

    "MAG",

    "ASPEX",

    "SWIS",

    "STEPS"

]


def extract_instrument_table(tables):
    """
    Extract payload instruments.
    """

    instruments = []

    for table in tables:

        for row in table["rows"]:

            row_text = " ".join(row)

            for instrument in INSTRUMENT_NAMES:

                if instrument.lower() in row_text.lower():

                    instruments.append({

                        "instrument": instrument,

                        "description": row_text

                    })

    return instruments


# ==========================================================
# Timeline Table Parser
# ==========================================================

def extract_timeline_table(tables):
    """
    Extract launch events.

    Example

    T+0

    PS1 Ignition
    """

    timeline = []

    for table in tables:

        for row in table["rows"]:

            if len(row) < 2:
                continue

            first = row[0]

            if re.search(

                r"T\+|Time",

                first,

                re.IGNORECASE

            ):

                timeline.append({

                    "time": row[0],

                    "event": row[1]

                })

    return timeline


# ==========================================================
# Table Knowledge Builder
# ==========================================================

def build_table_knowledge(document):

    layout = document["layout"]

    tables = build_table_rows(layout)

    document["layout_tables"] = tables

    document["table_specifications"] = (

        parse_key_value_tables(

            tables

        )

    )

    document["instrument_table"] = (

        extract_instrument_table(

            tables

        )

    )

    document["timeline_table"] = (

        extract_timeline_table(

            tables

        )

    )

    return document

# ==========================================================
# Header / Footer Detection
# ==========================================================

HEADER_FOOTER_THRESHOLD = 0.10  # Top/bottom 10% of page


def remove_headers_footers(layout):
    """
    Remove repeated headers and footers based on
    their vertical position.
    """

    cleaned_layout = []

    for page in layout:

        blocks = []

        for block in page["blocks"]:

            if not block["lines"]:
                continue

            y0 = block["bbox"][1]
            y1 = block["bbox"][3]

            page_height = 842.0  # Approximate A4 page height in points

            if y1 < page_height * HEADER_FOOTER_THRESHOLD:
                continue

            if y0 > page_height * (1 - HEADER_FOOTER_THRESHOLD):
                continue

            blocks.append(block)

        cleaned_layout.append({
            "page": page["page"],
            "blocks": blocks
        })

    return cleaned_layout


# ==========================================================
# Merge Multi-page Sections
# ==========================================================

def merge_sections(documents):
    """
    Merge sections with identical titles.
    """

    merged = {}

    for section in documents.get("sections", []):

        title = section["title"].strip()

        if title not in merged:
            merged[title] = []

        merged[title].append(section["content"])

    output = []

    for title, contents in merged.items():

        output.append({

            "title": title,

            "content": "\n".join(contents)

        })

    return output


# ==========================================================
# Merge Multi-page Tables
# ==========================================================

def merge_tables(document):
    """
    Merge tables split across pages.
    """

    merged = []

    current = []

    for table in document.get("layout_tables", []):

        rows = table["rows"]

        if not current:

            current.extend(rows)

            continue

        previous = current[-1]

        first = rows[0]

        if len(previous) == len(first):

            current.extend(rows)

        else:

            merged.append(current)

            current = rows.copy()

    if current:

        merged.append(current)

    return merged


# ==========================================================
# Duplicate Removal
# ==========================================================

def remove_duplicates(document):

    if "payloads" in document:

        document["payloads"] = sorted(

            list(set(document["payloads"]))

        )

    if "headings" in document:

        seen = set()

        unique = []

        for heading in document["headings"]:

            text = heading["heading"]

            if text not in seen:

                seen.add(text)

                unique.append(heading)

        document["headings"] = unique

    return document


# ==========================================================
# Final Knowledge Builder
# ==========================================================

def finalize_document(document, doc):

    layout = remove_headers_footers(

        document["layout"]

    )

    document["layout"] = layout

    document["merged_sections"] = merge_sections(

        document

    )

    document["merged_tables"] = merge_tables(

        document

    )

    document = remove_duplicates(

        document

    )

    document["knowledge_ready"] = True

    return document
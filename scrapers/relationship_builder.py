"""
==========================================================
Relationship Builder V2
==========================================================

Purpose
-------
Convert resolved entities into Knowledge Graph triples.

Responsibilities
----------------
1. Sentence-aware relationship extraction
2. Confidence scoring
3. Relationship validation
4. Duplicate fusion
5. Provenance tracking
6. Statistics generation

Output
------
{
    subject,
    predicate,
    object,
    confidence,
    document,
    sentence,
    source,
    method
}
"""

import re
from collections import defaultdict
from dataclasses import dataclass, asdict

# ==========================================================
# Configuration
# ==========================================================

ENABLE_SENTENCE_MATCHING = True

ENABLE_DOCUMENT_LEVEL_RELATIONS = True

ENABLE_DUPLICATE_FUSION = True

PRINT_STATISTICS = True

DEFAULT_CONFIDENCE = 0.60

SENTENCE_CONFIDENCE = 0.95

DOCUMENT_CONFIDENCE = 0.75

RULE_CONFIDENCE = 1.00

# ==========================================================
# Confidence Weights
# ==========================================================

PATTERN_BONUS = 0.20

SAME_SENTENCE_BONUS = 0.15

RULE_MATCH_BONUS = 0.10

ENTITY_DISTANCE_PENALTY = 0.03

LONG_ENTITY_BONUS = 0.03

HIGH_PRIORITY_RELATION_BONUS = 0.05

MAX_CONFIDENCE = 1.00

# ==========================================================
# Relationship Priority
# ==========================================================

RELATIONSHIP_PRIORITY = {

    "DEVELOPED_BY": 100,

    "LAUNCHED_BY": 95,

    "LAUNCHED_FROM": 94,

    "HAS_SPACECRAFT": 90,

    "HAS_SATELLITE": 89,

    "HAS_PAYLOAD": 88,

    "HAS_INSTRUMENT": 87,

    "CARRIES": 86,

    "CONTAINS": 85,

    "PART_OF_PROGRAM": 84,

    "TARGETS": 83,

    "USES_TECHNOLOGY": 82,

    "USES_FACILITY": 81,

    "OPERATES": 80,

    "VARIANT_OF": 79,

    "COLLABORATES_WITH": 78,

    "ASSOCIATED_WITH": 70
}

# ==========================================================
# Relationship Ontology
# ==========================================================

RELATIONSHIP_RULES = {

    "MISSION": {

        "ORGANIZATION": "DEVELOPED_BY",

        "SPACEPORT": "LAUNCHED_FROM",

        "LAUNCH_VEHICLE": "LAUNCHED_BY",

        "ROCKET_VARIANT": "LAUNCHED_BY",

        "SPACECRAFT": "HAS_SPACECRAFT",

        "SATELLITE": "HAS_SATELLITE",

        "PAYLOAD": "HAS_PAYLOAD",

        "INSTRUMENT": "HAS_INSTRUMENT",

        "PROGRAM": "PART_OF_PROGRAM",

        "CELESTIAL_BODY": "TARGETS",

        "TECHNOLOGY": "USES_TECHNOLOGY",

        "FACILITY": "USES_FACILITY",

        "LABORATORY": "USES_LABORATORY",

        "ASTRONAUT": "INVOLVES_ASTRONAUT",

        "SCIENTIST": "MENTIONS_SCIENTIST",

        "MISSION": "FOLLOWS",

        "COUNTRY": "ASSOCIATED_WITH",

        "STATE": "ASSOCIATED_WITH",

        "CITY": "ASSOCIATED_WITH"

    },

    "SPACECRAFT": {

        "PAYLOAD": "CARRIES",

        "INSTRUMENT": "CONTAINS"
    },

    "PAYLOAD": {

        "INSTRUMENT": "USES_INSTRUMENT"
    },

    "ORGANIZATION": {

        "CENTRE": "OPERATES",

        "FACILITY": "OPERATES",

        "LABORATORY": "OPERATES"
    },

    "ROCKET_VARIANT": {

        "LAUNCH_VEHICLE": "VARIANT_OF"
    }

}

# ==========================================================
# Reverse Relationships
# ==========================================================

REVERSE_RELATIONSHIPS = {

    "DEVELOPED_BY": "DEVELOPED",

    "LAUNCHED_BY": "LAUNCHED",

    "LAUNCHED_FROM": "LAUNCH_SITE",

    "HAS_SPACECRAFT": "PART_OF",

    "HAS_SATELLITE": "PART_OF",

    "HAS_PAYLOAD": "ONBOARD",

    "HAS_INSTRUMENT": "PART_OF",

    "CARRIES": "CARRIED_BY",

    "VARIANT_OF": "HAS_VARIANT",

    "OPERATES": "OPERATED_BY"

}

# ==========================================================
# Triple Dataclass
# ==========================================================

@dataclass
class Triple:

    # Nodes
    subject: str
    predicate: str
    object: str

    # Node Types
    subject_type: str = ""
    object_type: str = ""

    # Confidence
    confidence: float = DEFAULT_CONFIDENCE

    # Provenance
    source: str = ""
    document: str = ""
    sentence: str = ""
    method: str = ""

    # Evidence
    evidence: str = ""

    # Relationship Metadata
    rule: str = ""


# ==========================================================
# Statistics
# ==========================================================

class RelationshipStatistics:

    def __init__(self):

        self.documents = 0

        self.sentences = 0

        self.relationships = 0

        self.sentence_relationships = 0

        self.document_relationships = 0

        self.rule_relationships = 0

        self.invalid_relationships = 0

        self.duplicates_removed = 0

        self.fused_relationships = 0

        self.total_confidence = 0

    def print_summary(self):

        if not PRINT_STATISTICS:
            return

        print("\n" + "=" * 70)

        print("RELATIONSHIP BUILDER STATISTICS")

        print("=" * 70)

        print(f"Relationships Created   : {self.relationships}")

        average = 0

        if self.relationships:

            average = round(

                self.total_confidence /

                self.relationships,

                2

            )

        print(

            f"Average Confidence     : {average}"

        )

        print(f"Sentence Relations      : {self.sentence_relationships}")

        print(f"Document Relations      : {self.document_relationships}")

        print(f"Rule Based Relations    : {self.rule_relationships}")

        print(f"Invalid Removed         : {self.invalid_relationships}")

        print(f"Duplicate Removed       : {self.duplicates_removed}")

        print(f"Relationships Fused     : {self.fused_relationships}")

        print("=" * 70)


builder_stats = RelationshipStatistics()

# ==========================================================
# Context Memory
# ==========================================================

class ContextMemory:

    def __init__(self):

        self.last_mission = None

        self.last_spacecraft = None

        self.last_organization = None

        self.last_launch_vehicle = None

        self.last_spaceport = None

        self.last_payload = None

context_memory = ContextMemory()

# ==========================================================
# Sentence Splitter
# ==========================================================

def split_sentences(text):
    """
    Split document into clean sentences.
    """

    if not text:

        return []

    sentences = re.split(

        r"(?<=[.!?])\s+",

        text

    )

    cleaned = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 5:

            continue

        cleaned.append(sentence)

    return cleaned


# ==========================================================
# Entity Grouping
# ==========================================================

def group_entities(entities):
    """
    Group entities by entity type.

    Returns

    {
        "MISSION":[...],

        "SPACECRAFT":[...]
    }
    """

    grouped = defaultdict(list)

    for entity in entities:

        grouped[
            entity["type"]
        ].append(entity)

    return grouped


# ==========================================================
# Entity Search
# ==========================================================

def find_entities_in_sentence(sentence, entities):
    """
    Return entities appearing in a sentence.
    """

    sentence_lower = sentence.lower()

    matched = []

    for entity in entities:

        if entity["name"].lower() in sentence_lower:

            matched.append(entity)

        occupied = []

        for entity in sorted(

            entities,

            key=lambda e: len(e["name"]),

            reverse=True

        ):

            name = entity["name"].lower()

            start = sentence_lower.find(name)

            if start == -1:

                continue

            end = start + len(name)

            overlap = False

            for s, e in occupied:

                if not (

                    end <= s

                    or

                    start >= e

                ):

                    overlap = True

                    break

            if overlap:

                continue

            occupied.append(

                (

                    start,

                    end

                )

            )

            matched.append(entity)

    return matched

# ==========================================================
# Context Updater
# ==========================================================

def update_context(entities):

    global context_memory

    for entity in entities:

        entity_type = entity["type"]

        if entity_type == "MISSION":

            context_memory.last_mission = entity

        elif entity_type == "SPACECRAFT":

            context_memory.last_spacecraft = entity

        elif entity_type == "ORGANIZATION":

            context_memory.last_organization = entity

        elif entity_type == "LAUNCH_VEHICLE":

            context_memory.last_launch_vehicle = entity

        elif entity_type == "SPACEPORT":

            context_memory.last_spaceport = entity

        elif entity_type == "PAYLOAD":

            context_memory.last_payload = entity

# ==========================================================
# Pronoun Resolution
# ==========================================================

MISSION_PRONOUNS = {

    "it",

    "mission",

    "probe"

}

SPACECRAFT_PRONOUNS = {

    "rover",

    "lander",

    "orbiter",

    "spacecraft"

}

def resolve_context(sentence):

    lower = sentence.lower()

    resolved = []

    if any(word in lower for word in MISSION_PRONOUNS):

        if context_memory.last_mission:

            resolved.append(

                context_memory.last_mission

            )

    if any(word in lower for word in SPACECRAFT_PRONOUNS):

        if context_memory.last_spacecraft:

            resolved.append(

                context_memory.last_spacecraft

            )

    return resolved

# ==========================================================
# Triple Creation
# ==========================================================

def create_triple(

    subject,

    predicate,

    object,

    confidence,

    document,

    sentence,

    source,

    method,

    subject_type="",

    object_type="",

    evidence="",

    rule=""

):
    """
    Create Triple object.
    """

    builder_stats.relationships += 1

    builder_stats.total_confidence += confidence

    return Triple(

        subject=subject,

        predicate=predicate,

        object=object,

        subject_type=subject_type,

        object_type=object_type,

        confidence=confidence,

        source=source,

        document=document,

        sentence=sentence,

        method=method,

        evidence=evidence,

        rule=rule

    )


# ==========================================================
# Confidence Helpers
# ==========================================================

def calculate_relationship_confidence(

        subject,

        obj,

        predicate,

        sentence,

        pattern_found=False

):
    """
    Compute confidence for a relationship.
    """

    confidence = DEFAULT_CONFIDENCE

    # ----------------------------
    # Pattern Match
    # ----------------------------

    if pattern_found:

        confidence += PATTERN_BONUS

    # ----------------------------
    # Same Sentence
    # ----------------------------

    confidence += SAME_SENTENCE_BONUS

    # ----------------------------
    # Rule Match
    # ----------------------------

    confidence += RULE_MATCH_BONUS

    # ----------------------------
    # Relationship Priority
    # ----------------------------

    if predicate in RELATIONSHIP_PRIORITY:

        confidence += HIGH_PRIORITY_RELATION_BONUS

    # ----------------------------
    # Long Entity Bonus
    # ----------------------------

    if len(subject["name"].split()) >= 2:

        confidence += LONG_ENTITY_BONUS

    if len(obj["name"].split()) >= 2:

        confidence += LONG_ENTITY_BONUS

    # ----------------------------
    # Entity Distance
    # ----------------------------

    sentence_lower = sentence.lower()

    s = sentence_lower.find(

        subject["name"].lower()

    )

    o = sentence_lower.find(

        obj["name"].lower()

    )

    if s != -1 and o != -1:

        distance = abs(s - o)

        confidence -= (

            distance / 100

        ) * ENTITY_DISTANCE_PENALTY

    confidence = max(

        DEFAULT_CONFIDENCE,

        confidence

    )

    confidence = min(

        MAX_CONFIDENCE,

        confidence

    )

    return round(

        confidence,

        2

    )


def document_confidence():

    return DOCUMENT_CONFIDENCE


def rule_confidence():

    return RULE_CONFIDENCE

# ==========================================================
# Rule Lookup
# ==========================================================

def get_predicate(subject_type, object_type):
    """
    Return the relationship predicate between two entity types.

    Example

    MISSION + LAUNCH_VEHICLE

    →

    LAUNCHED_BY
    """

    if subject_type not in RELATIONSHIP_RULES:

        return None

    return RELATIONSHIP_RULES[subject_type].get(object_type)

# ==========================================================
# Invalid Relationship Rules
# ==========================================================

INVALID_RELATIONSHIPS = {

    ("MISSION", "MISSION"),

    ("PAYLOAD", "PAYLOAD"),

    ("SPACECRAFT", "SPACECRAFT"),

    ("ORGANIZATION", "ORGANIZATION")

}

def valid_relationship(subject_type, object_type):

    if (subject_type, object_type) in INVALID_RELATIONSHIPS:

        return False

    return True

# ==========================================================
# Sentence Relationship Extraction
# ==========================================================

def extract_sentence_relationships(document):
    """
    Extract relationships only between entities that
    occur inside the same sentence.
    """

    triples = []

    text = document.get("content", "")

    source = document.get("source", "Unknown")

    title = document.get("title", "")

    entities = document.get("entities", [])

    sentences = split_sentences(text)

    builder_stats.documents += 1

    builder_stats.sentences += len(sentences)

    # ------------------------------------------------------
    # Process every sentence
    # ------------------------------------------------------

    for sentence in sentences:

        matched = sorted(
            find_entities_in_sentence(

                sentence,

                entities
            ),

            key=lambda entity: len(entity["name"]),

            reverse=True
        )

        matched.extend(
            resolve_context(sentence)
        )

        unique = {}

        for entity in matched:

            key = (

                entity["name"],

                entity["type"]

            )

            unique[key] = entity

        matched = list(

            unique.values()

        )

        update_context(matched)

        relation_hints = detect_relations(sentence)

        if len(matched) < 2:

            continue

        # --------------------------------------------------
        # Compare every pair
        # --------------------------------------------------

        for i in range(len(matched)):

            for j in range(len(matched)):

                if i == j:

                    continue

                subject = matched[i]

                obj = matched[j]

                predicate = get_predicate(

                    subject["type"],

                    obj["type"]

                )

                if predicate is None:

                    continue

                if not valid_relationship(

                    subject["type"],

                    obj["type"]

                ):

                    builder_stats.invalid_relationships += 1

                    continue

                # ------------------------------------------------------
                # Sentence Pattern Verification
                # ------------------------------------------------------

                if relation_hints:

                    if predicate not in relation_hints:
                        continue

                triples.append(

                    create_triple(

                        subject["name"],

                        predicate,

                        obj["name"],

                        confidence=calculate_relationship_confidence(

                            subject,

                            obj,

                            predicate,

                            sentence,

                            pattern_found=predicate in relation_hints
                        ),

                        document=title,

                        sentence=sentence,

                        source=source,

                        method="sentence_match",

                        object_type=obj["type"],

                        evidence=sentence,

                        rule=f"Pattern:{predicate}"

                    )

                )

    return triples


# ==========================================================
# Document-Level Fallback
# ==========================================================

def extract_document_relationships(document):
    """
    Create relationships using entire document
    when sentence extraction misses them.
    """

    if not ENABLE_DOCUMENT_LEVEL_RELATIONS:

        return []

    triples = []

    grouped = group_entities(

        document.get("entities", [])

    )

    source = document.get("source", "Unknown")

    title = document.get("title", "")

    # ------------------------------------------------------
    # Mission Relationships
    # ------------------------------------------------------

    missions = grouped.get(

        "MISSION",

        []

    )

    for mission in missions:

        for object_type, predicate in RELATIONSHIP_RULES[
            "MISSION"
        ].items():

            objects = grouped.get(

                object_type,

                []

            )

            for obj in objects:

                if object_type == "ORGANIZATION":

                    continue

                triples.append(

                    create_triple(

                        mission["name"],

                        predicate,

                        obj["name"],

                        confidence=0.80,

                        document=title,

                        sentence="",

                        source=source,

                        method="document_match",

                        subject_type=mission["type"],

                        object_type=obj["type"],

                        evidence="",

                        rule=predicate

                    )

                )

    return triples


# ==========================================================
# Organization Collaboration
# ==========================================================

COLLABORATION_KEYWORDS = [

    "collaboration",

    "collaborated",

    "joint",

    "jointly",

    "partner",

    "partnership",

    "agreement",

    "cooperation",

    "signed",

    "memorandum",

    "mou"

]

# ==========================================================
# Sentence Pattern Rules
# ==========================================================

RELATION_PATTERNS = {

    "DEVELOPED_BY":[

        "developed by",

        "developed",

        "built by",

        "built",

        "designed",

        "designed by",

        "created",

        "created by"

    ],

    "LAUNCHED_BY":[

        "launched by",

        "launched",

        "lifted off",

        "launch vehicle",

        "aboard"

    ],

    "LAUNCHED_FROM":[

        "launched from",

        "lifted off from",

        "launch complex",

        "space centre",

        "space center"

    ],

    "HAS_PAYLOAD":[

        "payload",

        "payloads",

        "payload carrying",

        "carrying",

        "equipped with"

    ],

    "HAS_SPACECRAFT":[

        "rover",

        "lander",

        "orbiter",

        "spacecraft"

    ],

    "HAS_SATELLITE":[

        "satellite",

        "earth observation",

        "communication satellite"

    ],

    "TARGETS":[

        "moon",

        "mars",

        "sun",

        "venus",

        "asteroid",

        "to study",

        "to observe",

        "destination"

    ],

    "PART_OF_PROGRAM":[

        "programme",

        "program",

        "initiative"

    ]

}

def detect_collaboration(sentence):

    text = sentence.lower()

    for keyword in COLLABORATION_KEYWORDS:

        if keyword in text:

            return True

    return False

# ==========================================================
# Pattern Detection
# ==========================================================

def detect_relations(sentence):
    """
    Detect all relationship patterns
    present in a sentence.
    """

    text = sentence.lower()

    found = []

    for relation, keywords in RELATION_PATTERNS.items():

        for keyword in keywords:

            if keyword in text:

                found.append(relation)

                break

    return found

def extract_collaborations(document):
    """
    Create ORGANIZATION -> COLLABORATES_WITH
    only if collaboration evidence exists.
    """

    triples = []

    entities = document.get("entities", [])

    source = document.get("source", "Unknown")

    title = document.get("title", "")

    sentences = split_sentences(

        document.get("content", "")

    )

    for sentence in sentences:

        if not detect_collaboration(sentence):

            continue

        matched = sorted(

            find_entities_in_sentence(

                sentence,

                entities

            ),

            key=lambda entity: len(entity["name"]),

            reverse=True
        )

        organizations = [

            entity

            for entity in matched

            if entity["type"] == "ORGANIZATION"

        ]

        if len(organizations) < 2:

            continue

        for i in range(len(organizations)):

            for j in range(i + 1, len(organizations)):

                left = organizations[i]["name"]
                right = organizations[j]["name"]

                # Keep a consistent ordering
                if left > right:
                    left, right = right, left

                triples.append(

                    create_triple(

                        subject=left,

                        predicate="COLLABORATES_WITH",

                        object=right,

                        confidence=0.98,

                        document=title,

                        sentence=sentence,

                        source=source,

                        method="collaboration_rule",

                        subject_type="ORGANIZATION",

                        object_type="ORGANIZATION",

                        evidence=sentence,

                        rule="COLLABORATES_WITH"

                    )

                )

    return triples


# ==========================================================
# Complete Extraction
# ==========================================================

def extract_relationships(document):
    """
    Complete relationship extraction engine.
    """

    triples = []

    triples.extend(

        extract_sentence_relationships(document)

    )

    triples.extend(

        extract_document_relationships(document)

    )

    triples.extend(

        extract_collaborations(document)

    )

    return triples

# ==========================================================
# Relationship Key
# ==========================================================

def relationship_key(triple):
    """
    Unique key for identifying duplicate relationships.
    """

    return (

        triple.subject,

        triple.predicate,

        triple.object

    )


# ==========================================================
# Duplicate Relationship Fusion
# ==========================================================

def fuse_relationships(triples):
    """
    Merge duplicate relationships coming from
    different sentences or documents.

    Keeps the highest confidence while combining
    provenance information.
    """

    if not ENABLE_DUPLICATE_FUSION:

        return triples

    fused = {}

    for triple in triples:

        key = relationship_key(triple)

        if key not in fused:

            fused[key] = {

                "subject": triple.subject,

                "predicate": triple.predicate,

                "object": triple.object,

                "confidence": triple.confidence,

                "documents": {triple.document},

                "sources": {triple.source},

                "sentences": {triple.sentence}
                if triple.sentence else set(),

                "methods": {triple.method}

            }

            continue

        builder_stats.fused_relationships += 1

        item = fused[key]

        item["confidence"] = max(

            item["confidence"],

            triple.confidence

        )

        item["documents"].add(

            triple.document

        )

        item["sources"].add(

            triple.source

        )

        if triple.sentence:

            item["sentences"].add(

                triple.sentence

            )

        item["methods"].add(

            triple.method

        )

    results = []

    for item in fused.values():

        results.append({

            "subject": item["subject"],

            "predicate": item["predicate"],

            "object": item["object"],

            "confidence": round(
                item["confidence"],
                2
            ),

            "documents": sorted(
                item["documents"]
            ),

            "sources": sorted(
                item["sources"]
            ),

            "sentences": sorted(
                item["sentences"]
            ),

            "methods": sorted(
                item["methods"]
            )
        })

    return results


# ==========================================================
# Relationship Validation
# ==========================================================

def validate_relationships(relationships):
    """
    Remove invalid relationships.
    """

    validated = []

    seen = set()

    for rel in relationships:

        key = (

            rel["subject"],

            rel["predicate"],

            rel["object"]

        )

        if rel["subject"] == rel["object"]:

            builder_stats.duplicates_removed += 1

            continue

        if key in seen:

            builder_stats.duplicates_removed += 1

            continue

        seen.add(key)

        validated.append(rel)

    return validated


# ==========================================================
# Export Helpers
# ==========================================================

def export_for_neo4j(relationships):
    """
    Neo4j-friendly relationship format.
    """

    exported = []

    for rel in relationships:

        exported.append({

            "start_node": rel["subject"],

            "relationship": rel["predicate"],

            "end_node": rel["object"],

            "confidence": rel["confidence"],

            "sources": rel["sources"],

            "rule": rel["methods"],

            "documents": rel["documents"]

        })

    return exported


def export_for_mongodb(relationships):
    """
    MongoDB-friendly relationship documents.
    """

    exported = []

    for rel in relationships:

        exported.append({

            "_id": (

                f"{rel['subject']}|"

                f"{rel['predicate']}|"

                f"{rel['object']}"

            ),

            **rel

        })

    return exported


# ==========================================================
# Statistics Access
# ==========================================================

def get_statistics():

    return {

        "documents":

            builder_stats.documents,

        "sentences":

            builder_stats.sentences,

        "relationships":

            builder_stats.relationships,

        "duplicates_removed":

            builder_stats.duplicates_removed,

        "fused_relationships":

            builder_stats.fused_relationships

    }


def print_statistics():

    builder_stats.print_summary()


# ==========================================================
# Main Pipeline
# ==========================================================

def build_relationships(document):
    """
    Complete relationship-building pipeline.

    Parameters
    ----------
    document : dict

    Returns
    -------
    List[dict]
    """

    # Step 1
    reset_context()
    triples = extract_relationships(document)

    # Step 2
    fused = fuse_relationships(triples)

    # Step 3
    validated = validate_relationships(fused)

    return validated


# ==========================================================
# Batch Processing
# ==========================================================

def build_relationships_batch(documents):
    """
    Build relationships from multiple documents.
    """

    all_relationships = []

    for document in documents:

        relationships = build_relationships(document)

        all_relationships.extend(
            relationships
        )

    # Fuse across all documents
    all_relationships = fuse_relationships(

        [
            Triple(
                subject=r["subject"],
                predicate=r["predicate"],
                object=r["object"],
                confidence=r["confidence"],
                source=r["sources"][0] if r["sources"] else "",
                document=r["documents"][0] if r["documents"] else "",
                sentence=r["sentences"][0] if r["sentences"] else "",
                method=r["methods"][0] if r["methods"] else ""
            )

            for r in all_relationships
        ]
    )

    return validate_relationships(
        all_relationships
    )


# ==========================================================
# Pretty Printer
# ==========================================================

def print_relationships(relationships):
    """
    Pretty-print relationships.
    """

    print("\n" + "=" * 90)
    print("KNOWLEDGE GRAPH RELATIONSHIPS")
    print("=" * 90)

    for rel in relationships:

        print(

            f"{rel['subject']}\n"

            f"   │\n"

            f"   ├── {rel['predicate']} "

            f"(confidence={rel['confidence']:.2f})\n"

            f"   ▼\n"

            f"{rel['object']}\n"

        )

        print(

            f"Sources   : {', '.join(rel['sources'])}"

        )

        print(

            f"Documents : {', '.join(rel['documents'])}"

        )

        print("-" * 90)


# ==========================================================
# JSON Helpers
# ==========================================================

import json


def save_relationships(path, relationships):
    """
    Save relationships to JSON.
    """

    with open(path, "w", encoding="utf-8") as f:

        json.dump(

            relationships,

            f,

            indent=4,

            ensure_ascii=False

        )


def load_relationships(path):
    """
    Load relationships from JSON.
    """

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)


# ==========================================================
# Reset Statistics
# ==========================================================

def reset_statistics():
    """
    Reset builder statistics.
    """

    global builder_stats

    builder_stats = RelationshipStatistics()

def reset_context():

    global context_memory

    context_memory = ContextMemory()

# ==========================================================
# Test Block
# ==========================================================

if __name__ == "__main__":

    sample_document = {

        "title": "Chandrayaan-3",

        "source": "Wikipedia",

        "content":

        """
        Chandrayaan-3 was launched by LVM3-M4
        from Satish Dhawan Space Centre.

        ISRO developed the Chandrayaan-3 mission.

        ISRO and NASA signed an agreement
        for future lunar exploration.
        """,

        "entities":[

            {
                "name":"Chandrayaan-3",
                "type":"MISSION"
            },

            {
                "name":"LVM3-M4",
                "type":"ROCKET_VARIANT"
            },

            {
                "name":"Satish Dhawan Space Centre",
                "type":"SPACEPORT"
            },

            {
                "name":"ISRO",
                "type":"ORGANIZATION"
            },

            {
                "name":"NASA",
                "type":"ORGANIZATION"
            }

        ]
    }

    relationships = build_relationships(

        sample_document

    )

    print_relationships(

        relationships

    )

    print_statistics()

    print("\nNeo4j Export\n")

    print(

        export_for_neo4j(

            relationships

        )

    )

    print("\nMongoDB Export\n")

    print(

        export_for_mongodb(

            relationships

        )

    )

    print("\nDone.\n")
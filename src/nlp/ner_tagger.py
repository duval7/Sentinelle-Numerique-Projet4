"""
ner_tagger.py — Named Entity Recognition Module
Sentinelle Numérique | Groupe 4 | FAVOUR Noella
SUP'PTIC ITT3-IR | 2025–2026

WHAT THIS FILE DOES:
--------------------
This module takes a piece of text and finds all the important "named entities"
inside it — things like people's names, countries, dates, percentages, and
numbers. These entities are what we use to check if a claim is verifiable.

For example, in the sentence:
    "Emmanuel Macron announced a 5% tax increase on January 10th, 2025"
The NER tagger would find:
    - PERSON  → Emmanuel Macron
    - PERCENT → 5%
    - DATE    → January 10th, 2025

We use spaCy's 'en_core_web_sm' model to do this automatically.
"""

import spacy
from typing import List, Dict


# ── Entity types we care about (the ones relevant to fact-checking) ──────────
RELEVANT_ENTITY_TYPES = {
    "PERSON",    # People's names        e.g. "Elon Musk"
    "ORG",       # Organisations         e.g. "World Health Organization"
    "GPE",       # Geo-political entity  e.g. "France", "Cameroon", "Paris"
    "DATE",      # Dates                 e.g. "January 2024", "last Tuesday"
    "PERCENT",   # Percentages           e.g. "5%", "thirty percent"
    "CARDINAL",  # Numbers               e.g. "1,000 deaths", "three million"
    "MONEY",     # Monetary values       e.g. "$500 billion"
    "LOC",       # Locations             e.g. "Mount Cameroon", "Sahara"
    "EVENT",     # Named events          e.g. "World Cup", "COP28"
    "LAW",       # Laws / bills          e.g. "Article 19", "the GDPR"
}


class NERTagger:
    """
    Named Entity Recognition tagger.

    Usage:
        tagger = NERTagger()
        entities = tagger.tag("Apple reported $90 billion in revenue in 2023.")
        # Returns a list of entity dicts
    """

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Load the spaCy NLP model when the class is created.
        
        Args:
            model: Name of the spaCy model to use.
                   'en_core_web_sm' is small and fast — good for our MVP.
                   You can switch to 'en_core_web_lg' later for more accuracy.
        """
        try:
            self.nlp = spacy.load(model)
            self.model_name = model
        except OSError:
            raise OSError(
                f"spaCy model '{model}' not found.\n"
                f"Please run:  python -m spacy download {model}"
            )

    def tag(self, text: str) -> List[Dict]:
        """
        Find all named entities in the given text.

        Args:
            text: A plain string of text (already cleaned by preprocessor.py).

        Returns:
            A list of entity dictionaries, each containing:
                - 'text'  : the actual word(s) found  (e.g. "Emmanuel Macron")
                - 'label' : the entity type           (e.g. "PERSON")
                - 'start' : character index where it starts in the text
                - 'end'   : character index where it ends

        Example:
            [
                {"text": "Apple", "label": "ORG",      "start": 0,  "end": 5},
                {"text": "$90 billion", "label": "MONEY", "start": 14, "end": 25},
                {"text": "2023", "label": "DATE",      "start": 38, "end": 42},
            ]
        """
        if not text or not text.strip():
            return []

        # Pass the text through spaCy — it tokenizes, parses, and tags it
        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            # Only keep entity types that are useful for fact-checking
            if ent.label_ in RELEVANT_ENTITY_TYPES:
                entities.append({
                    "text":  ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end":   ent.end_char,
                })

        return entities

    def tag_sentences(self, sentences: List[str]) -> List[List[Dict]]:
        """
        Tag a list of sentences (one result list per sentence).

        This is a convenience wrapper used by ClaimExtractor:
        it calls tag() on each sentence and returns a parallel list.

        Args:
            sentences: List of sentence strings.

        Returns:
            List of entity lists (one per sentence).

        Example:
            Input:  ["Apple earned $90B.", "Macron visited Paris."]
            Output: [
                        [{"text":"Apple","label":"ORG",...}, {"text":"$90B","label":"MONEY",...}],
                        [{"text":"Macron","label":"PERSON",...}, {"text":"Paris","label":"GPE",...}]
                    ]
        """
        return [self.tag(sentence) for sentence in sentences]

    def has_verifiable_entities(self, entities: List[Dict]) -> bool:
        """
        Check if a list of entities contains at least ONE verifiable item.

        A sentence is 'verifiable' if it has a PERSON, ORG, GPE, DATE,
        PERCENT, CARDINAL, or MONEY entity — something we can look up.

        This is used by claim_extractor.py to decide which sentences to keep.

        Args:
            entities: Output from tag() or tag_sentences().

        Returns:
            True if there is at least one verifiable entity, False otherwise.
        """
        verifiable_types = {"PERSON", "ORG", "GPE", "DATE", "PERCENT",
                            "CARDINAL", "MONEY", "LOC", "EVENT", "LAW"}
        return any(e["label"] in verifiable_types for e in entities)

    def extract_numerical_value(self, entities: List[Dict]) -> float:
        """
        Pull the first numerical value from the entity list and return it
        as a float. Returns 0.0 if no numerical entity is found.

        This value is stored in the Claim object as 'numericalValue'.

        Why? Claims with specific numbers (e.g., "GDP grew by 3.5%") are
        more precisely verifiable than vague claims ("the economy grew").

        Args:
            entities: Output from tag().

        Returns:
            A float (e.g., 3.5 from "3.5%"), or 0.0 if nothing found.
        """
        numerical_types = {"PERCENT", "CARDINAL", "MONEY"}
        for entity in entities:
            if entity["label"] in numerical_types:
                # Strip non-numeric characters to parse the float
                raw = entity["text"]
                cleaned = "".join(c for c in raw if c.isdigit() or c == ".")
                try:
                    return float(cleaned)
                except ValueError:
                    continue
        return 0.0


# ── Quick manual test — run this file directly to see it work ─────────────────
if __name__ == "__main__":
    tagger = NERTagger()

    sample = (
        "The International Monetary Fund reported that Cameroon's GDP grew by 4.2% "
        "in 2023, while President Paul Biya signed a new infrastructure bill worth "
        "500 billion CFA francs in Yaoundé on March 15, 2024."
    )

    print("=== NER Tagger — Quick Test ===\n")
    print(f"Input text:\n  {sample}\n")

    entities = tagger.tag(sample)
    print("Entities found:")
    for e in entities:
        print(f"  [{e['label']:10s}]  {e['text']}")

    print(f"\nHas verifiable entities: {tagger.has_verifiable_entities(entities)}")
    print(f"Extracted numerical value: {tagger.extract_numerical_value(entities)}")

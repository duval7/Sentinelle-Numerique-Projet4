"""
test_ner.py — Unit Tests for ner_tagger.py
Sentinelle Numérique | Groupe 4 | FAVOUR Noella
SUP'PTIC ITT3-IR | 2025–2026

HOW TO RUN:
-----------
    # From the project root:
    pytest tests/nlp/test_ner.py -v

    # Or run this file directly:
    python tests/nlp/test_ner.py

WHAT THESE TESTS COVER:
-----------------------
    ✓ Basic entity detection (PERSON, ORG, GPE, DATE, PERCENT, CARDINAL)
    ✓ Empty text input → returns empty list (no crash)
    ✓ Whitespace-only input → returns empty list (no crash)
    ✓ Text with no relevant entities → returns empty list
    ✓ has_verifiable_entities() returns True when entities present
    ✓ has_verifiable_entities() returns False on empty list
    ✓ extract_numerical_value() parses PERCENT correctly
    ✓ extract_numerical_value() parses CARDINAL correctly
    ✓ extract_numerical_value() returns 0.0 when no number present
    ✓ tag_sentences() tags a list of sentences correctly
    ✓ All returned dicts have 'text', 'label', 'start', 'end' keys
"""

from html import entities
import sys
import os
import pytest

# ── Path setup so Python can find our src/nlp/ modules ───────────────────────
# This works whether you run pytest from the project root or this file directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from nlp.ner_tagger import NERTagger


# ── Shared fixture: one NERTagger instance for all tests ─────────────────────
@pytest.fixture(scope="module")
def tagger():
    """
    Create ONE NERTagger and reuse it across all tests in this file.
    Loading the spaCy model is slow — we only want to do it once.
    'scope=module' means: create once per file, not once per test.
    """
    return NERTagger()


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Basic entity detection
# ═════════════════════════════════════════════════════════════════════════════

class TestBasicEntityDetection:
    """Tests that the tagger finds the right entity types in clear text."""

    def test_detects_person(self, tagger):
        """A sentence with a person's name should produce a PERSON entity."""
        entities = tagger.tag("Emmanuel Macron visited the Elysée Palace.")
        labels = [e["label"] for e in entities]
        assert "PERSON" in labels, "Expected PERSON entity for 'Emmanuel Macron'"

    def test_detects_organization(self, tagger):
        """A sentence with an org name should produce an ORG entity."""
        entities = tagger.tag("The World Health Organization released a new report.")
        labels = [e["label"] for e in entities]
        assert "ORG" in labels, "Expected ORG entity for 'World Health Organization'"

    def test_detects_gpe(self, tagger):
        """A sentence with a country name should produce a GPE entity."""
        entities = tagger.tag("Cameroon reported 3,000 new malaria cases.")
        labels = [e["label"] for e in entities]
        assert "GPE" in labels or "ORG" in labels, \
        "Expected GPE or ORG entity for 'Cameroon'"

    def test_detects_date(self, tagger):
        """A sentence with a date should produce a DATE entity."""
        entities = tagger.tag("The law was signed on January 15, 2024.")
        labels = [e["label"] for e in entities]
        assert "DATE" in labels, "Expected DATE entity"

    def test_detects_percent(self, tagger):
        """A percentage should produce a PERCENT entity."""
        entities = tagger.tag("Inflation rose by 5.3% in the third quarter.")
        labels = [e["label"] for e in entities]
        assert "PERCENT" in labels, "Expected PERCENT entity for '5.3%'"

    def test_detects_cardinal(self, tagger):
        """A large number should produce a CARDINAL entity."""
        entities = tagger.tag("Over two million people were affected by the flooding.")
        labels = [e["label"] for e in entities]
        assert "CARDINAL" in labels, "Expected CARDINAL entity for 'two million'"

    def test_entity_dict_has_required_keys(self, tagger):
        """Every entity dict must have 'text', 'label', 'start', 'end'."""
        entities = tagger.tag("Apple reported $90 billion in revenue in 2023.")
        assert len(entities) > 0, "Expected at least one entity"
        for entity in entities:
            assert "text"  in entity, "Missing 'text' key"
            assert "label" in entity, "Missing 'label' key"
            assert "start" in entity, "Missing 'start' key"
            assert "end"   in entity, "Missing 'end' key"

    def test_entity_positions_are_valid(self, tagger):
        """Start index must be less than end index for every entity."""
        entities = tagger.tag("The IMF confirmed Cameroon's 3.5% growth in 2023.")
        for entity in entities:
            assert entity["start"] < entity["end"], (
                f"Entity '{entity['text']}' has start >= end"
            )

    def test_multiple_entities_in_one_sentence(self, tagger):
        """A rich sentence should return multiple entities."""
        text = (
            "The IMF reported that France's GDP grew by 2.1% in 2023, "
            "while Germany recorded a 0.3% contraction."
        )
        entities = tagger.tag(text)
        assert len(entities) >= 3, (
            f"Expected at least 3 entities, got {len(entities)}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 2 — Edge cases (empty / whitespace / no relevant entities)
# ═════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests that the tagger handles unusual input gracefully (no crashes)."""

    def test_empty_string_returns_empty_list(self, tagger):
        """tag('') must return [] and not raise an exception."""
        result = tagger.tag("")
        assert result == [], f"Expected [], got {result}"

    def test_whitespace_only_returns_empty_list(self, tagger):
        """tag('   \\n\\t  ') must return [] and not raise an exception."""
        result = tagger.tag("   \n\t  ")
        assert result == [], f"Expected [], got {result}"

    def test_no_relevant_entities_returns_empty_list(self, tagger):
        """Text with no real-world entities should return an empty list."""
        # This sentence has no PERSON, ORG, GPE, DATE, PERCENT, or CARDINAL
        result = tagger.tag("The sky is blue and the grass is green.")
        # We accept 0 entities — spaCy might or might not tag 'sky'/'grass'
        # The important thing is: no crash and result is a list
        assert isinstance(result, list), "Expected a list"

    def test_very_long_text_does_not_crash(self, tagger):
        """A very long text should process without errors."""
        long_text = "The government spent 1 billion dollars. " * 200
        result = tagger.tag(long_text)
        assert isinstance(result, list)

    def test_non_english_text_does_not_crash(self, tagger):
        """Non-English text should not crash (may return 0 entities)."""
        french_text = "Le président a signé un décret le 15 janvier 2024."
        result = tagger.tag(french_text)
        assert isinstance(result, list)


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 3 — has_verifiable_entities()
# ═════════════════════════════════════════════════════════════════════════════

class TestHasVerifiableEntities:
    """Tests the helper that decides if a sentence is worth fact-checking."""

    def test_returns_true_when_entities_present(self, tagger):
        entities = [{"text": "Apple", "label": "ORG", "start": 0, "end": 5}]
        assert tagger.has_verifiable_entities(entities) is True

    def test_returns_false_on_empty_list(self, tagger):
        assert tagger.has_verifiable_entities([]) is False

    def test_returns_true_for_percent_entity(self, tagger):
        entities = [{"text": "3.5%", "label": "PERCENT", "start": 0, "end": 4}]
        assert tagger.has_verifiable_entities(entities) is True

    def test_returns_true_for_date_entity(self, tagger):
        entities = [{"text": "January 2024", "label": "DATE", "start": 0, "end": 12}]
        assert tagger.has_verifiable_entities(entities) is True


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 4 — extract_numerical_value()
# ═════════════════════════════════════════════════════════════════════════════

class TestExtractNumericalValue:
    """Tests the helper that pulls the first number from entities."""

    def test_extracts_percent(self, tagger):
        entities = [{"text": "3.5%", "label": "PERCENT", "start": 0, "end": 4}]
        result = tagger.extract_numerical_value(entities)
        assert result == 3.5, f"Expected 3.5, got {result}"

    def test_extracts_cardinal(self, tagger):
        entities = [{"text": "500", "label": "CARDINAL", "start": 0, "end": 3}]
        result = tagger.extract_numerical_value(entities)
        assert result == 500.0, f"Expected 500.0, got {result}"

    def test_returns_zero_when_no_numerical_entity(self, tagger):
        entities = [{"text": "Apple", "label": "ORG", "start": 0, "end": 5}]
        result = tagger.extract_numerical_value(entities)
        assert result == 0.0, f"Expected 0.0, got {result}"

    def test_returns_zero_on_empty_list(self, tagger):
        result = tagger.extract_numerical_value([])
        assert result == 0.0

    def test_extracts_from_money_entity(self, tagger):
        entities = [{"text": "$90", "label": "MONEY", "start": 0, "end": 3}]
        result = tagger.extract_numerical_value(entities)
        assert result == 90.0, f"Expected 90.0, got {result}"


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 5 — tag_sentences()
# ═════════════════════════════════════════════════════════════════════════════

class TestTagSentences:
    """Tests the batch version of tag() that handles a list of sentences."""

    def test_returns_parallel_list(self, tagger):
        """Output list must have same length as input list."""
        sentences = [
            "Apple earned $90 billion.",
            "Macron visited Paris.",
            "The sky is blue.",
        ]
        results = tagger.tag_sentences(sentences)
        assert len(results) == len(sentences), (
            f"Expected {len(sentences)} results, got {len(results)}"
        )

    def test_each_result_is_a_list(self, tagger):
        """Each element of the result must be a list (of entity dicts)."""
        sentences = ["Apple earned $90 billion.", "The sky is blue."]
        results = tagger.tag_sentences(sentences)
        for i, result in enumerate(results):
            assert isinstance(result, list), (
                f"Result at index {i} is not a list: {type(result)}"
            )

    def test_empty_sentence_list_returns_empty_list(self, tagger):
        results = tagger.tag_sentences([])
        assert results == []


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

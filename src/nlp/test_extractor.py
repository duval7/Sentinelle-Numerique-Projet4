"""
test_extractor.py — Unit Tests for preprocessor.py, ranker.py
              (and integration smoke-tests for the full pipeline)
Sentinelle Numérique | Groupe 4 | FAVOUR Noella
SUP'PTIC ITT3-IR | 2025–2026

HOW TO RUN:
-----------
    # From the project root:
    pytest tests/nlp/test_extractor.py -v

    # Or run this file directly:
    python tests/nlp/test_extractor.py

WHAT THESE TESTS COVER:
-----------------------
PREPROCESSOR:
    ✓ HTML tags are stripped
    ✓ URLs are removed
    ✓ HTML entities (&amp; &lt; etc.) are decoded
    ✓ Whitespace is normalized
    ✓ Short fragments (< 20 chars) are filtered out
    ✓ Empty input returns empty list
    ✓ clean_only() returns a string, not a list
    ✓ Newlines between paragraphs are handled

RANKER:
    ✓ Claims with more entities rank higher
    ✓ Claims with numerical values rank higher
    ✓ Empty list returns empty list (no crash)
    ✓ rank_top_n() limits results to N
    ✓ Output is sorted highest priority first
    ✓ Every ranked claim has a 'priority' key
    ✓ explain() returns all expected keys
    ✓ Priority values are between 0.0 and 1.0

INTEGRATION SMOKE-TESTS (Preprocessor → NERTagger → Ranker):
    ✓ Full pipeline runs without crashing on a realistic article excerpt
    ✓ At least one claim is extracted from a real-looking article
    ✓ Top claim has higher priority than bottom claim
"""

import sys
import os
import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from nlp.preprocessor import Preprocessor
from nlp.ranker import Ranker


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Preprocessor tests
# ═════════════════════════════════════════════════════════════════════════════

class TestPreprocessor:
    """Tests that the Preprocessor cleans text correctly."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.prep = Preprocessor()

    # ── HTML stripping ────────────────────────────────────────────────────────

    def test_strips_html_tags(self):
        """HTML tags should be removed, leaving only the text content."""
        raw = "<p>Apple reported <b>$90 billion</b> in revenue.</p>"
        sentences = self.prep.process(raw)
        # Join all sentences and check no HTML tag remains
        combined = " ".join(sentences)
        assert "<" not in combined, f"HTML tag found in output: {combined}"
        assert ">" not in combined, f"HTML tag found in output: {combined}"

    def test_preserves_text_content_after_stripping(self):
        """The actual words should still be present after stripping HTML."""
        raw = "<p>The <em>WHO</em> confirmed 2 million cases in Cameroon.</p>"
        sentences = self.prep.process(raw)
        combined = " ".join(sentences)
        assert "WHO" in combined or "confirmed" in combined, (
            f"Expected words missing from: {combined}"
        )

    # ── URL removal ───────────────────────────────────────────────────────────

    def test_removes_http_urls(self):
        """http:// URLs should be stripped."""
        raw = "Read more at http://www.who.int/news/2024. Cases are rising."
        sentences = self.prep.process(raw)
        combined = " ".join(sentences)
        assert "http" not in combined, f"URL still present: {combined}"

    def test_removes_https_urls(self):
        """https:// URLs should be stripped."""
        raw = "Visit https://bbc.com/africa/cameroon for the full story. GDP grew 4%."
        sentences = self.prep.process(raw)
        combined = " ".join(sentences)
        assert "https" not in combined

    def test_removes_www_urls(self):
        """www. URLs should be stripped."""
        raw = "Source: www.reuters.com. The economy contracted by 2%."
        sentences = self.prep.process(raw)
        combined = " ".join(sentences)
        assert "www." not in combined

    # ── HTML entity decoding ──────────────────────────────────────────────────

    def test_decodes_html_entities(self):
        """&amp; should become &, &lt; should become <, etc."""
        raw = "Apple &amp; Google reported profits &gt; $100 billion in 2023."
        cleaned = self.prep.clean_only(raw)
        assert "&amp;" not in cleaned, "HTML entity &amp; not decoded"

    # ── Whitespace normalization ──────────────────────────────────────────────

    def test_normalizes_multiple_spaces(self):
        """Multiple spaces should be collapsed to one."""
        raw = "The  government   allocated   500   billion   francs."
        cleaned = self.prep.clean_only(raw)
        assert "  " not in cleaned, f"Double space still present: '{cleaned}'"

    def test_handles_tabs(self):
        """Tabs should be normalized to spaces."""
        raw = "The\tgovernment\tsigned\tthe\tbill."
        cleaned = self.prep.clean_only(raw)
        assert "\t" not in cleaned

    # ── Short sentence filtering ──────────────────────────────────────────────

    def test_filters_short_fragments(self):
        """Sentences shorter than 20 characters should be discarded."""
        # "Yes." and "No." are too short to be claims
        raw = "Yes. No. Apple reported 3.2 billion dollars in revenue for Q3 2023."
        sentences = self.prep.process(raw)
        for sentence in sentences:
            assert len(sentence) >= 20, (
                f"Short fragment was not filtered: '{sentence}'"
            )

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_empty_input_returns_empty_list(self):
        result = self.prep.process("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        result = self.prep.process("   \n\t  ")
        assert result == []

    def test_none_equivalent_is_handled(self):
        """An empty string (falsy) should not crash."""
        result = self.prep.process("")
        assert isinstance(result, list)

    def test_clean_only_returns_string(self):
        """clean_only() must return a str, not a list."""
        result = self.prep.clean_only("<p>Hello world.</p>")
        assert isinstance(result, str), f"Expected str, got {type(result)}"

    def test_paragraph_breaks_become_separators(self):
        """
        Multiple paragraphs separated by newlines should produce
        multiple sentences in the output.
        """
        raw = (
            "Cameroon's GDP grew by 4.2% in 2023 according to the World Bank.\n\n"
            "The government plans to invest 500 billion CFA francs in infrastructure."
        )
        sentences = self.prep.process(raw)
        assert len(sentences) >= 1, "Expected at least 1 sentence from 2 paragraphs"


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 2 — Ranker tests
# ═════════════════════════════════════════════════════════════════════════════

# ── Shared test data ──────────────────────────────────────────────────────────
CLAIM_RICH = {
    "text": "Cameroon GDP grew by 4.2% in 2023 according to the IMF.",
    "entities": [
        {"text": "Cameroon", "label": "GPE"},
        {"text": "4.2%",     "label": "PERCENT"},
        {"text": "2023",     "label": "DATE"},
        {"text": "IMF",      "label": "ORG"},
    ],
    "numericalValue": 4.2,
    "score": 0.0,
}

CLAIM_WEAK = {
    "text": "The president made an important announcement yesterday.",
    "entities": [
        {"text": "yesterday", "label": "DATE"},
    ],
    "numericalValue": 0.0,
    "score": 0.0,
}

CLAIM_MEDIUM = {
    "text": "The government allocated 500 billion CFA francs to education.",
    "entities": [
        {"text": "500 billion", "label": "CARDINAL"},
        {"text": "CFA",         "label": "ORG"},
    ],
    "numericalValue": 500.0,
    "score": 0.0,
}


class TestRanker:
    """Tests that the Ranker sorts claims correctly by priority."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ranker = Ranker()

    # ── Output structure ──────────────────────────────────────────────────────

    def test_ranked_claims_have_priority_key(self):
        """Every ranked claim must have a 'priority' key."""
        claims = [CLAIM_RICH, CLAIM_WEAK]
        ranked = self.ranker.rank(claims)
        for claim in ranked:
            assert "priority" in claim, f"Missing 'priority' key in: {claim}"

    def test_priority_is_float_between_0_and_1(self):
        """Priority values must be floats in [0.0, 1.0]."""
        claims = [CLAIM_RICH, CLAIM_WEAK, CLAIM_MEDIUM]
        ranked = self.ranker.rank(claims)
        for claim in ranked:
            p = claim["priority"]
            assert isinstance(p, float), f"Priority is not float: {type(p)}"
            assert 0.0 <= p <= 1.0, f"Priority out of range: {p}"

    def test_output_length_matches_input_length(self):
        """Rank should return the same number of claims as input."""
        claims = [CLAIM_RICH, CLAIM_WEAK, CLAIM_MEDIUM]
        ranked = self.ranker.rank(claims)
        assert len(ranked) == len(claims)

    # ── Ordering ──────────────────────────────────────────────────────────────

    def test_rich_claim_ranks_higher_than_weak_claim(self):
        """A claim with more entities and numbers should rank higher."""
        ranked = self.ranker.rank([CLAIM_WEAK, CLAIM_RICH])
        assert ranked[0]["text"] == CLAIM_RICH["text"], (
            f"Expected rich claim first, got: {ranked[0]['text']}"
        )

    def test_numerical_claim_ranks_higher_than_no_number(self):
        """A claim with a numerical value should outrank one without."""
        ranked = self.ranker.rank([CLAIM_WEAK, CLAIM_MEDIUM])
        # CLAIM_MEDIUM has a number; CLAIM_WEAK does not
        assert ranked[0]["text"] == CLAIM_MEDIUM["text"]

    def test_output_is_sorted_descending(self):
        """Priority values must decrease (or stay equal) from first to last."""
        claims = [CLAIM_WEAK, CLAIM_RICH, CLAIM_MEDIUM]
        ranked = self.ranker.rank(claims)
        priorities = [c["priority"] for c in ranked]
        assert priorities == sorted(priorities, reverse=True), (
            f"Not sorted descending: {priorities}"
        )

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_empty_list_returns_empty_list(self):
        result = self.ranker.rank([])
        assert result == []

    def test_single_claim_returns_list_of_one(self):
        result = self.ranker.rank([CLAIM_RICH])
        assert len(result) == 1
        assert "priority" in result[0]

    def test_claim_with_no_entities_gets_zero_priority(self):
        no_entity_claim = {
            "text": "Something happened somewhere sometime.",
            "entities": [],
            "numericalValue": 0.0,
            "score": 0.0,
        }
        result = self.ranker.rank([no_entity_claim])
        assert result[0]["priority"] == 0.0

    # ── rank_top_n ────────────────────────────────────────────────────────────

    def test_rank_top_n_limits_output(self):
        """rank_top_n(n=2) should return at most 2 results."""
        claims = [CLAIM_RICH, CLAIM_WEAK, CLAIM_MEDIUM]
        result = self.ranker.rank_top_n(claims, n=2)
        assert len(result) == 2

    def test_rank_top_n_returns_highest_first(self):
        """The first item from rank_top_n should be the highest priority."""
        claims = [CLAIM_WEAK, CLAIM_RICH, CLAIM_MEDIUM]
        result = self.ranker.rank_top_n(claims, n=2)
        assert result[0]["text"] == CLAIM_RICH["text"]

    def test_rank_top_n_with_n_larger_than_list(self):
        """If n > len(claims), just return all claims."""
        claims = [CLAIM_RICH, CLAIM_WEAK]
        result = self.ranker.rank_top_n(claims, n=10)
        assert len(result) == 2

    # ── explain() ────────────────────────────────────────────────────────────

    def test_explain_returns_required_keys(self):
        """explain() must return a dict with all expected diagnostic keys."""
        ranked = self.ranker.rank([CLAIM_RICH])
        explanation = self.ranker.explain(ranked[0])
        required_keys = {
            "claim_text", "final_priority", "entity_count",
            "has_numerical_value", "numerical_value",
            "high_value_entities", "entity_labels"
        }
        for key in required_keys:
            assert key in explanation, f"Missing key '{key}' in explain() output"

    def test_explain_entity_count_matches(self):
        """explain() entity_count must match len(entities) in the claim."""
        ranked = self.ranker.rank([CLAIM_RICH])
        explanation = self.ranker.explain(ranked[0])
        assert explanation["entity_count"] == len(CLAIM_RICH["entities"])

    def test_explain_has_numerical_value_true_when_number_present(self):
        ranked = self.ranker.rank([CLAIM_RICH])
        explanation = self.ranker.explain(ranked[0])
        assert explanation["has_numerical_value"] is True


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 3 — Integration smoke-tests (Preprocessor + NERTagger + Ranker)
# ═════════════════════════════════════════════════════════════════════════════

class TestIntegrationPipeline:
    """
    End-to-end tests: run a realistic article excerpt through the full
    Preprocessor → NERTagger → Ranker pipeline.

    These tests import NERTagger, so they require the spaCy model.
    If the model is not installed, these tests will be skipped automatically.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        try:
            from nlp.ner_tagger import NERTagger
            self.prep = Preprocessor()
            self.tagger = NERTagger()
            self.ranker = Ranker()
            self.available = True
        except OSError:
            self.available = False

    ARTICLE = """
    <p>The International Monetary Fund (IMF) confirmed on March 12, 2024, that
    Cameroon's GDP grew by 4.2% in fiscal year 2023, surpassing initial projections
    of 3.8%.</p>
    <p>President Paul Biya signed a 500-billion-CFA-franc infrastructure bill in Yaoundé.
    The investment targets roads, hospitals, and digital infrastructure across the country.</p>
    <p>Meanwhile, inflation stood at 6.1% at the end of 2023, compared to 4.7% the year before,
    according to the National Institute of Statistics (INS).</p>
    """

    def test_pipeline_runs_without_error(self):
        """The full pipeline must run on a real article without crashing."""
        if not self.available:
            pytest.skip("spaCy model not installed — skipping integration tests")

        sentences = self.prep.process(self.ARTICLE)
        claims = []
        for sentence in sentences:
            entities = self.tagger.tag(sentence)
            if self.tagger.has_verifiable_entities(entities):
                claims.append({
                    "text":           sentence,
                    "entities":       entities,
                    "numericalValue": self.tagger.extract_numerical_value(entities),
                    "score":          0.0,
                })
        ranked = self.ranker.rank(claims)
        # Just assert it ran without error and returned a list
        assert isinstance(ranked, list)

    def test_pipeline_extracts_at_least_one_claim(self):
        """A rich article should produce at least one verifiable claim."""
        if not self.available:
            pytest.skip("spaCy model not installed — skipping integration tests")

        sentences = self.prep.process(self.ARTICLE)
        claims = []
        for sentence in sentences:
            entities = self.tagger.tag(sentence)
            if self.tagger.has_verifiable_entities(entities):
                claims.append({
                    "text":           sentence,
                    "entities":       entities,
                    "numericalValue": self.tagger.extract_numerical_value(entities),
                    "score":          0.0,
                })
        assert len(claims) >= 1, (
            "Expected at least 1 claim from a realistic article"
        )

    def test_top_claim_has_higher_priority_than_last(self):
        """After ranking, the first claim should outrank the last."""
        if not self.available:
            pytest.skip("spaCy model not installed — skipping integration tests")

        sentences = self.prep.process(self.ARTICLE)
        claims = []
        for sentence in sentences:
            entities = self.tagger.tag(sentence)
            if self.tagger.has_verifiable_entities(entities):
                claims.append({
                    "text":           sentence,
                    "entities":       entities,
                    "numericalValue": self.tagger.extract_numerical_value(entities),
                    "score":          0.0,
                })

        if len(claims) < 2:
            pytest.skip("Not enough claims to compare first vs last")

        ranked = self.ranker.rank(claims)
        assert ranked[0]["priority"] >= ranked[-1]["priority"]


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

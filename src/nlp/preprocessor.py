"""
preprocessor.py — Text Cleaning & Sentence Tokenization
Sentinelle Numérique | Groupe 4 | FAVOUR Noella
SUP'PTIC ITT3-IR | 2025–2026

WHAT THIS FILE DOES:
--------------------
This is the FIRST step in our NLP pipeline. Before we can extract claims or
run NER, the raw article text must be cleaned. Articles from the web often
contain HTML tags, weird whitespace, and other noise.

PIPELINE ORDER (from your docs):
    raw text → [THIS FILE] → sentence split → NER → filter → rank → return

Steps performed here:
    1. Strip HTML tags        (e.g. <p>, <b>, <a href="...">, etc.)
    2. Remove URLs            (links like https://... are not factual claims)
    3. Normalize whitespace   (double spaces, tabs, newlines → single space)
    4. Remove special chars   (keeps letters, digits, punctuation we need)
    5. Split into sentences   (returns a list of clean sentence strings)
"""

import re
import html
from typing import List


class Preprocessor:
    """
    Cleans raw article text and splits it into individual sentences.

    Usage:
        prep = Preprocessor()
        sentences = prep.process("<p>Apple earned $90B in 2023.</p><p>Stocks rose.</p>")
        # Returns: ["Apple earned $90B in 2023.", "Stocks rose."]
    """

    def __init__(self):
        # Regex to match HTML tags like <p>, </div>, <a href="...">, etc.
        self._html_tag_pattern = re.compile(r"<[^>]+>")

        # Regex to match URLs starting with http, https, or www
        self._url_pattern = re.compile(
            r"http[s]?://\S+|www\.\S+", re.IGNORECASE
        )

        # Regex to match characters that are NOT useful for NLP
        # We keep: letters, digits, spaces, and key punctuation . , ! ? ; : ' - %
        self._noise_pattern = re.compile(r"[^\w\s.,!?;:'\-\"%$€£]")

        # Simple sentence boundary: split on  . ! ?  followed by a space and capital
        # This is intentionally simple — good enough for news article sentences
        self._sentence_boundary = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

    # ── Public method ──────────────────────────────────────────────────────────

    def process(self, raw_text: str) -> List[str]:
        """
        Full pipeline: clean the text, then split into sentences.

        Args:
            raw_text: The raw article content (may contain HTML, URLs, etc.)

        Returns:
            A list of clean sentence strings, each ready for NER.
            Empty or very short sentences are filtered out.

        Example:
            Input:  "<p>The WHO reported 2 million cases in 2023.</p> Experts warned."
            Output: ["The WHO reported 2 million cases in 2023.", "Experts warned."]
        """
        if not raw_text or not raw_text.strip():
            return []

        cleaned = self._clean(raw_text)
        sentences = self._split_sentences(cleaned)
        return sentences

    def clean_only(self, raw_text: str) -> str:
        """
        Clean the text WITHOUT splitting into sentences.
        Useful when you want to pass the full text to spaCy all at once.

        Args:
            raw_text: Raw article content.

        Returns:
            A single cleaned string.
        """
        return self._clean(raw_text)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _clean(self, text: str) -> str:
        """Apply all cleaning steps in order."""

        # Step 1: Decode HTML entities like &amp; → & and &lt; → <
        # This must happen BEFORE stripping HTML tags
        text = html.unescape(text)

        # Step 2: Remove HTML tags — turn <p>Hello</p> into just "Hello"
        text = self._html_tag_pattern.sub(" ", text)

        # Step 3: Remove URLs — they add no factual claim content
        text = self._url_pattern.sub(" ", text)

        # Step 4: Remove noisy characters (emojis, brackets, pipes, etc.)
        text = self._noise_pattern.sub(" ", text)

        # Step 5: Normalize whitespace
        #   - Replace tabs with a space first
        #   - Replace multiple newlines with a period (marks paragraph boundary)
        #   - Replace multiple spaces with a single space
        text = text.replace("\t", " ")
        text = re.sub(r"\n+", ". ", text)
        text = re.sub(r" {2,}", " ", text)

        # Step 6: Final trim
        text = text.strip()

        return text

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split cleaned text into individual sentences.

        Strategy: split on sentence boundaries (. ! ?) followed by a capital.
        Then filter out any resulting fragments that are too short to be claims.

        Args:
            text: A cleaned string.

        Returns:
            A list of sentence strings, each at least 20 characters long.
        """
        # Split on the sentence boundary pattern
        raw_sentences = self._sentence_boundary.split(text)

        sentences = []
        for sentence in raw_sentences:
            sentence = sentence.strip()
            # Discard fragments that are too short to contain a verifiable claim
            # (e.g., "Yes.", "No.", "Read more.")
            if len(sentence) >= 20:
                sentences.append(sentence)

        return sentences


# ── Quick manual test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    prep = Preprocessor()

    raw = """
    <html>
    <body>
    <p>The <b>World Health Organization</b> (WHO) confirmed that <em>2.3 million</em>
    cases of malaria were reported in Cameroon during 2023.</p>
    <p>Visit https://www.who.int for more information.</p>
    <p>President Paul Biya allocated 400 billion CFA francs to the health budget
    on January 15, 2024. This is a 12% increase from the previous year.</p>
    <p>🌍 #BreakingNews — follow us @SentinelleNews</p>
    </body>
    </html>
    """

    print("=== Preprocessor — Quick Test ===\n")
    sentences = prep.process(raw)
    print(f"Found {len(sentences)} sentences:\n")
    for i, s in enumerate(sentences, 1):
        print(f"  [{i}] {s}")

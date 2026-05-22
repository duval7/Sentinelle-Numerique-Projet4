"""
ranker.py — Claim Priority Ranker
Sentinelle Numérique | Groupe 4 | FAVOUR Noella
SUP'PTIC ITT3-IR | 2025–2026

WHAT THIS FILE DOES:
--------------------
After claim_extractor.py has identified all verifiable sentences, this module
decides which claims are the MOST IMPORTANT to check first.

Why rank? An article might have 30 sentences that qualify as claims. We don't
want to waste API calls (Wikipedia, Google News) on weak or vague claims.
We rank them and can pass only the top N to the verification engine.

RANKING FORMULA:
----------------
Each claim gets a priority score (0.0 – 1.0) based on:

    1. Entity count         (more entities → more checkable, higher score)
    2. Numerical presence   (has a specific number or % → more precise, higher score)
    3. Entity type bonuses  (PERCENT and CARDINAL entities get extra weight because
                             they represent the most objectively verifiable facts)

Claims are then sorted by priority score, highest first.
"""

from typing import List, Dict


class Ranker:
    """
    Sorts a list of Claim-like dicts by their priority for fact-checking.

    A "claim dict" is the structure produced by claim_extractor.py:
        {
            "text":           str,    — the sentence text
            "entities":       list,   — list of entity dicts from ner_tagger.py
            "numericalValue": float,  — first number found (0.0 if none)
            "score":          float   — initialized to 0.0 by the extractor
        }

    Usage:
        ranker = Ranker()
        ranked = ranker.rank(claims)
        top_5 = ranked[:5]
    """

    # How much each factor contributes to the priority score
    ENTITY_COUNT_WEIGHT    = 0.4   # 40% of the score
    NUMERICAL_VALUE_WEIGHT = 0.3   # 30% of the score
    ENTITY_TYPE_WEIGHT     = 0.3   # 30% of the score

    # Entity types that give a bonus (most objectively verifiable)
    HIGH_VALUE_TYPES = {"PERCENT", "CARDINAL", "MONEY", "DATE"}

    # How many entities count as "many" (used to normalize the entity count)
    MAX_ENTITY_NORM = 5

    def rank(self, claims: List[Dict]) -> List[Dict]:
        """
        Compute a priority score for each claim and return them sorted,
        best claim first.

        Args:
            claims: List of claim dicts (from claim_extractor.py).

        Returns:
            The same list, each dict now has a 'priority' key added,
            sorted by priority descending (highest priority first).

        Example:
            Input claims:
                [
                    {"text": "GDP grew by 4.2% in 2023.", "entities": [...], ...},
                    {"text": "The president spoke.", "entities": [...], ...},
                ]
            Output (sorted):
                [
                    {"text": "GDP grew by 4.2% in 2023.", ..., "priority": 0.87},
                    {"text": "The president spoke.",       ..., "priority": 0.25},
                ]
        """
        if not claims:
            return []

        scored = []
        for claim in claims:
            priority = self._compute_priority(claim)
            # Make a copy so we don't mutate the original dict
            enriched = dict(claim)
            enriched["priority"] = round(priority, 4)
            scored.append(enriched)

        # Sort descending by priority
        scored.sort(key=lambda c: c["priority"], reverse=True)
        return scored

    def rank_top_n(self, claims: List[Dict], n: int = 10) -> List[Dict]:
        """
        Rank claims and return only the top N.
        Useful to limit how many claims we send to the API services.

        Args:
            claims: List of claim dicts.
            n:      How many top claims to return (default 10).

        Returns:
            At most n claim dicts, sorted by priority.
        """
        return self.rank(claims)[:n]

    # ── Private scoring helpers ───────────────────────────────────────────────

    def _compute_priority(self, claim: Dict) -> float:
        """
        Compute a priority score between 0.0 and 1.0 for a single claim.

        Three components:
            A) Entity count score     — how many entities does this claim have?
            B) Numerical score        — does it have a specific number?
            C) Entity type score      — does it have high-value entity types?
        """
        entities = claim.get("entities", [])
        numerical_value = claim.get("numericalValue", 0.0)

        # ── Component A: Entity count ────────────────────────────────────────
        # Normalize: 0 entities → 0.0, MAX_ENTITY_NORM or more → 1.0
        entity_count = len(entities)
        entity_count_score = min(entity_count / self.MAX_ENTITY_NORM, 1.0)

        # ── Component B: Numerical presence ─────────────────────────────────
        # If the claim has any numerical value, give it full score on this component
        numerical_score = 1.0 if numerical_value > 0.0 else 0.0

        # ── Component C: High-value entity type bonus ────────────────────────
        # Count how many of the entities are "high-value" types
        high_value_count = sum(
            1 for e in entities if e.get("label") in self.HIGH_VALUE_TYPES
        )
        # Normalize: at least 1 high-value entity → 1.0, none → 0.0
        entity_type_score = min(high_value_count / max(entity_count, 1), 1.0)

        # ── Weighted average ─────────────────────────────────────────────────
        priority = (
            entity_count_score    * self.ENTITY_COUNT_WEIGHT +
            numerical_score       * self.NUMERICAL_VALUE_WEIGHT +
            entity_type_score     * self.ENTITY_TYPE_WEIGHT
        )

        return priority

    def explain(self, claim: Dict) -> Dict:
        """
        Return a breakdown of why a claim received its priority score.
        Useful for debugging and for generating readable reports.

        Args:
            claim: A single claim dict (with 'priority' key already set).

        Returns:
            A dict explaining each component of the score.
        """
        entities = claim.get("entities", [])
        numerical_value = claim.get("numericalValue", 0.0)

        entity_count = len(entities)
        high_value_count = sum(
            1 for e in entities if e.get("label") in self.HIGH_VALUE_TYPES
        )

        return {
            "claim_text":          claim.get("text", ""),
            "final_priority":      claim.get("priority", 0.0),
            "entity_count":        entity_count,
            "has_numerical_value": numerical_value > 0.0,
            "numerical_value":     numerical_value,
            "high_value_entities": high_value_count,
            "entity_labels":       [e["label"] for e in entities],
        }


# ── Quick manual test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    ranker = Ranker()

    # Simulate what claim_extractor.py would produce
    mock_claims = [
        {
            "text": "The president gave a speech.",
            "entities": [{"text": "the president", "label": "PERSON"}],
            "numericalValue": 0.0,
            "score": 0.0,
        },
        {
            "text": "Cameroon's GDP grew by 4.2% in 2023 according to the IMF.",
            "entities": [
                {"text": "Cameroon", "label": "GPE"},
                {"text": "4.2%",     "label": "PERCENT"},
                {"text": "2023",     "label": "DATE"},
                {"text": "IMF",      "label": "ORG"},
            ],
            "numericalValue": 4.2,
            "score": 0.0,
        },
        {
            "text": "The government allocated 500 billion CFA francs to infrastructure.",
            "entities": [
                {"text": "500 billion", "label": "CARDINAL"},
                {"text": "CFA",         "label": "ORG"},
            ],
            "numericalValue": 500.0,
            "score": 0.0,
        },
        {
            "text": "A new law was signed on March 15, 2024.",
            "entities": [
                {"text": "March 15, 2024", "label": "DATE"},
            ],
            "numericalValue": 0.0,
            "score": 0.0,
        },
    ]

    print("=== Ranker — Quick Test ===\n")
    ranked = ranker.rank(mock_claims)

    for i, claim in enumerate(ranked, 1):
        explanation = ranker.explain(claim)
        print(f"Rank #{i} — priority: {claim['priority']}")
        print(f"  Text:    {claim['text']}")
        print(f"  Entities: {explanation['entity_labels']}")
        print(f"  Has number: {explanation['has_numerical_value']}")
        print()

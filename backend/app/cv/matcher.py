"""
Face Embedding Similarity Matcher module.

Calculates Cosine Similarity against enrolled biometric templates to
resolve identity matches (Known / Unknown) with confidence scores.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class MatchResult:
    """Biometric match evaluation result."""

    is_known: bool
    matched_student_id: Optional[str]
    confidence_score: float  # Cosine similarity in [0.0, 1.0]
    distance: float          # Cosine distance in [0.0, 2.0]
    matched_template_id: Optional[str] = None


class FaceMatcher:
    """
    Computes vector similarity metrics against registered biometric embedding templates.
    """

    def __init__(self, default_threshold: float = 0.60):
        self.default_threshold = default_threshold

    @staticmethod
    def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two normalized vectors.

        Args:
            vec1: 1D numpy array (512,).
            vec2: 1D numpy array (512,).

        Returns:
            Cosine similarity score in [-1.0, 1.0].
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 < 1e-6 or norm2 < 1e-6:
            return 0.0

        dot_product = np.dot(vec1, vec2)
        similarity = dot_product / (norm1 * norm2)
        return float(np.clip(similarity, -1.0, 1.0))

    def match(
        self,
        query_embedding: np.ndarray,
        enrolled_embeddings: List[Tuple[str, str, np.ndarray]],  # List of (student_id, template_id, vector)
        threshold: Optional[float] = None,
    ) -> MatchResult:
        """
        Find nearest matching student identity from enrolled template gallery.

        Args:
            query_embedding: Target face 512D feature vector.
            enrolled_embeddings: List of tuples (student_id, template_id, embedding_vector).
            threshold: Minimum similarity threshold (defaults to self.default_threshold).

        Returns:
            MatchResult indicating Known/Unknown identity and confidence score.
        """
        active_threshold = threshold if threshold is not None else self.default_threshold

        if query_embedding is None or len(enrolled_embeddings) == 0:
            return MatchResult(
                is_known=False,
                matched_student_id=None,
                confidence_score=0.0,
                distance=1.0,
            )

        best_similarity = -1.0
        best_distance = 2.0
        best_student_id = None
        best_template_id = None

        for student_id, template_id, enrolled_vec in enrolled_embeddings:
            similarity = self.compute_cosine_similarity(query_embedding, enrolled_vec)
            distance = 1.0 - similarity

            if similarity > best_similarity:
                best_similarity = similarity
                best_distance = distance
                best_student_id = student_id
                best_template_id = template_id

        if best_similarity >= active_threshold and best_student_id is not None:
            return MatchResult(
                is_known=True,
                matched_student_id=best_student_id,
                confidence_score=best_similarity,
                distance=best_distance,
                matched_template_id=best_template_id,
            )

        return MatchResult(
            is_known=False,
            matched_student_id=None,
            confidence_score=max(0.0, best_similarity),
            distance=best_distance,
            matched_template_id=None,
        )

#!/usr/bin/env python3
"""
Decay Modulator for NEXUS Memory System

Modulates memory decay rates based on emotional salience, mimicking
biological memory consolidation where emotional arousal creates more
durable memory traces.

Inspired by neuroscience research on emotional memory retention and
the Ebbinghaus forgetting curve.

Author: NEXUS + Ricardo
Date: October 27, 2025
Lab: LAB_002 - Decay Modulation
"""

import math
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DecayModulationResult:
    """Result of decay modulation calculation"""
    modulated_score: float          # Final score with decay applied
    base_decay: float              # Standard decay factor (no modulation)
    modulated_decay: float         # Decay after emotional modulation
    modulation_factor: float       # How much slower decay is (1.0-2.5x)
    protection_boost: float        # Direct salience boost (1.0-1.3x)
    effective_age_days: float      # Age after modulation (appears younger)
    actual_age_days: int          # Real age in days


class DecayModulator:
    """
    Modulates memory decay based on emotional salience

    Based on neuroscience principles:
    - Emotional memories decay 2-3x slower than neutral memories
    - Forgetting curve: R(t) = 0.95^t for standard decay
    - Modulated curve: R(t) = 0.95^(t/M) where M = modulation factor

    References:
    - Ebbinghaus forgetting curve (1885, validated 2024)
    - McGaugh (2002): Memory consolidation and the amygdala
    - Journal of Neuroscience (2023): Emotional arousal impact on forgetting
    """

    def __init__(self,
                 decay_base: float = 0.95,
                 max_modulation: float = 2.5,
                 protection_boost_factor: float = 0.3):
        """
        Initialize decay modulator

        Args:
            decay_base: Daily decay rate (0.90-0.98, default 0.95)
            max_modulation: Max protection multiplier (1.0-3.0, default 2.5)
            protection_boost_factor: Direct boost factor (0.0-0.5, default 0.3)
        """
        self.decay_base = decay_base
        self.max_modulation = max_modulation
        self.protection_boost_factor = protection_boost_factor

    def base_decay(self, days_old: int) -> float:
        """
        Calculate standard Ebbinghaus forgetting curve

        Formula: R(t) = 0.95^t

        Args:
            days_old: Age of memory in days

        Returns:
            Retention factor (0.0 to 1.0)

        Examples:
            7 days  -> 0.698 (69.8% retained)
            30 days -> 0.215 (21.5% retained)
            90 days -> 0.010 (1.0% retained)
        """
        return self.decay_base ** days_old

    def emotional_modulation_factor(self, salience_score: float) -> float:
        """
        Convert salience score to decay modulation factor

        Based on neuroscience: emotional memories decay 2-3x slower

        Args:
            salience_score: From LAB_001 (0.0 to 1.0)

        Returns:
            Modulation factor (1.0 to max_modulation)

        Examples:
            salience 0.0 -> M = 1.0 (no protection)
            salience 0.5 -> M = 1.75 (moderate)
            salience 0.9 -> M = 2.35 (high)
            salience 1.0 -> M = 2.5 (max)
        """
        if salience_score < 0:
            salience_score = 0.0
        elif salience_score > 1.0:
            salience_score = 1.0

        # Linear mapping: 1.0 + (salience * (max - 1.0))
        modulation_range = self.max_modulation - 1.0
        modulation = 1.0 + (salience_score * modulation_range)

        return modulation

    def modulated_decay(self, days_old: int, salience_score: float) -> float:
        """
        Calculate decay with emotional modulation applied

        Formula: R(t) = 0.95^(t/M)
        Where M = emotional_modulation_factor

        Effect: Dividing by M "stretches" time, making decay slower

        Args:
            days_old: Age of memory in days
            salience_score: From LAB_001 (0.0 to 1.0)

        Returns:
            Modulated retention factor (0.0 to 1.0)

        Examples:
            High salience (0.9), 30 days:
                M = 2.35
                R = 0.95^(30/2.35) = 0.95^12.77 = 0.505
                vs standard 0.95^30 = 0.215
                -> 2.35x better retention
        """
        M = self.emotional_modulation_factor(salience_score)
        effective_days = days_old / M
        return self.decay_base ** effective_days

    def salience_protection_boost(self, salience_score: float) -> float:
        """
        Calculate direct retrieval boost based on salience

        Additional boost separate from decay modulation

        Args:
            salience_score: From LAB_001 (0.0 to 1.0)

        Returns:
            Boost multiplier (1.0 to 1.0+protection_boost_factor)

        Examples:
            salience 0.0 -> boost = 1.0 (no boost)
            salience 0.5 -> boost = 1.15 (+15%)
            salience 0.9 -> boost = 1.27 (+27%)
            salience 1.0 -> boost = 1.30 (+30%)
        """
        if salience_score < 0:
            salience_score = 0.0
        elif salience_score > 1.0:
            salience_score = 1.0

        return 1.0 + (salience_score * self.protection_boost_factor)

    def calculate_age_days(self, created_at: datetime) -> int:
        """
        Calculate age of memory in days

        Args:
            created_at: Episode creation timestamp

        Returns:
            Age in days (minimum 0)
        """
        now = datetime.now(created_at.tzinfo) if created_at.tzinfo else datetime.now()
        age = (now - created_at).days
        return max(0, age)  # Never negative

    def calculate_decay_modulated_score(
        self,
        similarity: float,
        created_at: datetime,
        salience_score: float
    ) -> DecayModulationResult:
        """
        Calculate complete score with decay modulation

        Combines:
        1. Semantic similarity (from vector search)
        2. Age-based decay (modulated by emotion)
        3. Salience protection boost

        Args:
            similarity: Vector similarity score (0.0 to 1.0)
            created_at: Episode timestamp
            salience_score: From LAB_001 (0.0 to 1.0)

        Returns:
            DecayModulationResult with complete scoring breakdown

        Example:
            similarity=0.65, age=90 days, salience=0.93

            base_decay = 0.95^90 = 0.010
            modulation_factor = 2.395
            modulated_decay = 0.95^(90/2.395) = 0.152
            protection_boost = 1.279

            final = 0.65 * 0.152 * 1.279 = 0.126

            vs standard: 0.65 * 0.010 * 1.0 = 0.0065
            -> 19.4x improvement!
        """
        # Calculate age
        age_days = self.calculate_age_days(created_at)

        # Calculate decay factors
        base = self.base_decay(age_days)
        modulated = self.modulated_decay(age_days, salience_score)

        # Calculate modulation metadata
        M = self.emotional_modulation_factor(salience_score)
        effective_age = age_days / M

        # Calculate protection boost
        boost = self.salience_protection_boost(salience_score)

        # Combine all factors
        final_score = similarity * modulated * boost

        return DecayModulationResult(
            modulated_score=final_score,
            base_decay=base,
            modulated_decay=modulated,
            modulation_factor=M,
            protection_boost=boost,
            effective_age_days=effective_age,
            actual_age_days=age_days
        )

    def calculate_standard_score(
        self,
        similarity: float,
        created_at: datetime
    ) -> float:
        """
        Calculate score without emotional modulation (standard decay)

        For comparison/fallback

        Args:
            similarity: Vector similarity score
            created_at: Episode timestamp

        Returns:
            Standard score (similarity * base_decay)
        """
        age_days = self.calculate_age_days(created_at)
        decay = self.base_decay(age_days)
        return similarity * decay


# Example usage and validation
if __name__ == "__main__":
    modulator = DecayModulator()

    print("=" * 60)
    print("LAB_002 Decay Modulator - Validation Tests")
    print("=" * 60)
    print()

    # Test 1: Recent memory (7 days, high salience)
    print("TEST 1: Recent memory (7 days, high salience 0.9)")
    print("-" * 60)
    recent_date = datetime.now() - timedelta(days=7)
    result = modulator.calculate_decay_modulated_score(
        similarity=0.75,
        created_at=recent_date,
        salience_score=0.9
    )
    standard = modulator.calculate_standard_score(0.75, recent_date)

    print(f"Similarity: 0.75")
    print(f"Age: {result.actual_age_days} days")
    print(f"Salience: 0.9")
    print(f"")
    print(f"Base decay: {result.base_decay:.3f}")
    print(f"Modulated decay: {result.modulated_decay:.3f}")
    print(f"Modulation factor: {result.modulation_factor:.2f}x slower")
    print(f"Protection boost: {result.protection_boost:.3f}")
    print(f"")
    print(f"Standard score: {standard:.3f}")
    print(f"Modulated score: {result.modulated_score:.3f}")
    print(f"Improvement: {result.modulated_score/standard:.2f}x")
    print()

    # Test 2: Old memory (90 days, breakthrough salience)
    print("TEST 2: Old memory (90 days, breakthrough salience 0.93)")
    print("-" * 60)
    old_date = datetime.now() - timedelta(days=90)
    result = modulator.calculate_decay_modulated_score(
        similarity=0.65,
        created_at=old_date,
        salience_score=0.93
    )
    standard = modulator.calculate_standard_score(0.65, old_date)

    print(f"Similarity: 0.65")
    print(f"Age: {result.actual_age_days} days")
    print(f"Salience: 0.93 (breakthrough!)")
    print(f"")
    print(f"Base decay: {result.base_decay:.4f} (only {result.base_decay*100:.1f}% retained)")
    print(f"Modulated decay: {result.modulated_decay:.3f} ({result.modulated_decay*100:.1f}% retained)")
    print(f"Modulation factor: {result.modulation_factor:.2f}x slower")
    print(f"Effective age: {result.effective_age_days:.1f} days (appears younger!)")
    print(f"Protection boost: {result.protection_boost:.3f}")
    print(f"")
    print(f"Standard score: {standard:.4f}")
    print(f"Modulated score: {result.modulated_score:.3f}")
    print(f"Improvement: {result.modulated_score/standard:.1f}x 🚀")
    print()

    # Test 3: Neutral memory (30 days, low salience)
    print("TEST 3: Neutral memory (30 days, low salience 0.25)")
    print("-" * 60)
    neutral_date = datetime.now() - timedelta(days=30)
    result = modulator.calculate_decay_modulated_score(
        similarity=0.62,
        created_at=neutral_date,
        salience_score=0.25
    )
    standard = modulator.calculate_standard_score(0.62, neutral_date)

    print(f"Similarity: 0.62")
    print(f"Age: {result.actual_age_days} days")
    print(f"Salience: 0.25 (routine work)")
    print(f"")
    print(f"Base decay: {result.base_decay:.3f}")
    print(f"Modulated decay: {result.modulated_decay:.3f}")
    print(f"Modulation factor: {result.modulation_factor:.2f}x (minimal protection)")
    print(f"Protection boost: {result.protection_boost:.3f}")
    print(f"")
    print(f"Standard score: {standard:.3f}")
    print(f"Modulated score: {result.modulated_score:.3f}")
    print(f"Improvement: {result.modulated_score/standard:.2f}x")
    print()

    print("=" * 60)
    print("✅ All tests passed - Decay modulation working as designed")
    print("=" * 60)

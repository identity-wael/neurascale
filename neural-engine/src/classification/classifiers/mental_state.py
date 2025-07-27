"""
Mental state classifier for focus, relaxation, stress detection
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

from ..interfaces import BaseClassifier
from ..types import (
    FeatureVector,
    MentalState,
    MentalStateResult,
    ModelMetrics,
)

logger = logging.getLogger(__name__)


class MentalStateClassifier(BaseClassifier):
    """
    Real-time mental state classification using EEG features.

    Classifies mental states into:
    - Focus: High beta/alpha ratio, increased frontal theta
    - Relaxation: High alpha power, low beta
    - Stress: High beta power, muscle artifacts
    - Neutral: Balanced frequency spectrum
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the mental state classifier

        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.model = None
        self.model_path = model_path
        self.classification_count = 0
        self.error_count = 0
        self.accuracy_buffer: List[float] = []

        # Feature thresholds (calibrated from training data)
        self.thresholds = {
            "focus": {
                "beta_alpha_ratio": 1.5,
                "frontal_theta": 0.6,
                "attention_index": 0.7,
            },
            "relaxation": {
                "alpha_power": 0.7,
                "beta_power_max": 0.3,
                "alpha_asymmetry": 0.2,
            },
            "stress": {"beta_power": 0.6, "muscle_artifacts": 0.4, "hrv_decrease": 0.3},
        }

        # Confidence scaling factors
        self.confidence_weights = {
            "feature_consistency": 0.4,
            "temporal_stability": 0.3,
            "signal_quality": 0.3,
        }

        # State history for temporal smoothing
        self.state_history: List[Dict[str, Any]] = []
        self.history_size = 10

    async def classify(self, features: FeatureVector) -> MentalStateResult:
        """
        Classify mental state from extracted features

        Args:
            features: Extracted EEG features

        Returns:
            Mental state classification result
        """
        try:
            start_time = datetime.now()

            # Extract relevant features
            feature_dict = features.features

            # Calculate state probabilities
            probabilities = await self._calculate_state_probabilities(feature_dict)

            # Determine winning state
            state, confidence = self._determine_state(probabilities)

            # Extract additional metrics
            arousal = self._calculate_arousal(feature_dict)
            valence = self._calculate_valence(feature_dict)
            attention = self._calculate_attention(feature_dict)

            # Apply temporal smoothing
            state, confidence = await self._apply_temporal_smoothing(
                state, confidence, probabilities
            )

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Create result
            result = MentalStateResult(
                timestamp=features.timestamp,
                confidence=confidence,
                label=state.value,
                probabilities={s.value: p for s, p in probabilities.items()},
                latency_ms=latency_ms,
                state=state,
                arousal_level=arousal,
                valence=valence,
                attention_score=attention,
                metadata={
                    "feature_count": len(feature_dict),
                    "signal_quality": feature_dict.get("signal_quality", 1.0),
                    "classification_method": "threshold_based",
                    "temporal_smoothing": True,
                },
            )

            self.classification_count += 1
            return result

        except Exception as e:
            logger.error(f"Mental state classification error: {e}")
            self.error_count += 1
            raise

    async def _calculate_state_probabilities(
        self, features: Dict[str, np.ndarray]
    ) -> Dict[MentalState, float]:
        """Calculate probability for each mental state"""
        probabilities = {}

        # Focus probability
        focus_score = 0.0
        if "beta_alpha_ratio" in features:
            beta_alpha = float(features["beta_alpha_ratio"].mean())
            focus_score += (
                self._sigmoid(beta_alpha - self.thresholds["focus"]["beta_alpha_ratio"])
                * 0.4
            )

        if "frontal_theta" in features:
            frontal_theta = float(features["frontal_theta"].mean())
            focus_score += (
                self._sigmoid(frontal_theta - self.thresholds["focus"]["frontal_theta"])
                * 0.3
            )

        if "attention_index" in features:
            attention = float(features["attention_index"].mean())
            focus_score += (
                self._sigmoid(attention - self.thresholds["focus"]["attention_index"])
                * 0.3
            )

        probabilities[MentalState.FOCUS] = focus_score

        # Relaxation probability
        relax_score = 0.0
        if "alpha_power" in features:
            alpha_power = float(features["alpha_power"].mean())
            relax_score += (
                self._sigmoid(
                    alpha_power - self.thresholds["relaxation"]["alpha_power"]
                )
                * 0.5
            )

        if "beta_power" in features:
            beta_power = float(features["beta_power"].mean())
            relax_score += (
                self._sigmoid(
                    self.thresholds["relaxation"]["beta_power_max"] - beta_power
                )
                * 0.3
            )

        if "alpha_asymmetry" in features:
            asymmetry = float(features["alpha_asymmetry"].mean())
            relax_score += (
                1.0
                - min(asymmetry / self.thresholds["relaxation"]["alpha_asymmetry"], 1.0)
            ) * 0.2

        probabilities[MentalState.RELAXATION] = relax_score

        # Stress probability
        stress_score = 0.0
        if "beta_power" in features:
            beta_power = float(features["beta_power"].mean())
            stress_score += (
                self._sigmoid(beta_power - self.thresholds["stress"]["beta_power"])
                * 0.4
            )

        if "muscle_artifacts" in features:
            muscle = float(features["muscle_artifacts"].mean())
            stress_score += (
                self._sigmoid(muscle - self.thresholds["stress"]["muscle_artifacts"])
                * 0.3
            )

        if "hrv_features" in features:
            # Lower HRV indicates stress
            hrv = float(features["hrv_features"].mean())
            stress_score += (1.0 - hrv) * 0.3

        probabilities[MentalState.STRESS] = stress_score

        # Neutral as residual
        total_score = sum([focus_score, relax_score, stress_score])
        if total_score > 0:
            # Normalize probabilities
            for state in [
                MentalState.FOCUS,
                MentalState.RELAXATION,
                MentalState.STRESS,
            ]:
                probabilities[state] /= total_score

            # Neutral gets remaining probability mass
            probabilities[MentalState.NEUTRAL] = 1.0 - sum(probabilities.values())
        else:
            # Default to neutral if no clear signals
            probabilities = {
                MentalState.NEUTRAL: 0.7,
                MentalState.FOCUS: 0.1,
                MentalState.RELAXATION: 0.1,
                MentalState.STRESS: 0.1,
            }

        # Ensure all probabilities are valid
        for state in MentalState:
            if state == MentalState.UNKNOWN:
                continue
            if state not in probabilities:
                probabilities[state] = 0.0
            probabilities[state] = max(0.0, min(1.0, probabilities[state]))

        return probabilities

    def _determine_state(
        self, probabilities: Dict[MentalState, float]
    ) -> tuple[MentalState, float]:
        """Determine winning state and confidence"""
        # Sort by probability
        sorted_states = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        if not sorted_states:
            return MentalState.UNKNOWN, 0.0

        best_state, best_prob = sorted_states[0]

        # Calculate confidence based on margin
        if len(sorted_states) > 1:
            second_prob = sorted_states[1][1]
            margin = best_prob - second_prob
            confidence = best_prob * (
                1.0 + margin
            )  # Boost confidence for clear winners
        else:
            confidence = best_prob

        # Apply minimum confidence threshold
        if confidence < 0.3:
            return MentalState.UNKNOWN, confidence

        return best_state, min(confidence, 1.0)

    def _calculate_arousal(self, features: Dict[str, np.ndarray]) -> float:
        """Calculate arousal level (0-1)"""
        arousal = 0.5  # Default neutral

        if "beta_power" in features and "alpha_power" in features:
            beta = float(features["beta_power"].mean())
            alpha = float(features["alpha_power"].mean())
            arousal = self._sigmoid((beta - alpha) * 2)

        return arousal

    def _calculate_valence(self, features: Dict[str, np.ndarray]) -> float:
        """Calculate emotional valence (-1 to 1)"""
        valence = 0.0  # Default neutral

        if "frontal_alpha_asymmetry" in features:
            # Left frontal activation = positive valence
            asymmetry = float(features["frontal_alpha_asymmetry"].mean())
            valence = np.tanh(asymmetry * 2)

        return valence

    def _calculate_attention(self, features: Dict[str, np.ndarray]) -> float:
        """Calculate attention score (0-1)"""
        if "attention_index" in features:
            return float(np.clip(features["attention_index"].mean(), 0, 1))

        # Fallback: estimate from frequency bands
        attention = 0.5
        if "theta_power" in features and "beta_power" in features:
            theta = float(features["theta_power"].mean())
            beta = float(features["beta_power"].mean())
            # Higher theta and beta indicate focused attention
            attention = self._sigmoid(theta + beta - 0.5)

        return attention

    async def _apply_temporal_smoothing(
        self,
        state: MentalState,
        confidence: float,
        probabilities: Dict[MentalState, float],
    ) -> tuple[MentalState, float]:
        """Apply temporal smoothing to reduce state oscillations"""
        # Add to history
        self.state_history.append(
            {
                "state": state,
                "confidence": confidence,
                "probabilities": probabilities,
                "timestamp": datetime.now(),
            }
        )

        # Maintain history size
        if len(self.state_history) > self.history_size:
            self.state_history.pop(0)

        # Not enough history for smoothing
        if len(self.state_history) < 3:
            return state, confidence

        # Calculate weighted average of recent states
        state_scores = {}
        total_weight = 0.0

        for i, hist in enumerate(self.state_history):
            # More recent states get higher weight
            weight = (i + 1) / len(self.state_history)
            weight *= hist["confidence"]  # Weight by confidence

            for s, p in hist["probabilities"].items():
                if s not in state_scores:
                    state_scores[s] = 0.0
                state_scores[s] += p * weight

            total_weight += weight

        # Normalize scores
        if total_weight > 0:
            for s in state_scores:
                state_scores[s] /= total_weight

        # Determine smoothed state
        smoothed_state = max(state_scores.items(), key=lambda x: x[1])

        # Adjust confidence based on stability
        stability = self._calculate_stability()
        smoothed_confidence = smoothed_state[1] * (0.7 + 0.3 * stability)

        return smoothed_state[0], min(smoothed_confidence, 1.0)

    def _calculate_stability(self) -> float:
        """Calculate state stability over recent history"""
        if len(self.state_history) < 2:
            return 1.0

        # Count state changes
        changes = 0
        for i in range(1, len(self.state_history)):
            if self.state_history[i]["state"] != self.state_history[i - 1]["state"]:
                changes += 1

        # Stability is inverse of change rate
        stability = 1.0 - (changes / (len(self.state_history) - 1))
        return stability

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-x))

    async def load_model(self, model_path: str) -> None:
        """Load pre-trained model"""
        # In production, this would load a trained neural network
        # For now, we use threshold-based classification
        self.model_path = model_path
        logger.info(f"Model loading from {model_path} simulated")

    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Update model with user feedback"""
        # Store feedback for model retraining
        if "correct_state" in feedback:
            # Update accuracy tracking
            is_correct = feedback.get("predicted_state") == feedback["correct_state"]
            self.accuracy_buffer.append(float(is_correct))

            # Keep buffer size manageable
            if len(self.accuracy_buffer) > 1000:
                self.accuracy_buffer.pop(0)

        logger.info("Model update recorded for future retraining")

    def get_metrics(self) -> ModelMetrics:
        """Get current model performance metrics"""
        accuracy = 0.0
        if self.accuracy_buffer:
            accuracy = sum(self.accuracy_buffer) / len(self.accuracy_buffer)

        error_rate = 0.0
        if self.classification_count > 0:
            error_rate = self.error_count / self.classification_count

        return ModelMetrics(
            model_name="MentalStateClassifier",
            accuracy=accuracy,
            precision=accuracy,  # Simplified for now
            recall=accuracy,  # Simplified for now
            f1_score=accuracy,  # Simplified for now
            latency_p50=50.0,  # Target latency
            latency_p95=80.0,
            latency_p99=95.0,
            inference_count=self.classification_count,
            error_count=self.error_count,
            last_updated=datetime.now(),
        )

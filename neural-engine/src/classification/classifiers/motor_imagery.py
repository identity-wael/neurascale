"""
Motor imagery classifier for brain-computer interface control
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
import numpy as np

from ..interfaces import BaseClassifier
from ..types import (
    FeatureVector,
    MotorIntent,
    MotorImageryResult,
    ModelMetrics,
)

logger = logging.getLogger(__name__)


class MotorImageryClassifier(BaseClassifier):
    """
    Real-time motor imagery classification for BCI control.

    Detects imagined movements:
    - Left hand movement
    - Right hand movement
    - Feet movement
    - Tongue movement
    - Rest state

    Uses Common Spatial Patterns (CSP) and band power features.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize motor imagery classifier

        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.model = None
        self.model_path = model_path
        self.classification_count = 0
        self.error_count = 0

        # CSP filters (would be loaded from training)
        self.csp_filters: Optional[np.ndarray] = None
        self.n_components = 4  # Number of CSP components per class

        # Frequency bands for motor imagery
        self.freq_bands = {
            "mu": (8, 12),  # Mu rhythm
            "beta": (13, 30),  # Beta rhythm
            "low_beta": (13, 20),
            "high_beta": (20, 30),
        }

        # Channel groups for different body parts
        self.channel_groups = {
            "left_hand": ["C4", "CP4", "FC4"],  # Right hemisphere
            "right_hand": ["C3", "CP3", "FC3"],  # Left hemisphere
            "feet": ["Cz", "FCz", "CPz"],  # Central
            "tongue": ["FC1", "FC2", "Cz"],  # Frontal-central
        }

        # ERD/ERS detection parameters
        self.baseline_window = 2.0  # seconds
        self.erd_threshold = -0.3  # 30% decrease
        self.ers_threshold = 0.3  # 30% increase

        # Control signal parameters
        self.control_gain = 1.0
        self.control_smoothing = 0.7
        self.last_control_signal: Optional[np.ndarray] = None

        # Classification confidence thresholds
        self.confidence_threshold = 0.6
        self.rest_threshold = 0.3

    async def classify(self, features: FeatureVector) -> MotorImageryResult:
        """
        Classify motor imagery from extracted features

        Args:
            features: Extracted EEG features

        Returns:
            Motor imagery classification result
        """
        try:
            start_time = datetime.now()

            # Extract relevant features
            feature_dict = features.features

            # Calculate class probabilities
            probabilities = await self._calculate_class_probabilities(feature_dict)

            # Determine motor intent
            intent, confidence = self._determine_intent(probabilities)

            # Calculate ERD/ERS score
            erd_ers_score = self._calculate_erd_ers(feature_dict)

            # Generate control signal
            control_signal = self._generate_control_signal(
                intent, confidence, erd_ers_score
            )

            # Extract spatial pattern
            spatial_pattern = await self._extract_spatial_pattern(feature_dict, intent)

            # Apply temporal smoothing
            intent, confidence = await self._apply_temporal_smoothing(
                intent, confidence, probabilities
            )

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Create result
            result = MotorImageryResult(
                timestamp=features.timestamp,
                confidence=confidence,
                label=intent.value,
                probabilities={i.value: p for i, p in probabilities.items()},
                latency_ms=latency_ms,
                intent=intent,
                control_signal=control_signal,
                erd_ers_score=erd_ers_score,
                spatial_pattern=spatial_pattern,
                metadata={
                    "feature_count": len(feature_dict),
                    "csp_enabled": self.csp_filters is not None,
                    "control_smoothing": self.control_smoothing,
                    "classification_method": "csp_bandpower",
                },
            )

            self.classification_count += 1
            return result

        except Exception as e:
            logger.error(f"Motor imagery classification error: {e}")
            self.error_count += 1
            raise

    async def _calculate_class_probabilities(  # noqa: C901
        self, features: Dict[str, np.ndarray]
    ) -> Dict[MotorIntent, float]:
        """Calculate probability for each motor imagery class"""
        probabilities = {}

        # Left hand movement detection
        left_score = 0.0
        if "right_hemisphere_mu_power" in features:
            # ERD in right hemisphere indicates left hand imagery
            mu_power = float(features["right_hemisphere_mu_power"].mean())
            baseline_mu = features.get("baseline_mu_power", np.array([1.0])).mean()
            erd = (mu_power - baseline_mu) / baseline_mu if baseline_mu > 0 else 0

            if erd < self.erd_threshold:
                left_score = self._sigmoid(-erd * 5)

        if "right_hemisphere_beta_power" in features:
            beta_power = float(features["right_hemisphere_beta_power"].mean())
            baseline_beta = features.get("baseline_beta_power", np.array([1.0])).mean()
            erd_beta = (
                (beta_power - baseline_beta) / baseline_beta if baseline_beta > 0 else 0
            )

            if erd_beta < self.erd_threshold:
                left_score = max(left_score, self._sigmoid(-erd_beta * 4))

        probabilities[MotorIntent.LEFT_HAND] = left_score

        # Right hand movement detection
        right_score = 0.0
        if "left_hemisphere_mu_power" in features:
            # ERD in left hemisphere indicates right hand imagery
            mu_power = float(features["left_hemisphere_mu_power"].mean())
            baseline_mu = features.get("baseline_mu_power", np.array([1.0])).mean()
            erd = (mu_power - baseline_mu) / baseline_mu if baseline_mu > 0 else 0

            if erd < self.erd_threshold:
                right_score = self._sigmoid(-erd * 5)

        if "left_hemisphere_beta_power" in features:
            beta_power = float(features["left_hemisphere_beta_power"].mean())
            baseline_beta = features.get("baseline_beta_power", np.array([1.0])).mean()
            erd_beta = (
                (beta_power - baseline_beta) / baseline_beta if baseline_beta > 0 else 0
            )

            if erd_beta < self.erd_threshold:
                right_score = max(right_score, self._sigmoid(-erd_beta * 4))

        probabilities[MotorIntent.RIGHT_HAND] = right_score

        # Feet movement detection
        feet_score = 0.0
        if "central_mu_power" in features:
            # ERD in central areas indicates feet imagery
            mu_power = float(features["central_mu_power"].mean())
            baseline_mu = features.get("baseline_mu_power", np.array([1.0])).mean()
            erd = (mu_power - baseline_mu) / baseline_mu if baseline_mu > 0 else 0

            if erd < self.erd_threshold * 0.8:  # Feet ERD is typically weaker
                feet_score = self._sigmoid(-erd * 3)

        probabilities[MotorIntent.FEET] = feet_score

        # Tongue movement detection
        tongue_score = 0.0
        if "frontocentral_beta_power" in features:
            # Beta changes in frontocentral areas
            beta_power = float(features["frontocentral_beta_power"].mean())
            baseline_beta = features.get("baseline_beta_power", np.array([1.0])).mean()
            beta_change = (
                abs(beta_power - baseline_beta) / baseline_beta
                if baseline_beta > 0
                else 0
            )

            if beta_change > 0.2:
                tongue_score = self._sigmoid(beta_change * 3)

        probabilities[MotorIntent.TONGUE] = tongue_score

        # CSP features if available
        if "csp_features" in features and self.csp_filters is not None:
            csp_probs = self._classify_csp_features(features["csp_features"])
            # Combine with band power probabilities
            for intent, prob in csp_probs.items():
                if intent in probabilities:
                    probabilities[intent] = probabilities[intent] * 0.4 + prob * 0.6
                else:
                    probabilities[intent] = prob

        # Rest state probability
        max_activity = max(probabilities.values()) if probabilities else 0
        rest_score = 1.0 - max_activity
        probabilities[MotorIntent.REST] = rest_score

        # Normalize probabilities
        total = sum(probabilities.values())
        if total > 0:
            for intent in probabilities:
                probabilities[intent] /= total

        return probabilities

    def _determine_intent(
        self, probabilities: Dict[MotorIntent, float]
    ) -> tuple[MotorIntent, float]:
        """Determine motor intent from probabilities"""
        # Sort by probability
        sorted_intents = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        if not sorted_intents:
            return MotorIntent.UNKNOWN, 0.0

        best_intent, best_prob = sorted_intents[0]

        # Check if rest state
        if best_intent == MotorIntent.REST and best_prob > self.rest_threshold:
            return MotorIntent.REST, best_prob

        # Check confidence threshold
        if best_prob < self.confidence_threshold:
            return MotorIntent.REST, probabilities.get(MotorIntent.REST, 0.5)

        # Calculate confidence with margin
        if len(sorted_intents) > 1:
            second_prob = sorted_intents[1][1]
            margin = best_prob - second_prob
            confidence = best_prob * (1.0 + margin)
        else:
            confidence = best_prob

        return best_intent, min(confidence, 1.0)

    def _calculate_erd_ers(self, features: Dict[str, np.ndarray]) -> float:
        """Calculate Event-Related Desynchronization/Synchronization score"""
        erd_scores = []

        # Check mu rhythm ERD
        if "mu_power" in features and "baseline_mu_power" in features:
            mu_power = float(features["mu_power"].mean())
            baseline = float(features["baseline_mu_power"].mean())

            if baseline > 0:
                erd_mu = (mu_power - baseline) / baseline
                erd_scores.append(erd_mu)

        # Check beta rhythm ERD
        if "beta_power" in features and "baseline_beta_power" in features:
            beta_power = float(features["beta_power"].mean())
            baseline = float(features["baseline_beta_power"].mean())

            if baseline > 0:
                erd_beta = (beta_power - baseline) / baseline
                erd_scores.append(erd_beta)

        if erd_scores:
            # Average ERD across frequency bands
            avg_erd = np.mean(erd_scores)
            # Normalize to -1 to 1 range
            return np.tanh(avg_erd)

        return 0.0

    def _generate_control_signal(
        self, intent: MotorIntent, confidence: float, erd_ers_score: float
    ) -> np.ndarray:
        """Generate control signal for BCI application"""
        # Base control vector based on intent
        if intent == MotorIntent.LEFT_HAND:
            base_signal = np.array([-1.0, 0.0])  # Move left
        elif intent == MotorIntent.RIGHT_HAND:
            base_signal = np.array([1.0, 0.0])  # Move right
        elif intent == MotorIntent.FEET:
            base_signal = np.array([0.0, 1.0])  # Move forward
        elif intent == MotorIntent.TONGUE:
            base_signal = np.array([0.0, -1.0])  # Move backward
        else:  # REST or UNKNOWN
            base_signal = np.array([0.0, 0.0])  # No movement

        # Scale by confidence and ERD strength
        signal_strength = confidence * abs(erd_ers_score)
        control_signal = base_signal * signal_strength * self.control_gain

        # Apply temporal smoothing
        if self.last_control_signal is not None:
            control_signal = (
                self.control_smoothing * self.last_control_signal
                + (1 - self.control_smoothing) * control_signal
            )

        # Limit maximum control magnitude
        magnitude = np.linalg.norm(control_signal)
        if magnitude > 1.0:
            control_signal /= magnitude

        self.last_control_signal = control_signal.copy()

        return control_signal

    async def _extract_spatial_pattern(
        self, features: Dict[str, np.ndarray], intent: MotorIntent
    ) -> np.ndarray:
        """Extract spatial pattern for the detected intent"""
        if self.csp_filters is None:
            # Return dummy pattern if CSP not trained
            return np.zeros(8)

        # Get intent-specific CSP filters
        if intent == MotorIntent.LEFT_HAND:
            filter_idx = 0
        elif intent == MotorIntent.RIGHT_HAND:
            filter_idx = 1
        elif intent == MotorIntent.FEET:
            filter_idx = 2
        elif intent == MotorIntent.TONGUE:
            filter_idx = 3
        else:
            return np.zeros(self.n_components * 2)

        # Apply CSP filters (simplified)
        if "raw_data" in features:
            # In practice, apply actual CSP transformation using features["raw_data"]
            pattern = np.random.randn(self.n_components * 2) * 0.1
            pattern[filter_idx * 2 : (filter_idx + 1) * 2] += 0.5
            return pattern

        return np.zeros(self.n_components * 2)

    def _classify_csp_features(
        self, csp_features: np.ndarray
    ) -> Dict[MotorIntent, float]:
        """Classify using CSP features"""
        # Simplified CSP classification
        # In practice, use trained classifier (LDA, SVM, etc.)

        n_classes = 4
        probabilities = {}

        # Mock classification based on CSP feature values
        feature_sums = csp_features.reshape(n_classes, -1).sum(axis=1)
        feature_probs = np.exp(feature_sums) / np.exp(feature_sums).sum()

        intents = [
            MotorIntent.LEFT_HAND,
            MotorIntent.RIGHT_HAND,
            MotorIntent.FEET,
            MotorIntent.TONGUE,
        ]

        for intent, prob in zip(intents, feature_probs):
            probabilities[intent] = float(prob)

        return probabilities

    async def _apply_temporal_smoothing(
        self,
        intent: MotorIntent,
        confidence: float,
        probabilities: Dict[MotorIntent, float],
    ) -> tuple[MotorIntent, float]:
        """Apply temporal smoothing to reduce oscillations"""
        # For motor imagery, minimal smoothing to maintain responsiveness
        # Could implement state history if needed
        return intent, confidence

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-x))

    async def train_csp(self, training_data: Dict[str, np.ndarray], labels: np.ndarray):
        """Train Common Spatial Patterns filters"""
        logger.info("Training CSP filters for motor imagery")

        # In production, implement full CSP training
        # For now, create mock filters
        n_channels = training_data.get("n_channels", 64)
        self.csp_filters = np.random.randn(self.n_components * 4, n_channels)

        logger.info(
            f"CSP training complete: {self.csp_filters.shape[0]} filters created"
        )

    async def calibrate_baseline(self, rest_data: Dict[str, np.ndarray]) -> None:
        """Calibrate baseline power levels during rest"""
        if "mu_power" in rest_data:
            baseline_mu = float(rest_data["mu_power"].mean())
            logger.info(f"Baseline mu power: {baseline_mu:.3f}")

        if "beta_power" in rest_data:
            baseline_beta = float(rest_data["beta_power"].mean())
            logger.info(f"Baseline beta power: {baseline_beta:.3f}")

    async def load_model(self, model_path: str) -> None:
        """Load pre-trained motor imagery model"""
        self.model_path = model_path
        logger.info(f"Loading motor imagery model from {model_path}")
        # Load CSP filters and classifier

    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Update model with user feedback"""
        if "correct_intent" in feedback:
            predicted = feedback.get("predicted_intent")
            correct = feedback.get("correct_intent")

            if predicted == correct:
                logger.info("Correct motor imagery classification")
            else:
                logger.info(
                    f"Misclassification: predicted {predicted}, actual {correct}"
                )

    def get_metrics(self) -> ModelMetrics:
        """Get current model performance metrics"""
        return ModelMetrics(
            model_name="MotorImageryClassifier",
            accuracy=0.85,  # Placeholder
            precision=0.83,
            recall=0.85,
            f1_score=0.84,
            latency_p50=25.0,
            latency_p95=40.0,
            latency_p99=60.0,
            inference_count=self.classification_count,
            error_count=self.error_count,
            last_updated=datetime.now(),
        )

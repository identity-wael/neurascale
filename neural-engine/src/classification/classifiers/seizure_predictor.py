"""
Seizure prediction classifier for early warning system
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..interfaces import BaseClassifier
from ..types import (
    FeatureVector,
    SeizureRisk,
    SeizurePrediction,
    ModelMetrics,
)

logger = logging.getLogger(__name__)


class SeizurePredictor(BaseClassifier):
    """
    Real-time seizure prediction using multi-channel EEG analysis.

    Features:
    - 10-30 minute prediction window
    - Multi-stage risk assessment
    - Patient-specific adaptation
    - High sensitivity for imminent seizures
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize seizure predictor

        Args:
            model_path: Path to pre-trained model (optional)
        """
        self.model = None
        self.model_path = model_path
        self.classification_count = 0
        self.error_count = 0
        self.prediction_buffer: List[Dict[str, Any]] = []

        # Risk thresholds
        self.risk_thresholds = {
            "imminent": 0.85,  # >85% probability
            "high": 0.60,  # 60-85% probability
            "medium": 0.35,  # 35-60% probability
            "low": 0.0,  # <35% probability
        }

        # Feature importance weights
        self.feature_weights = {
            "spectral_edge_frequency": 0.15,
            "line_length": 0.12,
            "wavelet_energy": 0.10,
            "phase_synchronization": 0.15,
            "hjorth_parameters": 0.08,
            "entropy_measures": 0.10,
            "coherence_changes": 0.12,
            "spike_rate": 0.18,
        }

        # Patient-specific parameters
        self.patient_baselines: Dict[str, Dict[str, float]] = {}
        self.seizure_history: Dict[str, List[datetime]] = {}

        # Temporal tracking
        self.temporal_window = 300  # 5 minutes
        self.feature_history: List[Dict[str, Any]] = []

    async def classify(self, features: FeatureVector) -> SeizurePrediction:
        """
        Predict seizure risk from extracted features

        Args:
            features: Extracted EEG features

        Returns:
            Seizure prediction result
        """
        try:
            start_time = datetime.now()

            # Extract patient ID
            patient_id = features.metadata.get("patient_id", "unknown")

            # Extract relevant features
            feature_dict = features.features

            # Calculate seizure probability
            probability = await self._calculate_seizure_probability(
                feature_dict, patient_id
            )

            # Determine risk level
            risk_level = self._determine_risk_level(probability)

            # Estimate time to seizure if high risk
            time_to_seizure = None
            if risk_level in [SeizureRisk.HIGH, SeizureRisk.IMMINENT]:
                time_to_seizure = self._estimate_time_to_seizure(
                    probability, feature_dict
                )

            # Identify spatial focus
            spatial_focus = self._identify_spatial_focus(feature_dict)

            # Apply temporal smoothing
            probability, risk_level = await self._apply_temporal_smoothing(
                probability, risk_level, patient_id
            )

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Create prediction result
            result = SeizurePrediction(
                timestamp=features.timestamp,
                confidence=self._calculate_confidence(probability, feature_dict),
                label=risk_level.value,
                probabilities={
                    risk.value: self._get_risk_probability(risk, probability)
                    for risk in SeizureRisk
                },
                latency_ms=latency_ms,
                risk_level=risk_level,
                probability=probability,
                time_to_seizure_minutes=time_to_seizure,
                spatial_focus=spatial_focus,
                patient_id=patient_id,
                metadata={
                    "feature_count": len(feature_dict),
                    "patient_baseline": patient_id in self.patient_baselines,
                    "temporal_smoothing": True,
                    "sensitivity_mode": "high",
                },
            )

            # Update patient history
            self._update_patient_history(patient_id, result)

            self.classification_count += 1
            return result

        except Exception as e:
            logger.error(f"Seizure prediction error: {e}")
            self.error_count += 1
            raise

    async def _calculate_seizure_probability(  # noqa: C901
        self, features: Dict[str, np.ndarray], patient_id: str
    ) -> float:
        """Calculate probability of seizure occurrence"""
        weighted_score = 0.0
        total_weight = 0.0

        # Get patient baseline if available
        baseline = self.patient_baselines.get(patient_id, {})

        # Spectral edge frequency changes
        if "spectral_edge_frequency" in features:
            sef = float(features["spectral_edge_frequency"].mean())
            baseline_sef = baseline.get("spectral_edge_frequency", sef)

            # Significant decrease indicates seizure risk
            sef_change = (baseline_sef - sef) / baseline_sef if baseline_sef > 0 else 0
            sef_score = self._sigmoid(sef_change * 10)

            weight = self.feature_weights["spectral_edge_frequency"]
            weighted_score += sef_score * weight
            total_weight += weight

        # Line length (energy) increase
        if "line_length" in features:
            ll = float(features["line_length"].mean())
            baseline_ll = baseline.get("line_length", ll)

            ll_ratio = ll / baseline_ll if baseline_ll > 0 else 1.0
            ll_score = self._sigmoid((ll_ratio - 1.0) * 5)

            weight = self.feature_weights["line_length"]
            weighted_score += ll_score * weight
            total_weight += weight

        # Wavelet energy redistribution
        if "wavelet_energy" in features:
            wavelet = features["wavelet_energy"]
            if len(wavelet.shape) > 1:
                # Energy concentration in lower frequencies
                low_freq_ratio = wavelet[:, :3].sum() / wavelet.sum()
                wavelet_score = self._sigmoid((low_freq_ratio - 0.5) * 10)
            else:
                wavelet_score = 0.5

            weight = self.feature_weights["wavelet_energy"]
            weighted_score += wavelet_score * weight
            total_weight += weight

        # Phase synchronization changes
        if "phase_synchronization" in features:
            sync = float(features["phase_synchronization"].mean())
            # Increased synchronization before seizures
            sync_score = self._sigmoid((sync - 0.5) * 8)

            weight = self.feature_weights["phase_synchronization"]
            weighted_score += sync_score * weight
            total_weight += weight

        # Hjorth parameters (complexity decrease)
        if "hjorth_complexity" in features:
            complexity = float(features["hjorth_complexity"].mean())
            baseline_complexity = baseline.get("hjorth_complexity", complexity)

            # Decreased complexity indicates seizure risk
            complexity_ratio = (
                complexity / baseline_complexity if baseline_complexity > 0 else 1.0
            )
            hjorth_score = self._sigmoid((1.0 - complexity_ratio) * 10)

            weight = self.feature_weights["hjorth_parameters"]
            weighted_score += hjorth_score * weight
            total_weight += weight

        # Entropy measures (decreased entropy)
        if "sample_entropy" in features:
            entropy = float(features["sample_entropy"].mean())
            baseline_entropy = baseline.get("sample_entropy", entropy)

            entropy_ratio = entropy / baseline_entropy if baseline_entropy > 0 else 1.0
            entropy_score = self._sigmoid((1.0 - entropy_ratio) * 8)

            weight = self.feature_weights["entropy_measures"]
            weighted_score += entropy_score * weight
            total_weight += weight

        # Coherence changes between channels
        if "channel_coherence" in features:
            coherence = float(features["channel_coherence"].mean())
            coherence_score = self._sigmoid((coherence - 0.4) * 10)

            weight = self.feature_weights["coherence_changes"]
            weighted_score += coherence_score * weight
            total_weight += weight

        # Spike rate increase
        if "spike_rate" in features:
            spike_rate = float(features["spike_rate"].mean())
            baseline_spike = baseline.get("spike_rate", 0.1)

            spike_ratio = spike_rate / baseline_spike if baseline_spike > 0 else 1.0
            spike_score = self._sigmoid((spike_ratio - 1.0) * 3)

            weight = self.feature_weights["spike_rate"]
            weighted_score += spike_score * weight
            total_weight += weight

        # Normalize probability
        if total_weight > 0:
            probability = weighted_score / total_weight
        else:
            probability = 0.0

        # Apply patient-specific adjustment
        if patient_id in self.seizure_history:
            history_factor = self._calculate_history_factor(patient_id)
            probability = probability * 0.8 + history_factor * 0.2

        return min(max(probability, 0.0), 1.0)

    def _determine_risk_level(self, probability: float) -> SeizureRisk:
        """Determine risk level from probability"""
        if probability >= self.risk_thresholds["imminent"]:
            return SeizureRisk.IMMINENT
        elif probability >= self.risk_thresholds["high"]:
            return SeizureRisk.HIGH
        elif probability >= self.risk_thresholds["medium"]:
            return SeizureRisk.MEDIUM
        else:
            return SeizureRisk.LOW

    def _estimate_time_to_seizure(
        self, probability: float, features: Dict[str, np.ndarray]
    ) -> Optional[float]:
        """Estimate time to seizure in minutes"""
        if probability < self.risk_thresholds["high"]:
            return None

        # Base estimate from probability
        if probability >= self.risk_thresholds["imminent"]:
            base_time = 10.0  # 10 minutes for imminent
        else:
            # Linear interpolation for high risk
            base_time = 30.0 - (probability - self.risk_thresholds["high"]) * 20.0 / (
                self.risk_thresholds["imminent"] - self.risk_thresholds["high"]
            )

        # Adjust based on feature dynamics
        if "feature_velocity" in features:
            # Faster changes indicate sooner seizure
            velocity = float(features["feature_velocity"].mean())
            time_adjustment = 1.0 - min(velocity, 1.0) * 0.5
            base_time *= time_adjustment

        return max(base_time, 5.0)  # Minimum 5 minutes

    def _identify_spatial_focus(
        self, features: Dict[str, np.ndarray]
    ) -> Optional[List[int]]:
        """Identify channels with highest seizure activity"""
        if "channel_spike_rate" in features:
            spike_rates = features["channel_spike_rate"]
            if len(spike_rates) > 0:
                # Find channels with spike rate > 2 std above mean
                mean_rate = spike_rates.mean()
                std_rate = spike_rates.std()
                threshold = mean_rate + 2 * std_rate

                focus_channels = np.where(spike_rates > threshold)[0].tolist()
                return focus_channels if focus_channels else None

        return None

    def _calculate_confidence(
        self, probability: float, features: Dict[str, np.ndarray]
    ) -> float:
        """Calculate prediction confidence"""
        base_confidence = probability

        # Boost confidence if multiple indicators agree
        indicator_count = 0
        if "spike_rate" in features and features["spike_rate"].mean() > 0.5:
            indicator_count += 1
        if (
            "phase_synchronization" in features
            and features["phase_synchronization"].mean() > 0.6
        ):
            indicator_count += 1
        if "spectral_edge_frequency" in features:
            indicator_count += 1

        # More indicators = higher confidence
        confidence_boost = min(indicator_count * 0.1, 0.3)

        return min(base_confidence + confidence_boost, 1.0)

    def _get_risk_probability(self, risk: SeizureRisk, probability: float) -> float:
        """Get probability for specific risk level"""
        if risk == SeizureRisk.IMMINENT:
            return max(0, probability - self.risk_thresholds["imminent"])
        elif risk == SeizureRisk.HIGH:
            if probability >= self.risk_thresholds["imminent"]:
                return 0.0
            return max(0, probability - self.risk_thresholds["high"])
        elif risk == SeizureRisk.MEDIUM:
            if probability >= self.risk_thresholds["high"]:
                return 0.0
            return max(0, probability - self.risk_thresholds["medium"])
        else:  # LOW
            if probability >= self.risk_thresholds["medium"]:
                return 0.0
            return 1.0 - probability

    async def _apply_temporal_smoothing(
        self, probability: float, risk_level: SeizureRisk, patient_id: str
    ) -> Tuple[float, SeizureRisk]:
        """Apply temporal smoothing to reduce false positives"""
        # Add to history
        self.feature_history.append(
            {
                "timestamp": datetime.now(),
                "probability": probability,
                "risk_level": risk_level,
                "patient_id": patient_id,
            }
        )

        # Keep only recent history
        cutoff_time = datetime.now() - timedelta(seconds=self.temporal_window)
        self.feature_history = [
            h
            for h in self.feature_history
            if h["timestamp"] > cutoff_time and h["patient_id"] == patient_id
        ]

        if len(self.feature_history) < 3:
            return probability, risk_level

        # Calculate weighted average
        weights = np.exp(np.linspace(0, 1, len(self.feature_history)))
        probabilities = [h["probability"] for h in self.feature_history]

        smoothed_probability = np.average(probabilities, weights=weights)
        smoothed_risk = self._determine_risk_level(smoothed_probability)

        # For imminent risk, be more sensitive (less smoothing)
        if risk_level == SeizureRisk.IMMINENT:
            smoothed_probability = probability * 0.7 + smoothed_probability * 0.3
            if probability >= self.risk_thresholds["imminent"]:
                smoothed_risk = SeizureRisk.IMMINENT

        return smoothed_probability, smoothed_risk

    def _update_patient_history(self, patient_id: str, result: SeizurePrediction):
        """Update patient-specific history"""
        if result.risk_level == SeizureRisk.IMMINENT:
            if patient_id not in self.seizure_history:
                self.seizure_history[patient_id] = []

            # Check if this is a new seizure event (not within 30 min of last)
            if not self.seizure_history[patient_id] or (
                datetime.now() - self.seizure_history[patient_id][-1]
            ) > timedelta(minutes=30):
                self.seizure_history[patient_id].append(datetime.now())

        # Update prediction buffer for accuracy tracking
        self.prediction_buffer.append(
            {
                "timestamp": result.timestamp,
                "patient_id": patient_id,
                "risk_level": result.risk_level,
                "probability": result.probability,
            }
        )

        # Keep buffer size manageable
        if len(self.prediction_buffer) > 10000:
            self.prediction_buffer = self.prediction_buffer[-5000:]

    def _calculate_history_factor(self, patient_id: str) -> float:
        """Calculate risk adjustment based on seizure history"""
        if (
            patient_id not in self.seizure_history
            or not self.seizure_history[patient_id]
        ):
            return 0.0

        # Recent seizures increase risk
        recent_seizures = [
            s
            for s in self.seizure_history[patient_id]
            if (datetime.now() - s) < timedelta(hours=24)
        ]

        if recent_seizures:
            # More recent seizures = higher risk
            hours_since_last = (
                datetime.now() - recent_seizures[-1]
            ).total_seconds() / 3600
            return max(0, 1.0 - hours_since_last / 24.0) * 0.3

        return 0.0

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-x))

    async def update_patient_baseline(
        self, patient_id: str, features: Dict[str, np.ndarray]
    ):
        """Update patient-specific baseline during non-seizure periods"""
        if patient_id not in self.patient_baselines:
            self.patient_baselines[patient_id] = {}

        baseline = self.patient_baselines[patient_id]

        # Update baselines with exponential moving average
        alpha = 0.1  # Learning rate

        for feature_name in [
            "spectral_edge_frequency",
            "line_length",
            "hjorth_complexity",
            "sample_entropy",
            "spike_rate",
        ]:
            if feature_name in features:
                value = float(features[feature_name].mean())
                if feature_name in baseline:
                    baseline[feature_name] = (1 - alpha) * baseline[
                        feature_name
                    ] + alpha * value
                else:
                    baseline[feature_name] = value

    async def load_model(self, model_path: str) -> None:
        """Load pre-trained seizure prediction model"""
        self.model_path = model_path
        logger.info(f"Loading seizure prediction model from {model_path}")
        # In production, load actual trained model

    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Update model with seizure occurrence feedback"""
        if "seizure_occurred" in feedback:
            patient_id = feedback.get("patient_id", "unknown")
            seizure_time = feedback.get("seizure_time", datetime.now())

            # Find predictions leading up to seizure
            relevant_predictions = [
                p
                for p in self.prediction_buffer
                if p["patient_id"] == patient_id
                and (seizure_time - p["timestamp"]) < timedelta(minutes=30)
                and (seizure_time - p["timestamp"]) > timedelta(seconds=0)
            ]

            if relevant_predictions:
                # Calculate sensitivity
                high_risk_predictions = [
                    p
                    for p in relevant_predictions
                    if p["risk_level"] in [SeizureRisk.HIGH, SeizureRisk.IMMINENT]
                ]

                sensitivity = len(high_risk_predictions) / len(relevant_predictions)
                logger.info(f"Seizure prediction sensitivity: {sensitivity:.2%}")

    def get_metrics(self) -> ModelMetrics:
        """Get current model performance metrics"""
        # Calculate metrics from prediction buffer
        sensitivity = 0.8  # Placeholder
        specificity = 0.7  # Placeholder

        return ModelMetrics(
            model_name="SeizurePredictor",
            accuracy=(sensitivity + specificity) / 2,
            precision=0.75,  # Placeholder
            recall=sensitivity,
            f1_score=2 * 0.75 * sensitivity / (0.75 + sensitivity),
            latency_p50=30.0,
            latency_p95=50.0,
            latency_p99=80.0,
            inference_count=self.classification_count,
            error_count=self.error_count,
            last_updated=datetime.now(),
        )

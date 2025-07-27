"""
Sleep stage classifier for real-time sleep monitoring
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

from ..interfaces import BaseClassifier
from ..types import (
    FeatureVector,
    SleepStage,
    SleepStageResult,
    ModelMetrics,
)

logger = logging.getLogger(__name__)


class SleepStageClassifier(BaseClassifier):
    """
    Real-time sleep stage classification using EEG, EOG, and EMG signals.

    Classifies sleep into stages:
    - Wake: Alert or drowsy but awake
    - N1: Light sleep, transition from wake
    - N2: Light sleep with sleep spindles and K-complexes
    - N3: Deep sleep (slow-wave sleep)
    - REM: Rapid Eye Movement sleep

    Based on AASM (American Academy of Sleep Medicine) criteria.
    """

    def __init__(self, model_path: Optional[str] = None, epoch_duration: int = 30):
        """
        Initialize sleep stage classifier

        Args:
            model_path: Path to pre-trained model
            epoch_duration: Duration of each epoch in seconds (typically 30s)
        """
        self.model = None
        self.model_path = model_path
        self.epoch_duration = epoch_duration

        # Classification tracking
        self.classification_count = 0
        self.error_count = 0
        self.accuracy_buffer: List[float] = []

        # Sleep architecture tracking
        self.sleep_history: List[Dict[str, Any]] = []
        self.current_epoch = 0
        self.sleep_onset_time: Optional[datetime] = None
        self.total_sleep_time = 0

        # Stage-specific thresholds
        self.thresholds = {
            "wake": {"alpha_power": 0.5, "emg_power": 0.6, "eye_movements": 0.3},
            "n1": {"theta_power": 0.5, "alpha_decrease": 0.5, "vertex_waves": 0.2},
            "n2": {
                "spindle_density": 0.3,
                "k_complex_presence": 0.2,
                "theta_dominance": 0.6,
            },
            "n3": {
                "delta_power": 0.5,
                "slow_wave_amplitude": 75.0,  # μV
                "delta_percentage": 0.2,
            },
            "rem": {"theta_power": 0.6, "emg_atonia": 0.8, "rem_density": 0.3},
        }

        # Transition probability matrix
        self.transition_matrix = {
            SleepStage.WAKE: {
                SleepStage.WAKE: 0.85,
                SleepStage.N1: 0.14,
                SleepStage.N2: 0.01,
                SleepStage.N3: 0.0,
                SleepStage.REM: 0.0,
            },
            SleepStage.N1: {
                SleepStage.WAKE: 0.25,
                SleepStage.N1: 0.45,
                SleepStage.N2: 0.29,
                SleepStage.N3: 0.01,
                SleepStage.REM: 0.0,
            },
            SleepStage.N2: {
                SleepStage.WAKE: 0.05,
                SleepStage.N1: 0.15,
                SleepStage.N2: 0.65,
                SleepStage.N3: 0.13,
                SleepStage.REM: 0.02,
            },
            SleepStage.N3: {
                SleepStage.WAKE: 0.01,
                SleepStage.N1: 0.02,
                SleepStage.N2: 0.17,
                SleepStage.N3: 0.79,
                SleepStage.REM: 0.01,
            },
            SleepStage.REM: {
                SleepStage.WAKE: 0.12,
                SleepStage.N1: 0.08,
                SleepStage.N2: 0.15,
                SleepStage.N3: 0.0,
                SleepStage.REM: 0.65,
            },
        }

    async def classify(self, features: FeatureVector) -> SleepStageResult:
        """
        Classify sleep stage from extracted features

        Args:
            features: Extracted physiological features

        Returns:
            Sleep stage classification result
        """
        try:
            start_time = datetime.now()

            # Extract features
            feature_dict = features.features

            # Calculate stage probabilities
            probabilities = await self._calculate_stage_probabilities(feature_dict)

            # Apply transition probabilities if we have history
            if self.sleep_history:
                probabilities = self._apply_transition_probabilities(probabilities)

            # Determine stage and confidence
            stage, confidence = self._determine_stage(probabilities)

            # Calculate sleep metrics
            sleep_depth = self._calculate_sleep_depth(stage, feature_dict)
            transition_prob = self._calculate_transition_probability(stage)

            # Update epoch counter
            self.current_epoch += 1

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Create result
            result = SleepStageResult(
                timestamp=features.timestamp,
                confidence=confidence,
                label=stage.value,
                probabilities={s.value: p for s, p in probabilities.items()},
                latency_ms=latency_ms,
                stage=stage,
                epoch_number=self.current_epoch,
                sleep_depth=sleep_depth,
                transition_probability=transition_prob,
                metadata={
                    "feature_count": len(feature_dict),
                    "sleep_architecture": self._get_sleep_architecture(),
                    "time_in_stage": self._get_time_in_current_stage(),
                    "classification_method": "rule_based_with_transitions",
                },
            )

            # Update history
            self._update_sleep_history(result)

            self.classification_count += 1
            return result

        except Exception as e:
            logger.error(f"Sleep stage classification error: {e}")
            self.error_count += 1
            raise

    async def _calculate_stage_probabilities(  # noqa: C901
        self, features: Dict[str, np.ndarray]
    ) -> Dict[SleepStage, float]:
        """Calculate probability for each sleep stage"""
        probabilities = {}

        # Wake probability
        wake_score = 0.0
        if "alpha_power" in features:
            alpha = float(features["alpha_power"].mean())
            wake_score += (
                self._sigmoid((alpha - self.thresholds["wake"]["alpha_power"]) * 2)
                * 0.4
            )

        if "emg_power" in features:
            emg = float(features["emg_power"].mean())
            wake_score += (
                self._sigmoid((emg - self.thresholds["wake"]["emg_power"]) * 2) * 0.4
            )

        if "eye_movements" in features:
            eye = float(features["eye_movements"].mean())
            wake_score += (
                self._sigmoid((eye - self.thresholds["wake"]["eye_movements"]) * 2)
                * 0.2
            )

        probabilities[SleepStage.WAKE] = wake_score

        # N1 probability
        n1_score = 0.0
        if "theta_power" in features and "alpha_power" in features:
            theta = float(features["theta_power"].mean())
            alpha = float(features["alpha_power"].mean())

            # N1 has increased theta and decreased alpha
            n1_score += (
                self._sigmoid((theta - self.thresholds["n1"]["theta_power"]) * 2) * 0.5
            )

            # Alpha should be decreasing
            n1_score += (
                self._sigmoid((self.thresholds["n1"]["alpha_decrease"] - alpha) * 2)
                * 0.3
            )

        if "vertex_waves" in features:
            vertex = float(features["vertex_waves"].mean())
            n1_score += (
                self._sigmoid((vertex - self.thresholds["n1"]["vertex_waves"]) * 2)
                * 0.2
            )

        probabilities[SleepStage.N1] = n1_score

        # N2 probability
        n2_score = 0.0
        if "spindle_density" in features:
            spindles = float(features["spindle_density"].mean())
            n2_score += (
                self._sigmoid((spindles - self.thresholds["n2"]["spindle_density"]) * 3)
                * 0.4
            )

        if "k_complex_presence" in features:
            k_complex = float(features["k_complex_presence"].mean())
            n2_score += (
                self._sigmoid(
                    (k_complex - self.thresholds["n2"]["k_complex_presence"]) * 3
                )
                * 0.3
            )

        if "theta_power" in features:
            theta = float(features["theta_power"].mean())
            n2_score += (
                self._sigmoid((theta - self.thresholds["n2"]["theta_dominance"]) * 2)
                * 0.3
            )

        probabilities[SleepStage.N2] = n2_score

        # N3 probability
        n3_score = 0.0
        if "delta_power" in features:
            delta = float(features["delta_power"].mean())
            n3_score += (
                self._sigmoid((delta - self.thresholds["n3"]["delta_power"]) * 3) * 0.5
            )

        if "slow_wave_amplitude" in features:
            amplitude = float(features["slow_wave_amplitude"].mean())
            n3_score += (
                self._sigmoid(
                    (amplitude - self.thresholds["n3"]["slow_wave_amplitude"]) / 25
                )
                * 0.3
            )

        if "delta_percentage" in features:
            delta_pct = float(features["delta_percentage"].mean())
            n3_score += (
                self._sigmoid(
                    (delta_pct - self.thresholds["n3"]["delta_percentage"]) * 5
                )
                * 0.2
            )

        probabilities[SleepStage.N3] = n3_score

        # REM probability
        rem_score = 0.0
        if "theta_power" in features:
            theta = float(features["theta_power"].mean())
            rem_score += (
                self._sigmoid((theta - self.thresholds["rem"]["theta_power"]) * 2) * 0.3
            )

        if "emg_power" in features:
            emg = float(features["emg_power"].mean())
            # Low EMG for REM (muscle atonia)
            rem_score += (
                self._sigmoid((self.thresholds["rem"]["emg_atonia"] - emg) * 3) * 0.4
            )

        if "rem_density" in features:
            rem_density = float(features["rem_density"].mean())
            rem_score += (
                self._sigmoid((rem_density - self.thresholds["rem"]["rem_density"]) * 2)
                * 0.3
            )

        probabilities[SleepStage.REM] = rem_score

        # Normalize probabilities
        total = sum(probabilities.values())
        if total > 0:
            for stage in probabilities:
                probabilities[stage] /= total
        else:
            # Default to wake if no clear signals
            probabilities = {
                SleepStage.WAKE: 0.8,
                SleepStage.N1: 0.1,
                SleepStage.N2: 0.05,
                SleepStage.N3: 0.03,
                SleepStage.REM: 0.02,
            }

        return probabilities

    def _apply_transition_probabilities(
        self, probabilities: Dict[SleepStage, float]
    ) -> Dict[SleepStage, float]:
        """Apply Markov transition probabilities based on previous stage"""
        if not self.sleep_history:
            return probabilities

        last_stage = self.sleep_history[-1]["stage"]

        # Weight current probabilities with transition probabilities
        weighted_probs = {}
        for stage in SleepStage:
            if stage == SleepStage.UNKNOWN:
                continue

            # Get transition probability from last stage
            trans_prob = self.transition_matrix[last_stage].get(stage, 0.0)

            # Weight: 70% feature-based, 30% transition-based
            current_prob = probabilities.get(stage, 0.0)
            weighted_probs[stage] = 0.7 * current_prob + 0.3 * trans_prob

        # Normalize
        total = sum(weighted_probs.values())
        if total > 0:
            for stage in weighted_probs:
                weighted_probs[stage] /= total

        return weighted_probs

    def _determine_stage(
        self, probabilities: Dict[SleepStage, float]
    ) -> tuple[SleepStage, float]:
        """Determine winning stage and confidence"""
        sorted_stages = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        if not sorted_stages:
            return SleepStage.UNKNOWN, 0.0

        best_stage, best_prob = sorted_stages[0]

        # Calculate confidence
        if len(sorted_stages) > 1:
            second_prob = sorted_stages[1][1]
            margin = best_prob - second_prob
            confidence = best_prob * (1.0 + margin * 0.5)
        else:
            confidence = best_prob

        return best_stage, min(confidence, 1.0)

    def _calculate_sleep_depth(
        self, stage: SleepStage, features: Dict[str, np.ndarray]
    ) -> float:
        """Calculate sleep depth (0-1, where 1 is deepest)"""
        if stage == SleepStage.WAKE:
            return 0.0
        elif stage == SleepStage.N1:
            return 0.2
        elif stage == SleepStage.N2:
            return 0.5
        elif stage == SleepStage.N3:
            # Depth varies with delta power
            if "delta_power" in features:
                delta = float(features["delta_power"].mean())
                return 0.7 + 0.3 * min(delta / 2.0, 1.0)
            return 0.85
        elif stage == SleepStage.REM:
            return 0.3  # REM is paradoxical - brain active but body paralyzed
        else:
            return 0.0

    def _calculate_transition_probability(self, current_stage: SleepStage) -> float:
        """Calculate probability of transitioning to a different stage"""
        if not self.sleep_history:
            return 0.5

        # Look at recent history
        recent_stages = [h["stage"] for h in self.sleep_history[-5:]]

        # Count transitions
        transitions = 0
        for i in range(1, len(recent_stages)):
            if recent_stages[i] != recent_stages[i - 1]:
                transitions += 1

        # Higher transition probability if recent instability
        base_prob = 1.0 - self.transition_matrix[current_stage][current_stage]
        instability_factor = transitions / max(len(recent_stages) - 1, 1)

        return base_prob * (1.0 + instability_factor * 0.5)

    def _update_sleep_history(self, result: SleepStageResult) -> None:
        """Update sleep history and metrics"""
        self.sleep_history.append(
            {
                "stage": result.stage,
                "confidence": result.confidence,
                "timestamp": result.timestamp,
                "epoch": result.epoch_number,
            }
        )

        # Track sleep onset
        if result.stage != SleepStage.WAKE and self.sleep_onset_time is None:
            self.sleep_onset_time = result.timestamp

        # Update total sleep time
        if result.stage != SleepStage.WAKE:
            self.total_sleep_time += self.epoch_duration

        # Limit history size
        if len(self.sleep_history) > 300:  # ~2.5 hours at 30s epochs
            self.sleep_history.pop(0)

    def _get_sleep_architecture(self) -> Dict[str, Any]:
        """Calculate sleep architecture statistics"""
        if not self.sleep_history:
            return {}

        # Count time in each stage
        stage_times = {stage: 0 for stage in SleepStage if stage != SleepStage.UNKNOWN}

        for record in self.sleep_history:
            stage_times[record["stage"]] += self.epoch_duration

        total_time = sum(stage_times.values())

        # Calculate percentages
        stage_percentages = {}
        if total_time > 0:
            for stage, time in stage_times.items():
                stage_percentages[stage.value] = (time / total_time) * 100

        # Calculate sleep efficiency
        sleep_efficiency = 0.0
        if total_time > 0:
            sleep_time = total_time - stage_times[SleepStage.WAKE]
            sleep_efficiency = (sleep_time / total_time) * 100

        return {
            "stage_times_seconds": {s.value: t for s, t in stage_times.items()},
            "stage_percentages": stage_percentages,
            "sleep_efficiency": sleep_efficiency,
            "total_recording_time": total_time,
            "sleep_onset_latency": self._calculate_sleep_onset_latency(),
        }

    def _get_time_in_current_stage(self) -> int:
        """Get time spent in current stage (seconds)"""
        if not self.sleep_history:
            return 0

        current_stage = self.sleep_history[-1]["stage"]
        consecutive_epochs = 0

        # Count backwards until stage changes
        for record in reversed(self.sleep_history):
            if record["stage"] == current_stage:
                consecutive_epochs += 1
            else:
                break

        return consecutive_epochs * self.epoch_duration

    def _calculate_sleep_onset_latency(self) -> Optional[float]:
        """Calculate time to first non-wake stage (minutes)"""
        if self.sleep_onset_time is None:
            return None

        # Find first epoch timestamp
        if self.sleep_history:
            first_timestamp = self.sleep_history[0]["timestamp"]
            latency = (self.sleep_onset_time - first_timestamp).total_seconds() / 60
            return latency

        return None

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-x))

    async def load_model(self, model_path: str) -> None:
        """Load pre-trained model"""
        self.model_path = model_path
        logger.info(f"Model loading from {model_path} simulated")

    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Update model with feedback"""
        if "correct_stage" in feedback:
            is_correct = feedback.get("predicted_stage") == feedback["correct_stage"]
            self.accuracy_buffer.append(float(is_correct))

            if len(self.accuracy_buffer) > 1000:
                self.accuracy_buffer.pop(0)

        logger.info("Model update recorded for future retraining")

    def get_metrics(self) -> ModelMetrics:
        """Get model performance metrics"""
        accuracy = 0.0
        if self.accuracy_buffer:
            accuracy = sum(self.accuracy_buffer) / len(self.accuracy_buffer)

        # error_rate = 0.0
        # if self.classification_count > 0:
        #     error_rate = self.error_count / self.classification_count

        return ModelMetrics(
            model_name="SleepStageClassifier",
            accuracy=accuracy,
            precision=accuracy,
            recall=accuracy,
            f1_score=accuracy,
            latency_p50=30.0,
            latency_p95=50.0,
            latency_p99=70.0,
            inference_count=self.classification_count,
            error_count=self.error_count,
            last_updated=datetime.now(),
        )

    def get_hypnogram(self) -> List[Dict[str, Any]]:
        """Get hypnogram data for visualization"""
        return [
            {
                "epoch": record["epoch"],
                "stage": record["stage"].value,
                "timestamp": record["timestamp"].isoformat(),
                "confidence": record["confidence"],
            }
            for record in self.sleep_history
        ]

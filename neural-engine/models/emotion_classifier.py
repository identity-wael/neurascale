"""Emotion classification models for neural signals."""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# import torch  # Unused import
# import torch.nn as nn  # Unused import
from typing import Dict, Optional, Tuple, List, Any
import logging

from .base_models import TensorFlowBaseModel

logger = logging.getLogger(__name__)


class EmotionClassifier(TensorFlowBaseModel):
    """Deep learning model for emotion classification from neural signals."""

    # Emotion categories based on dimensional model
    EMOTION_CATEGORIES = {
        "valence_arousal": 4,  # High / Low Valence × High / Low Arousal
        "basic_emotions": 7,  # Happy, Sad, Angry, Fear, Surprise, Disgust, Neutral
        "complex_emotions": 15,  # Extended emotion set
    }

    def __init__(
        self,
        n_channels: int,
        n_samples: int,
        emotion_model: str = "basic_emotions",
        **kwargs: Any,
    ) -> None:
        """
        Initialize emotion classifier.

        Args:
            n_channels: Number of neural recording channels
            n_samples: Number of time samples per window
            emotion_model: Type of emotion model ('valence_arousal', 'basic_emotions', 'complex_emotions')
        """
        n_classes = self.EMOTION_CATEGORIES.get(emotion_model, 7)

        super().__init__(
            model_name="EmotionClassifier",
            input_shape=(n_samples, n_channels),
            output_shape=n_classes,
            config=kwargs,
        )
        self.n_channels = n_channels
        self.n_samples = n_samples
        self.n_classes = n_classes
        self.emotion_model = emotion_model

    def build_model(self) -> keras.Model:
        """Build emotion classification architecture with multi - scale feature extraction."""
        # Parameters
        dropout_rate = self.config.get("dropout_rate", 0.4)
        use_spatial_attention = self.config.get("use_spatial_attention", True)

        # Input layer
        inputs = keras.Input(shape=self.input_shape)

        # Multi - scale temporal convolutions
        conv_outputs = []
        kernel_sizes = [3, 7, 15]  # Different temporal scales

        for kernel_size in kernel_sizes:
            # Branch for each kernel size
            conv = layers.Conv1D(64, kernel_size, padding="same", activation="relu")(
                inputs
            )
            conv = layers.BatchNormalization()(conv)
            conv = layers.MaxPooling1D(2)(conv)
            conv = layers.Conv1D(128, kernel_size, padding="same", activation="relu")(
                conv
            )
            conv = layers.BatchNormalization()(conv)
            conv = layers.GlobalMaxPooling1D()(conv)
            conv_outputs.append(conv)

        # Concatenate multi - scale features
        concatenated = layers.Concatenate()(conv_outputs)

        # Spatial attention mechanism for channel selection
        if use_spatial_attention:
            # Create attention weights for channels
            attention = layers.Dense(self.n_channels, activation="sigmoid")(
                concatenated
            )
            attention = layers.Reshape((1, self.n_channels))(attention)

            # Apply attention to input
            attended_input = layers.Multiply()([inputs, attention])

            # Process attended features
            attended_features = layers.Conv1D(
                256, 5, padding="same", activation="relu"
            )(attended_input)
            attended_features = layers.GlobalMaxPooling1D()(attended_features)

            # Combine with multi - scale features
            concatenated = layers.Concatenate()([concatenated, attended_features])

        # Deep feature extraction
        x = layers.Dense(512, activation="relu")(concatenated)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout_rate)(x)

        x = layers.Dense(256, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout_rate)(x)

        x = layers.Dense(128, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout_rate)(x)

        # Output layer
        outputs = layers.Dense(
            self.n_classes, activation="softmax", name="emotion_output"
        )(x)

        model = keras.Model(inputs=inputs, outputs=outputs)
        return model

    def get_emotion_labels(self) -> List[str]:
        """Get emotion labels based on the emotion model."""
        if self.emotion_model == "valence_arousal":
            return ["HAHV", "HALV", "LAHV", "LALV"]  # High / Low Arousal / Valence
        elif self.emotion_model == "basic_emotions":
            return ["Happy", "Sad", "Angry", "Fear", "Surprise", "Disgust", "Neutral"]
        else:  # complex_emotions
            return [
                "Joy",
                "Trust",
                "Fear",
                "Surprise",
                "Sadness",
                "Disgust",
                "Anger",
                "Anticipation",
                "Love",
                "Optimism",
                "Submission",
                "Awe",
                "Disappointment",
                "Remorse",
                "Contempt",
            ]

    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict emotions with confidence scores.

        Returns:
            Tuple of (predicted_labels, confidence_scores)
        """
        probabilities = self.predict(X)
        predicted_labels = np.argmax(probabilities, axis=1)
        confidence_scores = np.max(probabilities, axis=1)

        return predicted_labels, confidence_scores


class ValenceArousalRegressor(TensorFlowBaseModel):
    """Regression model for continuous valence - arousal prediction."""

    def __init__(self, n_channels: int, n_samples: int, **kwargs: Any) -> None:
        """
        Initialize valence - arousal regressor.

        Args:
            n_channels: Number of neural recording channels
            n_samples: Number of time samples per window
        """
        super().__init__(
            model_name="ValenceArousalRegressor",
            input_shape=(n_samples, n_channels),
            output_shape=2,  # Valence and Arousal values
            config=kwargs,
        )
        self.n_channels = n_channels
        self.n_samples = n_samples

    def build_model(self) -> keras.Model:
        """Build regression model for continuous emotion dimensions."""
        # Parameters
        lstm_units = self.config.get("lstm_units", 128)
        dropout_rate = self.config.get("dropout_rate", 0.3)

        # Input layer
        inputs = keras.Input(shape=self.input_shape)

        # Bidirectional LSTM for temporal modeling
        x = layers.Bidirectional(layers.LSTM(lstm_units, return_sequences=True))(inputs)
        x = layers.Dropout(dropout_rate)(x)

        # Attention mechanism
        attention = layers.MultiHeadAttention(num_heads=4, key_dim=lstm_units // 4)(
            x, x
        )
        x = layers.Add()([x, attention])
        x = layers.LayerNormalization()(x)

        # Second LSTM layer
        x = layers.Bidirectional(layers.LSTM(lstm_units // 2))(x)
        x = layers.Dropout(dropout_rate)(x)

        # Dense layers
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(dropout_rate)(x)

        # Output layer with tanh activation for [-1, 1] range
        outputs = layers.Dense(2, activation="tanh", name="valence_arousal_output")(x)

        model = keras.Model(inputs=inputs, outputs=outputs)
        return model

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Train with custom loss for valence - arousal prediction."""
        if self.model is None:
            self.model = self.build_model()

        # Custom loss that weights valence and arousal differently
        def valence_arousal_loss(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
            valence_weight = self.config.get("valence_weight", 1.0)
            arousal_weight = self.config.get("arousal_weight", 1.0)

            valence_loss = tf.reduce_mean(tf.square(y_true[:, 0] - y_pred[:, 0]))
            arousal_loss = tf.reduce_mean(tf.square(y_true[:, 1] - y_pred[:, 1]))

            return valence_weight * valence_loss + arousal_weight * arousal_loss

        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(
                learning_rate=self.config.get("learning_rate", 0.001)
            ),
            loss=valence_arousal_loss,
            metrics=["mae"],
        )

        # Train
        history = self.model.fit(
            X_train,
            y_train,
            batch_size=self.config.get("batch_size", 32),
            epochs=self.config.get("epochs", 150),
            validation_data=(X_val, y_val) if X_val is not None else None,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor="val_loss", patience=20, restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor="val_loss", factor=0.5, patience=10
                ),
            ],
            verbose=self.config.get("verbose", 1),
        )

        self.is_trained = True

        return {
            "history": history.history,
            "final_loss": float(history.history["loss"][-1]),
            "final_val_loss": float(history.history.get("val_loss", [0])[-1]),
        }


class EmotionFeatureExtractor:
    """Extract emotion - relevant features from neural signals."""

    def __init__(self, sampling_rate: float = 250.0):
        self.sampling_rate = sampling_rate

    def extract_features(self, neural_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract features relevant for emotion recognition.

        Args:
            neural_data: Neural signals (n_samples, n_channels)

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Frequency band powers (emotion - relevant bands)
        features.update(self._extract_band_powers(neural_data))

        # Asymmetry features (frontal alpha asymmetry)
        features.update(self._extract_asymmetry_features(neural_data))

        # Connectivity features
        features.update(self._extract_connectivity_features(neural_data))

        # Statistical features
        features.update(self._extract_statistical_features(neural_data))

        return features

    def _extract_band_powers(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract power in emotion - relevant frequency bands."""
        from scipy import signal

        bands = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 50)}

        band_powers = {}

        for band_name, (low_freq, high_freq) in bands.items():
            # Butterworth bandpass filter
            b, a = signal.butter(
                4, [low_freq, high_freq], btype="band", fs=self.sampling_rate
            )

            # Filter each channel
            filtered = np.zeros_like(data)
            for ch in range(data.shape[1]):
                filtered[:, ch] = signal.filtfilt(b, a, data[:, ch])

            # Calculate power
            power = np.mean(filtered**2, axis=0)
            band_powers[f"{band_name}_power"] = power

        return band_powers

    def _extract_asymmetry_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract hemispheric asymmetry features."""
        features = {}

        # Assuming channels are organized with left hemisphere first, then right
        n_channels = data.shape[1]
        mid_point = n_channels // 2

        # Calculate alpha power for each hemisphere
        from scipy import signal

        b, a = signal.butter(4, [8, 13], btype="band", fs=self.sampling_rate)

        alpha_filtered = np.zeros_like(data)
        for ch in range(n_channels):
            alpha_filtered[:, ch] = signal.filtfilt(b, a, data[:, ch])

        # Left and right hemisphere alpha power
        left_alpha = np.mean(alpha_filtered[:, :mid_point] ** 2, axis=0)
        right_alpha = np.mean(alpha_filtered[:, mid_point:] ** 2, axis=0)

        # Frontal alpha asymmetry (log right - log left)
        features["frontal_alpha_asymmetry"] = np.log(right_alpha[:4]) - np.log(
            left_alpha[:4]
        )

        return features

    def _extract_connectivity_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract functional connectivity features."""
        features = {}

        # Phase Locking Value (PLV) between channels
        from scipy.signal import hilbert

        # Focus on alpha band for emotion
        from scipy import signal

        b, a = signal.butter(4, [8, 13], btype="band", fs=self.sampling_rate)

        filtered_data = np.zeros_like(data)
        for ch in range(data.shape[1]):
            filtered_data[:, ch] = signal.filtfilt(b, a, data[:, ch])

        # Compute instantaneous phase
        analytic_signal = hilbert(filtered_data, axis=0)
        phases = np.angle(analytic_signal)

        # Compute PLV for key channel pairs
        n_channels = data.shape[1]
        plv_matrix = np.zeros((n_channels, n_channels))

        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                phase_diff = phases[:, i] - phases[:, j]
                plv_matrix[i, j] = np.abs(np.mean(np.exp(1j * phase_diff)))
                plv_matrix[j, i] = plv_matrix[i, j]

        # Extract upper triangle as features
        features["plv_features"] = plv_matrix[np.triu_indices(n_channels, k=1)]

        return features

    def _extract_statistical_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract statistical features relevant for emotion."""
        from scipy import stats

        features = {
            "mean": np.mean(data, axis=0),
            "std": np.std(data, axis=0),
            "skewness": stats.skew(data, axis=0),
            "kurtosis": stats.kurtosis(data, axis=0),
            "hjorth_mobility": self._hjorth_mobility(data),
            "hjorth_complexity": self._hjorth_complexity(data),
        }

        return features

    def _hjorth_mobility(self, data: np.ndarray) -> np.ndarray:
        """Calculate Hjorth mobility parameter."""
        diff = np.diff(data, axis=0)
        result = np.sqrt(np.var(diff, axis=0) / np.var(data, axis=0))
        return np.array(result)

    def _hjorth_complexity(self, data: np.ndarray) -> np.ndarray:
        """Calculate Hjorth complexity parameter."""
        mobility = self._hjorth_mobility(data)
        diff2 = np.diff(data, n=2, axis=0)
        mobility2 = np.sqrt(
            np.var(diff2, axis=0) / np.var(np.diff(data, axis=0), axis=0)
        )
        result = mobility2 / mobility
        return np.array(result)

"""Movement decoder models for BCI applications."""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
from typing import Dict, Optional, Tuple, List, Any
import logging

from .base_models import TensorFlowBaseModel, PyTorchBaseModel, EEGNet

logger = logging.getLogger(__name__)


class MovementDecoder(TensorFlowBaseModel):
    """Deep learning model for decoding movement intentions from neural signals."""

    def __init__(self, n_channels: int, n_samples: int, n_outputs: int = 3, **kwargs: Any) -> None:
        """
        Initialize movement decoder.

        Args:
            n_channels: Number of neural recording channels
            n_samples: Number of time samples per window
            n_outputs: Number of movement dimensions (default: 3 for x, y, z)
        """
        super().__init__(
            model_name='MovementDecoder',
            input_shape=(n_samples, n_channels),
            output_shape=n_outputs,
            config=kwargs
        )
        self.n_channels = n_channels
        self.n_samples = n_samples
        self.n_outputs = n_outputs
        self.decoder_type = self.config.get('decoder_type', 'velocity')  # 'velocity' or 'position'

    def build_model(self) -> keras.Model:
        """Build movement decoder architecture."""
        # Parameters
        conv_filters = self.config.get('conv_filters', [64, 128, 256])
        lstm_units = self.config.get('lstm_units', 128)
        dropout_rate = self.config.get('dropout_rate', 0.3)
        use_attention = self.config.get('use_attention', True)

        # Input layer
        inputs = keras.Input(shape=self.input_shape)

        # Expand dims for Conv1D
        x = layers.Reshape((self.n_samples, self.n_channels, 1))(inputs)

        # Convolutional feature extraction
        for i, filters in enumerate(conv_filters):
            x = layers.TimeDistributed(
                layers.Conv1D(filters, kernel_size=3, padding='same', activation='relu')
            )(x)
            if i < len(conv_filters) - 1:
                x = layers.TimeDistributed(layers.MaxPooling1D(2))(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(dropout_rate)(x)

        # Reshape for LSTM
        x = layers.TimeDistributed(layers.Flatten())(x)

        # Bidirectional LSTM for temporal modeling
        x = layers.Bidirectional(layers.LSTM(lstm_units, return_sequences=True))(x)
        x = layers.Dropout(dropout_rate)(x)

        # Attention mechanism
        if use_attention:
            # Self - attention layer
            attention = layers.MultiHeadAttention(
                num_heads=8,
                key_dim=lstm_units // 8
            )(x, x)
            x = layers.Add()([x, attention])
            x = layers.LayerNormalization()(x)

        # Additional LSTM layer
        x = layers.LSTM(lstm_units // 2)(x)
        x = layers.Dropout(dropout_rate)(x)

        # Dense layers for movement prediction
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(dropout_rate)(x)

        # Output layer (no activation for regression)
        outputs = layers.Dense(self.n_outputs, name='movement_output')(x)

        # Add velocity integration if decoding position
        if self.decoder_type == 'position':
            # Custom layer to integrate velocity to position
            outputs = VelocityIntegrationLayer()(outputs)

        model = keras.Model(inputs=inputs, outputs=outputs)
        return model

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Train movement decoder with custom loss."""
        if self.model is None:
            self.model = self.build_model()

        # Custom loss function for movement decoding
        def movement_loss(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
            # MSE for position / velocity
            mse_loss = tf.reduce_mean(tf.square(y_true - y_pred))

            # Add smoothness constraint
            if len(y_pred.shape) == 3:  # If temporal dimension exists
                diff = y_pred[:, 1:, :] - y_pred[:, :-1, :]
                smoothness_loss = tf.reduce_mean(tf.square(diff))
                return mse_loss + 0.1 * smoothness_loss

            return mse_loss

        # Compile model
        assert self.model is not None
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.get('learning_rate', 0.001)),
            loss=movement_loss,
            metrics=['mae', 'mse']
        )

        # Training with callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
        ]

        # Add custom callback for movement - specific metrics
        if X_val is not None and y_val is not None:
            callbacks.append(MovementMetricsCallback(X_val, y_val))

        # Train
        history = self.model.fit(
            X_train, y_train,
            batch_size=self.config.get('batch_size', 32),
            epochs=self.config.get('epochs', 200),
            validation_data=(X_val, y_val) if X_val is not None else None,
            callbacks=callbacks,
            verbose=self.config.get('verbose', 1)
        )

        self.is_trained = True

        return {
            'history': history.history,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history.get('val_loss', [0])[-1]),
            'correlation': self.calculate_correlation(X_val, y_val) if X_val is not None and y_val is not None else None
        }

    def calculate_correlation(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """Calculate correlation coefficient for each movement dimension."""
        y_pred = self.predict(X)

        correlations = {}
        dimension_names = ['x', 'y', 'z'][:self.n_outputs]

        for i, dim in enumerate(dimension_names):
            corr = np.corrcoef(y_true[:, i], y_pred[:, i])[0, 1]
            correlations[f'correlation_{dim}'] = float(corr)

        correlations['correlation_mean'] = float(np.mean(list(correlations.values())))

        return correlations


class KalmanFilterDecoder:
    """Kalman filter - based movement decoder for real - time BCI applications."""

    def __init__(self, n_channels: int, n_outputs: int = 2, dt: float = 0.05):
        """
        Initialize Kalman filter decoder.

        Args:
            n_channels: Number of neural recording channels
            n_outputs: Number of movement dimensions (default: 2 for x, y)
            dt: Time step in seconds
        """
        self.n_channels = n_channels
        self.n_outputs = n_outputs
        self.dt = dt

        # State dimension (position + velocity for each output)
        self.state_dim = n_outputs * 2

        # Initialize matrices
        self.A: Optional[np.ndarray] = None  # State transition matrix
        self.H: Optional[np.ndarray] = None  # Observation matrix
        self.Q: Optional[np.ndarray] = None  # Process noise covariance
        self.R: Optional[np.ndarray] = None  # Measurement noise covariance
        self.P: Optional[np.ndarray] = None  # State covariance
        self.x: Optional[np.ndarray] = None  # State estimate

        self._initialize_matrices()

    def _initialize_matrices(self) -> None:
        """Initialize Kalman filter matrices."""
        # State transition matrix (constant velocity model)
        self.A = np.eye(self.state_dim)
        for i in range(self.n_outputs):
            self.A[i * 2, i * 2 + 1] = self.dt

        # Process noise covariance
        self.Q = np.eye(self.state_dim) * 0.001

        # Initial state covariance
        self.P = np.eye(self.state_dim) * 0.1

        # Initial state (zeros)
        self.x = np.zeros(self.state_dim)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Fit Kalman filter parameters.

        Args:
            X_train: Neural features (n_samples, n_channels)
            y_train: Movement data (n_samples, n_outputs * 2) - positions and velocities
        """
        # Learn observation matrix H using linear regression
        from sklearn.linear_model import Ridge

        ridge = Ridge(alpha=1.0)
        ridge.fit(X_train, y_train)

        self.H = ridge.coef_

        # Estimate measurement noise covariance
        assert self.H is not None
        y_pred = X_train @ self.H.T
        residuals = y_train - y_pred
        self.R = np.cov(residuals.T)

        logger.info(f"Kalman filter fitted with observation matrix shape: {self.H.shape}")

    def predict_step(self, neural_features: np.ndarray) -> np.ndarray:
        """
        Single prediction step of Kalman filter.

        Args:
            neural_features: Current neural features (n_channels,)

        Returns:
            Predicted movement state (positions and velocities)
        """
        # Prediction step
        assert self.A is not None and self.x is not None and self.P is not None and self.Q is not None
        x_pred = self.A @ self.x
        P_pred = self.A @ self.P @ self.A.T + self.Q

        # Measurement prediction
        z = neural_features
        assert self.H is not None
        z_pred = self.H @ x_pred

        # Innovation
        y = z - z_pred
        assert self.R is not None
        S = self.H @ P_pred @ self.H.T + self.R

        # Kalman gain
        K = P_pred @ self.H.T @ np.linalg.inv(S)

        # Update step
        self.x = x_pred + K @ y
        self.P = (np.eye(self.state_dim) - K @ self.H) @ P_pred

        return self.x

    def reset_state(self) -> None:
        """Reset Kalman filter state."""
        self.x = np.zeros(self.state_dim)
        self.P = np.eye(self.state_dim) * 0.1


class VelocityIntegrationLayer(layers.Layer):
    """Custom layer to integrate velocity predictions to position."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        """Integrate velocities to get positions."""
        # Cumulative sum along time axis
        return tf.cumsum(inputs, axis=1)


class MovementMetricsCallback(keras.callbacks.Callback):
    """Custom callback to compute movement - specific metrics during training."""

    def __init__(self, X_val: np.ndarray, y_val: np.ndarray):
        super().__init__()
        self.X_val = X_val
        self.y_val = y_val

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, float]] = None) -> None:
        """Calculate and log movement metrics."""
        if self.X_val is not None:
            y_pred = self.model.predict(self.X_val, verbose=0)

            # Calculate correlation for each dimension
            correlations = []
            for i in range(y_pred.shape[1]):
                corr = np.corrcoef(self.y_val[:, i], y_pred[:, i])[0, 1]
                correlations.append(corr)

            mean_corr = np.mean(correlations)
            if logs is not None:
                logs['val_correlation'] = mean_corr

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch} - Val Correlation: {mean_corr:.4f}")


class CursorControlDecoder(MovementDecoder):
    """Specialized decoder for 2D cursor control in BCI applications."""

    def __init__(self, n_channels: int, n_samples: int, **kwargs: Any) -> None:
        """Initialize cursor control decoder for 2D movement."""
        super().__init__(
            n_channels=n_channels,
            n_samples=n_samples,
            n_outputs=2,  # x, y coordinates
            **kwargs
        )
        self.model_name = 'CursorControlDecoder'

    def build_model(self) -> keras.Model:
        """Build specialized architecture for cursor control."""
        # Use base movement decoder with modifications
        model = super().build_model()

        # Add output constraints for cursor control
        # Get the last layer and modify it
        x = model.layers[-2].output

        # Add sigmoid activation to constrain output to [0, 1] range
        cursor_output = layers.Dense(
            2,
            activation='sigmoid',
            name='cursor_position'
        )(x)

        # Create new model with constrained output
        constrained_model = keras.Model(
            inputs=model.input,
            outputs=cursor_output
        )

        return constrained_model

    def post_process_predictions(self, predictions: np.ndarray,
                               screen_width: int = 1920,
                               screen_height: int = 1080) -> np.ndarray:
        """
        Convert normalized predictions to screen coordinates.

        Args:
            predictions: Normalized cursor positions (n_samples, 2)
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            Screen coordinates (n_samples, 2)
        """
        screen_coords = predictions.copy()
        screen_coords[:, 0] *= screen_width
        screen_coords[:, 1] *= screen_height

        return screen_coords.astype(int)

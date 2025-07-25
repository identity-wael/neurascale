"""Base models for neural signal processing and BCI applications."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class BaseNeuralModel(ABC):
    """Abstract base class for all neural models."""

    def __init__(self,
                 model_name: str,
                 input_shape: Tuple[int, ...],
                 output_shape: Union[int, Tuple[int, ...]],
                 config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.config = config or {}
        self.model: Optional[Any] = None
        self.is_trained = False
        self.metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'framework': self.get_framework()
        }

    @abstractmethod
    def build_model(self) -> Any:
        """Build the neural network architecture."""
        pass

    @abstractmethod
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Save model to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load model from disk."""
        pass

    @abstractmethod
    def get_framework(self) -> str:
        """Return the framework name (tensorflow or pytorch)."""
        pass

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        predictions = self.predict(X_test)
        metrics = self.calculate_metrics(y_test, predictions)
        return metrics

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics."""
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

        if len(y_pred.shape) > 1 and y_pred.shape[1] > 1:
            # Multi - class classification
            y_pred = np.argmax(y_pred, axis=1)
        if len(y_true.shape) > 1 and y_true.shape[1] > 1:
            y_true = np.argmax(y_true, axis=1)

        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')

        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }

    def get_model_summary(self) -> Dict[str, Any]:
        """Get model summary and statistics."""
        return {
            'model_name': self.model_name,
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'is_trained': self.is_trained,
            'framework': self.get_framework(),
            'metadata': self.metadata,
            'config': self.config
        }


class TensorFlowBaseModel(BaseNeuralModel):
    """Base class for TensorFlow / Keras models."""

    def get_framework(self) -> str:
        return 'tensorflow'

    def build_model(self) -> keras.Model:
        """Build Keras model - to be implemented by subclasses."""
        raise NotImplementedError

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Train TensorFlow model."""
        if self.model is None:
            self.model = self.build_model()

        # Compile model
        assert self.model is not None
        self.model.compile(
            optimizer=self.config.get('optimizer', 'adam'),
            loss=self.config.get('loss', 'categorical_crossentropy'),
            metrics=self.config.get('metrics', ['accuracy'])
        )

        # Training parameters
        batch_size = self.config.get('batch_size', 32)
        epochs = self.config.get('epochs', 100)

        # Callbacks
        callbacks = []

        # Early stopping
        if self.config.get('early_stopping', True):
            callbacks.append(keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config.get('early_stopping_patience', 10),
                restore_best_weights=True
            ))

        # Reduce learning rate on plateau
        if self.config.get('reduce_lr', True):
            callbacks.append(keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            ))

        # Train model
        assert self.model is not None
        history = self.model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_val, y_val) if X_val is not None else None,
            callbacks=callbacks,
            verbose=self.config.get('verbose', 1)
        )

        self.is_trained = True

        return {
            'history': history.history,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history.get('val_loss', [0])[-1])
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with TensorFlow model."""
        if self.model is None:
            raise ValueError("Model not built or loaded")
        predictions = self.model.predict(X)
        return np.array(predictions)

    def save(self, filepath: str) -> None:
        """Save TensorFlow model."""
        if self.model is None:
            raise ValueError("No model to save")

        # Save model
        self.model.save(filepath)

        # Save metadata
        metadata_path = filepath + '_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(self.get_model_summary(), f, indent=2)

    def load(self, filepath: str) -> None:
        """Load TensorFlow model."""
        self.model = keras.models.load_model(filepath)

        # Load metadata if exists
        metadata_path = filepath + '_metadata.json'
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.metadata = metadata.get('metadata', self.metadata)
                self.is_trained = metadata.get('is_trained', True)


class PyTorchBaseModel(BaseNeuralModel):
    """Base class for PyTorch models."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.optimizer: Optional[torch.optim.Optimizer] = None
        self.criterion: Optional[nn.Module] = None

    def get_framework(self) -> str:
        return 'pytorch'

    def build_model(self) -> nn.Module:
        """Build PyTorch model - to be implemented by subclasses."""
        raise NotImplementedError

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Train PyTorch model."""
        if self.model is None:
            self.model = self.build_model().to(self.device)

        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train).to(self.device)
        y_train_tensor = torch.LongTensor(y_train).to(self.device)

        if X_val is not None:
            X_val_tensor = torch.FloatTensor(X_val).to(self.device)
            y_val_tensor = torch.LongTensor(y_val).to(self.device)

        # Setup optimizer and loss
        if self.optimizer is None:
            self.optimizer = torch.optim.Adam(
                self.model.parameters(),
                lr=self.config.get('learning_rate', 0.001)
            )

        if self.criterion is None:
            self.criterion = nn.CrossEntropyLoss()

        # Training parameters
        batch_size = self.config.get('batch_size', 32)
        epochs = self.config.get('epochs', 100)

        # Create data loader
        dataset = torch.utils.data.TensorDataset(X_train_tensor, y_train_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Training history
        history: Dict[str, List[float]] = {'loss': [], 'val_loss': []}
        best_val_loss = float('in')
        patience_counter = 0

        # Training loop
        for epoch in range(epochs):
            # Training phase
            assert self.model is not None
            self.model.train()
            train_loss = 0.0

            for batch_X, batch_y in dataloader:
                assert self.optimizer is not None and self.model is not None
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                assert self.criterion is not None
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                self.optimizer.step()
                train_loss += loss.item()

            avg_train_loss = train_loss / len(dataloader)
            history['loss'].append(avg_train_loss)

            # Validation phase
            if X_val is not None:
                assert self.model is not None and self.criterion is not None
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(X_val_tensor)
                    val_loss = self.criterion(val_outputs, y_val_tensor).item()
                    history['val_loss'].append(val_loss)

                # Early stopping
                if self.config.get('early_stopping', True):
                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        patience_counter = 0
                        # Save best model state
                        assert self.model is not None
                        best_model_state = self.model.state_dict()
                    else:
                        patience_counter += 1
                        if patience_counter >= self.config.get('early_stopping_patience', 10):
                            # Restore best model
                            assert self.model is not None
                            self.model.load_state_dict(best_model_state)
                            break

            if epoch % 10 == 0 and self.config.get('verbose', 1):
                logger.info(f"Epoch {epoch}/{epochs} - Loss: {avg_train_loss:.4f}")

        self.is_trained = True

        return {
            'history': history,
            'final_loss': float(history['loss'][-1]),
            'final_val_loss': float(history.get('val_loss', [0])[-1])
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with PyTorch model."""
        if self.model is None:
            raise ValueError("Model not built or loaded")

        assert self.model is not None
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            # Convert to probabilities
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            return probabilities.cpu().numpy()

    def save(self, filepath: str) -> None:
        """Save PyTorch model."""
        if self.model is None:
            raise ValueError("No model to save")

        # Save model state
        assert self.model is not None
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'model_config': self.config,
            'metadata': self.get_model_summary()
        }, filepath)

    def load(self, filepath: str) -> None:
        """Load PyTorch model."""
        checkpoint = torch.load(filepath, map_location=self.device)

        # Build model if not exists
        if self.model is None:
            self.model = self.build_model().to(self.device)

        # Load state
        assert self.model is not None
        self.model.load_state_dict(checkpoint['model_state_dict'])

        # Load optimizer if exists
        if self.optimizer and checkpoint.get('optimizer_state_dict'):
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # Load metadata
        if 'metadata' in checkpoint:
            metadata = checkpoint['metadata']
            self.metadata = metadata.get('metadata', self.metadata)
            self.is_trained = metadata.get('is_trained', True)


class EEGNet(TensorFlowBaseModel):
    """EEGNet implementation for EEG signal classification."""

    def __init__(self, n_channels: int, n_samples: int, n_classes: int, **kwargs: Any) -> None:
        super().__init__(
            model_name='EEGNet',
            input_shape=(n_samples, n_channels, 1),
            output_shape=n_classes,
            config=kwargs
        )
        self.n_channels = n_channels
        self.n_samples = n_samples
        self.n_classes = n_classes

    def build_model(self) -> keras.Model:
        """Build EEGNet architecture."""
        # Parameters
        F1 = self.config.get('F1', 8)
        F2 = self.config.get('F2', 16)
        D = self.config.get('D', 2)
        dropout_rate = self.config.get('dropout_rate', 0.5)

        # Input layer
        inputs = keras.Input(shape=self.input_shape)

        # Block 1
        block1 = layers.Conv2D(F1, (1, 64), padding='same', use_bias=False)(inputs)
        block1 = layers.BatchNormalization()(block1)
        block1 = layers.DepthwiseConv2D((self.n_channels, 1), use_bias=False,
                                       depth_multiplier=D,
                                       depthwise_constraint=keras.constraints.max_norm(1.))(block1)
        block1 = layers.BatchNormalization()(block1)
        block1 = layers.Activation('elu')(block1)
        block1 = layers.AveragePooling2D((1, 4))(block1)
        block1 = layers.Dropout(dropout_rate)(block1)

        # Block 2
        block2 = layers.SeparableConv2D(F2, (1, 16), use_bias=False, padding='same')(block1)
        block2 = layers.BatchNormalization()(block2)
        block2 = layers.Activation('elu')(block2)
        block2 = layers.AveragePooling2D((1, 8))(block2)
        block2 = layers.Dropout(dropout_rate)(block2)

        # Classification block
        flatten = layers.Flatten()(block2)
        dense = layers.Dense(self.n_classes, name='dense',
                           kernel_constraint=keras.constraints.max_norm(0.25))(flatten)
        outputs = layers.Activation('softmax', name='softmax')(dense)

        model = keras.Model(inputs=inputs, outputs=outputs)
        return model


class CNNLSTMModel(TensorFlowBaseModel):
    """CNN - LSTM hybrid model for temporal neural signal processing."""

    def __init__(self, n_channels: int, n_timesteps: int, n_classes: int, **kwargs: Any) -> None:
        super().__init__(
            model_name='CNN - LSTM',
            input_shape=(n_timesteps, n_channels),
            output_shape=n_classes,
            config=kwargs
        )
        self.n_channels = n_channels
        self.n_timesteps = n_timesteps
        self.n_classes = n_classes

    def build_model(self) -> keras.Model:
        """Build CNN - LSTM architecture."""
        # Parameters
        cnn_filters = self.config.get('cnn_filters', 64)
        lstm_units = self.config.get('lstm_units', 128)
        dropout_rate = self.config.get('dropout_rate', 0.5)

        # Input layer
        inputs = keras.Input(shape=self.input_shape)

        # Reshape for CNN
        x = layers.Reshape((self.n_timesteps, self.n_channels, 1))(inputs)

        # CNN layers
        x = layers.TimeDistributed(layers.Conv1D(cnn_filters, 3, activation='relu'))(x)
        x = layers.TimeDistributed(layers.MaxPooling1D(2))(x)
        x = layers.TimeDistributed(layers.Conv1D(cnn_filters // 2, 3, activation='relu'))(x)
        x = layers.TimeDistributed(layers.GlobalMaxPooling1D())(x)

        # LSTM layers
        x = layers.LSTM(lstm_units, return_sequences=True)(x)
        x = layers.Dropout(dropout_rate)(x)
        x = layers.LSTM(lstm_units // 2)(x)
        x = layers.Dropout(dropout_rate)(x)

        # Output layer
        outputs = layers.Dense(self.n_classes, activation='softmax')(x)

        model = keras.Model(inputs=inputs, outputs=outputs)
        return model


class NeuralTransformer(nn.Module):
    """Transformer architecture for neural signal processing."""

    def __init__(self, n_channels: int, n_classes: int, d_model: int = 256,
                 n_heads: int = 8, n_layers: int = 4, dropout: float = 0.1) -> None:
        super().__init__()
        self.d_model = d_model
        self.input_projection = nn.Linear(n_channels, d_model)

        # Positional encoding
        self.pos_encoding = nn.Parameter(torch.randn(1, 1000, d_model))

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dropout=dropout
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Output layers
        self.fc1 = nn.Linear(d_model, d_model // 2)
        self.fc2 = nn.Linear(d_model // 2, n_classes)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, sequence_length, n_channels)
        batch_size, seq_len, _ = x.shape

        # Project input
        x = self.input_projection(x)

        # Add positional encoding
        x = x + self.pos_encoding[:, :seq_len, :]

        # Transformer expects (seq_len, batch_size, d_model)
        x = x.transpose(0, 1)

        # Apply transformer
        x = self.transformer(x)

        # Global average pooling
        x = x.mean(dim=0)

        # Classification head
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)

        return x


class TransformerModel(PyTorchBaseModel):
    """Transformer - based model for neural signal processing."""

    def __init__(self, n_channels: int, sequence_length: int, n_classes: int, **kwargs: Any) -> None:
        super().__init__(
            model_name='Transformer',
            input_shape=(sequence_length, n_channels),
            output_shape=n_classes,
            config=kwargs
        )
        self.n_channels = n_channels
        self.sequence_length = sequence_length
        self.n_classes = n_classes

    def build_model(self) -> nn.Module:
        """Build Transformer architecture."""
        return NeuralTransformer(
            self.n_channels,
            self.n_classes,
            d_model=self.config.get('d_model', 256),
            n_heads=self.config.get('n_heads', 8),
            n_layers=self.config.get('n_layers', 4),
            dropout=self.config.get('dropout', 0.1)
        )

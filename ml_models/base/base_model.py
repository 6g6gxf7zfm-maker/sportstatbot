"""
Base model class for all SportStatBot ML models
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import pickle
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for ML models"""
    model_name: str
    version: str = "1.0.0"
    sport: Optional[str] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class BaseModel(ABC):
    """
    Abstract base class for all ML models in SportStatBot

    Provides common interface for training, prediction, and persistence.
    """

    def __init__(self, config: ModelConfig):
        """
        Initialize model with configuration

        Args:
            config: ModelConfig object with model settings
        """
        self.config = config
        self.is_trained = False
        self.model = None
        self.metadata = {}

    @abstractmethod
    def train(self, data: Any, labels: Optional[Any] = None) -> Dict[str, float]:
        """
        Train the model on provided data

        Args:
            data: Training data
            labels: Training labels (for supervised learning)

        Returns:
            Dict of training metrics
        """
        pass

    @abstractmethod
    def predict(self, data: Any) -> Any:
        """
        Make predictions on new data

        Args:
            data: Input data for prediction

        Returns:
            Model predictions
        """
        pass

    @abstractmethod
    def evaluate(self, data: Any, labels: Any) -> Dict[str, float]:
        """
        Evaluate model performance

        Args:
            data: Test data
            labels: True labels

        Returns:
            Dict of evaluation metrics
        """
        pass

    def save(self, path: str) -> None:
        """
        Save model to disk

        Args:
            path: Path to save model
        """
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save model object
        model_path = save_path.with_suffix('.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

        # Save metadata
        metadata = {
            'config': {
                'model_name': self.config.model_name,
                'version': self.config.version,
                'sport': self.config.sport,
                'parameters': self.config.parameters
            },
            'is_trained': self.is_trained,
            'metadata': self.metadata
        }

        metadata_path = save_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Model saved to {model_path}")

    def load(self, path: str) -> None:
        """
        Load model from disk

        Args:
            path: Path to load model from
        """
        load_path = Path(path)

        # Load model object
        model_path = load_path.with_suffix('.pkl')
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        # Load metadata
        metadata_path = load_path.with_suffix('.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        self.is_trained = metadata['is_trained']
        self.metadata = metadata['metadata']

        print(f"✅ Model loaded from {model_path}")

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance if available

        Returns:
            Dict mapping feature names to importance scores
        """
        # Override in subclasses that support feature importance
        return None

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"name={self.config.model_name}, "
                f"version={self.config.version}, "
                f"trained={self.is_trained})")

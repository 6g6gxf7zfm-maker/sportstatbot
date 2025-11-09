# Model Artifacts

This directory stores trained machine learning model weights and artifacts.

## File Naming Convention

```
{model_name}_{sport}_{version}_{date}.{ext}

Examples:
- injury_predictor_nba_v1.0_20250109.pkl
- stability_index_nfl_v1.2_20250115.h5
- market_value_mlb_v2.0_20250201.pth
```

## Extensions

- `.pkl` - scikit-learn models (pickle format)
- `.h5` - Keras/TensorFlow models
- `.pth/.pt` - PyTorch models
- `.joblib` - Joblib serialized models
- `.json` - Model metadata and configurations

## Usage

```python
from ml_models.predictive.stability_index import PerformanceStabilityAnalyzer

# Models that inherit from BaseModel can save/load
model = PerformanceStabilityAnalyzer()
# model.save('artifacts/stability_index_nba_v1.0')
# model.load('artifacts/stability_index_nba_v1.0')
```

## Storage

Large model files (>100MB) should not be committed to git. Use:
- Cloud storage (S3, Google Cloud Storage)
- Model registry (MLflow, Weights & Biases)
- DVC (Data Version Control)

For production deployment, implement a model download script that pulls artifacts from cloud storage.

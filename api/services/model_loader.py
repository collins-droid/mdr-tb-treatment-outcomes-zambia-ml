"""Model artifact loading and inference service."""

from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from src.models.predict import PredictionResult, RiskFactor, risk_level_from_score
from src.models.train import DEFAULT_MODEL_PATH, train_default_model


POOR_OUTCOME_CLASSES = {"Died", "Lost to Follow Up"}


class ModelService:
    """Prediction service backed by the trained outcome-model artifact."""

    def __init__(self, artifact: dict[str, object]) -> None:
        self.artifact = artifact
        self.model = artifact["model"]
        self.model_version = str(artifact["model_version"])
        self.features = list(artifact["features"])
        self.classes = list(artifact["classes"])

    def predict(self, patient: dict[str, object]) -> PredictionResult:
        frame = pd.DataFrame([{feature: patient[feature] for feature in self.features}])
        probabilities_raw = self.model.predict_proba(frame)[0]
        probabilities = {
            class_name: round(float(probability), 4)
            for class_name, probability in zip(self.model.classes_, probabilities_raw)
        }
        predicted_outcome = max(probabilities, key=probabilities.get)
        poor_outcome_risk = round(
            sum(probabilities.get(class_name, 0.0) for class_name in POOR_OUTCOME_CLASSES),
            4,
        )
        return PredictionResult(
            predicted_outcome=predicted_outcome,
            poor_outcome_risk=poor_outcome_risk,
            risk_level=risk_level_from_score(poor_outcome_risk),
            probabilities=probabilities,
            explanation=self._explain(frame, predicted_outcome),
            model_version=self.model_version,
            disclaimer=(
                "Model trained on the reconstructed aggregate-count dataset. "
                "Use for academic project demonstration, not clinical deployment."
            ),
        )

    def _explain(self, frame: pd.DataFrame, predicted_outcome: str) -> list[RiskFactor]:
        preprocess = self.model.named_steps["preprocess"]
        classifier = self.model.named_steps["classifier"]
        transformed = preprocess.transform(frame)
        feature_names = preprocess.get_feature_names_out()
        row = transformed.toarray()[0] if hasattr(transformed, "toarray") else transformed[0]
        if hasattr(classifier, "coef_"):
            coefficients = classifier.coef_[class_index]
            contributions = row * coefficients
            is_directional = True
        elif hasattr(classifier, "feature_importances_"):
            contributions = row * classifier.feature_importances_
            is_directional = False
        else:
            contributions = [0] * len(feature_names)
            is_directional = False

        ranked = sorted(
            [
                (feature_names[index], float(value))
                for index, value in enumerate(contributions)
                if abs(float(value)) > 0
            ],
            key=lambda item: abs(item[1]),
            reverse=True,
        )
        factors = []
        for feature_name, contribution in ranked[:4]:
            clean_name = feature_name.replace("categorical__", "").replace("_", " ")
            if is_directional:
                direction = "increases" if contribution > 0 else "decreases"
                effect = f"This patient value {direction} the model score for {predicted_outcome}."
            else:
                effect = f"This patient value strongly contributed to the model's prediction."
            
            factors.append(
                RiskFactor(
                    feature=feature_name,
                    label=clean_name,
                    effect=effect,
                    weight=round(contribution, 4),
                )
            )
        return factors


@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    if not DEFAULT_MODEL_PATH.exists():
        train_default_model()
    artifact = joblib.load(DEFAULT_MODEL_PATH)
    return ModelService(artifact)

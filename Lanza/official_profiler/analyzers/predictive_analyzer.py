"""
Predictive analysis system for forecasting political behaviors, relationships, and outcomes.
Uses historical patterns and machine learning to predict future political dynamics.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict, Counter
import structlog

# ML and statistical imports
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

from data.staten_island_officials import STATEN_ISLAND_OFFICIALS
from analyzers.relationship_tracker import RelationshipTracker, EvidenceStrength
from analyzers.evidence_classifier import EvidenceClassifier
from utils.temporal_analyzer import TemporalAnalyzer

logger = structlog.get_logger()


class PredictionType(Enum):
    """Types of predictions the system can make."""
    RELATIONSHIP_STRENGTH = "relationship_strength"
    COALITION_FORMATION = "coalition_formation"
    ISSUE_POSITION_CHANGE = "issue_position_change"
    LEGISLATIVE_SUCCESS = "legislative_success"
    ELECTORAL_PERFORMANCE = "electoral_performance"
    INFLUENCE_TRAJECTORY = "influence_trajectory"


class PredictionHorizon(Enum):
    """Time horizons for predictions."""
    SHORT_TERM = "short_term"  # 3-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"  # 2-5 years


class ConfidenceLevel(Enum):
    """Confidence levels for predictions."""
    HIGH = "high"  # >80% confidence
    MEDIUM = "medium"  # 60-80% confidence
    LOW = "low"  # 40-60% confidence
    VERY_LOW = "very_low"  # <40% confidence


@dataclass
class PredictionInput:
    """Input features for prediction models."""
    official: str
    historical_data: Dict[str, List[float]]
    relationship_features: Dict[str, float]
    temporal_features: Dict[str, float]
    contextual_features: Dict[str, Any]
    external_factors: Dict[str, float]


@dataclass
class Prediction:
    """A single prediction result."""
    prediction_type: PredictionType
    target_entity: str  # Official or relationship
    prediction_value: Union[float, str, Dict]
    confidence_level: ConfidenceLevel
    confidence_score: float
    prediction_horizon: PredictionHorizon
    key_factors: List[str]
    supporting_evidence: List[str]
    uncertainty_factors: List[str]
    timestamp: datetime


@dataclass
class PredictionScenario:
    """A scenario with multiple related predictions."""
    scenario_name: str
    scenario_probability: float
    component_predictions: List[Prediction]
    scenario_description: str
    key_assumptions: List[str]
    risk_factors: List[str]


class PredictiveAnalyzer:
    """Advanced predictive analysis for political dynamics."""

    def __init__(self):
        self.relationship_tracker = RelationshipTracker()
        self.evidence_classifier = EvidenceClassifier()
        self.temporal_analyzer = TemporalAnalyzer()

        # ML Models
        self.relationship_model = None
        self.coalition_model = None
        self.influence_model = None
        self.position_change_model = None

        # Feature scalers
        self.scalers = {}
        self.label_encoders = {}

        # Historical patterns
        self.historical_patterns = {}
        self.prediction_cache = {}

    async def initialize_models(self):
        """Initialize and train predictive models."""
        logger.info("Initializing predictive models")

        try:
            # Prepare training data
            training_data = await self._prepare_training_data()

            # Train relationship strength predictor
            await self._train_relationship_model(training_data)

            # Train coalition formation predictor
            await self._train_coalition_model(training_data)

            # Train influence trajectory predictor
            await self._train_influence_model(training_data)

            # Train position change predictor
            await self._train_position_change_model(training_data)

            logger.info("Predictive models initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize models", error=str(e))
            raise

    async def _prepare_training_data(self) -> Dict[str, pd.DataFrame]:
        """Prepare training data from historical patterns."""
        training_data = {}

        # Extract historical relationship data
        relationship_data = []
        all_relationships = await self.relationship_tracker.analyze_all_relationships()

        for official, relationships in all_relationships.items():
            for rel in relationships:
                relationship_data.append({
                    'official_1': rel.official_1,
                    'official_2': rel.official_2,
                    'cooperation_score': rel.cooperation_score,
                    'stability_score': rel.stability_score,
                    'evidence_count': rel.evidence_count,
                    'shared_issues_count': len(rel.shared_issues),
                    'relationship_age_days': (rel.last_interaction - rel.first_interaction).days,
                    'strength_label': rel.relationship_type.value
                })

        training_data['relationships'] = pd.DataFrame(relationship_data)

        # Extract historical position data
        position_data = []
        for official, data in STATEN_ISLAND_OFFICIALS.items():
            position_evolution = data.get('position_evolution', {})
            for issue, positions in position_evolution.items():
                for i, position in enumerate(positions):
                    if i > 0:  # Need previous position for change prediction
                        position_data.append({
                            'official': official,
                            'issue': issue,
                            'position_index': i,
                            'previous_position': positions[i-1].get('position', ''),
                            'current_position': position.get('position', ''),
                            'time_diff_days': self._calculate_time_diff(positions[i-1], position),
                            'context': position.get('context', ''),
                            'changed': positions[i-1].get('position', '') != position.get('position', '')
                        })

        training_data['positions'] = pd.DataFrame(position_data)

        # Extract achievement/influence data
        influence_data = []
        for official, data in STATEN_ISLAND_OFFICIALS.items():
            achievements = data.get('achievements', [])
            for achievement in achievements:
                influence_data.append({
                    'official': official,
                    'year': int(achievement.get('year', 2020)),
                    'achievement_type': achievement.get('category', 'general'),
                    'description_length': len(achievement.get('description', '')),
                    'position_type': data.get('position_type', ''),
                    'influence_score': self._calculate_influence_score(achievement)
                })

        training_data['influence'] = pd.DataFrame(influence_data)

        return training_data

    def _calculate_time_diff(self, pos1: Dict, pos2: Dict) -> int:
        """Calculate time difference between positions."""
        try:
            date1 = datetime.strptime(pos1.get('date', '2020-01-01'), '%Y-%m-%d')
            date2 = datetime.strptime(pos2.get('date', '2020-01-01'), '%Y-%m-%d')
            return (date2 - date1).days
        except:
            return 365  # Default to 1 year

    def _calculate_influence_score(self, achievement: Dict) -> float:
        """Calculate influence score from achievement."""
        description = achievement.get('description', '').lower()

        # Base score
        score = 0.5

        # Scoring keywords
        high_impact = ['secured', 'delivered', 'passed', 'established', 'created']
        medium_impact = ['supported', 'advocated', 'promoted', 'endorsed']
        scope_indicators = ['state', 'federal', 'statewide', 'national']

        # Apply scoring
        for keyword in high_impact:
            if keyword in description:
                score += 0.2

        for keyword in medium_impact:
            if keyword in description:
                score += 0.1

        for keyword in scope_indicators:
            if keyword in description:
                score += 0.1

        return min(1.0, score)

    async def _train_relationship_model(self, training_data: Dict[str, pd.DataFrame]):
        """Train relationship strength prediction model."""
        if 'relationships' not in training_data or training_data['relationships'].empty:
            logger.warning("No relationship data for training")
            return

        df = training_data['relationships']

        # Prepare features
        feature_columns = ['cooperation_score', 'stability_score', 'evidence_count',
                          'shared_issues_count', 'relationship_age_days']
        X = df[feature_columns]

        # Encode target labels
        le = LabelEncoder()
        y = le.fit_transform(df['strength_label'])
        self.label_encoders['relationship'] = le

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['relationship'] = scaler

        # Train model
        self.relationship_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.relationship_model.fit(X_scaled, y)

        # Evaluate
        scores = cross_val_score(self.relationship_model, X_scaled, y, cv=3)
        logger.info("Relationship model trained", accuracy=scores.mean())

    async def _train_coalition_model(self, training_data: Dict[str, pd.DataFrame]):
        """Train coalition formation prediction model."""
        # This would use network analysis and clustering patterns
        # For now, create a simple model based on relationship patterns
        self.coalition_model = "placeholder"  # Would implement sophisticated clustering model

    async def _train_influence_model(self, training_data: Dict[str, pd.DataFrame]):
        """Train influence trajectory prediction model."""
        if 'influence' not in training_data or training_data['influence'].empty:
            logger.warning("No influence data for training")
            return

        df = training_data['influence']

        # Prepare features (encode categorical variables)
        df_encoded = df.copy()

        # Encode position type
        le_position = LabelEncoder()
        df_encoded['position_type_encoded'] = le_position.fit_transform(df['position_type'])
        self.label_encoders['position_type'] = le_position

        # Encode achievement type
        le_achievement = LabelEncoder()
        df_encoded['achievement_type_encoded'] = le_achievement.fit_transform(df['achievement_type'])
        self.label_encoders['achievement_type'] = le_achievement

        feature_columns = ['year', 'description_length', 'position_type_encoded', 'achievement_type_encoded']
        X = df_encoded[feature_columns]
        y = df_encoded['influence_score']

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['influence'] = scaler

        # Train model
        self.influence_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.influence_model.fit(X_scaled, y)

        # Evaluate
        scores = cross_val_score(self.influence_model, X_scaled, y, cv=3, scoring='neg_mean_squared_error')
        logger.info("Influence model trained", rmse=np.sqrt(-scores.mean()))

    async def _train_position_change_model(self, training_data: Dict[str, pd.DataFrame]):
        """Train position change prediction model."""
        if 'positions' not in training_data or training_data['positions'].empty:
            logger.warning("No position data for training")
            return

        df = training_data['positions']

        # Simple features for position change prediction
        feature_columns = ['position_index', 'time_diff_days']
        X = df[feature_columns]
        y = df['changed'].astype(int)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['position_change'] = scaler

        # Train model
        self.position_change_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.position_change_model.fit(X_scaled, y)

        # Evaluate
        scores = cross_val_score(self.position_change_model, X_scaled, y, cv=3)
        logger.info("Position change model trained", accuracy=scores.mean())

    async def predict_relationship_evolution(self, official_1: str, official_2: str,
                                           horizon: PredictionHorizon) -> Prediction:
        """Predict how a relationship will evolve."""
        if not self.relationship_model:
            await self.initialize_models()

        # Get current relationship data
        current_rel = await self.relationship_tracker.analyze_relationship_pair(official_1, official_2)

        if not current_rel:
            return self._create_low_confidence_prediction(
                PredictionType.RELATIONSHIP_STRENGTH,
                f"{official_1}_{official_2}",
                "insufficient_data",
                horizon
            )

        # Prepare features
        features = np.array([[
            current_rel.cooperation_score,
            current_rel.stability_score,
            current_rel.evidence_count,
            len(current_rel.shared_issues),
            (current_rel.last_interaction - current_rel.first_interaction).days
        ]])

        # Scale features
        if 'relationship' in self.scalers:
            features_scaled = self.scalers['relationship'].transform(features)
        else:
            features_scaled = features

        # Make prediction
        try:
            prediction_proba = self.relationship_model.predict_proba(features_scaled)[0]
            predicted_class_idx = np.argmax(prediction_proba)
            predicted_class = self.label_encoders['relationship'].inverse_transform([predicted_class_idx])[0]
            confidence = float(prediction_proba[predicted_class_idx])

            # Determine confidence level
            if confidence > 0.8:
                conf_level = ConfidenceLevel.HIGH
            elif confidence > 0.6:
                conf_level = ConfidenceLevel.MEDIUM
            elif confidence > 0.4:
                conf_level = ConfidenceLevel.LOW
            else:
                conf_level = ConfidenceLevel.VERY_LOW

            # Generate supporting evidence
            supporting_evidence = [
                f"Current cooperation score: {current_rel.cooperation_score:.2f}",
                f"Relationship stability: {current_rel.stability_score:.2f}",
                f"Evidence pieces: {current_rel.evidence_count}",
                f"Shared issues: {len(current_rel.shared_issues)}"
            ]

            # Key factors (feature importance)
            key_factors = [
                "Historical cooperation patterns",
                "Relationship stability trends",
                "Frequency of interactions",
                "Shared policy interests"
            ]

            return Prediction(
                prediction_type=PredictionType.RELATIONSHIP_STRENGTH,
                target_entity=f"{official_1}_{official_2}",
                prediction_value=predicted_class,
                confidence_level=conf_level,
                confidence_score=confidence,
                prediction_horizon=horizon,
                key_factors=key_factors,
                supporting_evidence=supporting_evidence,
                uncertainty_factors=["External political changes", "New issue emergence"],
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error("Relationship prediction failed", error=str(e))
            return self._create_low_confidence_prediction(
                PredictionType.RELATIONSHIP_STRENGTH,
                f"{official_1}_{official_2}",
                "prediction_error",
                horizon
            )

    async def predict_coalition_formation(self, issue: str,
                                        horizon: PredictionHorizon) -> Prediction:
        """Predict likely coalition formation around an issue."""
        # Get all officials with positions on this issue
        issue_advocates = []
        for official, data in STATEN_ISLAND_OFFICIALS.items():
            focus_areas = data.get('focus_areas', [])
            if issue.lower() in [area.lower() for area in focus_areas]:
                issue_advocates.append(official)

        if len(issue_advocates) < 2:
            return self._create_low_confidence_prediction(
                PredictionType.COALITION_FORMATION,
                issue,
                {"coalition_size": 0, "members": []},
                horizon
            )

        # Analyze relationships between advocates
        coalition_strength = 0
        potential_members = []

        for i, official_1 in enumerate(issue_advocates):
            for j, official_2 in enumerate(issue_advocates[i+1:], i+1):
                rel = await self.relationship_tracker.analyze_relationship_pair(official_1, official_2)
                if rel and rel.cooperation_score > 0.6:
                    coalition_strength += rel.cooperation_score
                    if official_1 not in potential_members:
                        potential_members.append(official_1)
                    if official_2 not in potential_members:
                        potential_members.append(official_2)

        # Predict coalition likelihood
        coalition_probability = min(1.0, coalition_strength / len(issue_advocates))

        if coalition_probability > 0.7:
            conf_level = ConfidenceLevel.HIGH
        elif coalition_probability > 0.5:
            conf_level = ConfidenceLevel.MEDIUM
        else:
            conf_level = ConfidenceLevel.LOW

        return Prediction(
            prediction_type=PredictionType.COALITION_FORMATION,
            target_entity=issue,
            prediction_value={
                "coalition_probability": coalition_probability,
                "likely_members": potential_members,
                "coalition_size": len(potential_members)
            },
            confidence_level=conf_level,
            confidence_score=coalition_probability,
            prediction_horizon=horizon,
            key_factors=[
                "Historical cooperation patterns",
                "Shared issue focus",
                "Relationship strength between advocates"
            ],
            supporting_evidence=[
                f"Issue advocates identified: {len(issue_advocates)}",
                f"Strong relationships detected: {coalition_strength:.2f}",
                f"Potential coalition size: {len(potential_members)}"
            ],
            uncertainty_factors=[
                "Political climate changes",
                "New stakeholder entry",
                "Issue priority shifts"
            ],
            timestamp=datetime.now()
        )

    async def predict_influence_trajectory(self, official: str,
                                         horizon: PredictionHorizon) -> Prediction:
        """Predict an official's influence trajectory."""
        if not self.influence_model:
            await self.initialize_models()

        official_data = STATEN_ISLAND_OFFICIALS.get(official, {})
        if not official_data:
            return self._create_low_confidence_prediction(
                PredictionType.INFLUENCE_TRAJECTORY,
                official,
                "no_data",
                horizon
            )

        # Calculate current influence metrics
        achievements = official_data.get('achievements', [])
        current_year = datetime.now().year
        recent_achievements = [a for a in achievements if int(a.get('year', 2000)) >= current_year - 2]

        if not recent_achievements:
            return self._create_low_confidence_prediction(
                PredictionType.INFLUENCE_TRAJECTORY,
                official,
                "insufficient_recent_data",
                horizon
            )

        # Prepare features for prediction
        position_type = official_data.get('position_type', '')
        avg_achievement_length = sum(len(a.get('description', '')) for a in recent_achievements) / len(recent_achievements)

        try:
            # Encode features
            position_encoded = self.label_encoders['position_type'].transform([position_type])[0]
            achievement_type = recent_achievements[0].get('category', 'general')
            achievement_encoded = self.label_encoders['achievement_type'].transform([achievement_type])[0]

            features = np.array([[current_year, avg_achievement_length, position_encoded, achievement_encoded]])
            features_scaled = self.scalers['influence'].transform(features)

            # Make prediction
            predicted_influence = self.influence_model.predict(features_scaled)[0]

            # Calculate confidence based on model performance and data quality
            confidence = 0.7 if len(recent_achievements) >= 3 else 0.5

            if confidence > 0.6:
                conf_level = ConfidenceLevel.MEDIUM
            else:
                conf_level = ConfidenceLevel.LOW

            # Interpret trajectory
            current_influence = sum(self._calculate_influence_score(a) for a in recent_achievements) / len(recent_achievements)
            trajectory = "increasing" if predicted_influence > current_influence else "stable" if abs(predicted_influence - current_influence) < 0.1 else "declining"

            return Prediction(
                prediction_type=PredictionType.INFLUENCE_TRAJECTORY,
                target_entity=official,
                prediction_value={
                    "trajectory": trajectory,
                    "predicted_influence_score": float(predicted_influence),
                    "current_influence_score": float(current_influence)
                },
                confidence_level=conf_level,
                confidence_score=confidence,
                prediction_horizon=horizon,
                key_factors=[
                    "Recent achievement patterns",
                    "Position type influence potential",
                    "Historical influence trends"
                ],
                supporting_evidence=[
                    f"Recent achievements: {len(recent_achievements)}",
                    f"Current influence score: {current_influence:.2f}",
                    f"Position type: {position_type}"
                ],
                uncertainty_factors=[
                    "Electoral changes",
                    "Policy priority shifts",
                    "External political events"
                ],
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error("Influence prediction failed", official=official, error=str(e))
            return self._create_low_confidence_prediction(
                PredictionType.INFLUENCE_TRAJECTORY,
                official,
                "prediction_error",
                horizon
            )

    def _create_low_confidence_prediction(self, pred_type: PredictionType, target: str,
                                        value: Any, horizon: PredictionHorizon) -> Prediction:
        """Create a low-confidence prediction for insufficient data."""
        return Prediction(
            prediction_type=pred_type,
            target_entity=target,
            prediction_value=value,
            confidence_level=ConfidenceLevel.VERY_LOW,
            confidence_score=0.1,
            prediction_horizon=horizon,
            key_factors=["Insufficient historical data"],
            supporting_evidence=["Limited evidence available"],
            uncertainty_factors=["Data availability", "Model limitations"],
            timestamp=datetime.now()
        )

    async def generate_prediction_scenarios(self) -> List[PredictionScenario]:
        """Generate comprehensive prediction scenarios."""
        scenarios = []

        # Scenario 1: Increased Staten Island Coordination
        coordination_predictions = []
        key_officials = ["Charles Schumer", "Andrew Lanza", "Nicole Malliotakis"]

        for i, official_1 in enumerate(key_officials):
            for official_2 in key_officials[i+1:]:
                pred = await self.predict_relationship_evolution(
                    official_1, official_2, PredictionHorizon.MEDIUM_TERM
                )
                coordination_predictions.append(pred)

        scenarios.append(PredictionScenario(
            scenario_name="Enhanced Staten Island Federal-State Coordination",
            scenario_probability=0.7,
            component_predictions=coordination_predictions,
            scenario_description="Increased coordination between federal and state representatives on Staten Island priorities",
            key_assumptions=[
                "Continued shared focus on infrastructure",
                "Stable political relationships",
                "No major electoral changes"
            ],
            risk_factors=[
                "National political polarization",
                "Budget constraints",
                "Competing regional priorities"
            ]
        ))

        # Scenario 2: Infrastructure Coalition Formation
        infrastructure_pred = await self.predict_coalition_formation(
            "Infrastructure", PredictionHorizon.SHORT_TERM
        )

        scenarios.append(PredictionScenario(
            scenario_name="Staten Island Infrastructure Coalition",
            scenario_probability=0.6,
            component_predictions=[infrastructure_pred],
            scenario_description="Formation of strong multi-level coalition for infrastructure projects",
            key_assumptions=[
                "Federal infrastructure funding availability",
                "State budget support",
                "Local government alignment"
            ],
            risk_factors=[
                "Federal funding delays",
                "Environmental challenges",
                "Community opposition"
            ]
        ))

        # Scenario 3: Individual Influence Trajectories
        influence_predictions = []
        for official in ["Charles Schumer", "Andrew Lanza", "Nicole Malliotakis"]:
            influence_pred = await self.predict_influence_trajectory(
                official, PredictionHorizon.LONG_TERM
            )
            influence_predictions.append(influence_pred)

        scenarios.append(PredictionScenario(
            scenario_name="Individual Influence Evolution",
            scenario_probability=0.8,
            component_predictions=influence_predictions,
            scenario_description="Evolution of individual official influence over long term",
            key_assumptions=[
                "Continued tenure in current positions",
                "Stable political environment",
                "Consistent policy priorities"
            ],
            risk_factors=[
                "Electoral challenges",
                "Health considerations",
                "Political realignments"
            ]
        ))

        return scenarios

    async def generate_comprehensive_predictions(self) -> Dict[str, Any]:
        """Generate comprehensive predictive analysis report."""
        # Generate individual predictions
        relationship_predictions = {}
        officials = list(STATEN_ISLAND_OFFICIALS.keys())[:5]  # Limit for demo

        for i, official_1 in enumerate(officials):
            for official_2 in officials[i+1:]:
                key = f"{official_1}_{official_2}"
                pred = await self.predict_relationship_evolution(
                    official_1, official_2, PredictionHorizon.MEDIUM_TERM
                )
                relationship_predictions[key] = pred

        # Generate coalition predictions
        coalition_predictions = {}
        key_issues = ["Infrastructure", "Transportation", "Healthcare"]
        for issue in key_issues:
            pred = await self.predict_coalition_formation(issue, PredictionHorizon.MEDIUM_TERM)
            coalition_predictions[issue] = pred

        # Generate influence predictions
        influence_predictions = {}
        for official in officials[:3]:  # Top 3 officials
            pred = await self.predict_influence_trajectory(official, PredictionHorizon.LONG_TERM)
            influence_predictions[official] = pred

        # Generate scenarios
        scenarios = await self.generate_prediction_scenarios()

        return {
            "prediction_summary": {
                "total_relationship_predictions": len(relationship_predictions),
                "total_coalition_predictions": len(coalition_predictions),
                "total_influence_predictions": len(influence_predictions),
                "total_scenarios": len(scenarios),
                "generated_at": datetime.now().isoformat()
            },
            "relationship_predictions": {
                key: {
                    "prediction_value": pred.prediction_value,
                    "confidence_level": pred.confidence_level.value,
                    "confidence_score": pred.confidence_score,
                    "key_factors": pred.key_factors
                }
                for key, pred in relationship_predictions.items()
            },
            "coalition_predictions": {
                issue: {
                    "prediction_value": pred.prediction_value,
                    "confidence_level": pred.confidence_level.value,
                    "confidence_score": pred.confidence_score,
                    "key_factors": pred.key_factors
                }
                for issue, pred in coalition_predictions.items()
            },
            "influence_predictions": {
                official: {
                    "prediction_value": pred.prediction_value,
                    "confidence_level": pred.confidence_level.value,
                    "confidence_score": pred.confidence_score,
                    "key_factors": pred.key_factors
                }
                for official, pred in influence_predictions.items()
            },
            "prediction_scenarios": [
                {
                    "scenario_name": scenario.scenario_name,
                    "scenario_probability": scenario.scenario_probability,
                    "description": scenario.scenario_description,
                    "prediction_count": len(scenario.component_predictions),
                    "key_assumptions": scenario.key_assumptions,
                    "risk_factors": scenario.risk_factors
                }
                for scenario in scenarios
            ]
        }
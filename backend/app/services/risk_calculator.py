import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskCalculatorService:
    """
    Service for calculating
    overall risk scores
    """

    def __init__(self):

        self.risk_weights = {
            "behavioral": 0.25,
            "document": 0.25,
            "biometric": 0.20,
            "intelligence": 0.30
        }

    def calculate_risk_score(
        self,
        risk_factors: Dict
    ) -> Dict:
        """
        Calculate overall risk score
        """

        try:

            behavioral = max(
                0,
                min(
                    1,
                    risk_factors.get(
                        "behavioral_risk",
                        0.0
                    )
                )
            )

            document = max(
                0,
                min(
                    1,
                    risk_factors.get(
                        "document_risk",
                        0.0
                    )
                )
            )

            biometric = max(
                0,
                min(
                    1,
                    risk_factors.get(
                        "biometric_risk",
                        0.0
                    )
                )
            )

            intelligence = max(
                0,
                min(
                    1,
                    risk_factors.get(
                        "intelligence_match_risk",
                        0.0
                    )
                )
            )

            weighted_score = (

                behavioral *
                self.risk_weights[
                    "behavioral"
                ]

                +

                document *
                self.risk_weights[
                    "document"
                ]

                +

                biometric *
                self.risk_weights[
                    "biometric"
                ]

                +

                intelligence *
                self.risk_weights[
                    "intelligence"
                ]
            )

            risk_score = round(
                max(
                    0.0,
                    min(
                        1.0,
                        weighted_score
                    )
                ),
                3
            )

            risk_level = (
                self
                ._get_risk_level(
                    risk_score
                )
            )

            recommendations = (
                self
                ._get_recommendations(
                    risk_level
                )
            )

            logger.info(
                f"Risk score "
                f"calculated: "
                f"{risk_score}"
            )

            return {

                "success": True,

                "risk_score":
                    risk_score,

                "risk_percentage":
                    round(
                        risk_score * 100,
                        2
                    ),

                "risk_level":
                    risk_level,

                "components": {

                    "behavioral":
                        behavioral,

                    "document":
                        document,

                    "biometric":
                        biometric,

                    "intelligence":
                        intelligence
                },

                "weights":
                    self.risk_weights,

                "recommendations":
                    recommendations,

                "timestamp":
                    datetime
                    .utcnow()
                    .isoformat()
            }

        except Exception as e:

            logger.exception(
                str(e)
            )

            return {
                "success": False,
                "error": str(e),
                "risk_score": 0.0,
                "risk_level": "UNKNOWN"
            }

    def get_risk_indicators(
        self,
        person_data: Dict
    ) -> List[str]:

        indicators = []

        age = person_data.get(
            "age_estimated"
        )

        if (
            age and
            (
                age < 18 or
                age > 65
            )
        ):
            indicators.append(
                f"Age anomaly: "
                f"{age}"
            )

        document_status = (
            person_data.get(
                "document_status"
            )
        )

        if (
            document_status
            ==
            "expired"
        ):
            indicators.append(
                "Expired document"
            )

        elif (
            document_status
            ==
            "suspicious"
        ):
            indicators.append(
                "Suspicious document"
            )

        confidence = (
            person_data.get(
                "detection_confidence",
                1.0
            )
        )

        if confidence < 0.70:
            indicators.append(
                f"Low confidence: "
                f"{confidence}"
            )

        if person_data.get(
            "behavioral_flags"
        ):

            for flag in (
                person_data[
                    "behavioral_flags"
                ]
            ):

                indicators.append(
                    f"Behavioral: "
                    f"{flag}"
                )

        if person_data.get(
            "face_match"
        ) is False:

            indicators.append(
                "Face mismatch"
            )

        if person_data.get(
            "watchlist_match"
        ):

            indicators.append(
                "Watchlist hit"
            )

        return indicators

    @staticmethod
    def _get_risk_level(
        score: float
    ):

        if score >= 0.80:
            return "CRITICAL"

        elif score >= 0.60:
            return "HIGH"

        elif score >= 0.40:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _get_recommendations(
        level: str
    ):

        recommendations = {

            "LOW": [
                "Allow passage"
            ],

            "MEDIUM": [
                "Secondary screening"
            ],

            "HIGH": [
                "Manual inspection",
                "Verify documents"
            ],

            "CRITICAL": [
                "Detain person",
                "Notify security",
                "Start investigation"
            ]
        }

        return (
            recommendations
            .get(
                level,
                []
            )
        )

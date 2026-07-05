def analyze_person(self, person_data: Dict) -> Dict:
    """
    Analyze person using ML model + rule fallback
    """

    try:
        threat_indicators = []

        # ---------------------
        # Threat DB matching
        # ---------------------
        matches = self._check_threat_database(
            person_data
        )

        intelligence_risk = (
            1.0 if matches else 0.0
        )

        if matches:
            for match in matches:
                threat_indicators.append(
                    f"Threat match: "
                    f"{match['type']}"
                )

        # ---------------------
        # Document risk
        # ---------------------
        document_risk = 0.0

        if (
            person_data.get(
                "document_status"
            )
            == "suspicious"
        ):
            document_risk = 1.0

            threat_indicators.append(
                "Suspicious document"
            )

        # ---------------------
        # Behavioral risk
        # ---------------------
        behavioral_risk = 0.0

        if person_data.get(
            "behavioral_flags"
        ):
            behavioral_risk = 1.0

            threat_indicators.append(
                "Behavioral anomaly"
            )

        # ---------------------
        # Face risk
        # ---------------------
        face_confidence = (
            person_data.get(
                "face_confidence",
                1.0
            )
        )

        biometric_risk = (
            1.0 - face_confidence
        )

        # ---------------------
        # Use trained ML model
        # ---------------------
        if self.model:

            features = [[
                behavioral_risk,
                document_risk,
                biometric_risk,
                intelligence_risk
            ]]

            threat_score = float(
                self.model
                .predict_proba(
                    features
                )[0][1]
            )

        # ---------------------
        # Rule fallback
        # ---------------------
        else:

            threat_score = (
                behavioral_risk * 0.25
                + document_risk * 0.25
                + biometric_risk * 0.20
                + intelligence_risk * 0.30
            )

        threat_score = max(
            0.0,
            min(
                1.0,
                threat_score
            )
        )

        logger.info(
            f"Threat analysis "
            f"completed for "
            f"{person_data.get('id')}"
        )

        return {
            "success": True,

            "person_id":
                person_data.get(
                    "id"
                ),

            "threat_score":
                threat_score,

            "threat_level":
                self._calculate_threat_level(
                    threat_score
                ),

            "matches":
                matches,

            "indicators":
                threat_indicators,

            "components": {
                "behavioral":
                    behavioral_risk,

                "document":
                    document_risk,

                "biometric":
                    biometric_risk,

                "intelligence":
                    intelligence_risk
            },

            "timestamp":
                datetime.utcnow()
                .isoformat()
        }

    except Exception as e:

        logger.exception(
            f"Threat analysis "
            f"error: {e}"
        )

        return {
            "success": False,
            "error": str(e),
            "threat_score": 0.0,
            "indicators": []
        }

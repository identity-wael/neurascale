"""Analysis resolver implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import random

from ..schema.types import Analysis

logger = logging.getLogger(__name__)


class AnalysisResolver:
    """Resolver for analysis-related queries."""

    def __init__(self):
        """Initialize analysis resolver."""
        self.analyses_db = self._create_mock_analyses()

    def _create_mock_analyses(self) -> Dict[str, Analysis]:
        """Create mock analyses for testing."""
        analyses = {}
        analysis_types = [
            "spectral_analysis",
            "connectivity_analysis",
            "erp_analysis",
            "source_localization",
            "artifact_detection",
            "seizure_detection",
            "sleep_staging",
            "cognitive_state_classification",
        ]

        for i in range(200):
            analysis_id = f"ana_{i + 1:06d}"
            session_id = f"ses_{(i % 100) + 1:06d}"

            # Generate timestamps
            hours_ago = random.randint(0, 72)
            created_at = datetime.utcnow() - timedelta(hours=hours_ago)

            # Determine status and completion time
            status = random.choice(["completed", "processing", "failed", "queued"])
            if status == "completed":
                processing_time = random.uniform(30, 300)  # 30 seconds to 5 minutes
                completed_at = created_at + timedelta(seconds=processing_time)
                results = self._generate_mock_results(
                    analysis_types[i % len(analysis_types)]
                )
            else:
                completed_at = None
                results = None

            analysis = Analysis(
                id=analysis_id,
                session_id=session_id,
                type=analysis_types[i % len(analysis_types)],
                status=status,
                created_at=created_at,
                completed_at=completed_at,
                results=results,
            )
            analyses[analysis_id] = analysis

        return analyses

    def _generate_mock_results(self, analysis_type: str) -> Dict[str, Any]:
        """Generate mock results based on analysis type."""
        if analysis_type == "spectral_analysis":
            return {
                "dominant_frequency": random.uniform(8, 12),
                "band_powers": {
                    "delta": random.uniform(10, 30),
                    "theta": random.uniform(15, 35),
                    "alpha": random.uniform(20, 40),
                    "beta": random.uniform(10, 25),
                    "gamma": random.uniform(5, 15),
                },
                "peak_frequencies": {
                    "alpha": random.uniform(9, 11),
                    "beta": random.uniform(15, 25),
                },
            }
        elif analysis_type == "connectivity_analysis":
            return {
                "coherence_matrix": [
                    [random.random() for _ in range(32)] for _ in range(32)
                ],
                "phase_lag_index": random.uniform(0.1, 0.9),
                "granger_causality": {
                    "significant_connections": random.randint(5, 20),
                    "average_strength": random.uniform(0.1, 0.5),
                },
            }
        elif analysis_type == "seizure_detection":
            return {
                "seizures_detected": random.randint(0, 3),
                "seizure_probability": random.uniform(0, 0.3),
                "high_risk_periods": [
                    {
                        "start": random.randint(0, 300),
                        "end": random.randint(300, 600),
                        "confidence": random.uniform(0.7, 0.95),
                    }
                ],
            }
        else:
            return {
                "summary": f"Analysis completed for {analysis_type}",
                "confidence": random.uniform(0.7, 0.99),
                "processing_time_seconds": random.uniform(10, 300),
            }

    async def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        """Get an analysis by ID."""
        return self.analyses_db.get(analysis_id)

    async def get_analyses_by_session(self, session_id: str) -> List[Analysis]:
        """Get all analyses for a session."""
        session_analyses = [
            analysis
            for analysis in self.analyses_db.values()
            if analysis.session_id == session_id
        ]

        # Sort by creation time (newest first)
        session_analyses.sort(key=lambda a: a.created_at, reverse=True)

        return session_analyses

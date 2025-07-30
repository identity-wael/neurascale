"""Analysis MCP Server implementation."""

from typing import Dict, Any, List, Optional

from ...core.base_server import BaseNeuralMCPServer
from ...utils.validators import (
    validate_analysis_params,
    validate_model_params,
    validate_prediction_params,
)
from .handlers import AnalysisHandlers


class AnalysisMCPServer(BaseNeuralMCPServer):
    """MCP server for advanced neural data analysis and ML operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Analysis MCP server.

        Args:
            config: Server configuration
        """
        super().__init__("neurascale-analysis", "1.0.0", config)

        # Initialize handlers
        self.handlers = AnalysisHandlers(config.get("analysis_engine", {}))

    async def register_tools(self) -> None:
        """Register all analysis tools."""

        # Time-Frequency Analysis
        self.register_tool(
            name="compute_time_frequency",
            handler=self._compute_time_frequency,
            description="Compute time-frequency representation of neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to analyze",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["morlet", "multitaper", "stockwell", "hilbert"],
                        "default": "morlet",
                        "description": "Time-frequency method",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [1, 100],
                        "description": "Frequency range [min, max] in Hz",
                    },
                    "time_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Time range [start, end] in seconds",
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "n_cycles": {"type": "number", "default": 7},
                            "output": {
                                "type": "string",
                                "enum": ["power", "phase", "complex"],
                                "default": "power",
                            },
                        },
                        "description": "Method-specific parameters",
                    },
                },
                "required": ["session_id"],
            },
            permissions=["analysis.compute", "neural_data.read"],
        )

        # Connectivity Analysis
        self.register_tool(
            name="analyze_connectivity",
            handler=self._analyze_connectivity,
            description="Analyze functional connectivity between brain regions",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "method": {
                        "type": "string",
                        "enum": [
                            "coherence",
                            "plv",
                            "pli",
                            "granger_causality",
                            "transfer_entropy",
                            "mutual_information",
                        ],
                        "description": "Connectivity method",
                    },
                    "channel_pairs": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2,
                        },
                        "description": "Channel pairs to analyze (optional, all pairs if not specified)",
                    },
                    "frequency_bands": {
                        "type": "object",
                        "properties": {
                            "delta": {"type": "array", "default": [0.5, 4]},
                            "theta": {"type": "array", "default": [4, 8]},
                            "alpha": {"type": "array", "default": [8, 13]},
                            "beta": {"type": "array", "default": [13, 30]},
                            "gamma": {"type": "array", "default": [30, 100]},
                        },
                        "description": "Frequency bands for analysis",
                    },
                    "window_size": {
                        "type": "number",
                        "minimum": 0.1,
                        "default": 1.0,
                        "description": "Window size in seconds",
                    },
                    "overlap": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 0.95,
                        "default": 0.5,
                        "description": "Window overlap (0-1)",
                    },
                },
                "required": ["session_id", "method"],
            },
            permissions=["analysis.connectivity", "neural_data.read"],
        )

        # Source Localization
        self.register_tool(
            name="localize_sources",
            handler=self._localize_sources,
            description="Perform source localization of neural activity",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["mne", "loreta", "beamformer", "dipole_fit"],
                        "description": "Source localization method",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Time window for localization [start, end] in seconds",
                    },
                    "frequency_band": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Frequency band for analysis [min, max] Hz",
                    },
                    "head_model": {
                        "type": "string",
                        "enum": ["spherical", "realistic", "individual"],
                        "default": "spherical",
                        "description": "Head model type",
                    },
                    "noise_covariance": {
                        "type": "string",
                        "description": "Noise covariance matrix ID (optional)",
                    },
                },
                "required": ["session_id", "method"],
            },
            permissions=["analysis.source_localization", "neural_data.read"],
        )

        # Event-Related Analysis
        self.register_tool(
            name="analyze_events",
            handler=self._analyze_events,
            description="Analyze event-related potentials/fields",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "event_markers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event markers to analyze",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["erp", "erf", "time_frequency", "induced", "evoked"],
                        "description": "Type of event-related analysis",
                    },
                    "epoch_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-0.2, 0.8],
                        "description": "Epoch window [pre, post] in seconds",
                    },
                    "baseline": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-0.2, 0],
                        "description": "Baseline period [start, end] in seconds",
                    },
                    "reject_criteria": {
                        "type": "object",
                        "properties": {
                            "eeg": {
                                "type": "number",
                                "description": "EEG rejection threshold (μV)",
                            },
                            "eog": {
                                "type": "number",
                                "description": "EOG rejection threshold (μV)",
                            },
                            "emg": {
                                "type": "number",
                                "description": "EMG rejection threshold (μV)",
                            },
                        },
                        "description": "Artifact rejection criteria",
                    },
                },
                "required": ["session_id", "event_markers", "analysis_type"],
            },
            permissions=["analysis.events", "neural_data.read"],
        )

        # Machine Learning Models
        self.register_tool(
            name="train_classifier",
            handler=self._train_classifier,
            description="Train a machine learning classifier on neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Training dataset identifier",
                    },
                    "model_type": {
                        "type": "string",
                        "enum": [
                            "svm",
                            "random_forest",
                            "neural_network",
                            "xgboost",
                            "riemannian",
                        ],
                        "description": "Type of classifier",
                    },
                    "target_variable": {
                        "type": "string",
                        "description": "Target variable to predict",
                    },
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Features to use for training",
                    },
                    "validation_method": {
                        "type": "string",
                        "enum": [
                            "cross_validation",
                            "train_test_split",
                            "time_series_split",
                        ],
                        "default": "cross_validation",
                        "description": "Validation method",
                    },
                    "hyperparameters": {
                        "type": "object",
                        "description": "Model-specific hyperparameters",
                    },
                    "optimization": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["grid_search", "random_search", "bayesian"],
                                "default": "random_search",
                            },
                            "metric": {
                                "type": "string",
                                "enum": ["accuracy", "f1", "auc", "balanced_accuracy"],
                                "default": "balanced_accuracy",
                            },
                            "cv_folds": {"type": "integer", "minimum": 2, "default": 5},
                        },
                        "description": "Hyperparameter optimization settings",
                    },
                },
                "required": ["dataset_id", "model_type", "target_variable"],
            },
            permissions=["ml.train", "data.read"],
        )

        self.register_tool(
            name="predict_neural_states",
            handler=self._predict_neural_states,
            description="Predict neural states using trained models",
            input_schema={
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "Trained model identifier",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session to make predictions on",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Time window for prediction [start, end] seconds",
                    },
                    "sliding_window": {
                        "type": "object",
                        "properties": {
                            "size": {"type": "number", "default": 1.0},
                            "step": {"type": "number", "default": 0.1},
                        },
                        "description": "Sliding window parameters",
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.5,
                        "description": "Minimum confidence for predictions",
                    },
                },
                "required": ["model_id", "session_id"],
            },
            permissions=["ml.predict", "neural_data.read"],
        )

        # Deep Learning Analysis
        self.register_tool(
            name="run_deep_analysis",
            handler=self._run_deep_analysis,
            description="Run deep learning analysis on neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "architecture": {
                        "type": "string",
                        "enum": ["cnn", "lstm", "transformer", "wavenet", "eegnet"],
                        "description": "Deep learning architecture",
                    },
                    "task": {
                        "type": "string",
                        "enum": [
                            "classification",
                            "regression",
                            "sequence_prediction",
                            "anomaly_detection",
                            "representation_learning",
                        ],
                        "description": "Analysis task",
                    },
                    "pretrained_model": {
                        "type": "string",
                        "description": "ID of pretrained model to use (optional)",
                    },
                    "training_config": {
                        "type": "object",
                        "properties": {
                            "epochs": {"type": "integer", "minimum": 1, "default": 100},
                            "batch_size": {
                                "type": "integer",
                                "minimum": 1,
                                "default": 32,
                            },
                            "learning_rate": {"type": "number", "default": 0.001},
                            "early_stopping": {"type": "boolean", "default": True},
                        },
                        "description": "Training configuration",
                    },
                },
                "required": ["session_id", "architecture", "task"],
            },
            permissions=["deep_learning.run", "neural_data.read"],
        )

        # Statistical Analysis
        self.register_tool(
            name="statistical_analysis",
            handler=self._statistical_analysis,
            description="Perform statistical analysis on neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "dataset_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "description": "Dataset identifiers to analyze",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": [
                            "hypothesis_test",
                            "correlation",
                            "regression",
                            "anova",
                            "time_series",
                            "clustering",
                        ],
                        "description": "Type of statistical analysis",
                    },
                    "variables": {
                        "type": "object",
                        "properties": {
                            "dependent": {"type": "string"},
                            "independent": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "covariates": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "description": "Variables for analysis",
                    },
                    "test_parameters": {
                        "type": "object",
                        "properties": {
                            "alpha": {"type": "number", "default": 0.05},
                            "correction": {
                                "type": "string",
                                "enum": ["none", "bonferroni", "fdr", "holm"],
                                "default": "fdr",
                            },
                            "test_type": {"type": "string"},
                        },
                        "description": "Statistical test parameters",
                    },
                },
                "required": ["dataset_ids", "analysis_type"],
            },
            permissions=["analysis.statistics", "data.read"],
        )

        # Biomarker Discovery
        self.register_tool(
            name="discover_biomarkers",
            handler=self._discover_biomarkers,
            description="Discover neural biomarkers for conditions",
            input_schema={
                "type": "object",
                "properties": {
                    "cohort_id": {
                        "type": "string",
                        "description": "Patient cohort identifier",
                    },
                    "condition": {
                        "type": "string",
                        "description": "Condition to find biomarkers for",
                    },
                    "data_modalities": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["eeg", "meg", "fmri", "fnirs", "combined"],
                        },
                        "description": "Data modalities to analyze",
                    },
                    "feature_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "spectral",
                                "temporal",
                                "connectivity",
                                "nonlinear",
                                "morphological",
                            ],
                        },
                        "default": ["spectral", "temporal", "connectivity"],
                        "description": "Types of features to extract",
                    },
                    "validation_strategy": {
                        "type": "string",
                        "enum": ["cross_validation", "external", "prospective"],
                        "default": "cross_validation",
                        "description": "Validation strategy",
                    },
                    "significance_threshold": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.01,
                        "description": "Statistical significance threshold",
                    },
                },
                "required": ["cohort_id", "condition", "data_modalities"],
            },
            permissions=["biomarker.discover", "cohort.read"],
        )

        # Real-time Analysis
        self.register_tool(
            name="setup_realtime_analysis",
            handler=self._setup_realtime_analysis,
            description="Setup real-time neural data analysis pipeline",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device to stream data from",
                    },
                    "pipeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "stage": {"type": "string"},
                                "method": {"type": "string"},
                                "parameters": {"type": "object"},
                            },
                            "required": ["stage", "method"],
                        },
                        "description": "Analysis pipeline stages",
                    },
                    "output_config": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["stream", "events", "metrics"],
                            },
                            "destination": {"type": "string"},
                            "update_rate": {"type": "number", "default": 10},
                        },
                        "description": "Output configuration",
                    },
                    "buffer_size": {
                        "type": "integer",
                        "minimum": 100,
                        "default": 1000,
                        "description": "Buffer size in samples",
                    },
                },
                "required": ["device_id", "pipeline"],
            },
            permissions=["realtime.setup", "device.read"],
        )

        # Report Generation
        self.register_tool(
            name="generate_analysis_report",
            handler=self._generate_analysis_report,
            description="Generate comprehensive analysis report",
            input_schema={
                "type": "object",
                "properties": {
                    "analysis_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Analysis results to include",
                    },
                    "report_type": {
                        "type": "string",
                        "enum": [
                            "technical",
                            "clinical",
                            "research",
                            "executive_summary",
                        ],
                        "default": "technical",
                        "description": "Type of report",
                    },
                    "include_visualizations": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include visualizations",
                    },
                    "include_raw_data": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include raw data",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "html", "jupyter", "latex"],
                        "default": "pdf",
                        "description": "Report format",
                    },
                },
                "required": ["analysis_ids"],
            },
            permissions=["report.generate", "analysis.read"],
        )

    # Tool Implementation Methods
    async def _compute_time_frequency(
        self,
        session_id: str,
        channels: Optional[List[int]] = None,
        method: str = "morlet",
        freq_range: List[float] = None,
        time_range: Optional[List[float]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compute time-frequency representation."""
        if freq_range is None:
            freq_range = [1, 100]

        # Validate parameters
        validate_analysis_params(
            {
                "session_id": session_id,
                "method": method,
                "freq_range": freq_range,
            }
        )

        return await self.handlers.compute_time_frequency(
            session_id=session_id,
            channels=channels,
            method=method,
            freq_range=freq_range,
            time_range=time_range,
            parameters=parameters or {},
        )

    async def _analyze_connectivity(
        self,
        session_id: str,
        method: str,
        channel_pairs: Optional[List[List[int]]] = None,
        frequency_bands: Optional[Dict[str, List[float]]] = None,
        window_size: float = 1.0,
        overlap: float = 0.5,
    ) -> Dict[str, Any]:
        """Analyze functional connectivity."""
        return await self.handlers.analyze_connectivity(
            session_id=session_id,
            method=method,
            channel_pairs=channel_pairs,
            frequency_bands=frequency_bands,
            window_size=window_size,
            overlap=overlap,
        )

    async def _localize_sources(
        self,
        session_id: str,
        method: str,
        time_window: Optional[List[float]] = None,
        frequency_band: Optional[List[float]] = None,
        head_model: str = "spherical",
        noise_covariance: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform source localization."""
        return await self.handlers.localize_sources(
            session_id=session_id,
            method=method,
            time_window=time_window,
            frequency_band=frequency_band,
            head_model=head_model,
            noise_covariance=noise_covariance,
        )

    async def _analyze_events(
        self,
        session_id: str,
        event_markers: List[str],
        analysis_type: str,
        epoch_window: List[float] = None,
        baseline: List[float] = None,
        reject_criteria: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Analyze event-related activity."""
        if epoch_window is None:
            epoch_window = [-0.2, 0.8]
        if baseline is None:
            baseline = [-0.2, 0]

        return await self.handlers.analyze_events(
            session_id=session_id,
            event_markers=event_markers,
            analysis_type=analysis_type,
            epoch_window=epoch_window,
            baseline=baseline,
            reject_criteria=reject_criteria or {},
        )

    async def _train_classifier(
        self,
        dataset_id: str,
        model_type: str,
        target_variable: str,
        features: Optional[List[str]] = None,
        validation_method: str = "cross_validation",
        hyperparameters: Optional[Dict[str, Any]] = None,
        optimization: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Train ML classifier."""
        # Validate parameters
        validate_model_params(
            {
                "model_type": model_type,
                "validation_method": validation_method,
            }
        )

        return await self.handlers.train_classifier(
            dataset_id=dataset_id,
            model_type=model_type,
            target_variable=target_variable,
            features=features,
            validation_method=validation_method,
            hyperparameters=hyperparameters or {},
            optimization=optimization or {},
        )

    async def _predict_neural_states(
        self,
        model_id: str,
        session_id: str,
        time_window: Optional[List[float]] = None,
        sliding_window: Optional[Dict[str, float]] = None,
        confidence_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Predict neural states."""
        # Validate parameters
        validate_prediction_params(
            {
                "model_id": model_id,
                "confidence_threshold": confidence_threshold,
            }
        )

        return await self.handlers.predict_neural_states(
            model_id=model_id,
            session_id=session_id,
            time_window=time_window,
            sliding_window=sliding_window or {"size": 1.0, "step": 0.1},
            confidence_threshold=confidence_threshold,
        )

    async def _run_deep_analysis(
        self,
        session_id: str,
        architecture: str,
        task: str,
        pretrained_model: Optional[str] = None,
        training_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run deep learning analysis."""
        return await self.handlers.run_deep_analysis(
            session_id=session_id,
            architecture=architecture,
            task=task,
            pretrained_model=pretrained_model,
            training_config=training_config or {},
        )

    async def _statistical_analysis(
        self,
        dataset_ids: List[str],
        analysis_type: str,
        variables: Optional[Dict[str, Any]] = None,
        test_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform statistical analysis."""
        return await self.handlers.statistical_analysis(
            dataset_ids=dataset_ids,
            analysis_type=analysis_type,
            variables=variables or {},
            test_parameters=test_parameters or {},
        )

    async def _discover_biomarkers(
        self,
        cohort_id: str,
        condition: str,
        data_modalities: List[str],
        feature_types: List[str] = None,
        validation_strategy: str = "cross_validation",
        significance_threshold: float = 0.01,
    ) -> Dict[str, Any]:
        """Discover biomarkers."""
        if feature_types is None:
            feature_types = ["spectral", "temporal", "connectivity"]

        return await self.handlers.discover_biomarkers(
            cohort_id=cohort_id,
            condition=condition,
            data_modalities=data_modalities,
            feature_types=feature_types,
            validation_strategy=validation_strategy,
            significance_threshold=significance_threshold,
        )

    async def _setup_realtime_analysis(
        self,
        device_id: str,
        pipeline: List[Dict[str, Any]],
        output_config: Optional[Dict[str, Any]] = None,
        buffer_size: int = 1000,
    ) -> Dict[str, Any]:
        """Setup real-time analysis."""
        return await self.handlers.setup_realtime_analysis(
            device_id=device_id,
            pipeline=pipeline,
            output_config=output_config or {},
            buffer_size=buffer_size,
        )

    async def _generate_analysis_report(
        self,
        analysis_ids: List[str],
        report_type: str = "technical",
        include_visualizations: bool = True,
        include_raw_data: bool = False,
        format: str = "pdf",
    ) -> Dict[str, Any]:
        """Generate analysis report."""
        return await self.handlers.generate_analysis_report(
            analysis_ids=analysis_ids,
            report_type=report_type,
            include_visualizations=include_visualizations,
            include_raw_data=include_raw_data,
            format=format,
        )

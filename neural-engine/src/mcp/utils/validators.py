"""Input validation utilities for MCP servers."""

from typing import Any, Dict
import jsonschema
from jsonschema import validate, ValidationError


def validate_tool_input(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Validate tool input against JSON schema.

    Args:
        data: Input data to validate
        schema: JSON schema for validation

    Raises:
        ValueError: If validation fails
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        # Create more user-friendly error message
        error_path = " -> ".join(str(p) for p in e.absolute_path)
        if error_path:
            raise ValueError(f"Validation error at '{error_path}': {e.message}")
        else:
            raise ValueError(f"Validation error: {e.message}")


def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """Validate that a dictionary is a valid JSON schema.

    Args:
        schema: Schema to validate

    Returns:
        True if valid schema

    Raises:
        ValueError: If schema is invalid
    """
    try:
        # Use Draft 7 meta-schema for validation
        meta_schema = jsonschema.Draft7Validator.META_SCHEMA
        jsonschema.validate(schema, meta_schema)
        return True
    except ValidationError as e:
        raise ValueError(f"Invalid JSON schema: {e.message}")


def validate_mcp_request(request: Dict[str, Any]) -> None:
    """Validate MCP request structure.

    Args:
        request: MCP request to validate

    Raises:
        ValueError: If request is invalid
    """
    # Basic JSON-RPC 2.0 structure
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")

    if request.get("jsonrpc") != "2.0":
        raise ValueError("Request must have jsonrpc: '2.0'")

    if "method" not in request:
        raise ValueError("Request must have a 'method' field")

    if not isinstance(request["method"], str):
        raise ValueError("Method must be a string")

    # Validate ID if present
    if "id" in request:
        if not isinstance(request["id"], (str, int, type(None))):
            raise ValueError("ID must be a string, number, or null")

    # Validate params if present
    if "params" in request:
        if not isinstance(request["params"], (dict, list)):
            raise ValueError("Params must be an object or array")


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if format is valid

    Raises:
        ValueError: If format is invalid
    """
    if not isinstance(api_key, str):
        raise ValueError("API key must be a string")

    if len(api_key) < 32:
        raise ValueError("API key must be at least 32 characters long")

    if len(api_key) > 128:
        raise ValueError("API key must be at most 128 characters long")

    # Check for basic format (alphanumeric + some special chars)
    import re

    if not re.match(r"^[A-Za-z0-9_\-\.]+$", api_key):
        raise ValueError("API key contains invalid characters")

    return True


def validate_session_id_format(session_id: str) -> bool:
    """Validate session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if format is valid

    Raises:
        ValueError: If format is invalid
    """
    if not isinstance(session_id, str):
        raise ValueError("Session ID must be a string")

    import re

    # UUID format or similar
    if not re.match(r"^[A-Za-z0-9\-]{8,64}$", session_id):
        raise ValueError("Invalid session ID format")

    return True


def validate_neural_data_params(params: Dict[str, Any]) -> None:
    """Validate neural data query parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Session ID is required
    if "session_id" not in params:
        raise ValueError("session_id is required")

    validate_session_id_format(params["session_id"])

    # Validate channels if provided
    if "channels" in params:
        channels = params["channels"]
        if not isinstance(channels, list):
            raise ValueError("channels must be a list")

        if not all(isinstance(ch, int) and ch >= 0 for ch in channels):
            raise ValueError("channels must be non-negative integers")

        if len(channels) > 512:  # Reasonable upper limit
            raise ValueError("Too many channels specified (max 512)")

    # Validate time ranges if provided
    if "start_time" in params:
        start_time = params["start_time"]
        if not isinstance(start_time, (int, float)) or start_time < 0:
            raise ValueError("start_time must be a non-negative number")

    if "end_time" in params:
        end_time = params["end_time"]
        if not isinstance(end_time, (int, float)) or end_time < 0:
            raise ValueError("end_time must be a non-negative number")

        # Check time ordering
        if "start_time" in params and end_time <= params["start_time"]:
            raise ValueError("end_time must be greater than start_time")

    # Validate downsample factor
    if "downsample_factor" in params:
        factor = params["downsample_factor"]
        if not isinstance(factor, int) or factor < 1 or factor > 100:
            raise ValueError("downsample_factor must be an integer between 1 and 100")


def validate_device_params(params: Dict[str, Any]) -> None:
    """Validate device control parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Device ID validation
    if "device_id" in params:
        device_id = params["device_id"]
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("device_id must be a non-empty string")

    # Device type validation
    if "device_type" in params:
        device_type = params["device_type"]
        valid_types = ["EEG", "EMG", "ECG", "fNIRS", "TMS", "tDCS", "HYBRID"]
        if device_type not in valid_types:
            raise ValueError(f"device_type must be one of: {valid_types}")

    # Status validation
    if "status" in params:
        status = params["status"]
        valid_statuses = ["connected", "disconnected", "all"]
        if status not in valid_statuses:
            raise ValueError(f"status must be one of: {valid_statuses}")


def validate_filter_params(params: Dict[str, Any]) -> None:
    """Validate signal processing filter parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Filter type is required
    if "filter_type" not in params:
        raise ValueError("filter_type is required")

    filter_type = params["filter_type"]
    valid_types = ["bandpass", "highpass", "lowpass", "notch"]
    if filter_type not in valid_types:
        raise ValueError(f"filter_type must be one of: {valid_types}")

    # Frequency validation
    if "low_freq" in params:
        low_freq = params["low_freq"]
        if not isinstance(low_freq, (int, float)) or low_freq <= 0:
            raise ValueError("low_freq must be a positive number")
        if low_freq > 1000:  # Reasonable upper limit
            raise ValueError("low_freq must be <= 1000 Hz")

    if "high_freq" in params:
        high_freq = params["high_freq"]
        if not isinstance(high_freq, (int, float)) or high_freq <= 0:
            raise ValueError("high_freq must be a positive number")
        if high_freq > 1000:  # Reasonable upper limit
            raise ValueError("high_freq must be <= 1000 Hz")

        # Check frequency ordering for bandpass
        if filter_type == "bandpass" and "low_freq" in params:
            if high_freq <= params["low_freq"]:
                raise ValueError(
                    "high_freq must be greater than low_freq for bandpass filter"
                )

    # Filter order validation
    if "order" in params:
        order = params["order"]
        if not isinstance(order, int) or order < 1 or order > 20:
            raise ValueError("order must be an integer between 1 and 20")


def validate_clinical_protocol_params(params: Dict[str, Any]) -> None:
    """Validate clinical protocol parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Required parameters
    required = ["protocol_id", "patient_id", "device_id"]
    for param in required:
        if param not in params:
            raise ValueError(f"{param} is required")
        if not isinstance(params[param], str) or not params[param].strip():
            raise ValueError(f"{param} must be a non-empty string")

    # Validate protocol parameters if provided
    if "parameters" in params:
        protocol_params = params["parameters"]
        if not isinstance(protocol_params, dict):
            raise ValueError("parameters must be an object")


def validate_export_params(params: Dict[str, Any]) -> None:
    """Validate data export parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Session ID is required
    if "session_id" not in params:
        raise ValueError("session_id is required")

    validate_session_id_format(params["session_id"])

    # Format validation
    if "format" not in params:
        raise ValueError("format is required")

    format_type = params["format"]
    valid_formats = ["json", "csv", "edf", "mat", "fif", "parquet"]
    if format_type not in valid_formats:
        raise ValueError(f"format must be one of: {valid_formats}")

    # Options validation
    if "options" in params:
        options = params["options"]
        if not isinstance(options, dict):
            raise ValueError("options must be an object")


def sanitize_string_input(value: str, max_length: int = 1000) -> str:
    """Sanitize string input by removing/escaping potentially harmful content.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValueError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Check length
    if len(value) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")

    # Remove control characters except common whitespace
    import re

    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

    # Basic HTML/script tag removal (very basic)
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    return sanitized.strip()


def validate_pagination_params(params: Dict[str, Any]) -> None:
    """Validate pagination parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    if "limit" in params:
        limit = params["limit"]
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValueError("limit must be an integer between 1 and 1000")

    if "offset" in params:
        offset = params["offset"]
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a non-negative integer")

    if "cursor" in params:
        cursor = params["cursor"]
        if not isinstance(cursor, str) or not cursor.strip():
            raise ValueError("cursor must be a non-empty string")


def validate_patient_params(params: Dict[str, Any]) -> None:
    """Validate patient-related parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # External ID validation
    if "external_id" in params:
        external_id = params["external_id"]
        if not isinstance(external_id, str) or not external_id.strip():
            raise ValueError("external_id must be a non-empty string")
        if len(external_id) > 100:
            raise ValueError("external_id must be at most 100 characters")

    # Demographics validation
    if "demographics" in params:
        demographics = params["demographics"]
        if not isinstance(demographics, dict):
            raise ValueError("demographics must be an object")

        # Validate date of birth if present
        if "date_of_birth" in demographics:
            import re

            dob = demographics["date_of_birth"]
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
                raise ValueError("date_of_birth must be in YYYY-MM-DD format")

    # Consent validation
    if "consent" in params:
        consent = params["consent"]
        if not isinstance(consent, dict):
            raise ValueError("consent must be an object")

        # Check required consent fields
        if "data_collection" not in consent:
            raise ValueError("consent.data_collection is required")
        if "consent_date" not in consent:
            raise ValueError("consent.consent_date is required")


def validate_treatment_params(params: Dict[str, Any]) -> None:
    """Validate treatment-related parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Treatment type validation
    if "treatment_type" in params:
        treatment_type = params["treatment_type"]
        valid_types = [
            "neurostimulation",
            "neurofeedback",
            "medication",
            "therapy",
            "combined",
        ]
        if treatment_type not in valid_types:
            raise ValueError(f"treatment_type must be one of: {valid_types}")

    # Protocol validation
    if "protocol" in params:
        protocol = params["protocol"]
        if not isinstance(protocol, dict):
            raise ValueError("protocol must be an object")

        # Check required protocol fields
        required_fields = ["name", "sessions_per_week", "total_sessions"]
        for field in required_fields:
            if field not in protocol:
                raise ValueError(f"protocol.{field} is required")

        # Validate session numbers
        if protocol["sessions_per_week"] < 1 or protocol["sessions_per_week"] > 7:
            raise ValueError("sessions_per_week must be between 1 and 7")
        if protocol["total_sessions"] < 1 or protocol["total_sessions"] > 100:
            raise ValueError("total_sessions must be between 1 and 100")

    # Start date validation
    if "start_date" in params:
        import re

        start_date = params["start_date"]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date):
            raise ValueError("start_date must be in YYYY-MM-DD format")


def validate_report_params(params: Dict[str, Any]) -> None:
    """Validate report generation parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Report type validation
    if "report_type" in params:
        report_type = params["report_type"]
        valid_types = [
            "progress_summary",
            "treatment_outcome",
            "assessment_results",
            "discharge_summary",
            "referral_letter",
        ]
        if report_type not in valid_types:
            raise ValueError(f"report_type must be one of: {valid_types}")

    # Date range validation
    if "date_range" in params:
        date_range = params["date_range"]
        if not isinstance(date_range, dict):
            raise ValueError("date_range must be an object")

        # Check required fields
        if "start_date" not in date_range or "end_date" not in date_range:
            raise ValueError("date_range must include start_date and end_date")

        # Validate date formats
        import re

        for date_field in ["start_date", "end_date"]:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_range[date_field]):
                raise ValueError(f"{date_field} must be in YYYY-MM-DD format")

    # Format validation
    if "format" in params:
        format_type = params["format"]
        valid_formats = ["pdf", "html", "json", "docx"]
        if format_type not in valid_formats:
            raise ValueError(f"format must be one of: {valid_formats}")


def validate_analysis_params(params: Dict[str, Any]) -> None:
    """Validate analysis-related parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Session ID is required for most analyses
    if "session_id" in params:
        validate_session_id_format(params["session_id"])

    # Method validation
    if "method" in params:
        method = params["method"]
        valid_methods = {
            "time_frequency": ["morlet", "multitaper", "stockwell", "hilbert"],
            "connectivity": [
                "coherence",
                "plv",
                "pli",
                "granger_causality",
                "transfer_entropy",
                "mutual_information",
            ],
            "source_localization": ["mne", "loreta", "beamformer", "dipole_fit"],
        }
        # Check if method is in any of the valid method lists
        all_methods = []
        for methods in valid_methods.values():
            all_methods.extend(methods)
        if method not in all_methods:
            raise ValueError(f"Invalid analysis method: {method}")

    # Frequency range validation
    if "freq_range" in params:
        freq_range = params["freq_range"]
        if not isinstance(freq_range, list) or len(freq_range) != 2:
            raise ValueError("freq_range must be a list of two numbers [min, max]")
        if not all(isinstance(f, (int, float)) and f > 0 for f in freq_range):
            raise ValueError("freq_range values must be positive numbers")
        if freq_range[0] >= freq_range[1]:
            raise ValueError("freq_range[0] must be less than freq_range[1]")
        if freq_range[1] > 1000:  # Reasonable upper limit
            raise ValueError("Maximum frequency must be <= 1000 Hz")

    # Time range validation
    if "time_range" in params:
        time_range = params["time_range"]
        if not isinstance(time_range, list) or len(time_range) != 2:
            raise ValueError("time_range must be a list of two numbers [start, end]")
        if not all(isinstance(t, (int, float)) for t in time_range):
            raise ValueError("time_range values must be numbers")
        if time_range[0] >= time_range[1]:
            raise ValueError("time_range[0] must be less than time_range[1]")


def validate_model_params(params: Dict[str, Any]) -> None:
    """Validate machine learning model parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Model type validation
    if "model_type" in params:
        model_type = params["model_type"]
        valid_types = [
            "svm",
            "random_forest",
            "neural_network",
            "xgboost",
            "riemannian",
        ]
        if model_type not in valid_types:
            raise ValueError(f"model_type must be one of: {valid_types}")

    # Validation method
    if "validation_method" in params:
        validation_method = params["validation_method"]
        valid_methods = ["cross_validation", "train_test_split", "time_series_split"]
        if validation_method not in valid_methods:
            raise ValueError(f"validation_method must be one of: {valid_methods}")

    # Hyperparameters validation
    if "hyperparameters" in params:
        hyperparams = params["hyperparameters"]
        if not isinstance(hyperparams, dict):
            raise ValueError("hyperparameters must be a dictionary")

    # Optimization settings validation
    if "optimization" in params:
        optimization = params["optimization"]
        if not isinstance(optimization, dict):
            raise ValueError("optimization must be a dictionary")

        if "method" in optimization:
            opt_method = optimization["method"]
            valid_opt_methods = ["grid_search", "random_search", "bayesian"]
            if opt_method not in valid_opt_methods:
                raise ValueError(
                    f"optimization.method must be one of: {valid_opt_methods}"
                )

        if "cv_folds" in optimization:
            cv_folds = optimization["cv_folds"]
            if not isinstance(cv_folds, int) or cv_folds < 2 or cv_folds > 20:
                raise ValueError(
                    "optimization.cv_folds must be an integer between 2 and 20"
                )


def validate_prediction_params(params: Dict[str, Any]) -> None:
    """Validate prediction-related parameters.

    Args:
        params: Parameters to validate

    Raises:
        ValueError: If parameters are invalid
    """
    # Model ID validation
    if "model_id" in params:
        model_id = params["model_id"]
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("model_id must be a non-empty string")

    # Confidence threshold validation
    if "confidence_threshold" in params:
        threshold = params["confidence_threshold"]
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            raise ValueError("confidence_threshold must be a number between 0 and 1")

    # Time window validation
    if "time_window" in params:
        time_window = params["time_window"]
        if not isinstance(time_window, list) or len(time_window) != 2:
            raise ValueError("time_window must be a list of two numbers [start, end]")
        if not all(isinstance(t, (int, float)) and t >= 0 for t in time_window):
            raise ValueError("time_window values must be non-negative numbers")
        if time_window[0] >= time_window[1]:
            raise ValueError("time_window[0] must be less than time_window[1]")

    # Sliding window validation
    if "sliding_window" in params:
        sliding_window = params["sliding_window"]
        if not isinstance(sliding_window, dict):
            raise ValueError("sliding_window must be a dictionary")

        if "size" in sliding_window:
            size = sliding_window["size"]
            if not isinstance(size, (int, float)) or size <= 0:
                raise ValueError("sliding_window.size must be a positive number")

        if "step" in sliding_window:
            step = sliding_window["step"]
            if not isinstance(step, (int, float)) or step <= 0:
                raise ValueError("sliding_window.step must be a positive number")

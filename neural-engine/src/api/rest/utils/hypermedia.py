"""HATEOAS hypermedia utilities."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel


def add_hateoas_links(
    resource: BaseModel,
    resource_type: str,
    resource_id: str,
    base_url: str = "/api/v2",
) -> Dict[str, Dict[str, str]]:
    """
    Add HATEOAS links to a resource.

    Args:
        resource: Resource object
        resource_type: Type of resource (e.g., 'device', 'session')
        resource_id: Resource identifier
        base_url: API base URL

    Returns:
        Dictionary of links
    """
    links = {"self": {"href": f"{base_url}/{resource_type}s/{resource_id}"}}

    # Add resource-specific links
    if resource_type == "device":
        links.update(
            {
                "sessions": {"href": f"{base_url}/sessions?device_id={resource_id}"},
                "calibration": {
                    "href": f"{base_url}/devices/{resource_id}/calibration"
                },
                "metrics": {"href": f"{base_url}/devices/{resource_id}/metrics"},
                "status": {"href": f"{base_url}/devices/{resource_id}/status"},
            }
        )

    elif resource_type == "session":
        links.update(
            {
                "data": {"href": f"{base_url}/neural-data/sessions/{resource_id}"},
                "analysis": {"href": f"{base_url}/analysis/sessions/{resource_id}"},
                "patient": {
                    "href": f"{base_url}/patients/{getattr(resource, 'patient_id', '')}"
                },
                "device": {
                    "href": f"{base_url}/devices/{getattr(resource, 'device_id', '')}"
                },
                "export": {"href": f"{base_url}/sessions/{resource_id}/export"},
            }
        )

    elif resource_type == "patient":
        links.update(
            {
                "sessions": {"href": f"{base_url}/sessions?patient_id={resource_id}"},
                "treatments": {
                    "href": f"{base_url}/clinical/treatments?patient_id={resource_id}"
                },
                "assessments": {
                    "href": f"{base_url}/clinical/assessments?patient_id={resource_id}"
                },
                "reports": {
                    "href": f"{base_url}/clinical/reports?patient_id={resource_id}"
                },
            }
        )

    elif resource_type == "analysis":
        links.update(
            {
                "session": {
                    "href": f"{base_url}/sessions/{getattr(resource, 'session_id', '')}"
                },
                "results": {"href": f"{base_url}/analysis/{resource_id}/results"},
                "visualizations": {
                    "href": f"{base_url}/visualizations?analysis_id={resource_id}"
                },
                "ml_model": {
                    "href": f"{base_url}/ml-models/{getattr(resource, 'model_id', '')}"
                },
            }
        )

    elif resource_type == "ml_model":
        links.update(
            {
                "versions": {"href": f"{base_url}/ml-models/{resource_id}/versions"},
                "metrics": {"href": f"{base_url}/ml-models/{resource_id}/metrics"},
                "predictions": {"href": f"{base_url}/ml-models/{resource_id}/predict"},
                "training": {"href": f"{base_url}/ml-models/{resource_id}/train"},
            }
        )

    return links


def add_collection_links(
    collection_type: str,
    page: int,
    size: int,
    total_pages: int,
    filters: Optional[Dict[str, Any]] = None,
    base_url: str = "/api/v2",
) -> Dict[str, Dict[str, str]]:
    """
    Add HATEOAS links to a collection.

    Args:
        collection_type: Type of collection
        page: Current page
        size: Page size
        total_pages: Total number of pages
        filters: Applied filters
        base_url: API base URL

    Returns:
        Dictionary of links
    """
    # Build query string
    query_parts = [f"page={page}", f"size={size}"]
    if filters:
        for key, value in filters.items():
            if value is not None:
                query_parts.append(f"{key}={value}")

    query_string = "&".join(query_parts)

    links = {"self": {"href": f"{base_url}/{collection_type}?{query_string}"}}

    # Navigation links
    if page > 1:
        prev_query = query_string.replace(f"page={page}", f"page={page - 1}")
        links["prev"] = {"href": f"{base_url}/{collection_type}?{prev_query}"}
        links["first"] = {
            "href": f"{base_url}/{collection_type}?{query_string.replace(f'page={page}', 'page=1')}"
        }

    if page < total_pages:
        next_query = query_string.replace(f"page={page}", f"page={page + 1}")
        links["next"] = {"href": f"{base_url}/{collection_type}?{next_query}"}
        links["last"] = {
            "href": f"{base_url}/{collection_type}?{query_string.replace(f'page={page}', f'page={total_pages}')}"
        }

    return links


def create_action_links(
    resource_type: str,
    resource_id: str,
    available_actions: List[str],
    base_url: str = "/api/v2",
) -> Dict[str, Dict[str, Any]]:
    """
    Create action links for a resource.

    Args:
        resource_type: Type of resource
        resource_id: Resource identifier
        available_actions: List of available actions
        base_url: API base URL

    Returns:
        Dictionary of action links
    """
    action_definitions = {
        "start": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/start",
            "method": "POST",
            "description": f"Start the {resource_type}",
        },
        "stop": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/stop",
            "method": "POST",
            "description": f"Stop the {resource_type}",
        },
        "pause": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/pause",
            "method": "POST",
            "description": f"Pause the {resource_type}",
        },
        "resume": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/resume",
            "method": "POST",
            "description": f"Resume the {resource_type}",
        },
        "calibrate": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/calibrate",
            "method": "POST",
            "description": f"Calibrate the {resource_type}",
        },
        "export": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/export",
            "method": "GET",
            "description": f"Export {resource_type} data",
            "formats": ["json", "csv", "edf", "mat"],
        },
        "analyze": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/analyze",
            "method": "POST",
            "description": f"Run analysis on {resource_type}",
        },
        "train": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/train",
            "method": "POST",
            "description": f"Train the {resource_type}",
        },
        "predict": {
            "href": f"{base_url}/{resource_type}s/{resource_id}/predict",
            "method": "POST",
            "description": f"Make predictions using {resource_type}",
        },
    }

    actions = {}
    for action in available_actions:
        if action in action_definitions:
            actions[action] = action_definitions[action]

    return actions

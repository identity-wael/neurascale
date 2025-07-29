"""VR controller for immersive neural visualization."""

import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ControllerButton(Enum):
    """VR controller button mappings."""

    TRIGGER = "trigger"
    GRIP = "grip"
    MENU = "menu"
    TOUCHPAD = "touchpad"
    A = "a"
    B = "b"
    X = "x"
    Y = "y"


@dataclass
class ControllerState:
    """State of a VR controller."""

    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float, float]  # Quaternion
    buttons: Dict[ControllerButton, bool]
    triggers: Dict[str, float]  # Analog values
    touchpad: Tuple[float, float]
    velocity: Tuple[float, float, float]
    angular_velocity: Tuple[float, float, float]


class VRController:
    """Manages VR controllers for neural visualization interaction.

    Supports OpenXR-compatible controllers with haptic feedback,
    gesture recognition, and spatial interaction.
    """

    def __init__(self) -> None:
        """Initialize VR controller."""
        self.left_controller: Optional[ControllerState] = None
        self.right_controller: Optional[ControllerState] = None

        # Interaction settings
        self.laser_pointer_enabled = True
        self.haptic_feedback_enabled = True
        self.gesture_recognition_enabled = True

        # Selection and manipulation
        self.selected_object = None
        self.manipulation_mode = "translate"  # translate, rotate, scale
        self.selection_radius = 0.05

        # Tools
        self.active_tool = "pointer"  # pointer, slicer, probe, annotate
        self.tool_settings: Dict[str, Dict[str, Any]] = {}

        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            "select": [],
            "deselect": [],
            "manipulate": [],
            "tool_activate": [],
            "gesture": [],
        }

        logger.info("VRController initialized")

    async def initialize(self) -> bool:
        """Initialize VR system and controllers.

        Returns:
            Success status
        """
        try:
            # Initialize OpenXR or similar VR API
            await self._initialize_vr_system()

            # Detect controllers
            await self._detect_controllers()

            # Set up haptic feedback
            if self.haptic_feedback_enabled:
                await self._initialize_haptics()

            # Initialize tools
            self._initialize_tools()

            logger.info("VR controllers initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize VR controllers: {e}")
            return False

    async def update(self) -> None:
        """Update controller states."""
        # Poll controller data
        if self.left_controller:
            await self._update_controller_state("left")

        if self.right_controller:
            await self._update_controller_state("right")

        # Process interactions
        await self._process_interactions()

        # Update active tool
        await self._update_active_tool()

    async def _initialize_vr_system(self) -> None:
        """Initialize VR system (OpenXR, etc.)."""
        # In production, would initialize actual VR API
        logger.info("VR system initialized (simulated)")

    async def _detect_controllers(self) -> None:
        """Detect available VR controllers."""
        # Simulate controller detection
        self.left_controller = ControllerState(
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0, 1.0),
            buttons={button: False for button in ControllerButton},
            triggers={"index": 0.0, "hand": 0.0},
            touchpad=(0.0, 0.0),
            velocity=(0.0, 0.0, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
        )

        self.right_controller = ControllerState(
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0, 1.0),
            buttons={button: False for button in ControllerButton},
            triggers={"index": 0.0, "hand": 0.0},
            touchpad=(0.0, 0.0),
            velocity=(0.0, 0.0, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
        )

        logger.info("Detected left and right controllers")

    async def _initialize_haptics(self) -> None:
        """Initialize haptic feedback system."""
        # In production, would set up haptic devices
        logger.info("Haptic feedback initialized")

    def _initialize_tools(self) -> None:
        """Initialize interaction tools."""
        # Pointer tool
        self.tool_settings["pointer"] = {
            "laser_color": (0.0, 1.0, 1.0, 0.5),
            "laser_width": 0.002,
            "max_distance": 5.0,
        }

        # Slicer tool
        self.tool_settings["slicer"] = {
            "plane_color": (1.0, 0.0, 0.0, 0.3),
            "plane_size": 0.2,
            "slice_thickness": 0.01,
        }

        # Probe tool
        self.tool_settings["probe"] = {
            "probe_radius": 0.02,
            "sample_depth": 0.1,
            "display_values": True,
        }

        # Annotation tool
        self.tool_settings["annotate"] = {
            "annotation_color": (1.0, 1.0, 0.0, 1.0),
            "text_size": 0.02,
            "arrow_enabled": True,
        }

    async def _update_controller_state(self, hand: str) -> None:
        """Update state for specific controller.

        Args:
            hand: "left" or "right"
        """
        # In production, would poll actual controller data
        # For now, simulate with dummy data
        controller = self.left_controller if hand == "left" else self.right_controller

        if controller:
            # Simulate some movement
            t = np.random.rand()
            controller.position = (np.sin(t) * 0.1, 1.5, np.cos(t) * 0.1)

    async def _process_interactions(self) -> None:
        """Process controller interactions."""
        # Check for selection
        if self.right_controller and self.right_controller.buttons.get(
            ControllerButton.TRIGGER
        ):
            await self._handle_selection()

        # Check for manipulation
        if self.selected_object and self.right_controller:
            if self.right_controller.buttons.get(ControllerButton.GRIP):
                await self._handle_manipulation()

        # Check for tool activation
        if self.left_controller and self.left_controller.buttons.get(
            ControllerButton.TRIGGER
        ):
            await self._activate_tool()

    async def _handle_selection(self) -> None:
        """Handle object selection."""
        if not self.laser_pointer_enabled:
            return

        # Cast ray from controller
        ray_origin = self.right_controller.position
        ray_direction = self._get_controller_forward(self.right_controller)

        # Find intersection with scene objects
        hit_object = await self._raycast(ray_origin, ray_direction)

        if hit_object:
            if self.selected_object != hit_object:
                # Deselect previous
                if self.selected_object:
                    await self._deselect_object()

                # Select new
                self.selected_object = hit_object
                await self._select_object(hit_object)

                # Haptic feedback
                if self.haptic_feedback_enabled:
                    await self.trigger_haptic("select", "right")

    async def _handle_manipulation(self) -> None:
        """Handle object manipulation."""
        if not self.selected_object:
            return

        controller = self.right_controller

        # Calculate transformation
        if self.manipulation_mode == "translate":
            # Move with controller
            delta = np.array(controller.position) - np.array(self._last_controller_pos)
            await self._translate_object(self.selected_object, delta)

        elif self.manipulation_mode == "rotate":
            # Rotate based on controller rotation
            rotation_delta = self._calculate_rotation_delta(controller.rotation)
            await self._rotate_object(self.selected_object, rotation_delta)

        elif self.manipulation_mode == "scale":
            # Scale based on controller distance
            scale_factor = self._calculate_scale_factor()
            await self._scale_object(self.selected_object, scale_factor)

        # Update last position
        self._last_controller_pos = controller.position

        # Fire manipulation event
        for callback in self.event_callbacks["manipulate"]:
            callback(self.selected_object, self.manipulation_mode)

    async def _activate_tool(self) -> None:
        """Activate current tool."""
        if self.active_tool == "slicer":
            await self._use_slicer_tool()
        elif self.active_tool == "probe":
            await self._use_probe_tool()
        elif self.active_tool == "annotate":
            await self._use_annotation_tool()

        # Fire tool activation event
        for callback in self.event_callbacks["tool_activate"]:
            callback(self.active_tool)

    async def _use_slicer_tool(self) -> None:
        """Use brain slicer tool."""
        controller = self.left_controller
        settings = self.tool_settings["slicer"]

        # Create slice plane at controller position
        plane_position = controller.position
        plane_normal = self._get_controller_forward(controller)

        # Apply slice to brain visualization
        await self._apply_brain_slice(
            plane_position, plane_normal, settings["slice_thickness"]
        )

        # Visual feedback
        await self._show_slice_plane(
            plane_position, plane_normal, settings["plane_size"]
        )

    async def _use_probe_tool(self) -> None:
        """Use neural activity probe tool."""
        controller = self.left_controller
        settings = self.tool_settings["probe"]

        # Sample neural activity at probe position
        probe_position = controller.position
        activity_value = await self._sample_neural_activity(
            probe_position, settings["probe_radius"]
        )

        # Display value if enabled
        if settings["display_values"]:
            await self._display_probe_value(probe_position, activity_value)

        # Haptic feedback based on activity
        if self.haptic_feedback_enabled:
            intensity = min(activity_value / 100.0, 1.0)
            await self.trigger_haptic("probe", "left", intensity)

    async def _use_annotation_tool(self) -> None:
        """Use 3D annotation tool."""
        controller = self.left_controller
        settings = self.tool_settings["annotate"]

        # Create annotation at controller position
        annotation_pos = controller.position

        # Get annotation text (would come from UI)
        annotation_text = "Neural Activity Peak"

        # Create 3D annotation
        await self._create_annotation(
            annotation_pos,
            annotation_text,
            settings["annotation_color"],
            settings["text_size"],
        )

    def _get_controller_forward(
        self, controller: ControllerState
    ) -> Tuple[float, float, float]:
        """Get forward direction from controller orientation.

        Args:
            controller: Controller state

        Returns:
            Forward direction vector
        """
        # Convert quaternion to forward vector
        # Simplified - in production would use proper quaternion math
        return (0.0, 0.0, -1.0)

    async def _raycast(
        self, origin: Tuple[float, float, float], direction: Tuple[float, float, float]
    ) -> Optional[str]:
        """Cast ray and find intersection.

        Args:
            origin: Ray origin
            direction: Ray direction

        Returns:
            Hit object ID or None
        """
        # In production, would perform actual raycast
        # For now, return dummy object
        if np.random.rand() > 0.5:
            return "brain_region_1"
        return None

    async def _select_object(self, object_id: str) -> None:
        """Select an object.

        Args:
            object_id: Object to select
        """
        logger.info(f"Selected object: {object_id}")

        # Fire selection callbacks
        for callback in self.event_callbacks["select"]:
            callback(object_id)

    async def _deselect_object(self) -> None:
        """Deselect current object."""
        if self.selected_object:
            logger.info(f"Deselected object: {self.selected_object}")

            # Fire deselection callbacks
            for callback in self.event_callbacks["deselect"]:
                callback(self.selected_object)

            self.selected_object = None

    async def trigger_haptic(
        self, effect: str, hand: str, intensity: float = 1.0, duration: float = 0.1
    ) -> None:
        """Trigger haptic feedback.

        Args:
            effect: Effect name
            hand: "left" or "right"
            intensity: Effect intensity (0-1)
            duration: Effect duration in seconds
        """
        if not self.haptic_feedback_enabled:
            return

        # In production, would trigger actual haptic feedback
        logger.debug(f"Haptic feedback: {effect} on {hand} hand, intensity {intensity}")

    def register_event_callback(self, event: str, callback: Callable) -> None:
        """Register event callback.

        Args:
            event: Event name
            callback: Callback function
        """
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
            logger.info(f"Registered callback for {event} event")

    def set_active_tool(self, tool: str) -> None:
        """Set active interaction tool.

        Args:
            tool: Tool name
        """
        if tool in self.tool_settings:
            self.active_tool = tool
            logger.info(f"Active tool set to: {tool}")

    def set_manipulation_mode(self, mode: str) -> None:
        """Set object manipulation mode.

        Args:
            mode: Manipulation mode (translate, rotate, scale)
        """
        if mode in ["translate", "rotate", "scale"]:
            self.manipulation_mode = mode
            logger.info(f"Manipulation mode set to: {mode}")

    async def _translate_object(self, object_id: str, delta: np.ndarray) -> None:
        """Translate object in 3D space."""
        # In production, would update object transform
        logger.debug(f"Translating {object_id} by {delta}")

    async def _rotate_object(
        self, object_id: str, rotation: Tuple[float, float, float]
    ) -> None:
        """Rotate object in 3D space."""
        logger.debug(f"Rotating {object_id} by {rotation}")

    async def _scale_object(self, object_id: str, scale: float) -> None:
        """Scale object uniformly."""
        logger.debug(f"Scaling {object_id} by {scale}")

    def _calculate_rotation_delta(
        self, current_rotation: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float]:
        """Calculate rotation delta from quaternion."""
        # Simplified - in production would use proper quaternion math
        return (0.0, 0.0, 0.0)

    def _calculate_scale_factor(self) -> float:
        """Calculate scale factor from controller movement."""
        # In production, would calculate from controller distance
        return 1.0

    async def _apply_brain_slice(
        self,
        position: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        thickness: float,
    ) -> None:
        """Apply slice plane to brain visualization."""
        logger.info(f"Applying brain slice at {position} with normal {normal}")

    async def _show_slice_plane(
        self,
        position: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        size: float,
    ) -> None:
        """Show visual representation of slice plane."""
        pass

    async def _sample_neural_activity(
        self, position: Tuple[float, float, float], radius: float
    ) -> float:
        """Sample neural activity at position."""
        # In production, would sample actual data
        return np.random.rand() * 100.0

    async def _display_probe_value(
        self, position: Tuple[float, float, float], value: float
    ) -> None:
        """Display probe measurement value."""
        logger.info(f"Probe value at {position}: {value:.2f}")

    async def _create_annotation(
        self,
        position: Tuple[float, float, float],
        text: str,
        color: Tuple[float, float, float, float],
        size: float,
    ) -> None:
        """Create 3D annotation in scene."""
        logger.info(f"Created annotation: {text} at {position}")

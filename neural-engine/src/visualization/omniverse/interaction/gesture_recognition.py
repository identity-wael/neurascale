"""Gesture recognition for VR/AR neural visualization."""

import logging
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
from dataclasses import dataclass
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Recognized gesture types."""

    PINCH = "pinch"
    GRAB = "grab"
    POINT = "point"
    SWIPE = "swipe"
    ROTATE = "rotate"
    SCALE = "scale"
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    WAVE = "wave"
    CIRCLE = "circle"


@dataclass
class HandPose:
    """Hand pose data."""

    timestamp: float
    wrist: Tuple[float, float, float]
    thumb_tip: Tuple[float, float, float]
    index_tip: Tuple[float, float, float]
    middle_tip: Tuple[float, float, float]
    ring_tip: Tuple[float, float, float]
    pinky_tip: Tuple[float, float, float]
    palm_normal: Tuple[float, float, float]
    palm_center: Tuple[float, float, float]
    confidence: float


@dataclass
class Gesture:
    """Detected gesture."""

    type: GestureType
    confidence: float
    position: Tuple[float, float, float]
    direction: Optional[Tuple[float, float, float]] = None
    magnitude: Optional[float] = None
    hand: Optional[str] = None  # "left" or "right"


class GestureRecognition:
    """Recognizes hand gestures for neural visualization control.

    Supports both controller-based and hand-tracking gestures
    for intuitive interaction with brain visualizations.
    """

    def __init__(self) -> None:
        """Initialize gesture recognition."""
        self.enabled = True
        self.hand_tracking_enabled = True

        # Gesture detection thresholds
        self.pinch_threshold = 0.03  # 3cm
        self.grab_threshold = 0.05  # 5cm
        self.swipe_velocity_threshold = 0.5  # m/s
        self.tap_duration_threshold = 0.2  # seconds

        # Pose history for temporal gestures
        self.pose_history_size = 30  # frames
        self.left_hand_history: deque = deque(maxlen=self.pose_history_size)
        self.right_hand_history: deque = deque(maxlen=self.pose_history_size)

        # Current gestures
        self.active_gestures: Dict[str, Gesture] = {}

        # Gesture callbacks
        self.gesture_callbacks: Dict[GestureType, List[Callable]] = {
            gesture_type: [] for gesture_type in GestureType
        }

        # Gesture-specific settings
        self.gesture_settings = {
            GestureType.PINCH: {"hold_time": 0.1},
            GestureType.GRAB: {"hold_time": 0.2},
            GestureType.SWIPE: {"min_distance": 0.1},
            GestureType.ROTATE: {"min_angle": 15.0},
            GestureType.SCALE: {"min_scale": 0.1},
        }

        logger.info("GestureRecognition initialized")

    async def initialize(self) -> bool:
        """Initialize hand tracking system.

        Returns:
            Success status
        """
        try:
            if self.hand_tracking_enabled:
                await self._initialize_hand_tracking()

            logger.info("Gesture recognition initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize gesture recognition: {e}")
            return False

    async def update(
        self, left_hand: Optional[HandPose], right_hand: Optional[HandPose]
    ) -> List[Gesture]:
        """Update gesture recognition with new hand poses.

        Args:
            left_hand: Left hand pose
            right_hand: Right hand pose

        Returns:
            List of detected gestures
        """
        if not self.enabled:
            return []

        detected_gestures = []

        # Update pose history
        if left_hand:
            self.left_hand_history.append(left_hand)
            gestures = await self._detect_hand_gestures("left", left_hand)
            detected_gestures.extend(gestures)

        if right_hand:
            self.right_hand_history.append(right_hand)
            gestures = await self._detect_hand_gestures("right", right_hand)
            detected_gestures.extend(gestures)

        # Detect two-handed gestures
        if left_hand and right_hand:
            two_handed = await self._detect_two_handed_gestures(left_hand, right_hand)
            detected_gestures.extend(two_handed)

        # Update active gestures
        self._update_active_gestures(detected_gestures)

        # Fire callbacks
        for gesture in detected_gestures:
            await self._fire_gesture_callbacks(gesture)

        return detected_gestures

    async def _initialize_hand_tracking(self) -> None:
        """Initialize hand tracking system."""
        # In production, would initialize actual hand tracking
        # (Leap Motion, Oculus Hand Tracking, etc.)
        logger.info("Hand tracking initialized (simulated)")

    async def _detect_hand_gestures(self, hand: str, pose: HandPose) -> List[Gesture]:
        """Detect single-hand gestures.

        Args:
            hand: "left" or "right"
            pose: Current hand pose

        Returns:
            Detected gestures
        """
        gestures = []

        # Pinch detection
        pinch = self._detect_pinch(pose)
        if pinch:
            pinch.hand = hand
            gestures.append(pinch)

        # Grab detection
        grab = self._detect_grab(pose)
        if grab:
            grab.hand = hand
            gestures.append(grab)

        # Point detection
        point = self._detect_point(pose)
        if point:
            point.hand = hand
            gestures.append(point)

        # Temporal gestures (require history)
        history = self.left_hand_history if hand == "left" else self.right_hand_history

        if len(history) >= 10:
            # Swipe detection
            swipe = self._detect_swipe(list(history))
            if swipe:
                swipe.hand = hand
                gestures.append(swipe)

            # Tap detection
            tap = self._detect_tap(list(history))
            if tap:
                tap.hand = hand
                gestures.append(tap)

            # Circle detection
            circle = self._detect_circle(list(history))
            if circle:
                circle.hand = hand
                gestures.append(circle)

        return gestures

    def _detect_pinch(self, pose: HandPose) -> Optional[Gesture]:
        """Detect pinch gesture.

        Args:
            pose: Hand pose

        Returns:
            Pinch gesture or None
        """
        # Calculate distance between thumb and index finger
        thumb = np.array(pose.thumb_tip)
        index = np.array(pose.index_tip)
        distance = np.linalg.norm(thumb - index)

        if distance < self.pinch_threshold:
            return Gesture(
                type=GestureType.PINCH,
                confidence=1.0 - (distance / self.pinch_threshold),
                position=tuple((thumb + index) / 2),
                magnitude=distance,
            )

        return None

    def _detect_grab(self, pose: HandPose) -> Optional[Gesture]:
        """Detect grab gesture.

        Args:
            pose: Hand pose

        Returns:
            Grab gesture or None
        """
        # Check if all fingers are close to palm
        palm = np.array(pose.palm_center)
        fingers = [
            np.array(pose.index_tip),
            np.array(pose.middle_tip),
            np.array(pose.ring_tip),
            np.array(pose.pinky_tip),
        ]

        distances = [np.linalg.norm(finger - palm) for finger in fingers]
        avg_distance = np.mean(distances)

        if avg_distance < self.grab_threshold:
            return Gesture(
                type=GestureType.GRAB,
                confidence=1.0 - (avg_distance / self.grab_threshold),
                position=pose.palm_center,
                magnitude=avg_distance,
            )

        return None

    def _detect_point(self, pose: HandPose) -> Optional[Gesture]:
        """Detect pointing gesture.

        Args:
            pose: Hand pose

        Returns:
            Point gesture or None
        """
        # Check if index finger is extended while others are folded
        palm = np.array(pose.palm_center)
        index_dist = np.linalg.norm(np.array(pose.index_tip) - palm)

        other_distances = [
            np.linalg.norm(np.array(pose.middle_tip) - palm),
            np.linalg.norm(np.array(pose.ring_tip) - palm),
            np.linalg.norm(np.array(pose.pinky_tip) - palm),
        ]

        avg_other = np.mean(other_distances)

        if index_dist > avg_other * 1.5:  # Index significantly more extended
            # Calculate pointing direction
            direction = np.array(pose.index_tip) - np.array(pose.wrist)
            direction = direction / np.linalg.norm(direction)

            return Gesture(
                type=GestureType.POINT,
                confidence=min(index_dist / avg_other, 1.0),
                position=pose.index_tip,
                direction=tuple(direction),
            )

        return None

    def _detect_swipe(self, history: List[HandPose]) -> Optional[Gesture]:
        """Detect swipe gesture from pose history.

        Args:
            history: Hand pose history

        Returns:
            Swipe gesture or None
        """
        if len(history) < 10:
            return None

        # Calculate palm center trajectory
        positions = [np.array(pose.palm_center) for pose in history[-10:]]

        # Calculate velocity
        velocities = []
        for i in range(1, len(positions)):
            dt = history[i].timestamp - history[i - 1].timestamp
            if dt > 0:
                velocity = np.linalg.norm(positions[i] - positions[i - 1]) / dt
                velocities.append(velocity)

        avg_velocity = np.mean(velocities)

        if avg_velocity > self.swipe_velocity_threshold:
            # Calculate swipe direction
            direction = positions[-1] - positions[0]
            direction = direction / np.linalg.norm(direction)

            return Gesture(
                type=GestureType.SWIPE,
                confidence=min(avg_velocity / (self.swipe_velocity_threshold * 2), 1.0),
                position=history[-1].palm_center,
                direction=tuple(direction),
                magnitude=avg_velocity,
            )

        return None

    def _detect_tap(self, history: List[HandPose]) -> Optional[Gesture]:
        """Detect tap gesture from pose history.

        Args:
            history: Hand pose history

        Returns:
            Tap gesture or None
        """
        if len(history) < 5:
            return None

        # Look for quick forward-backward motion
        positions = [np.array(pose.palm_center) for pose in history[-5:]]

        # Calculate forward motion
        forward_dist = np.linalg.norm(positions[2] - positions[0])
        backward_dist = np.linalg.norm(positions[4] - positions[2])

        # Check timing
        duration = history[-1].timestamp - history[-5].timestamp

        if (
            forward_dist > 0.05
            and backward_dist > 0.05
            and duration < self.tap_duration_threshold
        ):
            return Gesture(
                type=GestureType.TAP, confidence=0.8, position=history[-1].palm_center
            )

        return None

    def _detect_circle(self, history: List[HandPose]) -> Optional[Gesture]:
        """Detect circular gesture from pose history.

        Args:
            history: Hand pose history

        Returns:
            Circle gesture or None
        """
        if len(history) < 20:
            return None

        # Analyze palm trajectory
        positions = [np.array(pose.palm_center) for pose in history[-20:]]

        # Fit circle to points (simplified)
        center = np.mean(positions, axis=0)
        radii = [np.linalg.norm(pos - center) for pos in positions]
        avg_radius = np.mean(radii)
        radius_variance = np.var(radii)

        # Check if points form a circle
        if radius_variance < (avg_radius * 0.2) ** 2:  # Low variance
            return Gesture(
                type=GestureType.CIRCLE,
                confidence=1.0 - (radius_variance / (avg_radius * 0.3) ** 2),
                position=tuple(center),
                magnitude=avg_radius,
            )

        return None

    async def _detect_two_handed_gestures(
        self, left_pose: HandPose, right_pose: HandPose
    ) -> List[Gesture]:
        """Detect two-handed gestures.

        Args:
            left_pose: Left hand pose
            right_pose: Right hand pose

        Returns:
            Detected gestures
        """
        gestures = []

        # Scale gesture (hands moving apart/together)
        scale = self._detect_scale_gesture(left_pose, right_pose)
        if scale:
            gestures.append(scale)

        # Rotate gesture (hands rotating around center)
        rotate = self._detect_rotate_gesture(left_pose, right_pose)
        if rotate:
            gestures.append(rotate)

        return gestures

    def _detect_scale_gesture(
        self, left_pose: HandPose, right_pose: HandPose
    ) -> Optional[Gesture]:
        """Detect scale gesture with two hands.

        Args:
            left_pose: Left hand pose
            right_pose: Right hand pose

        Returns:
            Scale gesture or None
        """
        # Check if both hands are pinching
        left_pinch = self._detect_pinch(left_pose)
        right_pinch = self._detect_pinch(right_pose)

        if left_pinch and right_pinch:
            # Calculate distance between hands
            left_pos = np.array(left_pose.palm_center)
            right_pos = np.array(right_pose.palm_center)
            distance = np.linalg.norm(right_pos - left_pos)

            # Check history for distance change
            if len(self.left_hand_history) >= 5 and len(self.right_hand_history) >= 5:
                prev_left = np.array(self.left_hand_history[-5].palm_center)
                prev_right = np.array(self.right_hand_history[-5].palm_center)
                prev_distance = np.linalg.norm(prev_right - prev_left)

                scale_factor = distance / prev_distance if prev_distance > 0 else 1.0

                if (
                    abs(scale_factor - 1.0)
                    > self.gesture_settings[GestureType.SCALE]["min_scale"]
                ):
                    return Gesture(
                        type=GestureType.SCALE,
                        confidence=(left_pinch.confidence + right_pinch.confidence) / 2,
                        position=tuple((left_pos + right_pos) / 2),
                        magnitude=scale_factor,
                    )

        return None

    def _detect_rotate_gesture(
        self, left_pose: HandPose, right_pose: HandPose
    ) -> Optional[Gesture]:
        """Detect rotation gesture with two hands.

        Args:
            left_pose: Left hand pose
            right_pose: Right hand pose

        Returns:
            Rotate gesture or None
        """
        # Check if both hands are grabbing
        left_grab = self._detect_grab(left_pose)
        right_grab = self._detect_grab(right_pose)

        if left_grab and right_grab:
            # Calculate rotation from hand positions
            if len(self.left_hand_history) >= 5 and len(self.right_hand_history) >= 5:
                # Current vector between hands
                current_vec = np.array(right_pose.palm_center) - np.array(
                    left_pose.palm_center
                )

                # Previous vector
                prev_left = self.left_hand_history[-5].palm_center
                prev_right = self.right_hand_history[-5].palm_center
                prev_vec = np.array(prev_right) - np.array(prev_left)

                # Calculate angle
                angle = np.degrees(
                    np.arccos(
                        np.clip(
                            np.dot(current_vec, prev_vec)
                            / (np.linalg.norm(current_vec) * np.linalg.norm(prev_vec)),
                            -1.0,
                            1.0,
                        )
                    )
                )

                if angle > self.gesture_settings[GestureType.ROTATE]["min_angle"]:
                    # Calculate rotation axis
                    axis = np.cross(prev_vec, current_vec)
                    axis = (
                        axis / np.linalg.norm(axis)
                        if np.linalg.norm(axis) > 0
                        else np.array([0, 1, 0])
                    )

                    return Gesture(
                        type=GestureType.ROTATE,
                        confidence=(left_grab.confidence + right_grab.confidence) / 2,
                        position=tuple(
                            (
                                np.array(left_pose.palm_center)
                                + np.array(right_pose.palm_center)
                            )
                            / 2
                        ),
                        direction=tuple(axis),
                        magnitude=angle,
                    )

        return None

    def _update_active_gestures(self, detected: List[Gesture]) -> None:
        """Update active gesture tracking.

        Args:
            detected: Newly detected gestures
        """
        # Update active gestures
        new_active = {}

        for gesture in detected:
            key = f"{gesture.type.value}_{gesture.hand or 'both'}"
            new_active[key] = gesture

        self.active_gestures = new_active

    async def _fire_gesture_callbacks(self, gesture: Gesture) -> None:
        """Fire callbacks for detected gesture.

        Args:
            gesture: Detected gesture
        """
        for callback in self.gesture_callbacks[gesture.type]:
            try:
                await callback(gesture)
            except Exception as e:
                logger.error(f"Error in gesture callback: {e}")

    def register_gesture_callback(
        self, gesture_type: GestureType, callback: Callable
    ) -> None:
        """Register callback for gesture type.

        Args:
            gesture_type: Type of gesture
            callback: Callback function
        """
        self.gesture_callbacks[gesture_type].append(callback)
        logger.info(f"Registered callback for {gesture_type.value} gesture")

    def set_threshold(
        self, gesture_type: GestureType, threshold_name: str, value: float
    ) -> None:
        """Set gesture detection threshold.

        Args:
            gesture_type: Gesture type
            threshold_name: Threshold parameter name
            value: Threshold value
        """
        if gesture_type in self.gesture_settings:
            self.gesture_settings[gesture_type][threshold_name] = value
            logger.info(f"Set {gesture_type.value} {threshold_name} to {value}")

    def enable_gesture(self, gesture_type: GestureType, enabled: bool = True) -> None:
        """Enable/disable specific gesture.

        Args:
            gesture_type: Gesture type
            enabled: Whether to enable
        """
        # In production, would selectively enable/disable gestures
        logger.info(
            f"{'Enabled' if enabled else 'Disabled'} {gesture_type.value} gesture"
        )

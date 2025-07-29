"""Animation engine for temporal neural data visualization."""

import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InterpolationType(Enum):
    """Animation interpolation types."""

    LINEAR = "linear"
    CUBIC = "cubic"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    STEP = "step"


@dataclass
class AnimationKeyframe:
    """Single keyframe in animation."""

    time: float
    value: Any
    interpolation: InterpolationType = InterpolationType.LINEAR
    tangent_in: Optional[float] = None
    tangent_out: Optional[float] = None


@dataclass
class AnimationTrack:
    """Animation track for a specific property."""

    name: str
    target_path: str
    property_name: str
    keyframes: List[AnimationKeyframe]
    is_looping: bool = False
    duration: float = 0.0


class AnimationEngine:
    """Manages animations for neural visualization.

    Handles keyframe animation, procedural animation,
    and real-time data-driven animations.
    """

    def __init__(self) -> None:
        """Initialize animation engine."""
        self.tracks: Dict[str, AnimationTrack] = {}
        self.active_animations: Dict[str, Dict[str, Any]] = {}
        self.procedural_animations: Dict[str, Callable] = {}

        # Animation settings
        self.default_fps = 60.0
        self.current_time = 0.0
        self.playback_speed = 1.0
        self.is_playing = False

        # Timeline
        self.timeline_start = 0.0
        self.timeline_end = 10.0
        self.timeline_loop = False

        # Registered update callbacks
        self.update_callbacks: List[Callable] = []

        logger.info("AnimationEngine initialized")

    def create_track(
        self,
        name: str,
        target_path: str,
        property_name: str,
        keyframes: List[AnimationKeyframe],
        is_looping: bool = False,
    ) -> AnimationTrack:
        """Create new animation track.

        Args:
            name: Track name
            target_path: Path to target object
            property_name: Property to animate
            keyframes: List of keyframes
            is_looping: Whether to loop animation

        Returns:
            Created animation track
        """
        # Sort keyframes by time
        keyframes.sort(key=lambda k: k.time)

        # Calculate duration
        duration = keyframes[-1].time if keyframes else 0.0

        track = AnimationTrack(
            name=name,
            target_path=target_path,
            property_name=property_name,
            keyframes=keyframes,
            is_looping=is_looping,
            duration=duration,
        )

        self.tracks[name] = track
        logger.info(f"Created animation track: {name}")

        return track

    def add_keyframe(
        self,
        track_name: str,
        time: float,
        value: Any,
        interpolation: InterpolationType = InterpolationType.LINEAR,
    ) -> None:
        """Add keyframe to existing track.

        Args:
            track_name: Name of track
            time: Keyframe time
            value: Keyframe value
            interpolation: Interpolation type
        """
        if track_name not in self.tracks:
            logger.error(f"Track not found: {track_name}")
            return

        keyframe = AnimationKeyframe(
            time=time, value=value, interpolation=interpolation
        )

        track = self.tracks[track_name]
        track.keyframes.append(keyframe)
        track.keyframes.sort(key=lambda k: k.time)

        # Update duration
        track.duration = track.keyframes[-1].time

    def create_neural_activity_animation(
        self, duration: float = 10.0, frequency: float = 1.0, amplitude: float = 1.0
    ) -> str:
        """Create animation for neural activity visualization.

        Args:
            duration: Animation duration
            frequency: Oscillation frequency
            amplitude: Activity amplitude

        Returns:
            Track name
        """
        track_name = "neural_activity"
        keyframes = []

        # Create sinusoidal activity pattern
        num_keyframes = int(duration * self.default_fps)
        for i in range(num_keyframes):
            time = i / self.default_fps
            value = amplitude * (0.5 + 0.5 * np.sin(2 * np.pi * frequency * time))

            keyframes.append(
                AnimationKeyframe(
                    time=time, value=value, interpolation=InterpolationType.CUBIC
                )
            )

        self.create_track(
            name=track_name,
            target_path="/Root/Brain",
            property_name="activity_intensity",
            keyframes=keyframes,
            is_looping=True,
        )

        return track_name

    def create_camera_orbit_animation(
        self,
        center: Tuple[float, float, float] = (0, 0, 0),
        radius: float = 2.0,
        duration: float = 10.0,
        vertical_angle: float = 30.0,
    ) -> str:
        """Create camera orbit animation.

        Args:
            center: Orbit center
            radius: Orbit radius
            duration: Orbit duration
            vertical_angle: Vertical angle in degrees

        Returns:
            Track name
        """
        track_name = "camera_orbit"
        keyframes = []

        # Convert vertical angle to radians
        v_angle = np.radians(vertical_angle)

        # Create orbit keyframes
        steps = int(duration * self.default_fps)
        for i in range(steps + 1):
            time = i / self.default_fps
            angle = (i / steps) * 2 * np.pi

            # Calculate position
            x = center[0] + radius * np.cos(angle) * np.cos(v_angle)
            y = center[1] + radius * np.sin(v_angle)
            z = center[2] + radius * np.sin(angle) * np.cos(v_angle)

            position = (x, y, z)

            keyframes.append(
                AnimationKeyframe(
                    time=time, value=position, interpolation=InterpolationType.LINEAR
                )
            )

        self.create_track(
            name=track_name,
            target_path="/Root/Camera",
            property_name="position",
            keyframes=keyframes,
            is_looping=True,
        )

        return track_name

    def create_pulse_animation(
        self,
        target_path: str,
        property_name: str = "scale",
        min_value: float = 0.9,
        max_value: float = 1.1,
        pulse_duration: float = 1.0,
        num_pulses: int = 10,
    ) -> str:
        """Create pulsing animation.

        Args:
            target_path: Target object path
            property_name: Property to pulse
            min_value: Minimum value
            max_value: Maximum value
            pulse_duration: Duration of one pulse
            num_pulses: Number of pulses

        Returns:
            Track name
        """
        track_name = f"pulse_{target_path.replace('/', '_')}"
        keyframes = []

        for pulse in range(num_pulses):
            base_time = pulse * pulse_duration

            # Create pulse
            keyframes.extend(
                [
                    AnimationKeyframe(
                        time=base_time,
                        value=min_value,
                        interpolation=InterpolationType.EASE_OUT,
                    ),
                    AnimationKeyframe(
                        time=base_time + pulse_duration * 0.5,
                        value=max_value,
                        interpolation=InterpolationType.EASE_IN,
                    ),
                    AnimationKeyframe(
                        time=base_time + pulse_duration,
                        value=min_value,
                        interpolation=InterpolationType.LINEAR,
                    ),
                ]
            )

        self.create_track(
            name=track_name,
            target_path=target_path,
            property_name=property_name,
            keyframes=keyframes,
            is_looping=True,
        )

        return track_name

    def register_procedural_animation(
        self, name: str, update_function: Callable[[float, float], Dict[str, Any]]
    ) -> None:
        """Register procedural animation function.

        Args:
            name: Animation name
            update_function: Function(time, dt) -> property updates
        """
        self.procedural_animations[name] = update_function
        logger.info(f"Registered procedural animation: {name}")

    def update(self, dt: float) -> Dict[str, Dict[str, Any]]:
        """Update all animations.

        Args:
            dt: Time delta

        Returns:
            Dictionary of property updates
        """
        if not self.is_playing:
            return {}

        self._update_time(dt)

        updates = {}
        self._update_keyframe_animations(updates)
        self._update_procedural_animations(updates, dt)
        self._fire_update_callbacks(updates)

        return updates

    def _update_time(self, dt: float) -> None:
        """Update current time and handle looping."""
        self.current_time += dt * self.playback_speed

        if self.timeline_loop and self.current_time > self.timeline_end:
            self.current_time = self.timeline_start

    def _update_keyframe_animations(self, updates: Dict[str, Dict[str, Any]]) -> None:
        """Update all keyframe animations."""
        for track_name, track in self.tracks.items():
            value = self._evaluate_track(track, self.current_time)
            if value is not None:
                if track.target_path not in updates:
                    updates[track.target_path] = {}
                updates[track.target_path][track.property_name] = value

    def _update_procedural_animations(
        self, updates: Dict[str, Dict[str, Any]], dt: float
    ) -> None:
        """Update all procedural animations."""
        for anim_name, anim_func in self.procedural_animations.items():
            if anim_name in self.active_animations:
                proc_updates = anim_func(self.current_time, dt)
                for target_path, properties in proc_updates.items():
                    if target_path not in updates:
                        updates[target_path] = {}
                    updates[target_path].update(properties)

    def _fire_update_callbacks(self, updates: Dict[str, Dict[str, Any]]) -> None:
        """Fire all update callbacks."""
        for callback in self.update_callbacks:
            callback(self.current_time, updates)

    def _evaluate_track(self, track: AnimationTrack, time: float) -> Any:
        """Evaluate animation track at given time.

        Args:
            track: Animation track
            time: Evaluation time

        Returns:
            Interpolated value
        """
        if not track.keyframes:
            return None

        # Handle looping
        if track.is_looping and track.duration > 0:
            time = time % track.duration

        # Find surrounding keyframes
        prev_key = None
        next_key = None

        for i, keyframe in enumerate(track.keyframes):
            if keyframe.time <= time:
                prev_key = keyframe
                if i < len(track.keyframes) - 1:
                    next_key = track.keyframes[i + 1]
            else:
                break

        # No previous keyframe
        if prev_key is None:
            return track.keyframes[0].value

        # No next keyframe or exact match
        if next_key is None or prev_key.time == time:
            return prev_key.value

        # Interpolate between keyframes
        t = (time - prev_key.time) / (next_key.time - prev_key.time)
        return self._interpolate(
            prev_key.value, next_key.value, t, prev_key.interpolation
        )

    def _interpolate(
        self, value1: Any, value2: Any, t: float, interpolation: InterpolationType
    ) -> Any:
        """Interpolate between two values.

        Args:
            value1: Start value
            value2: End value
            t: Interpolation parameter (0-1)
            interpolation: Interpolation type

        Returns:
            Interpolated value
        """
        # Apply easing
        if interpolation == InterpolationType.EASE_IN:
            t = t * t
        elif interpolation == InterpolationType.EASE_OUT:
            t = 1 - (1 - t) * (1 - t)
        elif interpolation == InterpolationType.EASE_IN_OUT:
            t = 3 * t * t - 2 * t * t * t
        elif interpolation == InterpolationType.STEP:
            return value1 if t < 1.0 else value2
        elif interpolation == InterpolationType.CUBIC:
            t = t * t * (3 - 2 * t)

        # Interpolate based on value type
        if isinstance(value1, (int, float)):
            return value1 + (value2 - value1) * t
        elif isinstance(value1, (list, tuple)):
            return type(value1)(v1 + (v2 - v1) * t for v1, v2 in zip(value1, value2))
        elif isinstance(value1, np.ndarray):
            return value1 + (value2 - value1) * t
        else:
            # Non-interpolatable, use step
            return value1 if t < 0.5 else value2

    def play(self) -> None:
        """Start animation playback."""
        self.is_playing = True
        logger.info("Animation playback started")

    def pause(self) -> None:
        """Pause animation playback."""
        self.is_playing = False
        logger.info("Animation playback paused")

    def stop(self) -> None:
        """Stop animation and reset time."""
        self.is_playing = False
        self.current_time = self.timeline_start
        logger.info("Animation playback stopped")

    def seek(self, time: float) -> None:
        """Seek to specific time.

        Args:
            time: Target time
        """
        self.current_time = max(self.timeline_start, min(time, self.timeline_end))
        logger.info(f"Animation seeked to {self.current_time}")

    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed multiplier.

        Args:
            speed: Playback speed (1.0 = normal)
        """
        self.playback_speed = speed
        logger.info(f"Playback speed set to {speed}x")

    def export_tracks(self) -> Dict[str, Any]:
        """Export animation tracks for serialization.

        Returns:
            Serializable animation data
        """
        export_data = {
            "tracks": {},
            "timeline": {
                "start": self.timeline_start,
                "end": self.timeline_end,
                "loop": self.timeline_loop,
                "fps": self.default_fps,
            },
        }

        for name, track in self.tracks.items():
            export_data["tracks"][name] = {
                "target_path": track.target_path,
                "property_name": track.property_name,
                "is_looping": track.is_looping,
                "duration": track.duration,
                "keyframes": [
                    {
                        "time": kf.time,
                        "value": kf.value,
                        "interpolation": kf.interpolation.value,
                    }
                    for kf in track.keyframes
                ],
            }

        return export_data

    def import_tracks(self, data: Dict[str, Any]) -> None:
        """Import animation tracks from serialized data.

        Args:
            data: Animation data
        """
        # Import timeline settings
        timeline = data.get("timeline", {})
        self.timeline_start = timeline.get("start", 0.0)
        self.timeline_end = timeline.get("end", 10.0)
        self.timeline_loop = timeline.get("loop", False)
        self.default_fps = timeline.get("fps", 60.0)

        # Import tracks
        for name, track_data in data.get("tracks", {}).items():
            keyframes = []
            for kf_data in track_data["keyframes"]:
                keyframes.append(
                    AnimationKeyframe(
                        time=kf_data["time"],
                        value=kf_data["value"],
                        interpolation=InterpolationType(kf_data["interpolation"]),
                    )
                )

            self.create_track(
                name=name,
                target_path=track_data["target_path"],
                property_name=track_data["property_name"],
                keyframes=keyframes,
                is_looping=track_data["is_looping"],
            )

        logger.info(f"Imported {len(data.get('tracks', {}))} animation tracks")

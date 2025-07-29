"""Volume renderer for 3D neural activity visualization."""

import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class VolumeRenderer:
    """Renders volumetric neural activity data.

    Uses ray marching techniques to visualize 3D neural
    activity distributions within the brain volume.
    """

    def __init__(self) -> None:
        """Initialize volume renderer."""
        self.volume_data: Optional[np.ndarray] = None
        self.transfer_function: Dict[str, Any] = {}
        self.render_settings: Dict[str, Any] = {}

        # Ray marching parameters
        self.step_size = 0.01
        self.max_steps = 200
        self.early_termination_threshold = 0.95

        # Volume properties
        self.volume_spacing = (1.0, 1.0, 1.0)  # mm
        self.volume_origin = (0.0, 0.0, 0.0)

        # Rendering mode
        self.render_mode = "mip"  # maximum intensity projection
        self.shading_enabled = True

        logger.info("VolumeRenderer initialized")

    async def set_volume_data(
        self,
        data: np.ndarray,
        spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """Set volume data for rendering.

        Args:
            data: 3D volume data
            spacing: Voxel spacing in mm
            origin: Volume origin in world space
        """
        self.volume_data = data
        self.volume_spacing = spacing
        self.volume_origin = origin

        # Update transfer function based on data range
        await self._update_transfer_function()

        logger.info(f"Volume data set: shape={data.shape}, spacing={spacing}")

    async def render_volume(
        self,
        camera_position: Tuple[float, float, float],
        camera_target: Tuple[float, float, float],
        resolution: Tuple[int, int] = (1920, 1080),
    ) -> np.ndarray:
        """Render volume from given camera position.

        Args:
            camera_position: Camera position in world space
            camera_target: Camera look-at target
            resolution: Output image resolution

        Returns:
            Rendered volume image
        """
        if self.volume_data is None:
            logger.error("No volume data set")
            return np.zeros((*resolution, 4), dtype=np.uint8)

        try:
            # Generate rays
            rays = self._generate_rays(camera_position, camera_target, resolution)

            # Ray march through volume
            if self.render_mode == "mip":
                image = await self._ray_march_mip(rays)
            elif self.render_mode == "composite":
                image = await self._ray_march_composite(rays)
            elif self.render_mode == "iso_surface":
                image = await self._ray_march_iso_surface(rays)
            else:
                raise ValueError(f"Unknown render mode: {self.render_mode}")

            # Apply shading if enabled
            if self.shading_enabled:
                image = self._apply_shading(image, rays)

            return image

        except Exception as e:
            logger.error(f"Volume rendering failed: {e}")
            return np.zeros((*resolution, 4), dtype=np.uint8)

    async def _update_transfer_function(self) -> None:
        """Update transfer function based on volume data."""
        if self.volume_data is None:
            return

        # Calculate data range
        data_min = float(np.min(self.volume_data))
        data_max = float(np.max(self.volume_data))

        # Create default transfer function
        self.transfer_function = {
            "color_map": [
                {"value": data_min, "color": (0.0, 0.0, 0.0), "opacity": 0.0},
                {
                    "value": data_min + 0.1 * (data_max - data_min),
                    "color": (0.0, 0.0, 1.0),
                    "opacity": 0.1,
                },
                {
                    "value": data_min + 0.5 * (data_max - data_min),
                    "color": (0.0, 1.0, 0.0),
                    "opacity": 0.5,
                },
                {
                    "value": data_min + 0.9 * (data_max - data_min),
                    "color": (1.0, 1.0, 0.0),
                    "opacity": 0.8,
                },
                {"value": data_max, "color": (1.0, 0.0, 0.0), "opacity": 1.0},
            ],
            "interpolation": "linear",
        }

    def _generate_rays(
        self,
        camera_pos: Tuple[float, float, float],
        camera_target: Tuple[float, float, float],
        resolution: Tuple[int, int],
    ) -> np.ndarray:
        """Generate rays for volume rendering.

        Returns:
            Ray origins and directions
        """
        width, height = resolution

        # Calculate camera basis vectors
        forward = np.array(camera_target) - np.array(camera_pos)
        forward = forward / np.linalg.norm(forward)

        right = np.cross([0, 1, 0], forward)
        right = right / np.linalg.norm(right)

        up = np.cross(forward, right)

        # Generate ray directions
        rays = np.zeros((height, width, 6))  # origin (3) + direction (3)

        fov = 60.0  # field of view in degrees
        aspect = width / height

        for y in range(height):
            for x in range(width):
                # Normalized device coordinates
                u = (2.0 * x / width - 1.0) * aspect
                v = 1.0 - 2.0 * y / height

                # Ray direction
                direction = (
                    forward
                    + u * right * np.tan(np.radians(fov / 2))
                    + v * up * np.tan(np.radians(fov / 2))
                )
                direction = direction / np.linalg.norm(direction)

                rays[y, x, :3] = camera_pos
                rays[y, x, 3:] = direction

        return rays

    async def _ray_march_mip(self, rays: np.ndarray) -> np.ndarray:
        """Maximum intensity projection ray marching.

        Args:
            rays: Ray origins and directions

        Returns:
            Rendered image
        """
        height, width = rays.shape[:2]
        image = np.zeros((height, width, 4), dtype=np.float32)

        # Simplified MIP rendering
        # In production, would properly intersect rays with volume
        for y in range(height):
            for x in range(width):
                max_value = 0.0

                # March along ray
                for step in range(self.max_steps):
                    # Sample position
                    t = step * self.step_size
                    pos = rays[y, x, :3] + t * rays[y, x, 3:]

                    # Check if inside volume (simplified)
                    if self._is_inside_volume(pos):
                        value = self._sample_volume(pos)
                        max_value = max(max_value, value)

                # Map to color
                color, opacity = self._apply_transfer_function(max_value)
                image[y, x] = (*color, opacity)

        return (image * 255).astype(np.uint8)

    async def _ray_march_composite(self, rays: np.ndarray) -> np.ndarray:
        """Composite ray marching with alpha blending.

        Args:
            rays: Ray origins and directions

        Returns:
            Rendered image
        """
        height, width = rays.shape[:2]
        image = np.zeros((height, width, 4), dtype=np.float32)

        # Simplified composite rendering
        for y in range(height):
            for x in range(width):
                accumulated_color = np.array([0.0, 0.0, 0.0])
                accumulated_opacity = 0.0

                # March along ray
                for step in range(self.max_steps):
                    # Early termination
                    if accumulated_opacity >= self.early_termination_threshold:
                        break

                    # Sample position
                    t = step * self.step_size
                    pos = rays[y, x, :3] + t * rays[y, x, 3:]

                    # Check if inside volume
                    if self._is_inside_volume(pos):
                        value = self._sample_volume(pos)
                        color, opacity = self._apply_transfer_function(value)

                        # Alpha blending
                        opacity *= self.step_size
                        weight = opacity * (1.0 - accumulated_opacity)
                        accumulated_color += np.array(color) * weight
                        accumulated_opacity += weight

                image[y, x] = (*accumulated_color, accumulated_opacity)

        return (image * 255).astype(np.uint8)

    async def _ray_march_iso_surface(self, rays: np.ndarray) -> np.ndarray:
        """Iso-surface rendering.

        Args:
            rays: Ray origins and directions

        Returns:
            Rendered image
        """
        # Simplified iso-surface rendering
        # In production, would use proper iso-surface extraction
        return await self._ray_march_mip(rays)

    def _is_inside_volume(self, pos: np.ndarray) -> bool:
        """Check if position is inside volume bounds."""
        if self.volume_data is None:
            return False

        # Convert world position to voxel coordinates
        voxel_pos = (pos - np.array(self.volume_origin)) / np.array(self.volume_spacing)

        # Check bounds
        return (
            0 <= voxel_pos[0] < self.volume_data.shape[0]
            and 0 <= voxel_pos[1] < self.volume_data.shape[1]
            and 0 <= voxel_pos[2] < self.volume_data.shape[2]
        )

    def _sample_volume(self, pos: np.ndarray) -> float:
        """Sample volume at world position with trilinear interpolation."""
        if self.volume_data is None:
            return 0.0

        # Convert to voxel coordinates
        voxel_pos = (pos - np.array(self.volume_origin)) / np.array(self.volume_spacing)

        # Trilinear interpolation (simplified)
        x, y, z = voxel_pos
        x0, y0, z0 = int(x), int(y), int(z)

        # Clamp to volume bounds
        x0 = max(0, min(x0, self.volume_data.shape[0] - 2))
        y0 = max(0, min(y0, self.volume_data.shape[1] - 2))
        z0 = max(0, min(z0, self.volume_data.shape[2] - 2))

        # Get fractional parts
        fx, fy, fz = x - x0, y - y0, z - z0

        # Sample 8 neighbors
        c000 = self.volume_data[x0, y0, z0]
        c001 = self.volume_data[x0, y0, z0 + 1]
        c010 = self.volume_data[x0, y0 + 1, z0]
        c011 = self.volume_data[x0, y0 + 1, z0 + 1]
        c100 = self.volume_data[x0 + 1, y0, z0]
        c101 = self.volume_data[x0 + 1, y0, z0 + 1]
        c110 = self.volume_data[x0 + 1, y0 + 1, z0]
        c111 = self.volume_data[x0 + 1, y0 + 1, z0 + 1]

        # Trilinear interpolation
        c00 = c000 * (1 - fx) + c100 * fx
        c01 = c001 * (1 - fx) + c101 * fx
        c10 = c010 * (1 - fx) + c110 * fx
        c11 = c011 * (1 - fx) + c111 * fx

        c0 = c00 * (1 - fy) + c10 * fy
        c1 = c01 * (1 - fy) + c11 * fy

        return float(c0 * (1 - fz) + c1 * fz)

    def _apply_transfer_function(
        self, value: float
    ) -> Tuple[Tuple[float, float, float], float]:
        """Apply transfer function to map value to color and opacity.

        Args:
            value: Scalar value

        Returns:
            Color (RGB) and opacity
        """
        color_map = self.transfer_function.get("color_map", [])

        if not color_map:
            return (1.0, 1.0, 1.0), 1.0

        # Find surrounding control points
        for i in range(len(color_map) - 1):
            if color_map[i]["value"] <= value <= color_map[i + 1]["value"]:
                # Linear interpolation
                t = (value - color_map[i]["value"]) / (
                    color_map[i + 1]["value"] - color_map[i]["value"]
                )

                color1 = color_map[i]["color"]
                color2 = color_map[i + 1]["color"]
                opacity1 = color_map[i]["opacity"]
                opacity2 = color_map[i + 1]["opacity"]

                color = tuple(color1[j] * (1 - t) + color2[j] * t for j in range(3))
                opacity = opacity1 * (1 - t) + opacity2 * t

                return color, opacity

        # Value outside range
        if value <= color_map[0]["value"]:
            return color_map[0]["color"], color_map[0]["opacity"]
        else:
            return color_map[-1]["color"], color_map[-1]["opacity"]

    def _apply_shading(self, image: np.ndarray, rays: np.ndarray) -> np.ndarray:
        """Apply shading to rendered volume.

        Args:
            image: Rendered image
            rays: Ray data

        Returns:
            Shaded image
        """
        # Simple ambient + diffuse shading
        # In production, would calculate gradients and proper lighting
        ambient = 0.3
        diffuse = 0.7

        shaded = image.copy()
        shaded[:, :, :3] = image[:, :, :3] * (ambient + diffuse)

        return shaded

    def set_render_mode(self, mode: str) -> None:
        """Set volume rendering mode.

        Args:
            mode: Rendering mode (mip, composite, iso_surface)
        """
        if mode in ["mip", "composite", "iso_surface"]:
            self.render_mode = mode
            logger.info(f"Volume render mode set to: {mode}")
        else:
            logger.error(f"Invalid render mode: {mode}")

    def update_transfer_function(self, transfer_function: Dict[str, Any]) -> None:
        """Update transfer function for volume rendering.

        Args:
            transfer_function: New transfer function definition
        """
        self.transfer_function = transfer_function
        logger.info("Transfer function updated")

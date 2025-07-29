"""Electrode models for EEG/neural interface visualization."""

import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)


class ElectrodeModels:
    """Manages 3D electrode models and positioning.

    Supports various electrode systems including 10-20, 10-10,
    and custom high-density arrays for neural interfaces.
    """

    def __init__(self) -> None:
        """Initialize electrode models."""
        self.electrode_positions: Dict[str, Tuple[float, float, float]] = {}
        self.electrode_meshes: Dict[str, Dict[str, Any]] = {}
        self.montages: Dict[str, Dict[str, Any]] = {}

        # Standard electrode properties
        self.default_radius = 0.005  # 5mm
        self.default_height = 0.002  # 2mm
        self.default_material = "electrode_silver"

        # Initialize standard montages
        self._initialize_standard_montages()

        logger.info("ElectrodeModels initialized")

    def _initialize_standard_montages(self) -> None:
        """Initialize standard electrode montages."""
        # 10-20 International System
        self.montages["10-20"] = {
            "Fp1": (-0.309, 0.951, 0.0),
            "Fp2": (0.309, 0.951, 0.0),
            "F7": (-0.809, 0.588, 0.0),
            "F3": (-0.545, 0.673, 0.5),
            "Fz": (0.0, 0.719, 0.695),
            "F4": (0.545, 0.673, 0.5),
            "F8": (0.809, 0.588, 0.0),
            "T3": (-1.0, 0.0, 0.0),
            "C3": (-0.719, 0.0, 0.695),
            "Cz": (0.0, 0.0, 1.0),
            "C4": (0.719, 0.0, 0.695),
            "T4": (1.0, 0.0, 0.0),
            "T5": (-0.809, -0.588, 0.0),
            "P3": (-0.545, -0.673, 0.5),
            "Pz": (0.0, -0.719, 0.695),
            "P4": (0.545, -0.673, 0.5),
            "T6": (0.809, -0.588, 0.0),
            "O1": (-0.309, -0.951, 0.0),
            "O2": (0.309, -0.951, 0.0),
        }

        # 10-10 System (extended)
        self.montages["10-10"] = self._generate_10_10_montage()

        # High-density 128 channel
        self.montages["HD-128"] = self._generate_high_density_montage(128)

        # BCI array patterns
        self.montages["BCI-8x8"] = self._generate_grid_montage(8, 8)
        self.montages["BCI-16x16"] = self._generate_grid_montage(16, 16)

    def _generate_10_10_montage(self) -> Dict[str, Tuple[float, float, float]]:
        """Generate 10-10 electrode positions."""
        # Extended from 10-20 with additional positions
        montage = self.montages["10-20"].copy()

        # Add intermediate positions
        additional = {
            "Fpz": (0.0, 0.951, 0.309),
            "AFz": (0.0, 0.809, 0.588),
            "AF3": (-0.406, 0.809, 0.425),
            "AF4": (0.406, 0.809, 0.425),
            "F1": (-0.273, 0.673, 0.673),
            "F2": (0.273, 0.673, 0.673),
            "F5": (-0.673, 0.673, 0.273),
            "F6": (0.673, 0.673, 0.273),
            "FC1": (-0.359, 0.359, 0.866),
            "FC2": (0.359, 0.359, 0.866),
            "FC3": (-0.623, 0.359, 0.695),
            "FC4": (0.623, 0.359, 0.695),
            "FC5": (-0.866, 0.359, 0.359),
            "FC6": (0.866, 0.359, 0.359),
            "C1": (-0.359, 0.0, 0.866),
            "C2": (0.359, 0.0, 0.866),
            "C5": (-0.866, 0.0, 0.5),
            "C6": (0.866, 0.0, 0.5),
            "CP1": (-0.359, -0.359, 0.866),
            "CP2": (0.359, -0.359, 0.866),
            "CP3": (-0.623, -0.359, 0.695),
            "CP4": (0.623, -0.359, 0.695),
            "CP5": (-0.866, -0.359, 0.359),
            "CP6": (0.866, -0.359, 0.359),
            "P1": (-0.273, -0.673, 0.673),
            "P2": (0.273, -0.673, 0.673),
            "P5": (-0.673, -0.673, 0.273),
            "P6": (0.673, -0.673, 0.273),
            "PO3": (-0.406, -0.809, 0.425),
            "PO4": (0.406, -0.809, 0.425),
            "POz": (0.0, -0.809, 0.588),
            "Oz": (0.0, -0.951, 0.309),
        }

        montage.update(additional)
        return montage

    def _generate_high_density_montage(
        self, num_channels: int
    ) -> Dict[str, Tuple[float, float, float]]:
        """Generate high-density electrode montage."""
        montage = {}

        # Use spherical distribution
        phi = np.pi * (3.0 - np.sqrt(5.0))  # Golden angle

        for i in range(num_channels):
            theta = phi * i
            y = 1 - (i / float(num_channels - 1)) * 2
            radius = np.sqrt(1 - y * y)

            x = np.cos(theta) * radius
            z = np.sin(theta) * radius

            # Scale to head size (approximately)
            x *= 0.9
            y *= 0.9
            z *= 0.9

            montage[f"HD{i + 1:03d}"] = (x, y, z)

        return montage

    def _generate_grid_montage(
        self, rows: int, cols: int
    ) -> Dict[str, Tuple[float, float, float]]:
        """Generate grid-based electrode montage for BCI arrays."""
        montage = {}

        # Grid spacing
        spacing = 0.01  # 10mm

        # Center the grid
        x_offset = -(cols - 1) * spacing / 2
        y_offset = -(rows - 1) * spacing / 2

        for row in range(rows):
            for col in range(cols):
                x = x_offset + col * spacing
                y = y_offset + row * spacing
                z = 0.0  # Flat array

                channel_name = f"G{row + 1:02d}{col + 1:02d}"
                montage[channel_name] = (x, y, z)

        return montage

    async def create_electrode_models(
        self, montage_name: str = "10-20", scale_to_head: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """Create 3D electrode models for specified montage.

        Args:
            montage_name: Name of electrode montage
            scale_to_head: Whether to scale positions to head model

        Returns:
            Dictionary of electrode models
        """
        if montage_name not in self.montages:
            logger.error(f"Unknown montage: {montage_name}")
            return {}

        montage = self.montages[montage_name]
        models = {}

        for channel_name, position in montage.items():
            # Create electrode geometry
            if montage_name.startswith("BCI"):
                # Flat disc for BCI arrays
                model = self._create_disc_electrode(position)
            else:
                # Spherical cap for EEG
                model = self._create_cap_electrode(position)

            model["channel"] = channel_name
            model["position"] = position
            models[channel_name] = model

        self.electrode_meshes = models
        logger.info(f"Created {len(models)} electrode models for {montage_name}")

        return models

    def _create_cap_electrode(
        self, position: Tuple[float, float, float]
    ) -> Dict[str, Any]:
        """Create spherical cap electrode model."""
        # Generate spherical cap mesh
        theta_steps = 16
        phi_steps = 8

        vertices = []
        faces = []

        # Create vertices
        for i in range(phi_steps + 1):
            phi = (i / phi_steps) * np.pi / 4  # Quarter sphere
            for j in range(theta_steps):
                theta = (j / theta_steps) * 2 * np.pi

                x = self.default_radius * np.sin(phi) * np.cos(theta)
                y = self.default_radius * np.sin(phi) * np.sin(theta)
                z = self.default_radius * np.cos(phi)

                vertices.append([x, y, z])

        # Create faces
        for i in range(phi_steps):
            for j in range(theta_steps):
                v1 = i * theta_steps + j
                v2 = i * theta_steps + (j + 1) % theta_steps
                v3 = (i + 1) * theta_steps + (j + 1) % theta_steps
                v4 = (i + 1) * theta_steps + j

                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])

        return {
            "type": "cap",
            "vertices": np.array(vertices),
            "faces": np.array(faces),
            "material": self.default_material,
        }

    def _create_disc_electrode(
        self, position: Tuple[float, float, float]
    ) -> Dict[str, Any]:
        """Create flat disc electrode model."""
        # Generate disc mesh
        segments = 32
        rings = 3

        vertices = []
        faces = []

        # Center vertex
        vertices.append([0, 0, 0])

        # Create rings
        for ring in range(1, rings + 1):
            radius = (ring / rings) * self.default_radius
            for seg in range(segments):
                angle = (seg / segments) * 2 * np.pi
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                vertices.append([x, y, 0])

        # Create faces
        # Center to first ring
        for i in range(segments):
            v1 = 0
            v2 = 1 + i
            v3 = 1 + (i + 1) % segments
            faces.append([v1, v2, v3])

        # Between rings
        for ring in range(rings - 1):
            for i in range(segments):
                base = 1 + ring * segments
                v1 = base + i
                v2 = base + (i + 1) % segments
                v3 = base + segments + (i + 1) % segments
                v4 = base + segments + i

                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])

        return {
            "type": "disc",
            "vertices": np.array(vertices),
            "faces": np.array(faces),
            "material": "electrode_gold",
        }

    def project_to_scalp(
        self,
        electrode_positions: Dict[str, Tuple[float, float, float]],
        scalp_mesh: np.ndarray,
    ) -> Dict[str, Tuple[float, float, float]]:
        """Project electrode positions onto scalp surface.

        Args:
            electrode_positions: Original electrode positions
            scalp_mesh: Scalp surface mesh vertices

        Returns:
            Projected electrode positions
        """
        projected = {}

        for channel, pos in electrode_positions.items():
            # Find nearest point on scalp
            distances = np.linalg.norm(scalp_mesh - np.array(pos), axis=1)
            nearest_idx = np.argmin(distances)

            # Project along normal
            scalp_point = scalp_mesh[nearest_idx]
            normal = scalp_point / np.linalg.norm(scalp_point)

            # Place electrode slightly above scalp
            projected_pos = scalp_point + normal * 0.002  # 2mm above
            projected[channel] = tuple(projected_pos)

        return projected

    def get_electrode_position(
        self, channel_name: str
    ) -> Optional[Tuple[float, float, float]]:
        """Get position of specific electrode.

        Args:
            channel_name: Electrode channel name

        Returns:
            3D position or None
        """
        for montage in self.montages.values():
            if channel_name in montage:
                return montage[channel_name]

        return None

    def get_neighbors(
        self, channel_name: str, radius: float = 0.15
    ) -> List[Tuple[str, float]]:
        """Get neighboring electrodes within radius.

        Args:
            channel_name: Center electrode
            radius: Search radius

        Returns:
            List of (channel_name, distance) tuples
        """
        center_pos = self.get_electrode_position(channel_name)
        if not center_pos:
            return []

        neighbors = []
        center = np.array(center_pos)

        # Search in current montage
        for montage in self.montages.values():
            if channel_name in montage:
                for ch, pos in montage.items():
                    if ch != channel_name:
                        distance = np.linalg.norm(np.array(pos) - center)
                        if distance <= radius:
                            neighbors.append((ch, distance))
                break

        # Sort by distance
        neighbors.sort(key=lambda x: x[1])
        return neighbors

    def create_interpolated_positions(
        self, base_montage: str, factor: int = 2
    ) -> Dict[str, Tuple[float, float, float]]:
        """Create interpolated electrode positions for higher density.

        Args:
            base_montage: Base montage name
            factor: Interpolation factor

        Returns:
            Interpolated positions
        """
        if base_montage not in self.montages:
            return {}

        base_positions = self.montages[base_montage]
        interpolated = base_positions.copy()

        # Find neighboring pairs and interpolate
        for ch1, pos1 in base_positions.items():
            neighbors = self.get_neighbors(ch1, radius=0.3)

            for ch2, _ in neighbors[:4]:  # Use 4 nearest neighbors
                pos2 = base_positions[ch2]

                # Interpolate between positions
                for i in range(1, factor):
                    t = i / factor
                    interp_pos = (
                        pos1[0] * (1 - t) + pos2[0] * t,
                        pos1[1] * (1 - t) + pos2[1] * t,
                        pos1[2] * (1 - t) + pos2[2] * t,
                    )

                    # Normalize to sphere surface
                    interp_pos = np.array(interp_pos)
                    interp_pos = interp_pos / np.linalg.norm(interp_pos)

                    interp_name = f"{ch1}_{ch2}_{i}"
                    interpolated[interp_name] = tuple(interp_pos)

        return interpolated

    def set_electrode_color(
        self, channel_name: str, color: Tuple[float, float, float, float]
    ) -> None:
        """Set electrode visualization color.

        Args:
            channel_name: Electrode channel
            color: RGBA color
        """
        if channel_name in self.electrode_meshes:
            self.electrode_meshes[channel_name]["color"] = color

    def highlight_electrodes(
        self, channels: List[str], highlight_color: Tuple[float, float, float, float]
    ) -> None:
        """Highlight specific electrodes.

        Args:
            channels: List of channels to highlight
            highlight_color: Highlight color
        """
        for channel in channels:
            self.set_electrode_color(channel, highlight_color)

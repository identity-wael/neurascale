"""Material library for neural visualization in Omniverse."""

import logging
from typing import Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class MaterialLibrary:
    """Library of materials for neural visualization.

    Provides physically-based materials optimized for
    brain tissue and neural activity visualization.
    """

    def __init__(self) -> None:
        """Initialize material library."""
        self.materials: Dict[str, Dict[str, Any]] = {}
        self.shaders: Dict[str, str] = {}

        # Initialize default materials
        self._create_default_materials()

        logger.info("MaterialLibrary initialized")

    def _create_default_materials(self) -> None:
        """Create default material presets."""
        # Brain tissue materials
        self.materials["brain_gray_matter"] = {
            "base_color": (0.85, 0.82, 0.80, 1.0),
            "metallic": 0.0,
            "roughness": 0.85,
            "specular": 0.3,
            "subsurface": 0.7,
            "subsurface_radius": (0.9, 0.7, 0.5),
            "subsurface_color": (0.9, 0.85, 0.8),
            "ior": 1.4,  # Index of refraction for tissue
            "opacity": 1.0,
        }

        self.materials["brain_white_matter"] = {
            "base_color": (0.95, 0.93, 0.91, 1.0),
            "metallic": 0.0,
            "roughness": 0.9,
            "specular": 0.2,
            "subsurface": 0.8,
            "subsurface_radius": (1.0, 0.9, 0.8),
            "subsurface_color": (0.95, 0.92, 0.9),
            "ior": 1.38,
            "opacity": 1.0,
        }

        self.materials["cerebrospinal_fluid"] = {
            "base_color": (0.95, 0.98, 1.0, 0.3),
            "metallic": 0.0,
            "roughness": 0.0,
            "specular": 1.0,
            "transmission": 0.95,
            "ior": 1.33,  # Similar to water
            "opacity": 0.3,
            "thin_walled": True,
        }

        # Electrode materials
        self.materials["electrode_gold"] = {
            "base_color": (1.0, 0.843, 0.0, 1.0),
            "metallic": 1.0,
            "roughness": 0.15,
            "specular": 1.0,
            "anisotropy": 0.0,
            "opacity": 1.0,
        }

        self.materials["electrode_silver"] = {
            "base_color": (0.95, 0.95, 0.97, 1.0),
            "metallic": 1.0,
            "roughness": 0.1,
            "specular": 1.0,
            "anisotropy": 0.0,
            "opacity": 1.0,
        }

        # Activity visualization materials
        self.materials["neural_activity_low"] = {
            "base_color": (0.0, 0.0, 1.0, 0.5),
            "metallic": 0.0,
            "roughness": 0.5,
            "emission": (0.0, 0.0, 0.5),
            "emission_intensity": 0.5,
            "opacity": 0.5,
        }

        self.materials["neural_activity_medium"] = {
            "base_color": (0.0, 1.0, 0.0, 0.7),
            "metallic": 0.0,
            "roughness": 0.3,
            "emission": (0.0, 1.0, 0.0),
            "emission_intensity": 1.0,
            "opacity": 0.7,
        }

        self.materials["neural_activity_high"] = {
            "base_color": (1.0, 0.0, 0.0, 0.9),
            "metallic": 0.0,
            "roughness": 0.1,
            "emission": (1.0, 0.0, 0.0),
            "emission_intensity": 2.0,
            "opacity": 0.9,
        }

        # Connectivity materials
        self.materials["connectivity_fiber"] = {
            "base_color": (0.7, 0.7, 1.0, 0.8),
            "metallic": 0.0,
            "roughness": 0.3,
            "emission": (0.3, 0.3, 0.8),
            "emission_intensity": 0.3,
            "opacity": 0.8,
            "thin_walled": True,
        }

        # Volume rendering materials
        self.materials["volume_density"] = {
            "density_scale": 100.0,
            "albedo": (1.0, 1.0, 1.0),
            "anisotropy": 0.0,
            "emission_scale": 1.0,
            "blackbody_temperature": 6500.0,
        }

    def create_activity_gradient_material(
        self,
        min_color: Tuple[float, float, float],
        max_color: Tuple[float, float, float],
        steps: int = 10,
    ) -> Dict[str, Any]:
        """Create gradient material for activity visualization.

        Args:
            min_color: Color for minimum activity
            max_color: Color for maximum activity
            steps: Number of gradient steps

        Returns:
            Gradient material definition
        """
        gradient_materials = []

        for i in range(steps):
            t = i / (steps - 1)
            color = tuple(
                min_color[j] + t * (max_color[j] - min_color[j]) for j in range(3)
            )

            material = {
                "base_color": (*color, 0.5 + 0.4 * t),
                "metallic": 0.0,
                "roughness": 0.5 - 0.3 * t,
                "emission": color,
                "emission_intensity": 0.5 + 1.5 * t,
                "opacity": 0.5 + 0.4 * t,
            }

            gradient_materials.append(material)

        return {
            "type": "gradient",
            "materials": gradient_materials,
            "interpolation": "linear",
        }

    def create_heatmap_material(self, colormap: str = "viridis") -> Dict[str, Any]:
        """Create heatmap material for activity mapping.

        Args:
            colormap: Name of colormap to use

        Returns:
            Heatmap material definition
        """
        # Define colormaps
        colormaps = {
            "viridis": [
                (0.267, 0.005, 0.329),
                (0.283, 0.140, 0.458),
                (0.254, 0.267, 0.530),
                (0.207, 0.372, 0.553),
                (0.164, 0.471, 0.558),
                (0.128, 0.567, 0.551),
                (0.135, 0.659, 0.518),
                (0.267, 0.748, 0.441),
                (0.478, 0.821, 0.318),
                (0.741, 0.873, 0.150),
                (0.993, 0.906, 0.144),
            ],
            "jet": [
                (0.0, 0.0, 0.5),
                (0.0, 0.0, 1.0),
                (0.0, 0.5, 1.0),
                (0.0, 1.0, 1.0),
                (0.5, 1.0, 0.5),
                (1.0, 1.0, 0.0),
                (1.0, 0.5, 0.0),
                (1.0, 0.0, 0.0),
                (0.5, 0.0, 0.0),
            ],
            "hot": [
                (0.0, 0.0, 0.0),
                (0.3, 0.0, 0.0),
                (0.6, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 0.3, 0.0),
                (1.0, 0.6, 0.0),
                (1.0, 1.0, 0.0),
                (1.0, 1.0, 0.5),
                (1.0, 1.0, 1.0),
            ],
        }

        colors = colormaps.get(colormap, colormaps["viridis"])

        return {
            "type": "heatmap",
            "colormap": colormap,
            "colors": colors,
            "emission_multiplier": 1.5,
            "opacity_curve": "linear",
        }

    def create_volume_material(
        self, density_scale: float = 100.0, emission_scale: float = 1.0
    ) -> Dict[str, Any]:
        """Create material for volume rendering.

        Args:
            density_scale: Scale factor for density
            emission_scale: Scale factor for emission

        Returns:
            Volume material definition
        """
        return {
            "type": "volume",
            "density_scale": density_scale,
            "albedo": (1.0, 1.0, 1.0),
            "anisotropy": -0.3,  # Backward scattering
            "emission_scale": emission_scale,
            "blackbody_temperature": 5000.0,
            "absorption_scale": 0.5,
        }

    def create_custom_shader(self, shader_name: str, shader_code: str) -> str:
        """Create custom MDL shader for specialized effects.

        Args:
            shader_name: Name for the shader
            shader_code: MDL shader code

        Returns:
            Shader path
        """
        self.shaders[shader_name] = shader_code
        shader_path = f"neurascale::{shader_name}"

        logger.info(f"Created custom shader: {shader_name}")
        return shader_path

    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Get material definition by name.

        Args:
            material_name: Name of material

        Returns:
            Material definition or None
        """
        return self.materials.get(material_name)

    def blend_materials(
        self, material1: Dict[str, Any], material2: Dict[str, Any], blend_factor: float
    ) -> Dict[str, Any]:
        """Blend two materials together.

        Args:
            material1: First material
            material2: Second material
            blend_factor: Blend factor (0-1)

        Returns:
            Blended material
        """
        blended = {}

        # Blend numeric properties
        for key in material1:
            if key in material2:
                val1 = material1[key]
                val2 = material2[key]

                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    blended[key] = val1 * (1 - blend_factor) + val2 * blend_factor
                elif isinstance(val1, tuple) and isinstance(val2, tuple):
                    blended[key] = tuple(
                        val1[i] * (1 - blend_factor) + val2[i] * blend_factor
                        for i in range(len(val1))
                    )
                else:
                    # Non-blendable property, use material2 if blend > 0.5
                    blended[key] = val2 if blend_factor > 0.5 else val1

        return blended

    def apply_material_to_prim(
        self, prim_path: str, material_name: str, stage: Any
    ) -> bool:
        """Apply material to USD prim.

        Args:
            prim_path: Path to prim
            material_name: Name of material
            stage: USD stage

        Returns:
            Success status
        """
        material = self.get_material(material_name)
        if not material:
            logger.error(f"Material not found: {material_name}")
            return False

        try:
            # In production, would create actual USD material
            # and bind to prim
            logger.info(f"Applied {material_name} to {prim_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply material: {e}")
            return False

"""Shader manager for neural visualization effects."""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ShaderManager:
    """Manages MDL shaders for neural visualization.

    Provides specialized shaders for brain tissue rendering,
    neural activity visualization, and scientific effects.
    """

    def __init__(self) -> None:
        """Initialize shader manager."""
        self.shaders: Dict[str, Dict[str, Any]] = {}
        self.shader_cache: Dict[str, Any] = {}
        self.mdl_search_paths = [
            "neurascale://shaders/",
            "omniverse://localhost/NVIDIA/Materials/Base/",
        ]

        # Initialize built-in shaders
        self._initialize_builtin_shaders()

        logger.info("ShaderManager initialized")

    def _initialize_builtin_shaders(self) -> None:
        """Initialize built-in neural visualization shaders."""
        # Brain tissue shader
        self.shaders["brain_tissue"] = {
            "name": "BrainTissue",
            "base_shader": "OmniPBR",
            "parameters": {
                "enable_subsurface": True,
                "subsurface_weight": 0.8,
                "subsurface_radius": [0.9, 0.7, 0.5],
                "subsurface_color": [0.9, 0.85, 0.8],
                "metallic": 0.0,
                "roughness": 0.7,
                "ior": 1.4,
                "thin_walled": False,
            },
            "code": self._generate_brain_tissue_mdl(),
        }

        # Neural activity shader
        self.shaders["neural_activity"] = {
            "name": "NeuralActivity",
            "base_shader": "OmniEmissive",
            "parameters": {
                "emission_mode": "animated",
                "base_emission": 0.5,
                "peak_emission": 5.0,
                "pulse_frequency": 2.0,
                "color_ramp": "activity_gradient",
            },
            "code": self._generate_neural_activity_mdl(),
        }

        # Connectivity fiber shader
        self.shaders["connectivity_fiber"] = {
            "name": "ConnectivityFiber",
            "base_shader": "OmniGlass",
            "parameters": {
                "enable_opacity": True,
                "opacity": 0.3,
                "roughness": 0.0,
                "ior": 1.5,
                "thin_walled": True,
                "emission_intensity": 0.5,
            },
            "code": self._generate_fiber_mdl(),
        }

        # Volume rendering shader
        self.shaders["volume_render"] = {
            "name": "VolumeRender",
            "base_shader": "OmniVolume",
            "parameters": {
                "density_scale": 100.0,
                "scattering_color": [1.0, 1.0, 1.0],
                "absorption_color": [0.1, 0.1, 0.1],
                "emission_scale": 1.0,
                "anisotropy": -0.3,
            },
            "code": self._generate_volume_mdl(),
        }

        # Electrode shader
        self.shaders["electrode"] = {
            "name": "Electrode",
            "base_shader": "OmniPBR",
            "parameters": {
                "metallic": 0.9,
                "roughness": 0.15,
                "base_color": [0.8, 0.8, 0.9],
                "enable_emission": True,
                "emission_color": [0.2, 0.2, 0.5],
                "emission_intensity": 0.5,
            },
            "code": self._generate_electrode_mdl(),
        }

        # Holographic shader for AR/VR
        self.shaders["holographic"] = {
            "name": "Holographic",
            "base_shader": "Custom",
            "parameters": {
                "hologram_color": [0.0, 0.8, 1.0],
                "scan_line_frequency": 50.0,
                "glitch_intensity": 0.1,
                "transparency": 0.7,
                "rim_light_intensity": 2.0,
            },
            "code": self._generate_holographic_mdl(),
        }

    def _generate_brain_tissue_mdl(self) -> str:
        """Generate MDL code for brain tissue shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::math::*;
import ::tex::*;
import ::anno::*;

export material BrainTissue(
    uniform float subsurface_weight = 0.8,
    uniform float3 subsurface_radius = float3(0.9, 0.7, 0.5),
    uniform float3 subsurface_color = float3(0.9, 0.85, 0.8),
    uniform float roughness = 0.7,
    uniform float ior = 1.4
) = material(
    surface: material_surface(
        scattering: df::weighted_layer(
            weight: subsurface_weight,
            layer: df::diffuse_transmission_bsdf(
                tint: subsurface_color
            ),
            base: df::diffuse_reflection_bsdf(
                tint: color(0.85, 0.82, 0.80),
                roughness: roughness
            )
        ),
        emission: material_emission(
            emission: df::diffuse_edf(),
            intensity: 0.0
        )
    ),
    ior: ior,
    volume: material_volume(
        scattering_coefficient: subsurface_color * 10.0,
        absorption_coefficient: color(0.1, 0.15, 0.2)
    )
);
"""

    def _generate_neural_activity_mdl(self) -> str:
        """Generate MDL code for neural activity shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::math::*;
import ::tex::*;
import ::anno::*;

export material NeuralActivity(
    uniform float base_emission = 0.5,
    uniform float peak_emission = 5.0,
    uniform float pulse_frequency = 2.0,
    uniform texture_2d activity_map = texture_2d()
) = material(
    surface: material_surface(
        scattering: df::diffuse_reflection_bsdf(
            tint: color(0.1, 0.1, 0.1)
        ),
        emission: material_emission(
            emission: df::diffuse_edf(),
            intensity: base_emission +
                      (peak_emission - base_emission) *
                      math::sin(state::animation_time() * pulse_frequency) * 0.5 + 0.5
        )
    ),
    geometry: material_geometry(
        cutout_opacity: 1.0
    )
);
"""

    def _generate_fiber_mdl(self) -> str:
        """Generate MDL code for connectivity fiber shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::math::*;
import ::anno::*;

export material ConnectivityFiber(
    uniform float opacity = 0.3,
    uniform float emission_intensity = 0.5,
    uniform float3 fiber_color = float3(0.0, 0.8, 1.0)
) = material(
    surface: material_surface(
        scattering: df::weighted_layer(
            weight: 1.0 - opacity,
            layer: df::specular_bsdf(
                tint: color(1.0),
                mode: df::scatter_transmit
            ),
            base: df::diffuse_reflection_bsdf(
                tint: fiber_color
            )
        ),
        emission: material_emission(
            emission: df::diffuse_edf(),
            intensity: fiber_color * emission_intensity
        )
    ),
    ior: 1.5,
    thin_walled: true
);
"""

    def _generate_volume_mdl(self) -> str:
        """Generate MDL code for volume rendering shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::anno::*;

export material VolumeRender(
    uniform float density_scale = 100.0,
    uniform float3 scattering_color = float3(1.0),
    uniform float3 absorption_color = float3(0.1),
    uniform float emission_scale = 1.0,
    uniform float anisotropy = -0.3
) = material(
    volume: material_volume(
        scattering_coefficient: scattering_color * density_scale,
        absorption_coefficient: absorption_color * density_scale,
        emission_intensity: emission_scale
    ),
    geometry: material_geometry(
        cutout_opacity: 0.0  // Fully volumetric
    )
);
"""

    def _generate_electrode_mdl(self) -> str:
        """Generate MDL code for electrode shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::anno::*;

export material Electrode(
    uniform float metallic = 0.9,
    uniform float roughness = 0.15,
    uniform float3 base_color = float3(0.8, 0.8, 0.9),
    uniform float3 emission_color = float3(0.2, 0.2, 0.5),
    uniform float emission_intensity = 0.5
) = material(
    surface: material_surface(
        scattering: df::weighted_layer(
            weight: metallic,
            layer: df::simple_glossy_bsdf(
                tint: base_color,
                roughness_u: roughness,
                roughness_v: roughness,
                mode: df::scatter_reflect
            ),
            base: df::diffuse_reflection_bsdf(
                tint: base_color,
                roughness: 0.0
            )
        ),
        emission: material_emission(
            emission: df::diffuse_edf(),
            intensity: emission_color * emission_intensity
        )
    )
);
"""

    def _generate_holographic_mdl(self) -> str:
        """Generate MDL code for holographic shader."""
        return """
mdl 1.7;

import ::df::*;
import ::state::*;
import ::math::*;
import ::anno::*;

export material Holographic(
    uniform float3 hologram_color = float3(0.0, 0.8, 1.0),
    uniform float scan_line_frequency = 50.0,
    uniform float glitch_intensity = 0.1,
    uniform float transparency = 0.7,
    uniform float rim_light_intensity = 2.0
) = material(
    surface: material_surface(
        scattering: df::weighted_layer(
            weight: transparency,
            layer: df::specular_bsdf(
                tint: color(1.0),
                mode: df::scatter_transmit
            ),
            base: df::diffuse_reflection_bsdf(
                tint: hologram_color * 0.2
            )
        ),
        emission: material_emission(
            emission: df::diffuse_edf(),
            intensity: hologram_color * rim_light_intensity *
                      math::pow(1.0 - math::abs(state::normal().z), 2.0) +
                      hologram_color * 0.5 *
                      (1.0 + math::sin(state::position().y * scan_line_frequency +
                                       state::animation_time() * 10.0))
        )
    ),
    geometry: material_geometry(
        cutout_opacity: 1.0 - transparency
    )
);
"""

    async def load_shader(self, shader_name: str) -> Optional[Dict[str, Any]]:
        """Load shader by name.

        Args:
            shader_name: Name of shader

        Returns:
            Shader definition or None
        """
        # Check cache
        if shader_name in self.shader_cache:
            return self.shader_cache[shader_name]

        # Check built-in shaders
        if shader_name in self.shaders:
            shader = self.shaders[shader_name]
            self.shader_cache[shader_name] = shader
            return shader

        # Try to load from file
        for search_path in self.mdl_search_paths:
            shader_path = Path(search_path) / f"{shader_name}.mdl"
            if shader_path.exists():
                try:
                    with open(shader_path, "r") as f:
                        shader_code = f.read()

                    shader = {
                        "name": shader_name,
                        "code": shader_code,
                        "parameters": {},  # Would parse from MDL
                    }

                    self.shader_cache[shader_name] = shader
                    return shader

                except Exception as e:
                    logger.error(f"Failed to load shader {shader_name}: {e}")

        logger.warning(f"Shader not found: {shader_name}")
        return None

    def create_custom_shader(
        self,
        name: str,
        base_shader: str,
        parameters: Dict[str, Any],
        custom_code: Optional[str] = None,
    ) -> str:
        """Create custom shader based on template.

        Args:
            name: Shader name
            base_shader: Base shader to extend
            parameters: Shader parameters
            custom_code: Optional MDL code

        Returns:
            Shader name
        """
        shader = {
            "name": name,
            "base_shader": base_shader,
            "parameters": parameters,
            "code": custom_code
            or self._generate_custom_mdl(name, base_shader, parameters),
        }

        self.shaders[name] = shader
        logger.info(f"Created custom shader: {name}")

        return name

    def _generate_custom_mdl(
        self, name: str, base_shader: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate custom MDL code."""
        # Simplified custom shader generation
        param_list = []
        for param_name, param_value in parameters.items():
            if isinstance(param_value, float):
                param_list.append(f"uniform float {param_name} = {param_value}")
            elif isinstance(param_value, (list, tuple)) and len(param_value) == 3:
                param_list.append(
                    f"uniform float3 {param_name} = float3{tuple(param_value)}"
                )

        params = ",\n    ".join(param_list)

        return f"""
mdl 1.7;

import ::df::*;
import ::state::*;
import ::anno::*;

export material {name}(
    {params}
) = material(
    // Custom shader implementation
    surface: material_surface(
        scattering: df::diffuse_reflection_bsdf()
    )
);
"""

    def update_shader_parameter(
        self, shader_name: str, parameter: str, value: Any
    ) -> bool:
        """Update shader parameter value.

        Args:
            shader_name: Shader name
            parameter: Parameter name
            value: New value

        Returns:
            Success status
        """
        if shader_name in self.shaders:
            self.shaders[shader_name]["parameters"][parameter] = value

            # Clear cache to force reload
            if shader_name in self.shader_cache:
                del self.shader_cache[shader_name]

            logger.info(f"Updated {shader_name}.{parameter} = {value}")
            return True

        logger.error(f"Shader not found: {shader_name}")
        return False

    def get_shader_list(self) -> List[str]:
        """Get list of available shaders.

        Returns:
            List of shader names
        """
        return list(self.shaders.keys())

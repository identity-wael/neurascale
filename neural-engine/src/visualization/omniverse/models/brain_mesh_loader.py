"""Brain mesh loader for patient-specific 3D models."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path
import asyncio

from ..types import BrainModel

logger = logging.getLogger(__name__)


class BrainMeshLoader:
    """Loads and processes brain meshes from MRI data.

    Converts MRI scans to 3D meshes suitable for
    real-time visualization in Omniverse.
    """

    def __init__(self):
        """Initialize brain mesh loader."""
        self.cache_dir = Path("cache/brain_models")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Standard brain templates
        self.templates = {
            "MNI152": "templates/MNI152_T1_1mm_brain.nii.gz",
            "ICBM452": "templates/ICBM452_T1_1mm_brain.nii.gz",
            "pediatric": "templates/pediatric_brain_4-8y.nii.gz",
        }

        # Mesh generation parameters
        self.mesh_resolution = "high"  # low, medium, high
        self.smoothing_iterations = 10
        self.decimation_factor = 0.5

        logger.info("BrainMeshLoader initialized")

    async def load_patient_model(
        self, patient_id: str, mri_path: Optional[str] = None
    ) -> BrainModel:
        """Load patient-specific brain model.

        Args:
            patient_id: Patient identifier
            mri_path: Optional path to patient MRI

        Returns:
            Brain model with mesh data
        """
        try:
            # Check cache first
            cached_model = await self._load_from_cache(patient_id)
            if cached_model:
                logger.info(f"Loaded cached model for patient {patient_id}")
                return cached_model

            # Generate from MRI or use template
            if mri_path and Path(mri_path).exists():
                brain_model = await self._generate_from_mri(patient_id, mri_path)
            else:
                brain_model = await self._generate_from_template(patient_id, "MNI152")

            # Cache the model
            await self._save_to_cache(brain_model)

            return brain_model

        except Exception as e:
            logger.error(f"Failed to load brain model: {e}")
            # Return default model on error
            return await self._get_default_model(patient_id)

    async def _generate_from_mri(self, patient_id: str, mri_path: str) -> BrainModel:
        """Generate brain mesh from MRI scan.

        Args:
            patient_id: Patient identifier
            mri_path: Path to MRI file

        Returns:
            Generated brain model
        """
        logger.info(f"Generating brain mesh from MRI: {mri_path}")

        # In production, this would:
        # 1. Load MRI data (NIfTI format)
        # 2. Perform brain extraction
        # 3. Generate surface mesh
        # 4. Map to standard atlas

        # Simulate MRI processing
        await asyncio.sleep(0.5)  # Simulate processing time

        # For now, generate a simplified mesh
        vertices, faces = self._generate_sphere_mesh(
            radius=0.08, subdivisions=4  # 80mm radius
        )

        # Add some deformation to make it brain-shaped
        vertices = self._deform_to_brain_shape(vertices)

        # Generate atlas regions
        regions = self._generate_atlas_regions(vertices)

        # Standard 10-20 electrode positions
        electrode_positions = self._get_standard_electrode_positions()

        return BrainModel(
            patient_id=patient_id,
            mesh_vertices=vertices,
            mesh_faces=faces,
            atlas_regions=regions,
            electrode_positions=electrode_positions,
            mri_source_path=mri_path,
        )

    async def _generate_from_template(
        self, patient_id: str, template_name: str
    ) -> BrainModel:
        """Generate brain model from template.

        Args:
            patient_id: Patient identifier
            template_name: Name of template to use

        Returns:
            Generated brain model
        """
        logger.info(f"Using template {template_name} for patient {patient_id}")

        # Generate template mesh
        vertices, faces = self._load_template_mesh(template_name)

        # Generate atlas regions
        regions = self._generate_atlas_regions(vertices)

        # Standard electrode positions
        electrode_positions = self._get_standard_electrode_positions()

        return BrainModel(
            patient_id=patient_id,
            mesh_vertices=vertices,
            mesh_faces=faces,
            atlas_regions=regions,
            electrode_positions=electrode_positions,
            mri_source_path=f"template:{template_name}",
        )

    def _generate_sphere_mesh(
        self, radius: float, subdivisions: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate sphere mesh as base geometry.

        Args:
            radius: Sphere radius
            subdivisions: Subdivision level

        Returns:
            Vertices and faces arrays
        """
        # Create icosahedron
        t = (1.0 + np.sqrt(5.0)) / 2.0
        vertices = (
            np.array(
                [
                    [-1, t, 0],
                    [1, t, 0],
                    [-1, -t, 0],
                    [1, -t, 0],
                    [0, -1, t],
                    [0, 1, t],
                    [0, -1, -t],
                    [0, 1, -t],
                    [t, 0, -1],
                    [t, 0, 1],
                    [-t, 0, -1],
                    [-t, 0, 1],
                ]
            )
            * radius
            / np.sqrt(1 + t * t)
        )

        faces = np.array(
            [
                [0, 11, 5],
                [0, 5, 1],
                [0, 1, 7],
                [0, 7, 10],
                [0, 10, 11],
                [1, 5, 9],
                [5, 11, 4],
                [11, 10, 2],
                [10, 7, 6],
                [7, 1, 8],
                [3, 9, 4],
                [3, 4, 2],
                [3, 2, 6],
                [3, 6, 8],
                [3, 8, 9],
                [4, 9, 5],
                [2, 4, 11],
                [6, 2, 10],
                [8, 6, 7],
                [9, 8, 1],
            ]
        )

        # Subdivide
        for _ in range(subdivisions):
            vertices, faces = self._subdivide_mesh(vertices, faces, radius)

        return vertices, faces

    def _subdivide_mesh(
        self, vertices: np.ndarray, faces: np.ndarray, radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Subdivide mesh for higher resolution.

        Args:
            vertices: Current vertices
            faces: Current faces
            radius: Target radius

        Returns:
            Subdivided vertices and faces
        """
        edge_map = {}
        new_vertices = list(vertices)
        new_faces = []

        def get_edge_point(v1_idx, v2_idx):
            edge = tuple(sorted([v1_idx, v2_idx]))
            if edge not in edge_map:
                v1, v2 = vertices[v1_idx], vertices[v2_idx]
                mid = (v1 + v2) / 2
                mid = mid / np.linalg.norm(mid) * radius
                edge_map[edge] = len(new_vertices)
                new_vertices.append(mid)
            return edge_map[edge]

        for face in faces:
            v1, v2, v3 = face

            # Get midpoints
            v12 = get_edge_point(v1, v2)
            v23 = get_edge_point(v2, v3)
            v31 = get_edge_point(v3, v1)

            # Create 4 new faces
            new_faces.extend(
                [[v1, v12, v31], [v2, v23, v12], [v3, v31, v23], [v12, v23, v31]]
            )

        return np.array(new_vertices), np.array(new_faces)

    def _deform_to_brain_shape(self, vertices: np.ndarray) -> np.ndarray:
        """Deform sphere to brain-like shape.

        Args:
            vertices: Sphere vertices

        Returns:
            Deformed vertices
        """
        # Apply ellipsoid deformation
        vertices[:, 0] *= 0.9  # Narrower width
        vertices[:, 1] *= 1.1  # Longer front-to-back
        vertices[:, 2] *= 0.85  # Flatter top-to-bottom

        # Add some asymmetry
        vertices[vertices[:, 0] > 0, 0] *= 1.02  # Right hemisphere slightly larger

        # Flatten bottom (brain stem area)
        bottom_mask = vertices[:, 2] < -0.05
        vertices[bottom_mask, 2] *= 0.7

        return vertices

    def _generate_atlas_regions(self, vertices: np.ndarray) -> Dict[str, List[int]]:
        """Generate brain atlas regions.

        Args:
            vertices: Brain mesh vertices

        Returns:
            Region name to vertex indices mapping
        """
        regions = {}

        # Simplified regions based on vertex positions
        # In production, would use actual atlas mapping

        # Frontal lobe
        frontal_mask = vertices[:, 1] > 0.03
        regions["frontal_lobe"] = np.where(frontal_mask)[0].tolist()

        # Parietal lobe
        parietal_mask = (
            (vertices[:, 1] > -0.03) & (vertices[:, 1] < 0.03) & (vertices[:, 2] > 0)
        )
        regions["parietal_lobe"] = np.where(parietal_mask)[0].tolist()

        # Temporal lobe
        temporal_mask = (
            (vertices[:, 2] < 0)
            & (vertices[:, 2] > -0.05)
            & (np.abs(vertices[:, 0]) > 0.04)
        )
        regions["temporal_lobe"] = np.where(temporal_mask)[0].tolist()

        # Occipital lobe
        occipital_mask = vertices[:, 1] < -0.05
        regions["occipital_lobe"] = np.where(occipital_mask)[0].tolist()

        # Motor cortex
        motor_mask = (
            (vertices[:, 1] > -0.01) & (vertices[:, 1] < 0.01) & (vertices[:, 2] > 0.03)
        )
        regions["motor_cortex"] = np.where(motor_mask)[0].tolist()

        # Sensory cortex
        sensory_mask = (
            (vertices[:, 1] > -0.02)
            & (vertices[:, 1] < -0.01)
            & (vertices[:, 2] > 0.03)
        )
        regions["sensory_cortex"] = np.where(sensory_mask)[0].tolist()

        return regions

    def _get_standard_electrode_positions(
        self,
    ) -> Dict[str, Tuple[float, float, float]]:
        """Get standard 10-20 electrode positions.

        Returns:
            Channel name to 3D position mapping
        """
        # Standard 10-20 system positions
        # These are approximate positions on a standard brain
        positions = {
            # Frontal
            "Fp1": (-0.025, 0.08, 0.02),
            "Fp2": (0.025, 0.08, 0.02),
            "F3": (-0.04, 0.05, 0.05),
            "F4": (0.04, 0.05, 0.05),
            "F7": (-0.07, 0.03, 0.0),
            "F8": (0.07, 0.03, 0.0),
            "Fz": (0.0, 0.05, 0.06),
            # Central
            "C3": (-0.05, 0.0, 0.07),
            "C4": (0.05, 0.0, 0.07),
            "Cz": (0.0, 0.0, 0.08),
            # Temporal
            "T3": (-0.08, 0.0, 0.0),
            "T4": (0.08, 0.0, 0.0),
            "T5": (-0.07, -0.05, 0.0),
            "T6": (0.07, -0.05, 0.0),
            # Parietal
            "P3": (-0.04, -0.05, 0.05),
            "P4": (0.04, -0.05, 0.05),
            "Pz": (0.0, -0.05, 0.06),
            # Occipital
            "O1": (-0.025, -0.08, 0.02),
            "O2": (0.025, -0.08, 0.02),
            # Reference
            "A1": (-0.08, -0.02, -0.03),
            "A2": (0.08, -0.02, -0.03),
        }

        return positions

    def _load_template_mesh(self, template_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load pre-computed template mesh.

        Args:
            template_name: Name of template

        Returns:
            Vertices and faces
        """
        # For now, generate a high-res sphere and deform it
        vertices, faces = self._generate_sphere_mesh(0.08, 5)
        vertices = self._deform_to_brain_shape(vertices)

        # Apply smoothing
        vertices = self._smooth_mesh(
            vertices, faces, iterations=self.smoothing_iterations
        )

        return vertices, faces

    def _smooth_mesh(
        self, vertices: np.ndarray, faces: np.ndarray, iterations: int
    ) -> np.ndarray:
        """Apply Laplacian smoothing to mesh.

        Args:
            vertices: Mesh vertices
            faces: Mesh faces
            iterations: Number of smoothing iterations

        Returns:
            Smoothed vertices
        """
        # Build adjacency
        adjacency = {i: set() for i in range(len(vertices))}
        for face in faces:
            for i in range(3):
                adjacency[face[i]].add(face[(i + 1) % 3])
                adjacency[face[(i + 1) % 3]].add(face[i])

        # Apply smoothing
        smoothed = vertices.copy()
        for _ in range(iterations):
            new_positions = np.zeros_like(smoothed)
            for i, neighbors in adjacency.items():
                if neighbors:
                    neighbor_positions = smoothed[list(neighbors)]
                    new_positions[i] = neighbor_positions.mean(axis=0)

            # Blend with original (0.5 factor preserves volume better)
            smoothed = 0.5 * smoothed + 0.5 * new_positions

        return smoothed

    async def _load_from_cache(self, patient_id: str) -> Optional[BrainModel]:
        """Load model from cache if available.

        Args:
            patient_id: Patient identifier

        Returns:
            Cached model or None
        """
        cache_path = self.cache_dir / f"{patient_id}_brain_model.npz"

        if not cache_path.exists():
            return None

        try:
            data = np.load(cache_path)

            # Reconstruct regions dict
            regions = {}
            for key in data.keys():
                if key.startswith("region_"):
                    region_name = key.replace("region_", "")
                    regions[region_name] = data[key].tolist()

            # Reconstruct electrode positions
            electrode_positions = {}
            if "electrode_names" in data and "electrode_positions" in data:
                for name, pos in zip(
                    data["electrode_names"], data["electrode_positions"]
                ):
                    electrode_positions[name] = tuple(pos)

            return BrainModel(
                patient_id=patient_id,
                mesh_vertices=data["vertices"],
                mesh_faces=data["faces"],
                atlas_regions=regions,
                electrode_positions=electrode_positions,
                mri_source_path=str(data.get("mri_source", "")),
            )

        except Exception as e:
            logger.error(f"Failed to load from cache: {e}")
            return None

    async def _save_to_cache(self, model: BrainModel):
        """Save model to cache.

        Args:
            model: Brain model to cache
        """
        cache_path = self.cache_dir / f"{model.patient_id}_brain_model.npz"

        try:
            # Prepare data for saving
            save_data = {
                "vertices": model.mesh_vertices,
                "faces": model.mesh_faces,
                "mri_source": model.mri_source_path or "",
            }

            # Add regions
            for region_name, indices in model.atlas_regions.items():
                save_data[f"region_{region_name}"] = np.array(indices)

            # Add electrode positions
            if model.electrode_positions:
                names = list(model.electrode_positions.keys())
                positions = [model.electrode_positions[name] for name in names]
                save_data["electrode_names"] = names
                save_data["electrode_positions"] = np.array(positions)

            np.savez_compressed(cache_path, **save_data)
            logger.info(f"Cached brain model for patient {model.patient_id}")

        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")

    async def _get_default_model(self, patient_id: str) -> BrainModel:
        """Get default brain model as fallback.

        Args:
            patient_id: Patient identifier

        Returns:
            Default brain model
        """
        logger.warning(f"Using default brain model for patient {patient_id}")
        return await self._generate_from_template(patient_id, "MNI152")

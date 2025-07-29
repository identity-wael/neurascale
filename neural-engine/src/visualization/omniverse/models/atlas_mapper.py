"""Brain atlas mapping for region identification and labeling."""

import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BrainRegion:
    """Brain region definition."""

    name: str
    label: str
    color: Tuple[float, float, float]
    parent: Optional[str] = None
    volume: float = 0.0
    center: Optional[Tuple[float, float, float]] = None
    vertices: Optional[List[int]] = None


class AtlasMapper:
    """Maps brain regions using standard atlases.

    Supports various brain atlases including AAL, Brodmann,
    FreeSurfer, and custom parcellations.
    """

    def __init__(self) -> None:
        """Initialize atlas mapper."""
        self.atlases: Dict[str, Dict[str, BrainRegion]] = {}
        self.current_atlas = "AAL"
        self.region_hierarchy: Dict[str, List[str]] = {}

        # Initialize standard atlases
        self._initialize_standard_atlases()

        logger.info("AtlasMapper initialized")

    def _initialize_standard_atlases(self) -> None:
        """Initialize standard brain atlases."""
        # AAL (Automated Anatomical Labeling) Atlas
        self.atlases["AAL"] = self._create_aal_atlas()

        # Brodmann Areas
        self.atlases["Brodmann"] = self._create_brodmann_atlas()

        # Lobes
        self.atlases["Lobes"] = self._create_lobe_atlas()

        # Functional Networks
        self.atlases["Networks"] = self._create_network_atlas()

    def _create_aal_atlas(self) -> Dict[str, BrainRegion]:
        """Create AAL atlas regions."""
        regions = {}

        # Frontal regions
        frontal_regions = [
            ("Precentral_L", "Left Precentral Gyrus", (0.8, 0.2, 0.2)),
            ("Precentral_R", "Right Precentral Gyrus", (0.8, 0.2, 0.2)),
            ("Frontal_Sup_L", "Left Superior Frontal Gyrus", (0.7, 0.3, 0.3)),
            ("Frontal_Sup_R", "Right Superior Frontal Gyrus", (0.7, 0.3, 0.3)),
            ("Frontal_Mid_L", "Left Middle Frontal Gyrus", (0.6, 0.4, 0.4)),
            ("Frontal_Mid_R", "Right Middle Frontal Gyrus", (0.6, 0.4, 0.4)),
            (
                "Frontal_Inf_Oper_L",
                "Left Inferior Frontal Gyrus (Opercular)",
                (0.5, 0.5, 0.5),
            ),
            (
                "Frontal_Inf_Oper_R",
                "Right Inferior Frontal Gyrus (Opercular)",
                (0.5, 0.5, 0.5),
            ),
        ]

        for name, label, color in frontal_regions:
            regions[name] = BrainRegion(
                name=name, label=label, color=color, parent="Frontal_Lobe"
            )

        # Temporal regions
        temporal_regions = [
            ("Temporal_Sup_L", "Left Superior Temporal Gyrus", (0.2, 0.8, 0.2)),
            ("Temporal_Sup_R", "Right Superior Temporal Gyrus", (0.2, 0.8, 0.2)),
            ("Temporal_Mid_L", "Left Middle Temporal Gyrus", (0.3, 0.7, 0.3)),
            ("Temporal_Mid_R", "Right Middle Temporal Gyrus", (0.3, 0.7, 0.3)),
            ("Temporal_Inf_L", "Left Inferior Temporal Gyrus", (0.4, 0.6, 0.4)),
            ("Temporal_Inf_R", "Right Inferior Temporal Gyrus", (0.4, 0.6, 0.4)),
        ]

        for name, label, color in temporal_regions:
            regions[name] = BrainRegion(
                name=name, label=label, color=color, parent="Temporal_Lobe"
            )

        # Parietal regions
        parietal_regions = [
            ("Postcentral_L", "Left Postcentral Gyrus", (0.2, 0.2, 0.8)),
            ("Postcentral_R", "Right Postcentral Gyrus", (0.2, 0.2, 0.8)),
            ("Parietal_Sup_L", "Left Superior Parietal Lobule", (0.3, 0.3, 0.7)),
            ("Parietal_Sup_R", "Right Superior Parietal Lobule", (0.3, 0.3, 0.7)),
            ("Parietal_Inf_L", "Left Inferior Parietal Lobule", (0.4, 0.4, 0.6)),
            ("Parietal_Inf_R", "Right Inferior Parietal Lobule", (0.4, 0.4, 0.6)),
        ]

        for name, label, color in parietal_regions:
            regions[name] = BrainRegion(
                name=name, label=label, color=color, parent="Parietal_Lobe"
            )

        # Occipital regions
        occipital_regions = [
            ("Occipital_Sup_L", "Left Superior Occipital Gyrus", (0.8, 0.8, 0.2)),
            ("Occipital_Sup_R", "Right Superior Occipital Gyrus", (0.8, 0.8, 0.2)),
            ("Occipital_Mid_L", "Left Middle Occipital Gyrus", (0.7, 0.7, 0.3)),
            ("Occipital_Mid_R", "Right Middle Occipital Gyrus", (0.7, 0.7, 0.3)),
            ("Occipital_Inf_L", "Left Inferior Occipital Gyrus", (0.6, 0.6, 0.4)),
            ("Occipital_Inf_R", "Right Inferior Occipital Gyrus", (0.6, 0.6, 0.4)),
        ]

        for name, label, color in occipital_regions:
            regions[name] = BrainRegion(
                name=name, label=label, color=color, parent="Occipital_Lobe"
            )

        # Subcortical regions
        subcortical_regions = [
            ("Hippocampus_L", "Left Hippocampus", (0.8, 0.2, 0.8)),
            ("Hippocampus_R", "Right Hippocampus", (0.8, 0.2, 0.8)),
            ("Amygdala_L", "Left Amygdala", (0.7, 0.3, 0.7)),
            ("Amygdala_R", "Right Amygdala", (0.7, 0.3, 0.7)),
            ("Thalamus_L", "Left Thalamus", (0.6, 0.4, 0.6)),
            ("Thalamus_R", "Right Thalamus", (0.6, 0.4, 0.6)),
        ]

        for name, label, color in subcortical_regions:
            regions[name] = BrainRegion(
                name=name, label=label, color=color, parent="Subcortical"
            )

        return regions

    def _create_brodmann_atlas(self) -> Dict[str, BrainRegion]:
        """Create Brodmann area atlas."""
        regions = {}

        # Primary areas
        primary_areas = [
            ("BA1", "Primary Somatosensory Cortex (BA1)", (1.0, 0.0, 0.0)),
            ("BA2", "Primary Somatosensory Cortex (BA2)", (0.9, 0.1, 0.0)),
            ("BA3", "Primary Somatosensory Cortex (BA3)", (0.8, 0.2, 0.0)),
            ("BA4", "Primary Motor Cortex", (0.0, 1.0, 0.0)),
            ("BA17", "Primary Visual Cortex", (0.0, 0.0, 1.0)),
            ("BA41", "Primary Auditory Cortex", (1.0, 1.0, 0.0)),
        ]

        for name, label, color in primary_areas:
            regions[name] = BrainRegion(name=name, label=label, color=color)

        # Association areas
        association_areas = [
            ("BA5", "Somatosensory Association Cortex", (0.7, 0.3, 0.3)),
            ("BA6", "Premotor and Supplementary Motor Cortex", (0.3, 0.7, 0.3)),
            ("BA7", "Visuo-Motor Coordination", (0.3, 0.3, 0.7)),
            ("BA9", "Dorsolateral Prefrontal Cortex", (0.5, 0.5, 0.0)),
            ("BA10", "Frontopolar Prefrontal Cortex", (0.5, 0.0, 0.5)),
            ("BA11", "Orbitofrontal Area", (0.0, 0.5, 0.5)),
        ]

        for name, label, color in association_areas:
            regions[name] = BrainRegion(name=name, label=label, color=color)

        return regions

    def _create_lobe_atlas(self) -> Dict[str, BrainRegion]:
        """Create lobe-based atlas."""
        return {
            "Frontal_Lobe": BrainRegion(
                name="Frontal_Lobe", label="Frontal Lobe", color=(0.8, 0.2, 0.2)
            ),
            "Temporal_Lobe": BrainRegion(
                name="Temporal_Lobe", label="Temporal Lobe", color=(0.2, 0.8, 0.2)
            ),
            "Parietal_Lobe": BrainRegion(
                name="Parietal_Lobe", label="Parietal Lobe", color=(0.2, 0.2, 0.8)
            ),
            "Occipital_Lobe": BrainRegion(
                name="Occipital_Lobe", label="Occipital Lobe", color=(0.8, 0.8, 0.2)
            ),
            "Cerebellum": BrainRegion(
                name="Cerebellum", label="Cerebellum", color=(0.5, 0.5, 0.5)
            ),
            "Brain_Stem": BrainRegion(
                name="Brain_Stem", label="Brain Stem", color=(0.4, 0.4, 0.4)
            ),
        }

    def _create_network_atlas(self) -> Dict[str, BrainRegion]:
        """Create functional network atlas."""
        return {
            "DMN": BrainRegion(
                name="DMN", label="Default Mode Network", color=(0.8, 0.2, 0.2)
            ),
            "CEN": BrainRegion(
                name="CEN", label="Central Executive Network", color=(0.2, 0.8, 0.2)
            ),
            "Salience": BrainRegion(
                name="Salience", label="Salience Network", color=(0.2, 0.2, 0.8)
            ),
            "Sensorimotor": BrainRegion(
                name="Sensorimotor", label="Sensorimotor Network", color=(0.8, 0.8, 0.2)
            ),
            "Visual": BrainRegion(
                name="Visual", label="Visual Network", color=(0.8, 0.2, 0.8)
            ),
            "Auditory": BrainRegion(
                name="Auditory", label="Auditory Network", color=(0.2, 0.8, 0.8)
            ),
        }

    def map_vertices_to_regions(
        self, vertices: np.ndarray, atlas_name: str = "AAL"
    ) -> Dict[int, str]:
        """Map mesh vertices to brain regions.

        Args:
            vertices: Mesh vertices (n_vertices, 3)
            atlas_name: Atlas to use

        Returns:
            Mapping of vertex index to region name
        """
        if atlas_name not in self.atlases:
            logger.error(f"Unknown atlas: {atlas_name}")
            return {}

        vertex_regions = {}

        # Simplified mapping based on spatial location
        # In production, would use actual atlas parcellation
        for i, vertex in enumerate(vertices):
            region = self._determine_region_for_vertex(vertex)

            # Check if region exists in atlas
            if region in self.atlases[atlas_name]:
                vertex_regions[i] = region
            else:
                vertex_regions[i] = "Unknown"

        return vertex_regions

    def _determine_region_for_vertex(self, vertex: np.ndarray) -> str:
        """Determine brain region for a single vertex."""
        x, y, z = vertex
        hemisphere = "L" if x < 0 else "R"

        # Determine lobe based on position
        if y > 0.3:  # Frontal
            return self._get_frontal_region(z, hemisphere)
        elif y < -0.3:  # Occipital
            return self._get_occipital_region(z, hemisphere)
        elif abs(x) > 0.5:  # Temporal
            return self._get_temporal_region(z, hemisphere)
        else:  # Parietal
            return self._get_parietal_region(z, hemisphere)

    def _get_frontal_region(self, z: float, hemisphere: str) -> str:
        """Get frontal lobe region based on z coordinate."""
        if z > 0.7:
            return f"Frontal_Sup_{hemisphere}"
        elif z > 0.4:
            return f"Frontal_Mid_{hemisphere}"
        else:
            return f"Frontal_Inf_Oper_{hemisphere}"

    def _get_occipital_region(self, z: float, hemisphere: str) -> str:
        """Get occipital lobe region based on z coordinate."""
        if z > 0.5:
            return f"Occipital_Sup_{hemisphere}"
        else:
            return f"Occipital_Inf_{hemisphere}"

    def _get_temporal_region(self, z: float, hemisphere: str) -> str:
        """Get temporal lobe region based on z coordinate."""
        if z > 0.5:
            return f"Temporal_Sup_{hemisphere}"
        else:
            return f"Temporal_Mid_{hemisphere}"

    def _get_parietal_region(self, z: float, hemisphere: str) -> str:
        """Get parietal lobe region based on z coordinate."""
        if z > 0.7:
            return f"Parietal_Sup_{hemisphere}"
        else:
            return f"Postcentral_{hemisphere}"

    def get_region_info(
        self, region_name: str, atlas_name: Optional[str] = None
    ) -> Optional[BrainRegion]:
        """Get information about a brain region.

        Args:
            region_name: Region name
            atlas_name: Specific atlas to search in

        Returns:
            BrainRegion or None
        """
        if atlas_name:
            return self.atlases.get(atlas_name, {}).get(region_name)

        # Search all atlases
        for atlas in self.atlases.values():
            if region_name in atlas:
                return atlas[region_name]

        return None

    def get_region_hierarchy(self, region_name: str) -> List[str]:
        """Get hierarchical path for a region.

        Args:
            region_name: Region name

        Returns:
            List of parent regions from root to region
        """
        hierarchy = [region_name]

        # Find region
        region = self.get_region_info(region_name)
        if not region:
            return hierarchy

        # Traverse up hierarchy
        current = region
        while current.parent:
            hierarchy.insert(0, current.parent)
            parent_region = self.get_region_info(current.parent)
            if not parent_region:
                break
            current = parent_region

        return hierarchy

    def get_regions_in_sphere(
        self,
        center: Tuple[float, float, float],
        radius: float,
        vertex_mapping: Dict[int, str],
        vertices: np.ndarray,
    ) -> List[str]:
        """Get regions within sphere around point.

        Args:
            center: Sphere center
            radius: Sphere radius
            vertex_mapping: Vertex to region mapping
            vertices: Mesh vertices

        Returns:
            List of region names
        """
        regions = set()
        center_array = np.array(center)

        for i, vertex in enumerate(vertices):
            distance = np.linalg.norm(vertex - center_array)
            if distance <= radius:
                region = vertex_mapping.get(i)
                if region and region != "Unknown":
                    regions.add(region)

        return list(regions)

    def calculate_region_volumes(
        self, vertex_mapping: Dict[int, str], vertices: np.ndarray, faces: np.ndarray
    ) -> Dict[str, float]:
        """Calculate volume for each region.

        Args:
            vertex_mapping: Vertex to region mapping
            vertices: Mesh vertices
            faces: Mesh faces

        Returns:
            Region volumes
        """
        region_volumes = {}

        # Calculate face areas and assign to regions
        for face in faces:
            # Get vertices of face
            v1, v2, v3 = vertices[face]

            # Calculate face area
            edge1 = v2 - v1
            edge2 = v3 - v1
            area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))

            # Assign to region (use majority vote)
            regions = [
                vertex_mapping.get(face[0], "Unknown"),
                vertex_mapping.get(face[1], "Unknown"),
                vertex_mapping.get(face[2], "Unknown"),
            ]

            # Count occurrences
            region_counts = {}
            for region in regions:
                if region != "Unknown":
                    region_counts[region] = region_counts.get(region, 0) + 1

            if region_counts:
                # Assign to most common region
                dominant_region = max(region_counts, key=region_counts.get)
                if dominant_region not in region_volumes:
                    region_volumes[dominant_region] = 0.0
                region_volumes[dominant_region] += area

        return region_volumes

    def create_region_labels(
        self, vertex_mapping: Dict[int, str], vertices: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Create 3D labels for brain regions.

        Args:
            vertex_mapping: Vertex to region mapping
            vertices: Mesh vertices

        Returns:
            List of label definitions
        """
        labels = []

        # Calculate region centers
        region_vertices = {}
        for i, region in vertex_mapping.items():
            if region != "Unknown":
                if region not in region_vertices:
                    region_vertices[region] = []
                region_vertices[region].append(vertices[i])

        # Create labels
        for region_name, region_verts in region_vertices.items():
            region_info = self.get_region_info(region_name)
            if not region_info:
                continue

            # Calculate center
            center = np.mean(region_verts, axis=0)

            labels.append(
                {
                    "text": region_info.label,
                    "position": tuple(center),
                    "color": region_info.color,
                    "size": 0.02,
                    "billboard": True,  # Always face camera
                }
            )

        return labels

    def export_parcellation(
        self, vertex_mapping: Dict[int, str], output_format: str = "nifti"
    ) -> bytes:
        """Export parcellation to standard format.

        Args:
            vertex_mapping: Vertex to region mapping
            output_format: Export format (nifti, gifti, etc.)

        Returns:
            Exported data
        """
        # In production, would export to actual neuroimaging format
        # For now, return dummy data
        logger.info(f"Exporting parcellation to {output_format} format")
        return b"parcellation_data"

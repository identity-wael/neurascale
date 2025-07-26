"""Spatial Features - Spatial complexity and topographical features.

This module implements spatial feature extraction including channel correlations,
spatial complexity measures, and topographical patterns.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy import stats
from sklearn.decomposition import PCA
import warnings

logger = logging.getLogger(__name__)


class SpatialFeatures:
    """Spatial feature extraction for multi-channel neural signals."""

    def __init__(self, config: Any):
        """Initialize spatial feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Spatial analysis parameters
        self.min_channels = 4  # Minimum channels for spatial analysis
        self.n_components = 3  # Number of PCA components

        # Channel locations (placeholder)
        self.channel_locations = None

        logger.info("SpatialFeatures initialized")

    async def extract_spatial_complexity(self, data: np.ndarray) -> np.ndarray:
        """Extract spatial complexity measure.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Spatial complexity value
        """
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            logger.warning(f"Not enough channels ({n_channels}) for spatial complexity")
            return np.array([0.0])

        try:
            # Compute spatial covariance matrix
            cov_matrix = np.cov(data)

            # Eigenvalue decomposition
            eigenvalues = np.linalg.eigvals(cov_matrix)
            eigenvalues = np.abs(eigenvalues)
            eigenvalues = np.sort(eigenvalues)[::-1]

            # Spatial complexity based on eigenvalue distribution
            # Higher complexity when eigenvalues are more evenly distributed
            if np.sum(eigenvalues) > 0:
                normalized_eigenvalues = eigenvalues / np.sum(eigenvalues)

                # Shannon entropy of eigenvalue distribution
                nonzero_eigs = normalized_eigenvalues[normalized_eigenvalues > 1e-10]
                spatial_complexity = -np.sum(nonzero_eigs * np.log(nonzero_eigs))

                # Normalize by maximum possible entropy
                max_entropy = np.log(n_channels)
                if max_entropy > 0:
                    spatial_complexity = spatial_complexity / max_entropy
            else:
                spatial_complexity = 0.0

            return np.array([spatial_complexity])

        except Exception as e:
            logger.error(f"Error computing spatial complexity: {str(e)}")
            return np.array([0.0])

    async def extract_correlation_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract features based on channel correlations.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of correlation features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < 2:
            logger.warning("Need at least 2 channels for correlation features")
            return features

        try:
            # Compute correlation matrix
            corr_matrix = np.corrcoef(data)

            # Extract upper triangle (excluding diagonal)
            upper_triangle = corr_matrix[np.triu_indices(n_channels, k=1)]

            # Basic statistics of correlations
            features["correlation_mean"] = np.array([np.mean(upper_triangle)])
            features["correlation_std"] = np.array([np.std(upper_triangle)])
            features["correlation_max"] = np.array([np.max(np.abs(upper_triangle))])
            features["correlation_min"] = np.array([np.min(upper_triangle)])

            # Correlation structure features
            # Average correlation per channel
            avg_corr_per_channel = np.zeros(n_channels)
            for i in range(n_channels):
                # Mean absolute correlation with other channels
                other_corrs = np.concatenate(
                    [corr_matrix[i, :i], corr_matrix[i, i + 1 :]]
                )
                avg_corr_per_channel[i] = np.mean(np.abs(other_corrs))

            features["channel_avg_correlation"] = avg_corr_per_channel

            # Global connectivity strength
            features["global_connectivity"] = np.array(
                [np.mean(np.abs(upper_triangle))]
            )

            # Clustering coefficient (local connectivity)
            clustering_coeff = await self._compute_clustering_coefficient(corr_matrix)
            features["clustering_coefficient"] = np.array([clustering_coeff])

            # Modularity features
            modularity_features = await self._compute_modularity_features(corr_matrix)
            features.update(modularity_features)

            return features

        except Exception as e:
            logger.error(f"Error extracting correlation features: {str(e)}")
            return features

    async def extract_spatial_patterns(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract spatial patterns using dimensionality reduction.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of spatial pattern features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            logger.warning(f"Not enough channels ({n_channels}) for spatial patterns")
            return features

        try:
            # PCA on spatial data
            pca = PCA(n_components=min(self.n_components, n_channels))

            # Fit PCA on channel data
            pca.fit(data.T)  # Transpose to have samples x channels

            # Explained variance ratios
            features["pca_explained_variance"] = pca.explained_variance_ratio_

            # First principal component loadings
            features["pca_first_component"] = np.abs(pca.components_[0, :])

            # Spatial focus (concentration of first component)
            first_comp_normalized = features["pca_first_component"] / np.sum(
                features["pca_first_component"]
            )
            spatial_focus = -np.sum(
                first_comp_normalized * np.log(first_comp_normalized + 1e-10)
            )
            features["spatial_focus"] = np.array([spatial_focus])

            # Transform data to principal components
            pc_data = pca.transform(data.T).T

            # Statistics of principal components
            for i in range(pc_data.shape[0]):
                features[f"pc{i+1}_variance"] = np.array([np.var(pc_data[i, :])])
                features[f"pc{i+1}_kurtosis"] = np.array(
                    [stats.kurtosis(pc_data[i, :])]
                )

            return features

        except Exception as e:
            logger.error(f"Error extracting spatial patterns: {str(e)}")
            return features

    async def extract_topographical_features(
        self, data: np.ndarray, channel_locations: Optional[np.ndarray] = None
    ) -> Dict[str, np.ndarray]:
        """Extract topographical features based on channel locations.

        Args:
            data: Signal data (channels x samples)
            channel_locations: 2D or 3D coordinates of channels

        Returns:
            Dictionary of topographical features
        """
        features = {}

        if channel_locations is None:
            # Generate default grid layout
            channel_locations = self._generate_default_locations(data.shape[0])

        try:
            # Spatial gradient features
            gradient_features = await self._compute_spatial_gradients(
                data, channel_locations
            )
            features.update(gradient_features)

            # Regional activity features
            regional_features = await self._compute_regional_features(
                data, channel_locations
            )
            features.update(regional_features)

            # Spatial autocorrelation
            spatial_autocorr = await self._compute_spatial_autocorrelation(
                data, channel_locations
            )
            features["spatial_autocorrelation"] = np.array([spatial_autocorr])

            return features

        except Exception as e:
            logger.error(f"Error extracting topographical features: {str(e)}")
            return features

    async def _compute_clustering_coefficient(
        self, corr_matrix: np.ndarray, threshold: float = 0.3
    ) -> float:
        """Compute clustering coefficient from correlation matrix.

        Args:
            corr_matrix: Channel correlation matrix
            threshold: Threshold for creating adjacency matrix

        Returns:
            Average clustering coefficient
        """
        n_channels = corr_matrix.shape[0]

        # Create binary adjacency matrix
        adj_matrix = (np.abs(corr_matrix) > threshold).astype(int)
        np.fill_diagonal(adj_matrix, 0)

        clustering_coeffs = []

        for i in range(n_channels):
            # Find neighbors
            neighbors = np.where(adj_matrix[i, :])[0]
            k = len(neighbors)

            if k >= 2:
                # Count connections between neighbors
                neighbor_connections = 0
                for j in range(len(neighbors)):
                    for l in range(j + 1, len(neighbors)):
                        if adj_matrix[neighbors[j], neighbors[l]]:
                            neighbor_connections += 1

                # Clustering coefficient
                max_connections = k * (k - 1) / 2
                if max_connections > 0:
                    clustering_coeffs.append(neighbor_connections / max_connections)
            else:
                clustering_coeffs.append(0)

        return np.mean(clustering_coeffs) if clustering_coeffs else 0.0

    async def _compute_modularity_features(
        self, corr_matrix: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute modularity-based features.

        Args:
            corr_matrix: Channel correlation matrix

        Returns:
            Dictionary of modularity features
        """
        features = {}

        # Simple community detection using correlation threshold
        threshold = np.percentile(
            np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]), 75
        )

        # Create communities based on strong correlations
        communities = []
        unassigned = set(range(corr_matrix.shape[0]))

        while unassigned:
            # Start new community
            node = unassigned.pop()
            community = {node}

            # Add strongly connected nodes
            to_check = [node]
            while to_check:
                current = to_check.pop()
                for neighbor in unassigned:
                    if np.abs(corr_matrix[current, neighbor]) > threshold:
                        community.add(neighbor)
                        to_check.append(neighbor)
                        unassigned.discard(neighbor)

            communities.append(community)

        # Modularity features
        features["n_communities"] = np.array([len(communities)])
        features["largest_community_size"] = np.array(
            [max(len(c) for c in communities)]
        )

        # Community size variance
        community_sizes = [len(c) for c in communities]
        features["community_size_variance"] = np.array([np.var(community_sizes)])

        return features

    async def _compute_spatial_gradients(
        self, data: np.ndarray, locations: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute spatial gradient features.

        Args:
            data: Signal data (channels x samples)
            locations: Channel locations

        Returns:
            Dictionary of gradient features
        """
        features = {}

        # Compute pairwise distances
        distances = squareform(pdist(locations))

        # Average signal power per channel
        channel_power = np.mean(data**2, axis=1)

        # Spatial gradients
        gradients = []
        for i in range(len(channel_power)):
            # Find nearby channels
            nearby_mask = (distances[i, :] > 0) & (
                distances[i, :] < np.percentile(distances[distances > 0], 25)
            )

            if np.any(nearby_mask):
                # Compute gradient
                power_diffs = np.abs(channel_power[nearby_mask] - channel_power[i])
                spatial_dists = distances[i, nearby_mask]

                # Average gradient
                gradient = np.mean(power_diffs / spatial_dists)
                gradients.append(gradient)

        if gradients:
            features["spatial_gradient_mean"] = np.array([np.mean(gradients)])
            features["spatial_gradient_max"] = np.array([np.max(gradients)])

        return features

    async def _compute_regional_features(
        self, data: np.ndarray, locations: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute features for different spatial regions.

        Args:
            data: Signal data (channels x samples)
            locations: Channel locations

        Returns:
            Dictionary of regional features
        """
        features = {}

        # Divide space into quadrants (simple approach)
        center_x = np.mean(locations[:, 0])
        center_y = np.mean(locations[:, 1])

        # Classify channels into regions
        regions = {
            "anterior": locations[:, 1] > center_y,
            "posterior": locations[:, 1] <= center_y,
            "left": locations[:, 0] < center_x,
            "right": locations[:, 0] >= center_x,
        }

        # Compute regional power
        for region_name, mask in regions.items():
            if np.any(mask):
                regional_data = data[mask, :]
                regional_power = np.mean(regional_data**2)
                features[f"{region_name}_power"] = np.array([regional_power])

        # Anterior-posterior gradient
        if "anterior_power" in features and "posterior_power" in features:
            ap_gradient = (
                features["anterior_power"][0] - features["posterior_power"][0]
            ) / (features["anterior_power"][0] + features["posterior_power"][0] + 1e-10)
            features["anterior_posterior_gradient"] = np.array([ap_gradient])

        # Left-right asymmetry
        if "left_power" in features and "right_power" in features:
            lr_asymmetry = (features["left_power"][0] - features["right_power"][0]) / (
                features["left_power"][0] + features["right_power"][0] + 1e-10
            )
            features["left_right_asymmetry"] = np.array([lr_asymmetry])

        return features

    async def _compute_spatial_autocorrelation(
        self, data: np.ndarray, locations: np.ndarray
    ) -> float:
        """Compute Moran's I spatial autocorrelation.

        Args:
            data: Signal data (channels x samples)
            locations: Channel locations

        Returns:
            Spatial autocorrelation value
        """
        # Use average power as the variable
        values = np.mean(data**2, axis=1)
        n = len(values)

        # Compute spatial weights (inverse distance)
        distances = squareform(pdist(locations))
        weights = np.zeros_like(distances)

        for i in range(n):
            for j in range(n):
                if i != j and distances[i, j] > 0:
                    weights[i, j] = 1.0 / distances[i, j]

        # Normalize weights
        row_sums = np.sum(weights, axis=1)
        for i in range(n):
            if row_sums[i] > 0:
                weights[i, :] /= row_sums[i]

        # Compute Moran's I
        mean_value = np.mean(values)

        numerator = 0
        for i in range(n):
            for j in range(n):
                numerator += (
                    weights[i, j] * (values[i] - mean_value) * (values[j] - mean_value)
                )

        denominator = np.sum((values - mean_value) ** 2)

        if denominator > 0:
            morans_i = (n / np.sum(weights)) * (numerator / denominator)
        else:
            morans_i = 0.0

        return morans_i

    def _generate_default_locations(self, n_channels: int) -> np.ndarray:
        """Generate default channel locations on a grid.

        Args:
            n_channels: Number of channels

        Returns:
            Array of 2D locations
        """
        # Create a grid layout
        grid_size = int(np.ceil(np.sqrt(n_channels)))
        locations = []

        for i in range(n_channels):
            x = (i % grid_size) / (grid_size - 1) if grid_size > 1 else 0.5
            y = (i // grid_size) / (grid_size - 1) if grid_size > 1 else 0.5
            locations.append([x, y])

        return np.array(locations)

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "min_channels" in params:
            self.min_channels = params["min_channels"]
        if "n_components" in params:
            self.n_components = params["n_components"]
        if "channel_locations" in params:
            self.channel_locations = params["channel_locations"]

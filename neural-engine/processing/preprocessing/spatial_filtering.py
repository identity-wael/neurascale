"""Spatial Filtering - Spatial filtering techniques for neural signals.

This module implements common average reference (CAR), Laplacian filtering,
and other spatial filtering methods to enhance signal quality.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import spsolve

logger = logging.getLogger(__name__)


class SpatialFilters:
    """Spatial filtering implementations for neural signals."""

    def __init__(self, config: Any):
        """Initialize spatial filters.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Laplacian parameters
        self.laplacian_radius = getattr(config, "laplacian_radius", 3.0)  # cm
        self.laplacian_type = "spline"  # 'spline' or 'hjorth'

        # Channel locations (placeholder - would come from montage)
        self.channel_locations = None
        self.laplacian_matrix = None

        # Bipolar montage pairs (if specified)
        self.bipolar_pairs = []

        logger.info("SpatialFilters initialized")

    async def common_average_reference(
        self, data: np.ndarray, exclude_channels: Optional[List[int]] = None
    ) -> np.ndarray:
        """Apply Common Average Reference (CAR) spatial filter.

        CAR subtracts the average of all channels from each channel,
        reducing common noise across electrodes.

        Args:
            data: Signal data (channels x samples)
            exclude_channels: Channels to exclude from average (e.g., bad channels)

        Returns:
            CAR-filtered data
        """
        try:
            # Determine channels to include in average
            if exclude_channels:
                include_mask = np.ones(data.shape[0], dtype=bool)
                include_mask[exclude_channels] = False
                included_channels = np.where(include_mask)[0]
            else:
                included_channels = np.arange(data.shape[0])

            if len(included_channels) == 0:
                logger.warning("No channels available for CAR")
                return data

            # Calculate common average
            common_average = np.mean(data[included_channels, :], axis=0)

            # Subtract from all channels
            car_data = data - common_average[np.newaxis, :]

            logger.debug(f"Applied CAR using {len(included_channels)} channels")

            return car_data

        except Exception as e:
            logger.error(f"Error in CAR filtering: {str(e)}")
            return data

    async def laplacian_filter(
        self, data: np.ndarray, montage: Optional[Any] = None
    ) -> np.ndarray:
        """Apply Laplacian spatial filter (surface Laplacian).

        The Laplacian enhances local sources and suppresses distant sources,
        improving spatial resolution.

        Args:
            data: Signal data (channels x samples)
            montage: Optional montage with electrode positions

        Returns:
            Laplacian-filtered data
        """
        try:
            # Initialize Laplacian matrix if not done
            if self.laplacian_matrix is None:
                self.laplacian_matrix = await self._compute_laplacian_matrix(
                    data.shape[0], montage
                )

            # Apply Laplacian filter
            if self.laplacian_matrix is not None:
                laplacian_data = self.laplacian_matrix @ data
            else:
                # Fallback to Hjorth Laplacian
                logger.warning("Using Hjorth Laplacian approximation")
                laplacian_data = await self._hjorth_laplacian(data)

            return laplacian_data

        except Exception as e:
            logger.error(f"Error in Laplacian filtering: {str(e)}")
            return data

    async def surface_laplacian(
        self,
        data: np.ndarray,
        electrode_positions: Optional[np.ndarray] = None,
        lambda_reg: float = 1e-5,
    ) -> np.ndarray:
        """Apply surface Laplacian using spline interpolation.

        This is a more sophisticated Laplacian that uses spherical splines
        to estimate the second spatial derivative of the potential field.

        Args:
            data: Signal data (channels x samples)
            electrode_positions: 3D electrode positions (channels x 3)
            lambda_reg: Regularization parameter

        Returns:
            Surface Laplacian filtered data
        """
        try:
            if electrode_positions is None:
                # Generate default positions if not provided
                electrode_positions = self._generate_default_positions(data.shape[0])

            # Compute spline Laplacian matrix
            G = await self._compute_spline_matrix(electrode_positions)
            H = await self._compute_laplacian_spline_matrix(electrode_positions)

            # Regularized solution
            n_channels = data.shape[0]
            C = G + lambda_reg * eye(n_channels)

            # Solve for spline coefficients
            coefficients = spsolve(C.tocsr(), data.T).T

            # Apply Laplacian
            laplacian_data = H @ coefficients

            return laplacian_data

        except Exception as e:
            logger.error(f"Error in surface Laplacian: {str(e)}")
            return await self._hjorth_laplacian(data)

    async def bipolar_montage(
        self, data: np.ndarray, bipolar_pairs: Optional[List[Tuple[int, int]]] = None
    ) -> np.ndarray:
        """Apply bipolar montage (differential pairs).

        Bipolar montage computes differences between pairs of electrodes,
        reducing common mode noise.

        Args:
            data: Signal data (channels x samples)
            bipolar_pairs: List of (channel1, channel2) pairs

        Returns:
            Bipolar montage data
        """
        try:
            if bipolar_pairs is None:
                # Use default sequential pairs
                bipolar_pairs = [(i, i + 1) for i in range(data.shape[0] - 1)]

            # Create bipolar signals
            bipolar_data = np.zeros((len(bipolar_pairs), data.shape[1]))

            for i, (ch1, ch2) in enumerate(bipolar_pairs):
                if ch1 < data.shape[0] and ch2 < data.shape[0]:
                    bipolar_data[i, :] = data[ch1, :] - data[ch2, :]
                else:
                    logger.warning(f"Invalid bipolar pair: ({ch1}, {ch2})")

            logger.debug(f"Applied bipolar montage with {len(bipolar_pairs)} pairs")

            return bipolar_data

        except Exception as e:
            logger.error(f"Error in bipolar montage: {str(e)}")
            return data

    async def local_average_reference(
        self,
        data: np.ndarray,
        radius: float = 3.0,
        electrode_positions: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Apply Local Average Reference (LAR).

        LAR subtracts the average of nearby electrodes from each electrode,
        providing a compromise between CAR and bipolar montages.

        Args:
            data: Signal data (channels x samples)
            radius: Radius for defining local neighborhood (cm)
            electrode_positions: 3D electrode positions

        Returns:
            LAR-filtered data
        """
        try:
            if electrode_positions is None:
                electrode_positions = self._generate_default_positions(data.shape[0])

            # Compute distance matrix
            distances = cdist(electrode_positions, electrode_positions)

            lar_data = np.zeros_like(data)

            # For each channel
            for ch in range(data.shape[0]):
                # Find neighbors within radius
                neighbors = np.where((distances[ch] > 0) & (distances[ch] <= radius))[0]

                if len(neighbors) > 0:
                    # Subtract local average
                    local_avg = np.mean(data[neighbors, :], axis=0)
                    lar_data[ch, :] = data[ch, :] - local_avg
                else:
                    # No neighbors, use original data
                    lar_data[ch, :] = data[ch, :]

            return lar_data

        except Exception as e:
            logger.error(f"Error in LAR filtering: {str(e)}")
            return data

    async def weighted_average_reference(
        self, data: np.ndarray, weights: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Apply Weighted Average Reference.

        Similar to CAR but with channel-specific weights, useful when
        channels have different noise characteristics.

        Args:
            data: Signal data (channels x samples)
            weights: Channel weights (default: inverse variance weighting)

        Returns:
            Weighted average referenced data
        """
        try:
            if weights is None:
                # Use inverse variance weighting
                variances = np.var(data, axis=1)
                weights = 1.0 / (
                    variances + 1e-10
                )  # Add small value to avoid division by zero
                weights = weights / np.sum(weights)  # Normalize

            # Calculate weighted average
            weighted_avg = np.sum(data * weights[:, np.newaxis], axis=0)

            # Subtract from all channels
            war_data = data - weighted_avg[np.newaxis, :]

            return war_data

        except Exception as e:
            logger.error(f"Error in weighted average reference: {str(e)}")
            return data

    async def _hjorth_laplacian(self, data: np.ndarray) -> np.ndarray:
        """Apply Hjorth Laplacian (nearest neighbor approximation).

        Simple Laplacian using nearest neighbors without electrode positions.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Hjorth Laplacian filtered data
        """
        laplacian_data = np.zeros_like(data)

        for ch in range(data.shape[0]):
            # Find nearest neighbors (simple approach: adjacent channels)
            neighbors = []
            if ch > 0:
                neighbors.append(ch - 1)
            if ch < data.shape[0] - 1:
                neighbors.append(ch + 1)

            if neighbors:
                # Hjorth Laplacian: channel - mean(neighbors)
                neighbor_mean = np.mean(data[neighbors, :], axis=0)
                laplacian_data[ch, :] = data[ch, :] - neighbor_mean
            else:
                # No neighbors, keep original
                laplacian_data[ch, :] = data[ch, :]

        return laplacian_data

    async def _compute_laplacian_matrix(
        self, n_channels: int, montage: Optional[Any] = None
    ) -> Optional[np.ndarray]:
        """Compute Laplacian transformation matrix.

        Args:
            n_channels: Number of channels
            montage: Optional montage with electrode positions

        Returns:
            Laplacian matrix or None
        """
        try:
            if montage is None or not hasattr(montage, "get_positions"):
                # Use simple Hjorth-style matrix
                L = np.eye(n_channels)
                for i in range(n_channels):
                    neighbors = []
                    if i > 0:
                        neighbors.append(i - 1)
                    if i < n_channels - 1:
                        neighbors.append(i + 1)

                    if neighbors:
                        for j in neighbors:
                            L[i, j] = -1.0 / len(neighbors)

                return L

            # Use actual electrode positions
            positions = montage.get_positions()["ch_pos"]
            electrode_positions = np.array(
                [positions[ch] for ch in self.config.channel_names]
            )

            # Compute distance-based Laplacian
            distances = cdist(electrode_positions, electrode_positions)

            # Create Laplacian matrix
            L = np.zeros((n_channels, n_channels))
            for i in range(n_channels):
                # Find neighbors within radius
                neighbors = np.where(
                    (distances[i] > 0) & (distances[i] <= self.laplacian_radius)
                )[0]

                if len(neighbors) > 0:
                    # Weight by inverse distance
                    weights = 1.0 / distances[i, neighbors]
                    weights = weights / np.sum(weights)

                    L[i, i] = 1.0
                    L[i, neighbors] = -weights
                else:
                    L[i, i] = 1.0

            return L

        except Exception as e:
            logger.error(f"Error computing Laplacian matrix: {str(e)}")
            return None

    async def _compute_spline_matrix(self, positions: np.ndarray) -> csr_matrix:
        """Compute spline interpolation matrix.

        Args:
            positions: Electrode positions (n_channels x 3)

        Returns:
            Spline matrix G
        """
        n = positions.shape[0]
        G = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    r = np.linalg.norm(positions[i] - positions[j])
                    G[i, j] = r * np.log(r + 1e-10)  # g(r) = r*log(r)

        return csr_matrix(G)

    async def _compute_laplacian_spline_matrix(
        self, positions: np.ndarray
    ) -> np.ndarray:
        """Compute Laplacian of spline basis functions.

        Args:
            positions: Electrode positions (n_channels x 3)

        Returns:
            Laplacian spline matrix H
        """
        n = positions.shape[0]
        H = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    r = np.linalg.norm(positions[i] - positions[j])
                    # Laplacian of g(r) = r*log(r) is proportional to 1/r
                    H[i, j] = 1.0 / (r + 1e-10)

        # Normalize rows
        row_sums = np.sum(np.abs(H), axis=1)
        H = H / row_sums[:, np.newaxis]

        return H

    def _generate_default_positions(self, n_channels: int) -> np.ndarray:
        """Generate default electrode positions on a spherical cap.

        Args:
            n_channels: Number of channels

        Returns:
            3D positions (n_channels x 3)
        """
        positions = []

        # Create a simple spherical cap arrangement
        n_rings = int(np.sqrt(n_channels))
        channels_per_ring = n_channels // n_rings

        for ring in range(n_rings):
            radius = 0.5 * (ring + 1) / n_rings
            z = 0.8 - 0.6 * (ring / n_rings)  # Height on sphere

            for ch in range(channels_per_ring):
                angle = 2 * np.pi * ch / channels_per_ring
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                positions.append([x, y, z])

        # Add remaining channels at center
        remaining = n_channels - len(positions)
        for i in range(remaining):
            positions.append([0, 0, 0.9 - 0.1 * i])

        return np.array(positions[:n_channels])

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update spatial filter configuration.

        Args:
            params: Parameters to update
        """
        if "laplacian_radius" in params:
            self.laplacian_radius = params["laplacian_radius"]
            # Clear cached Laplacian matrix
            self.laplacian_matrix = None

        if "spatial_filter_type" in params:
            self.config.spatial_filter_type = params["spatial_filter_type"]

        if "bipolar_pairs" in params:
            self.bipolar_pairs = params["bipolar_pairs"]

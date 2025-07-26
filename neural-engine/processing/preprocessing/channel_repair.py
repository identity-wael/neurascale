"""Channel Repair - Bad channel detection and interpolation.

This module implements methods for detecting bad channels and repairing them
through various interpolation techniques.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set
import numpy as np
from scipy.spatial.distance import cdist
from scipy.interpolate import griddata
from sklearn.covariance import EllipticEnvelope
import warnings

logger = logging.getLogger(__name__)


class ChannelRepair:
    """Bad channel detection and repair for neural signals."""

    def __init__(self, config: Any):
        """Initialize channel repair module.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Bad channel detection thresholds
        self.variance_threshold = 3.0  # z-score threshold
        self.correlation_threshold = 0.4  # minimum correlation with neighbors
        self.noise_threshold = 100.0  # microvolts RMS
        self.flatline_threshold = 0.5  # microvolts standard deviation

        # Channel location information (placeholder - would come from montage)
        self.channel_locations = None
        self.neighbor_matrix = None

        # Detection methods
        self.detection_methods = [
            "variance",
            "correlation",
            "noise",
            "flatline",
            "outlier",
        ]

        logger.info("ChannelRepair initialized")

    async def initialize(self) -> None:
        """Initialize channel repair components."""
        # Initialize channel locations if available
        if hasattr(self.config, "channel_names") and self.config.channel_names:
            self.channel_locations = self._generate_default_locations(
                len(self.config.channel_names)
            )
            self.neighbor_matrix = self._compute_neighbor_matrix()

        logger.info("Channel repair initialization complete")

    async def detect_bad_channels(
        self,
        data: np.ndarray,
        quality_metrics: Optional[Any] = None,
        methods: Optional[List[str]] = None,
    ) -> List[int]:
        """Detect bad channels using multiple criteria.

        Args:
            data: Signal data (channels x samples)
            quality_metrics: Optional pre-computed quality metrics
            methods: Detection methods to use (default: all)

        Returns:
            List of bad channel indices
        """
        bad_channels = set()
        methods = methods or self.detection_methods

        try:
            # Method 1: Variance-based detection
            if "variance" in methods:
                bad_variance = await self._detect_by_variance(data)
                bad_channels.update(bad_variance)
                if bad_variance:
                    logger.debug(
                        f"Variance detection found bad channels: {bad_variance}"
                    )

            # Method 2: Correlation-based detection
            if "correlation" in methods and self.neighbor_matrix is not None:
                bad_correlation = await self._detect_by_correlation(data)
                bad_channels.update(bad_correlation)
                if bad_correlation:
                    logger.debug(
                        f"Correlation detection found bad channels: {bad_correlation}"
                    )

            # Method 3: High noise detection
            if "noise" in methods:
                bad_noise = await self._detect_by_noise(data)
                bad_channels.update(bad_noise)
                if bad_noise:
                    logger.debug(f"Noise detection found bad channels: {bad_noise}")

            # Method 4: Flatline detection
            if "flatline" in methods:
                bad_flatline = await self._detect_flatlined_channels(data)
                bad_channels.update(bad_flatline)
                if bad_flatline:
                    logger.debug(
                        f"Flatline detection found bad channels: {bad_flatline}"
                    )

            # Method 5: Statistical outlier detection
            if "outlier" in methods:
                bad_outlier = await self._detect_by_outlier(data)
                bad_channels.update(bad_outlier)
                if bad_outlier:
                    logger.debug(f"Outlier detection found bad channels: {bad_outlier}")

            # Use quality metrics if provided
            if quality_metrics and hasattr(quality_metrics, "bad_channels"):
                bad_channels.update(quality_metrics.bad_channels)

            bad_channel_list = sorted(list(bad_channels))

            if bad_channel_list:
                logger.info(
                    f"Detected {len(bad_channel_list)} bad channels: {bad_channel_list}"
                )

            return bad_channel_list

        except Exception as e:
            logger.error(f"Error detecting bad channels: {str(e)}")
            return []

    async def interpolate_channels(
        self, data: np.ndarray, bad_channels: List[int], method: str = "spherical"
    ) -> np.ndarray:
        """Interpolate bad channels using good neighbors.

        Args:
            data: Signal data (channels x samples)
            bad_channels: Indices of bad channels
            method: Interpolation method ('spherical', 'linear', 'nearest')

        Returns:
            Data with interpolated channels
        """
        if not bad_channels:
            return data

        try:
            interpolated_data = data.copy()

            if method == "spherical" and self.channel_locations is not None:
                # Spherical spline interpolation
                interpolated_data = await self._interpolate_spherical(
                    interpolated_data, bad_channels
                )
            elif method == "linear":
                # Linear interpolation from nearest neighbors
                interpolated_data = await self._interpolate_linear(
                    interpolated_data, bad_channels
                )
            elif method == "nearest":
                # Simple nearest neighbor interpolation
                interpolated_data = await self._interpolate_nearest(
                    interpolated_data, bad_channels
                )
            else:
                logger.warning(f"Unknown interpolation method: {method}, using linear")
                interpolated_data = await self._interpolate_linear(
                    interpolated_data, bad_channels
                )

            # Validate interpolation quality
            success = await self.validate_repair_quality(
                data, interpolated_data, bad_channels
            )

            if success:
                logger.info(
                    f"Successfully interpolated {len(bad_channels)} channels using {method}"
                )
            else:
                logger.warning(
                    "Interpolation quality check failed, returning original data"
                )
                return data

            return interpolated_data

        except Exception as e:
            logger.error(f"Error interpolating channels: {str(e)}")
            return data

    async def validate_repair_quality(
        self, original: np.ndarray, repaired: np.ndarray, repaired_channels: List[int]
    ) -> bool:
        """Validate the quality of channel repair.

        Args:
            original: Original data
            repaired: Repaired data
            repaired_channels: Indices of repaired channels

        Returns:
            True if repair quality is acceptable
        """
        try:
            # Check that repaired channels have reasonable values
            for ch in repaired_channels:
                repaired_ch = repaired[ch, :]

                # Check for NaN or Inf
                if np.any(np.isnan(repaired_ch)) or np.any(np.isinf(repaired_ch)):
                    logger.warning(f"Channel {ch} contains NaN or Inf after repair")
                    return False

                # Check amplitude range
                ch_std = np.std(repaired_ch)
                if (
                    ch_std < self.flatline_threshold
                    or ch_std > self.noise_threshold * 2
                ):
                    logger.warning(
                        f"Channel {ch} has abnormal variance after repair: {ch_std}"
                    )
                    return False

                # Check that it's different from original (was actually repaired)
                if np.array_equal(original[ch, :], repaired[ch, :]):
                    logger.warning(f"Channel {ch} was not modified during repair")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating repair quality: {str(e)}")
            return False

    async def _detect_by_variance(self, data: np.ndarray) -> List[int]:
        """Detect channels with abnormal variance.

        Args:
            data: Signal data (channels x samples)

        Returns:
            List of bad channel indices
        """
        bad_channels = []

        # Calculate variance for each channel
        variances = np.var(data, axis=1)

        # Calculate z-scores
        mean_var = np.mean(variances)
        std_var = np.std(variances)

        if std_var > 0:
            z_scores = np.abs((variances - mean_var) / std_var)

            # Find channels with extreme variance
            bad_channels = np.where(z_scores > self.variance_threshold)[0].tolist()

        return bad_channels

    async def _detect_by_correlation(self, data: np.ndarray) -> List[int]:
        """Detect channels with low correlation to neighbors.

        Args:
            data: Signal data (channels x samples)

        Returns:
            List of bad channel indices
        """
        bad_channels = []

        if self.neighbor_matrix is None:
            return bad_channels

        # Calculate correlation matrix
        corr_matrix = np.corrcoef(data)

        # For each channel, check correlation with neighbors
        for ch in range(data.shape[0]):
            neighbors = self.neighbor_matrix[ch]
            if len(neighbors) > 0:
                # Calculate mean correlation with neighbors
                neighbor_corrs = corr_matrix[ch, neighbors]
                mean_corr = np.mean(np.abs(neighbor_corrs))

                if mean_corr < self.correlation_threshold:
                    bad_channels.append(ch)

        return bad_channels

    async def _detect_by_noise(self, data: np.ndarray) -> List[int]:
        """Detect channels with excessive noise.

        Args:
            data: Signal data (channels x samples)

        Returns:
            List of bad channel indices
        """
        bad_channels = []

        # Calculate RMS for each channel
        rms_values = np.sqrt(np.mean(data**2, axis=1))

        # Find channels exceeding noise threshold
        bad_channels = np.where(rms_values > self.noise_threshold)[0].tolist()

        return bad_channels

    async def _detect_flatlined_channels(self, data: np.ndarray) -> List[int]:
        """Detect flatlined (near-zero variance) channels.

        Args:
            data: Signal data (channels x samples)

        Returns:
            List of bad channel indices
        """
        bad_channels = []

        # Calculate standard deviation for each channel
        stds = np.std(data, axis=1)

        # Find near-zero variance channels
        bad_channels = np.where(stds < self.flatline_threshold)[0].tolist()

        return bad_channels

    async def _detect_by_outlier(self, data: np.ndarray) -> List[int]:
        """Detect outlier channels using robust covariance estimation.

        Args:
            data: Signal data (channels x samples)

        Returns:
            List of bad channel indices
        """
        bad_channels = []

        try:
            # Use channel statistics as features
            features = np.column_stack(
                [
                    np.mean(data, axis=1),
                    np.std(data, axis=1),
                    np.percentile(data, 25, axis=1),
                    np.percentile(data, 75, axis=1),
                ]
            )

            # Fit outlier detector
            detector = EllipticEnvelope(contamination=0.1, random_state=42)
            outlier_labels = detector.fit_predict(features)

            # Get outlier indices
            bad_channels = np.where(outlier_labels == -1)[0].tolist()

        except Exception as e:
            logger.debug(f"Outlier detection failed: {str(e)}")

        return bad_channels

    async def _interpolate_spherical(
        self, data: np.ndarray, bad_channels: List[int]
    ) -> np.ndarray:
        """Spherical spline interpolation for bad channels.

        Args:
            data: Signal data (channels x samples)
            bad_channels: Indices of bad channels

        Returns:
            Interpolated data
        """
        if self.channel_locations is None:
            logger.warning("No channel locations available for spherical interpolation")
            return await self._interpolate_linear(data, bad_channels)

        good_channels = [i for i in range(data.shape[0]) if i not in bad_channels]

        # Interpolate each time point
        for t in range(data.shape[1]):
            # Get values at good channels
            good_values = data[good_channels, t]
            good_locs = self.channel_locations[good_channels]

            # Interpolate values at bad channels
            bad_locs = self.channel_locations[bad_channels]

            # Use scipy griddata for interpolation
            interp_values = griddata(
                good_locs[:, :2],  # Use 2D projection for simplicity
                good_values,
                bad_locs[:, :2],
                method="cubic",
                fill_value=np.mean(good_values),
            )

            data[bad_channels, t] = interp_values

        return data

    async def _interpolate_linear(
        self, data: np.ndarray, bad_channels: List[int]
    ) -> np.ndarray:
        """Linear interpolation from nearest neighbors.

        Args:
            data: Signal data (channels x samples)
            bad_channels: Indices of bad channels

        Returns:
            Interpolated data
        """
        for bad_ch in bad_channels:
            # Find nearest good neighbors
            neighbors = await self._find_nearest_neighbors(bad_ch, bad_channels, k=3)

            if neighbors:
                # Average of nearest neighbors
                data[bad_ch, :] = np.mean(data[neighbors, :], axis=0)
            else:
                # If no good neighbors, use global average
                good_channels = [
                    i for i in range(data.shape[0]) if i not in bad_channels
                ]
                if good_channels:
                    data[bad_ch, :] = np.mean(data[good_channels, :], axis=0)

        return data

    async def _interpolate_nearest(
        self, data: np.ndarray, bad_channels: List[int]
    ) -> np.ndarray:
        """Nearest neighbor interpolation.

        Args:
            data: Signal data (channels x samples)
            bad_channels: Indices of bad channels

        Returns:
            Interpolated data
        """
        for bad_ch in bad_channels:
            # Find single nearest good neighbor
            neighbors = await self._find_nearest_neighbors(bad_ch, bad_channels, k=1)

            if neighbors:
                data[bad_ch, :] = data[neighbors[0], :]
            else:
                # If no good neighbors, use channel average
                good_channels = [
                    i for i in range(data.shape[0]) if i not in bad_channels
                ]
                if good_channels:
                    data[bad_ch, :] = np.mean(data[good_channels, :], axis=0)

        return data

    async def _find_nearest_neighbors(
        self, channel: int, bad_channels: List[int], k: int = 3
    ) -> List[int]:
        """Find k nearest good neighbors for a channel.

        Args:
            channel: Channel index
            bad_channels: List of bad channels to exclude
            k: Number of neighbors to find

        Returns:
            List of neighbor channel indices
        """
        if self.neighbor_matrix is not None:
            # Use precomputed neighbors
            all_neighbors = self.neighbor_matrix[channel]
            good_neighbors = [n for n in all_neighbors if n not in bad_channels]
            return good_neighbors[:k]
        else:
            # Simple approach: use adjacent channels
            neighbors = []
            for offset in [1, -1, 2, -2, 3, -3]:
                neighbor_idx = channel + offset
                if (
                    0 <= neighbor_idx < self.config.num_channels
                    and neighbor_idx not in bad_channels
                ):
                    neighbors.append(neighbor_idx)
                if len(neighbors) >= k:
                    break
            return neighbors[:k]

    def _generate_default_locations(self, n_channels: int) -> np.ndarray:
        """Generate default channel locations on a grid.

        Args:
            n_channels: Number of channels

        Returns:
            Array of channel locations (n_channels x 3)
        """
        # Create a simple grid layout
        grid_size = int(np.ceil(np.sqrt(n_channels)))
        locations = []

        for i in range(n_channels):
            x = (i % grid_size) / (grid_size - 1) - 0.5
            y = (i // grid_size) / (grid_size - 1) - 0.5
            z = 0.1  # Small z value for slight curvature
            locations.append([x, y, z])

        return np.array(locations)

    def _compute_neighbor_matrix(self) -> Dict[int, List[int]]:
        """Compute neighbor relationships based on channel locations.

        Returns:
            Dictionary mapping channel index to list of neighbor indices
        """
        if self.channel_locations is None:
            return None

        # Compute pairwise distances
        distances = cdist(self.channel_locations, self.channel_locations)

        neighbor_matrix = {}
        for i in range(len(self.channel_locations)):
            # Sort by distance (excluding self)
            sorted_indices = np.argsort(distances[i])[1:]
            # Take nearest neighbors (up to 6)
            neighbor_matrix[i] = sorted_indices[:6].tolist()

        return neighbor_matrix

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update channel repair configuration.

        Args:
            params: Parameters to update
        """
        if "variance_threshold" in params:
            self.variance_threshold = params["variance_threshold"]
        if "correlation_threshold" in params:
            self.correlation_threshold = params["correlation_threshold"]
        if "noise_threshold" in params:
            self.noise_threshold = params["noise_threshold"]
        if "flatline_threshold" in params:
            self.flatline_threshold = params["flatline_threshold"]

    async def cleanup(self) -> None:
        """Cleanup channel repair resources."""
        self.channel_locations = None
        self.neighbor_matrix = None
        logger.info("Channel repair cleanup complete")

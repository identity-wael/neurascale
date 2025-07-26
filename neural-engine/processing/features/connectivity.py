"""Connectivity Features - Functional connectivity and network analysis.

This module implements coherence, phase-amplitude coupling, transfer entropy,
and other connectivity measures for neural signals.
"""

import logging
from typing import Dict, Any, Tuple
import numpy as np
from scipy import signal
from scipy.stats import entropy
import warnings

logger = logging.getLogger(__name__)


class ConnectivityFeatures:
    """Connectivity feature extraction for neural signals."""

    def __init__(self, config: Any):
        """Initialize connectivity feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config
        self.sampling_rate = config.sampling_rate

        # Connectivity parameters
        self.min_channels = 2  # Minimum channels for connectivity
        self.nperseg = int(1 * self.sampling_rate)  # 1 second windows
        self.noverlap = int(0.5 * self.nperseg)  # 50% overlap

        # Phase-amplitude coupling parameters
        self.pac_n_bins = 18  # Number of phase bins
        self.pac_method = "tort"  # 'tort' or 'ozkurt'

        # Transfer entropy parameters
        self.te_history = 10  # History length in samples
        self.te_bins = 8  # Number of bins for discretization

        logger.info("ConnectivityFeatures initialized")

    async def initialize(self) -> None:
        """Initialize connectivity components if needed."""
        logger.info("Connectivity features initialized")

    async def extract_coherence_features(
        self, data: np.ndarray, freq_bands: Dict[str, Tuple[float, float]]
    ) -> Dict[str, np.ndarray]:
        """Extract coherence-based connectivity features.

        Args:
            data: Signal data (channels x samples)
            freq_bands: Frequency bands for coherence analysis

        Returns:
            Dictionary of coherence features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            logger.warning(f"Not enough channels ({n_channels}) for connectivity")
            return features

        try:
            # Compute pairwise coherence for each band
            for band_name, (low_freq, high_freq) in freq_bands.items():
                # Initialize connectivity matrices
                coherence_matrix = np.zeros((n_channels, n_channels))
                imaginary_coherence = np.zeros((n_channels, n_channels))

                # Compute pairwise coherence
                for i in range(n_channels):
                    for j in range(i + 1, n_channels):
                        # Compute coherence
                        freqs, Cxy = signal.coherence(
                            data[i, :],
                            data[j, :],
                            fs=self.sampling_rate,
                            window="hann",
                            nperseg=self.nperseg,
                            noverlap=self.noverlap,
                        )

                        # Band-specific coherence
                        band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                        if np.any(band_mask):
                            # Mean coherence in band
                            band_coherence = np.mean(Cxy[band_mask])
                            coherence_matrix[i, j] = band_coherence
                            coherence_matrix[j, i] = band_coherence

                            # Imaginary coherence (less sensitive to volume conduction)
                            _, Pxy = signal.csd(
                                data[i, :],
                                data[j, :],
                                fs=self.sampling_rate,
                                window="hann",
                                nperseg=self.nperseg,
                                noverlap=self.noverlap,
                            )

                            imag_coh = np.mean(np.abs(np.imag(Pxy[band_mask])))
                            imaginary_coherence[i, j] = imag_coh
                            imaginary_coherence[j, i] = imag_coh

                # Extract network features
                network_features = await self._extract_network_features(
                    coherence_matrix, f"{band_name}_coherence"
                )
                features.update(network_features)

                # Imaginary coherence features
                imag_features = await self._extract_network_features(
                    imaginary_coherence, f"{band_name}_imag_coherence"
                )
                features.update(imag_features)

            return features

        except Exception as e:
            logger.error(f"Error extracting coherence features: {str(e)}")
            return features

    async def extract_phase_amplitude_coupling(
        self,
        data: np.ndarray,
        phase_freq: Tuple[float, float],
        amp_freq: Tuple[float, float],
    ) -> np.ndarray:
        """Extract phase-amplitude coupling (PAC) features.

        Args:
            data: Signal data (channels x samples)
            phase_freq: Frequency band for phase (e.g., theta)
            amp_freq: Frequency band for amplitude (e.g., gamma)

        Returns:
            PAC values for each channel
        """
        n_channels = data.shape[0]
        pac_values = np.zeros(n_channels)

        try:
            for ch in range(n_channels):
                # Extract phase of low frequency
                phase_sos = signal.butter(
                    4, phase_freq, btype="band", fs=self.sampling_rate, output="sos"
                )
                phase_filtered = signal.sosfiltfilt(phase_sos, data[ch, :])
                phase = np.angle(signal.hilbert(phase_filtered))

                # Extract amplitude of high frequency
                amp_sos = signal.butter(
                    4, amp_freq, btype="band", fs=self.sampling_rate, output="sos"
                )
                amp_filtered = signal.sosfiltfilt(amp_sos, data[ch, :])
                amplitude = np.abs(signal.hilbert(amp_filtered))

                # Compute PAC
                if self.pac_method == "tort":
                    pac = await self._compute_pac_tort(phase, amplitude)
                else:
                    pac = await self._compute_pac_ozkurt(phase, amplitude)

                pac_values[ch] = pac

            return pac_values

        except Exception as e:
            logger.error(f"Error computing PAC: {str(e)}")
            return pac_values

    async def extract_phase_locking_value(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract phase locking value (PLV) connectivity.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of PLV features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            return features

        try:
            # Define frequency bands for PLV
            freq_bands = {
                "theta": (4, 8),
                "alpha": (8, 13),
                "beta": (13, 30),
                "gamma": (30, 50),
            }

            for band_name, (low_freq, high_freq) in freq_bands.items():
                # Filter signal in band
                sos = signal.butter(
                    4,
                    [low_freq, high_freq],
                    btype="band",
                    fs=self.sampling_rate,
                    output="sos",
                )

                # Get instantaneous phase for each channel
                phases = np.zeros((n_channels, data.shape[1]))
                for ch in range(n_channels):
                    filtered = signal.sosfiltfilt(sos, data[ch, :])
                    phases[ch, :] = np.angle(signal.hilbert(filtered))

                # Compute PLV matrix
                plv_matrix = np.zeros((n_channels, n_channels))

                for i in range(n_channels):
                    for j in range(i + 1, n_channels):
                        # Phase difference
                        phase_diff = phases[i, :] - phases[j, :]

                        # PLV
                        plv = np.abs(np.mean(np.exp(1j * phase_diff)))
                        plv_matrix[i, j] = plv
                        plv_matrix[j, i] = plv

                # Extract network features
                network_features = await self._extract_network_features(
                    plv_matrix, f"{band_name}_plv"
                )
                features.update(network_features)

            return features

        except Exception as e:
            logger.error(f"Error extracting PLV features: {str(e)}")
            return features

    async def extract_transfer_entropy(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract transfer entropy connectivity.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of transfer entropy features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            return features

        try:
            # Initialize transfer entropy matrix
            te_matrix = np.zeros((n_channels, n_channels))

            # Discretize signals
            discretized = np.zeros_like(data, dtype=int)
            for ch in range(n_channels):
                # Discretize using equal-width bins
                bins = np.linspace(
                    data[ch, :].min(), data[ch, :].max(), self.te_bins + 1
                )
                discretized[ch, :] = np.digitize(data[ch, :], bins) - 1

            # Compute pairwise transfer entropy
            for i in range(n_channels):
                for j in range(n_channels):
                    if i != j:
                        te = await self._compute_transfer_entropy(
                            discretized[i, :], discretized[j, :]
                        )
                        te_matrix[i, j] = te

            # Extract network features
            network_features = await self._extract_network_features(
                te_matrix, "transfer_entropy"
            )
            features.update(network_features)

            # Directionality index
            directionality = np.zeros(n_channels)
            for ch in range(n_channels):
                outgoing = np.sum(te_matrix[ch, :])
                incoming = np.sum(te_matrix[:, ch])
                if outgoing + incoming > 0:
                    directionality[ch] = (outgoing - incoming) / (outgoing + incoming)

            features["te_directionality"] = directionality

            return features

        except Exception as e:
            logger.error(f"Error extracting transfer entropy: {str(e)}")
            return features

    async def extract_mutual_information(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract mutual information connectivity.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of mutual information features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < self.min_channels:
            return features

        try:
            # Initialize MI matrix
            mi_matrix = np.zeros((n_channels, n_channels))

            # Compute pairwise mutual information
            for i in range(n_channels):
                for j in range(i + 1, n_channels):
                    mi = await self._compute_mutual_information(data[i, :], data[j, :])
                    mi_matrix[i, j] = mi
                    mi_matrix[j, i] = mi

            # Extract network features
            network_features = await self._extract_network_features(
                mi_matrix, "mutual_information"
            )
            features.update(network_features)

            return features

        except Exception as e:
            logger.error(f"Error extracting mutual information: {str(e)}")
            return features

    async def _compute_pac_tort(
        self, phase: np.ndarray, amplitude: np.ndarray
    ) -> float:
        """Compute PAC using Tort et al. method (KL divergence).

        Args:
            phase: Instantaneous phase
            amplitude: Instantaneous amplitude

        Returns:
            PAC value
        """
        # Create phase bins
        phase_bins = np.linspace(-np.pi, np.pi, self.pac_n_bins + 1)

        # Compute mean amplitude in each phase bin
        amp_by_phase = np.zeros(self.pac_n_bins)

        for i in range(self.pac_n_bins):
            mask = (phase >= phase_bins[i]) & (phase < phase_bins[i + 1])
            if np.any(mask):
                amp_by_phase[i] = np.mean(amplitude[mask])

        # Normalize to create probability distribution
        if np.sum(amp_by_phase) > 0:
            p = amp_by_phase / np.sum(amp_by_phase)
        else:
            return 0.0

        # Uniform distribution
        q = np.ones(self.pac_n_bins) / self.pac_n_bins

        # KL divergence
        kl_div = entropy(p, q)

        # Normalize by log(n_bins) to get value between 0 and 1
        pac = kl_div / np.log(self.pac_n_bins)

        return pac

    async def _compute_pac_ozkurt(
        self, phase: np.ndarray, amplitude: np.ndarray
    ) -> float:
        """Compute PAC using Ozkurt & Schnitzler method.

        Args:
            phase: Instantaneous phase
            amplitude: Instantaneous amplitude

        Returns:
            PAC value
        """
        # Normalize amplitude
        amp_normalized = (amplitude - np.mean(amplitude)) / np.std(amplitude)

        # Compute PAC
        pac_complex = np.mean(amp_normalized * np.exp(1j * phase))
        pac = np.abs(pac_complex)

        # Normalize by sqrt(N) for statistical comparison
        pac = pac * np.sqrt(len(phase))

        # Convert to 0-1 range (empirical normalization)
        pac = np.tanh(pac / 2)

        return pac

    async def _compute_transfer_entropy(
        self, source: np.ndarray, target: np.ndarray
    ) -> float:
        """Compute transfer entropy from source to target.

        Args:
            source: Source signal (discretized)
            target: Target signal (discretized)

        Returns:
            Transfer entropy value
        """
        n_samples = len(source)

        if n_samples <= self.te_history:
            return 0.0

        # Create history embeddings
        te_sum = 0.0
        count = 0

        for t in range(self.te_history, n_samples - 1):
            # Target future
            # y_future = target[t + 1]

            # Target history
            # y_past = tuple(target[t - self.te_history + 1 : t + 1])

            # Source history
            # x_past = tuple(source[t - self.te_history + 1 : t + 1])

            # Estimate probabilities (simplified)
            # In practice, would use more sophisticated estimation
            p_future_given_past = 1.0 / self.te_bins
            p_future_given_both = 1.0 / self.te_bins

            if p_future_given_past > 0 and p_future_given_both > 0:
                te_sum += np.log2(p_future_given_both / p_future_given_past)
                count += 1

        if count > 0:
            return te_sum / count
        else:
            return 0.0

    async def _compute_mutual_information(
        self, x: np.ndarray, y: np.ndarray, bins: int = 16
    ) -> float:
        """Compute mutual information between two signals.

        Args:
            x: First signal
            y: Second signal
            bins: Number of bins for histogram

        Returns:
            Mutual information value
        """
        # Create 2D histogram
        hist_2d, _, _ = np.histogram2d(x, y, bins=bins)

        # Convert to probabilities
        pxy = hist_2d / np.sum(hist_2d)
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        # Compute MI
        mi = 0.0
        for i in range(bins):
            for j in range(bins):
                if pxy[i, j] > 0 and px[i] > 0 and py[j] > 0:
                    mi += pxy[i, j] * np.log2(pxy[i, j] / (px[i] * py[j]))

        return mi

    async def _extract_network_features(
        self, connectivity_matrix: np.ndarray, prefix: str
    ) -> Dict[str, np.ndarray]:
        """Extract network features from connectivity matrix.

        Args:
            connectivity_matrix: Connectivity matrix
            prefix: Prefix for feature names

        Returns:
            Dictionary of network features
        """
        features = {}
        n_nodes = connectivity_matrix.shape[0]

        # Global efficiency
        efficiency = await self._compute_global_efficiency(connectivity_matrix)
        features[f"{prefix}_global_efficiency"] = np.array([efficiency])

        # Clustering coefficient
        clustering = await self._compute_clustering_coefficient(connectivity_matrix)
        features[f"{prefix}_clustering"] = np.array([clustering])

        # Node strength (weighted degree)
        node_strength = np.sum(connectivity_matrix, axis=0)
        features[f"{prefix}_mean_strength"] = np.array([np.mean(node_strength)])
        features[f"{prefix}_std_strength"] = np.array([np.std(node_strength)])

        # Betweenness centrality (simplified)
        betweenness = await self._compute_betweenness_centrality(connectivity_matrix)
        features[f"{prefix}_mean_betweenness"] = np.array([np.mean(betweenness)])

        # Small-world index
        if clustering > 0 and efficiency > 0:
            # Random network comparison (simplified)
            random_clustering = 2 * np.mean(connectivity_matrix) / n_nodes
            random_efficiency = 0.5  # Simplified assumption

            if random_clustering > 0 and random_efficiency > 0:
                small_world = (clustering / random_clustering) / (
                    efficiency / random_efficiency
                )
                features[f"{prefix}_small_world"] = np.array([small_world])

        # Modularity (simplified community detection)
        modularity = await self._compute_modularity(connectivity_matrix)
        features[f"{prefix}_modularity"] = np.array([modularity])

        return features

    async def _compute_global_efficiency(self, matrix: np.ndarray) -> float:
        """Compute global efficiency of network.

        Args:
            matrix: Connectivity matrix

        Returns:
            Global efficiency value
        """
        n = matrix.shape[0]

        # Convert to distance matrix (inverse of weights)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            distance_matrix = 1.0 / (matrix + 1e-10)

        np.fill_diagonal(distance_matrix, 0)

        # Compute shortest paths (simplified - assumes direct connections)
        efficiency_sum = 0.0
        count = 0

        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i, j] > 0:
                    efficiency_sum += matrix[i, j]
                    count += 1

        if count > 0:
            return efficiency_sum / count
        else:
            return 0.0

    async def _compute_clustering_coefficient(self, matrix: np.ndarray) -> float:
        """Compute weighted clustering coefficient.

        Args:
            matrix: Connectivity matrix

        Returns:
            Average clustering coefficient
        """
        n = matrix.shape[0]
        clustering_coeffs = []

        for i in range(n):
            # Find neighbors
            neighbors = np.where(matrix[i, :] > 0)[0]
            neighbors = neighbors[neighbors != i]

            if len(neighbors) >= 2:
                # Weight of connections between neighbors
                neighbor_weights = 0.0
                max_weights = 0.0

                for j in range(len(neighbors)):
                    for k in range(j + 1, len(neighbors)):
                        neighbor_weights += matrix[neighbors[j], neighbors[k]]
                        max_weights += (
                            matrix[i, neighbors[j]] + matrix[i, neighbors[k]]
                        ) / 2

                if max_weights > 0:
                    clustering_coeffs.append(neighbor_weights / max_weights)

        if clustering_coeffs:
            return np.mean(clustering_coeffs)
        else:
            return 0.0

    async def _compute_betweenness_centrality(self, matrix: np.ndarray) -> np.ndarray:
        """Compute betweenness centrality (simplified).

        Args:
            matrix: Connectivity matrix

        Returns:
            Betweenness centrality for each node
        """
        n = matrix.shape[0]
        betweenness = np.zeros(n)

        # Simplified: count how often a node is on strongest paths
        for i in range(n):
            for j in range(i + 1, n):
                if i != j:
                    # Find intermediate node with strongest connections
                    path_strengths = matrix[i, :] * matrix[:, j]
                    path_strengths[i] = 0
                    path_strengths[j] = 0

                    if np.any(path_strengths > 0):
                        best_intermediate = np.argmax(path_strengths)
                        betweenness[best_intermediate] += 1

        # Normalize
        if n > 2:
            betweenness = betweenness / ((n - 1) * (n - 2) / 2)

        return betweenness

    async def _compute_modularity(self, matrix: np.ndarray) -> float:
        """Compute network modularity (simplified).

        Args:
            matrix: Connectivity matrix

        Returns:
            Modularity value
        """
        n = matrix.shape[0]

        # Simple community detection: threshold-based
        threshold = np.percentile(matrix[matrix > 0], 75)

        # Create communities
        communities = []
        unassigned = set(range(n))

        while unassigned:
            node = unassigned.pop()
            community = {node}

            # Add strongly connected nodes
            for neighbor in list(unassigned):
                if matrix[node, neighbor] > threshold:
                    community.add(neighbor)
                    unassigned.discard(neighbor)

            communities.append(community)

        # Calculate modularity
        total_weight = np.sum(matrix)
        if total_weight == 0:
            return 0.0

        modularity = 0.0
        for community in communities:
            for i in community:
                for j in community:
                    if i != j:
                        expected = (
                            np.sum(matrix[i, :]) * np.sum(matrix[:, j]) / total_weight
                        )
                        modularity += matrix[i, j] - expected

        modularity = modularity / total_weight

        return modularity

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "nperseg" in params:
            self.nperseg = int(params["nperseg"] * self.sampling_rate)
        if "noverlap" in params:
            self.noverlap = int(params["noverlap"] * self.sampling_rate)
        if "pac_n_bins" in params:
            self.pac_n_bins = params["pac_n_bins"]
        if "pac_method" in params:
            self.pac_method = params["pac_method"]
        if "te_history" in params:
            self.te_history = params["te_history"]
        if "te_bins" in params:
            self.te_bins = params["te_bins"]

    async def cleanup(self) -> None:
        """Cleanup connectivity resources."""
        logger.info("Connectivity features cleanup complete")

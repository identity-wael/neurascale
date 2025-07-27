"""PhysioNet dataset loader for EEG and ECG datasets."""

import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum
import mne
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_dataset import BaseDataset, DatasetConfig

logger = logging.getLogger(__name__)


class PhysioNetDataset(Enum):
    """Available PhysioNet datasets."""

    # EEG Datasets
    CHB_MIT = "chb-mit"  # CHB-MIT Scalp EEG Database (epilepsy)
    EEGMMIDB = "eegmmidb"  # EEG Motor Movement/Imagery Database
    TUEG = "tueg"  # Temple University Hospital EEG Database
    TUAB = "tuab"  # Temple University Hospital Abnormal EEG Corpus

    # Sleep EEG
    SLEEP_EDF = "sleep-edf"  # Sleep-EDF Database
    SLEEP_EDFX = "sleep-edfx"  # Sleep-EDF Database Expanded

    # ECG Datasets
    MIT_BIH = "mitdb"  # MIT-BIH Arrhythmia Database
    PTB_DIAGNOSTIC = "ptbdb"  # PTB Diagnostic ECG Database

    # Multi-modal
    CAPSLPDB = "capslpdb"  # CAP Sleep Database


@dataclass
class PhysioNetConfig(DatasetConfig):
    """Configuration specific to PhysioNet datasets."""

    dataset_type: PhysioNetDataset = PhysioNetDataset.EEGMMIDB
    subjects: Optional[List[str]] = None  # None means all subjects
    tasks: Optional[List[str]] = None  # For motor imagery tasks
    channels: Optional[List[str]] = None  # None means all channels
    sampling_rate: Optional[float] = None  # Target sampling rate for resampling
    window_size: float = 2.0  # Window size in seconds for epoching
    overlap: float = 0.5  # Overlap between windows (0-1)
    bandpass_freq: Tuple[float, float] = (0.5, 50.0)  # Bandpass filter frequencies
    notch_freq: Optional[float] = 60.0  # Notch filter frequency (50 or 60 Hz)
    reference: str = "average"  # Reference type: "average", "linked-ears", etc.


class PhysioNetLoader(BaseDataset):
    """Loader for PhysioNet datasets."""

    # Base URLs for different datasets
    BASE_URLS = {
        PhysioNetDataset.CHB_MIT: "https://physionet.org/files/chbmit/1.0.0/",
        PhysioNetDataset.EEGMMIDB: "https://physionet.org/files/eegmmidb/1.0.0/",
        PhysioNetDataset.SLEEP_EDF: "https://physionet.org/files/sleep-edf/1.0.0/",
        PhysioNetDataset.MIT_BIH: "https://physionet.org/files/mitdb/1.0.0/",
        PhysioNetDataset.PTB_DIAGNOSTIC: "https://physionet.org/files/ptbdb/1.0.0/",
    }

    def __init__(self, config: PhysioNetConfig):
        """Initialize PhysioNet loader."""
        super().__init__(config)
        self.config: PhysioNetConfig = config
        self.dataset_dir = self.cache_dir / config.dataset_type.value
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

        # Dataset-specific settings
        self._subject_data: Dict[str, Any] = {}
        self._channel_names: List[str] = []
        self._original_sampling_rate: float = 0.0

    def download(self) -> None:
        """Download PhysioNet dataset if not present."""
        if self.config.dataset_type == PhysioNetDataset.EEGMMIDB:
            self._download_eegmmidb()
        elif self.config.dataset_type == PhysioNetDataset.CHB_MIT:
            self._download_chbmit()
        elif self.config.dataset_type == PhysioNetDataset.SLEEP_EDF:
            self._download_sleep_edf()
        else:
            raise NotImplementedError(
                f"Download not implemented for {self.config.dataset_type}"
            )

    def _download_eegmmidb(self) -> None:
        """Download EEG Motor Movement/Imagery Database."""
        base_url = self.BASE_URLS[PhysioNetDataset.EEGMMIDB]

        # Get list of subjects
        subjects = self.config.subjects
        if subjects is None:
            # Download all 109 subjects
            subjects = [f"S{i:03d}" for i in range(1, 110)]

        logger.info(f"Downloading EEGMMIDB dataset for {len(subjects)} subjects...")

        # Download subjects in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for subject in subjects:
                subject_dir = self.dataset_dir / subject
                if not subject_dir.exists():
                    subject_dir.mkdir(parents=True, exist_ok=True)
                    futures.append(
                        executor.submit(
                            self._download_subject_eegmmidb, subject, base_url
                        )
                    )

            # Wait for downloads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error downloading subject: {e}")

    def _download_subject_eegmmidb(self, subject: str, base_url: str) -> None:
        """Download single subject from EEGMMIDB."""
        subject_dir = self.dataset_dir / subject

        # Each subject has 14 runs
        runs = []
        for i in range(1, 15):
            runs.append(f"{subject}R{i:02d}.edf")

        for run_file in runs:
            file_path = subject_dir / run_file
            if not file_path.exists():
                url = f"{base_url}{subject}/{run_file}"
                self._download_file(url, file_path)

        logger.info(f"Downloaded subject {subject}")

    def _download_chbmit(self) -> None:
        """Download CHB-MIT Scalp EEG Database."""
        base_url = self.BASE_URLS[PhysioNetDataset.CHB_MIT]

        # Get list of subjects (chb01 to chb24)
        subjects = self.config.subjects
        if subjects is None:
            subjects = [f"chb{i:02d}" for i in range(1, 25)]

        logger.info(f"Downloading CHB-MIT dataset for {len(subjects)} subjects...")

        for subject in subjects:
            subject_dir = self.dataset_dir / subject
            if not subject_dir.exists():
                subject_dir.mkdir(parents=True, exist_ok=True)

            # Download summary file
            summary_file = subject_dir / f"{subject}-summary.txt"
            if not summary_file.exists():
                url = f"{base_url}{subject}/{subject}-summary.txt"
                self._download_file(url, summary_file)

            # Parse summary to get EDF files
            if summary_file.exists():
                with open(summary_file, "r") as f:
                    content = f.read()

                # Extract EDF filenames
                edf_files = []
                for line in content.split("\n"):
                    if line.endswith(".edf"):
                        edf_files.append(line.strip())

                # Download EDF files
                for edf_file in edf_files:
                    file_path = subject_dir / edf_file
                    if not file_path.exists():
                        url = f"{base_url}{subject}/{edf_file}"
                        self._download_file(url, file_path)

        logger.info("CHB-MIT download complete")

    def _download_sleep_edf(self) -> None:
        """Download Sleep-EDF Database."""
        base_url = self.BASE_URLS[PhysioNetDataset.SLEEP_EDF]

        # Sleep-EDF has specific structure
        logger.info("Downloading Sleep-EDF dataset...")

        # Download RECORDS file first
        records_file = self.dataset_dir / "RECORDS"
        if not records_file.exists():
            self._download_file(f"{base_url}RECORDS", records_file)

        # Parse RECORDS to get file list
        if records_file.exists():
            with open(records_file, "r") as f:
                files = [line.strip() for line in f.readlines()]

            # Download each file
            for file_name in files:
                file_path = self.dataset_dir / file_name
                if not file_path.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    url = f"{base_url}{file_name}"
                    self._download_file(url, file_path)

        logger.info("Sleep-EDF download complete")

    def _download_file(self, url: str, file_path: Path) -> None:
        """Download a single file."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Write to file
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.debug(f"Downloaded: {file_path.name}")

        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            raise

    def load(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load PhysioNet dataset."""
        # Check cache first
        if self.config.lazy_loading and self.cache_exists():
            data, labels, metadata = self.load_cache()
            self._metadata = metadata
            return data, labels

        # Download if needed
        if self.config.download_if_missing and not self._check_dataset_exists():
            self.download()

        # Load based on dataset type
        if self.config.dataset_type == PhysioNetDataset.EEGMMIDB:
            data, labels = self._load_eegmmidb()
        elif self.config.dataset_type == PhysioNetDataset.CHB_MIT:
            data, labels = self._load_chbmit()
        elif self.config.dataset_type == PhysioNetDataset.SLEEP_EDF:
            data, labels = self._load_sleep_edf()
        else:
            raise NotImplementedError(
                f"Loading not implemented for {self.config.dataset_type}"
            )

        # Cache the loaded data
        if self.config.lazy_loading:
            self.save_cache(data, labels, self._metadata)

        return data, labels

    def _check_dataset_exists(self) -> bool:
        """Check if dataset files exist locally."""
        if self.config.dataset_type == PhysioNetDataset.EEGMMIDB:
            # Check for at least one subject
            subjects = self.config.subjects or ["S001"]
            subject_dir = self.dataset_dir / subjects[0]
            return subject_dir.exists() and any(subject_dir.glob("*.edf"))
        return self.dataset_dir.exists() and any(self.dataset_dir.rglob("*.edf"))

    def _load_eegmmidb(self) -> Tuple[np.ndarray, np.ndarray]:  # noqa: C901
        """Load EEG Motor Movement/Imagery Database."""
        subjects = self.config.subjects
        if subjects is None:
            subjects = [f"S{i:03d}" for i in range(1, 110)]

        all_data = []
        all_labels = []

        # Task mapping for EEGMMIDB
        task_mapping = {
            1: "rest",  # Baseline, eyes open
            2: "rest",  # Baseline, eyes closed
            3: "left_fist",  # Motor execution
            4: "right_fist",  # Motor execution
            5: "both_fists",  # Motor execution
            6: "both_feet",  # Motor execution
            7: "left_fist",  # Motor imagery
            8: "right_fist",  # Motor imagery
            9: "both_fists",  # Motor imagery
            10: "both_feet",  # Motor imagery
        }

        # Filter tasks if specified
        if self.config.tasks:
            task_mapping = {
                k: v for k, v in task_mapping.items() if v in self.config.tasks
            }

        for subject in subjects:
            logger.info(f"Loading subject {subject}")
            subject_dir = self.dataset_dir / subject

            # Load all runs for the subject
            for run_file in sorted(subject_dir.glob("*.edf")):
                # Parse run number
                run_num = int(run_file.stem[-2:])

                # Determine task from run number
                if run_num in [1, 2]:  # Baseline runs
                    task = task_mapping.get(run_num, "rest")
                else:
                    # Runs 3-14 cycle through tasks 3-10
                    task_idx = ((run_num - 3) % 4) + 3
                    if run_num >= 7:
                        task_idx += 4
                    task = task_mapping.get(task_idx, "unknown")

                if self.config.tasks and task not in self.config.tasks:
                    continue

                # Load EDF file
                try:
                    raw = mne.io.read_raw_edf(
                        str(run_file), preload=True, verbose=False
                    )

                    # Store original sampling rate
                    if self._original_sampling_rate == 0:
                        self._original_sampling_rate = raw.info["sfreq"]

                    # Apply preprocessing
                    raw = self._preprocess_raw(raw)

                    # Extract epochs
                    epochs_data, epochs_labels = self._extract_epochs(raw, task)

                    all_data.append(epochs_data)
                    all_labels.extend(epochs_labels)

                except Exception as e:
                    logger.error(f"Error loading {run_file}: {e}")
                    continue

        # Concatenate all data
        data = np.concatenate(all_data, axis=0)
        labels = np.array(all_labels)

        # Store metadata
        self._metadata = {
            "dataset": self.config.dataset_type.value,
            "n_subjects": len(subjects),
            "n_samples": len(data),
            "n_channels": data.shape[1],
            "sampling_rate": self.config.sampling_rate or self._original_sampling_rate,
            "channel_names": self._channel_names,
            "tasks": list(set(labels)),
        }

        logger.info(f"Loaded {len(data)} epochs from {len(subjects)} subjects")

        return data, labels

    def _load_chbmit(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load CHB-MIT Scalp EEG Database."""
        subjects = self.config.subjects
        if subjects is None:
            subjects = [f"chb{i:02d}" for i in range(1, 25)]

        all_data = []
        all_labels = []

        for subject in subjects:
            logger.info(f"Loading subject {subject}")
            subject_dir = self.dataset_dir / subject

            # Read summary file to get seizure annotations
            summary_file = subject_dir / f"{subject}-summary.txt"
            seizure_info = self._parse_chbmit_summary(summary_file)

            # Load EDF files
            for edf_file in sorted(subject_dir.glob("*.edf")):
                if edf_file.name == f"{subject}-summary.txt":
                    continue

                try:
                    raw = mne.io.read_raw_edf(
                        str(edf_file), preload=True, verbose=False
                    )

                    if self._original_sampling_rate == 0:
                        self._original_sampling_rate = raw.info["sfreq"]

                    # Apply preprocessing
                    raw = self._preprocess_raw(raw)

                    # Get seizure periods for this file
                    file_seizures = seizure_info.get(edf_file.name, [])

                    # Extract epochs with labels
                    epochs_data, epochs_labels = self._extract_seizure_epochs(
                        raw, file_seizures
                    )

                    all_data.append(epochs_data)
                    all_labels.extend(epochs_labels)

                except Exception as e:
                    logger.error(f"Error loading {edf_file}: {e}")
                    continue

        # Concatenate all data
        data = np.concatenate(all_data, axis=0)
        labels = np.array(all_labels)

        # Store metadata
        self._metadata = {
            "dataset": self.config.dataset_type.value,
            "n_subjects": len(subjects),
            "n_samples": len(data),
            "n_channels": data.shape[1],
            "sampling_rate": self.config.sampling_rate or self._original_sampling_rate,
            "channel_names": self._channel_names,
            "n_seizure": np.sum(labels == 1),
            "n_normal": np.sum(labels == 0),
        }

        logger.info(
            f"Loaded {len(data)} epochs ({np.sum(labels == 1)} seizure, "
            f"{np.sum(labels == 0)} normal)"
        )

        return data, labels

    def _load_sleep_edf(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load Sleep-EDF Database."""
        all_data = []
        all_labels = []

        # Sleep stage mapping
        sleep_stages = {
            "W": 0,  # Wake
            "N1": 1,  # NREM stage 1
            "N2": 2,  # NREM stage 2
            "N3": 3,  # NREM stage 3
            "REM": 4,  # REM sleep
        }

        # Find all PSG files (polysomnography)
        psg_files = list(self.dataset_dir.glob("*PSG.edf"))

        for psg_file in psg_files:
            # Find corresponding hypnogram file
            hypno_file = psg_file.parent / psg_file.name.replace(
                "PSG.edf", "Hypnogram.edf"
            )

            if not hypno_file.exists():
                logger.warning(f"No hypnogram found for {psg_file}")
                continue

            try:
                # Load PSG data
                raw = mne.io.read_raw_edf(str(psg_file), preload=True, verbose=False)

                if self._original_sampling_rate == 0:
                    self._original_sampling_rate = raw.info["sfreq"]

                # Load annotations from hypnogram
                annotations = mne.read_annotations(str(hypno_file))
                raw.set_annotations(annotations)

                # Apply preprocessing
                raw = self._preprocess_raw(raw)

                # Extract epochs based on sleep stages
                events, event_id = mne.events_from_annotations(
                    raw, event_id=sleep_stages
                )

                # Create epochs (30-second windows for sleep staging)
                epochs = mne.Epochs(
                    raw,
                    events,
                    event_id,
                    tmin=0,
                    tmax=30,  # 30-second epochs
                    baseline=None,
                    preload=True,
                    verbose=False,
                )

                # Get data and labels
                epochs_data = epochs.get_data()
                epochs_labels = events[:, 2]

                all_data.append(epochs_data)
                all_labels.extend(epochs_labels)

            except Exception as e:
                logger.error(f"Error loading {psg_file}: {e}")
                continue

        # Concatenate all data
        data = np.concatenate(all_data, axis=0) if all_data else np.array([])
        labels = np.array(all_labels)

        # Store metadata
        self._metadata = {
            "dataset": self.config.dataset_type.value,
            "n_files": len(psg_files),
            "n_samples": len(data),
            "n_channels": data.shape[1] if len(data) > 0 else 0,
            "sampling_rate": self.config.sampling_rate or self._original_sampling_rate,
            "channel_names": self._channel_names,
            "sleep_stages": sleep_stages,
        }

        logger.info(f"Loaded {len(data)} sleep epochs")

        return data, labels

    def _preprocess_raw(self, raw: mne.io.Raw) -> mne.io.Raw:
        """Apply preprocessing to raw data."""
        # Select channels if specified
        if self.config.channels:
            available_channels = [
                ch for ch in self.config.channels if ch in raw.ch_names
            ]
            if available_channels:
                raw.pick_channels(available_channels)

        # Store channel names
        self._channel_names = raw.ch_names

        # Set reference
        if self.config.reference == "average":
            raw.set_eeg_reference("average", projection=True)
        elif self.config.reference == "linked-ears":
            if "A1" in raw.ch_names and "A2" in raw.ch_names:
                raw.set_eeg_reference(["A1", "A2"])

        # Apply filters
        if self.config.bandpass_freq:
            raw.filter(
                l_freq=self.config.bandpass_freq[0],
                h_freq=self.config.bandpass_freq[1],
                fir_design="firwin",
            )

        # Apply notch filter
        if self.config.notch_freq:
            raw.notch_filter(
                freqs=self.config.notch_freq, filter_length="auto", phase="zero"
            )

        # Resample if needed
        if self.config.sampling_rate and raw.info["sfreq"] != self.config.sampling_rate:
            raw.resample(self.config.sampling_rate)

        return raw

    def _extract_epochs(
        self, raw: mne.io.Raw, label: str
    ) -> Tuple[np.ndarray, List[str]]:
        """Extract fixed-length epochs from continuous data."""
        # Calculate epoch parameters
        sfreq = raw.info["sfreq"]
        window_samples = int(self.config.window_size * sfreq)
        overlap_samples = int(window_samples * self.config.overlap)
        step_samples = window_samples - overlap_samples

        # Get data
        data = raw.get_data()
        n_channels, n_samples = data.shape

        # Extract epochs
        epochs = []
        labels = []

        for start in range(0, n_samples - window_samples + 1, step_samples):
            end = start + window_samples
            epoch = data[:, start:end]

            # Transpose to (samples, channels)
            epochs.append(epoch.T)
            labels.append(label)

        return np.array(epochs), labels

    def _extract_seizure_epochs(
        self, raw: mne.io.Raw, seizure_periods: List[Tuple[float, float]]
    ) -> Tuple[np.ndarray, List[int]]:
        """Extract epochs with seizure/normal labels."""
        sfreq = raw.info["sfreq"]
        duration = raw.times[-1]

        # Create events for epoching
        events_list: List[List[int]] = []
        event_id = {"normal": 0, "seizure": 1}

        # Generate events every window_size seconds
        for t in np.arange(0, duration, self.config.window_size):
            sample = int(t * sfreq)

            # Check if this time point is during a seizure
            is_seizure = False
            for start, end in seizure_periods:
                if start <= t <= end:
                    is_seizure = True
                    break

            label = 1 if is_seizure else 0
            events_list.append([sample, 0, label])

        events = np.array(events_list)

        # Create epochs
        epochs = mne.Epochs(
            raw,
            events,
            event_id,
            tmin=0,
            tmax=self.config.window_size,
            baseline=None,
            preload=True,
            verbose=False,
        )

        # Get data and labels
        epochs_data = epochs.get_data()
        labels_array = events[: len(epochs_data), 2]

        return epochs_data, labels_array.tolist()

    def _parse_chbmit_summary(
        self, summary_file: Path
    ) -> Dict[str, List[Tuple[float, float]]]:
        """Parse CHB-MIT summary file for seizure annotations."""
        seizure_info: Dict[str, List[Tuple[float, float]]] = {}

        if not summary_file.exists():
            return seizure_info

        with open(summary_file, "r") as f:
            lines = f.readlines()

        current_file = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("File Name:"):
                current_file = line.split(":")[1].strip()
                seizure_info[current_file] = []

            elif line.startswith("Number of Seizures in File:"):
                n_seizures = int(line.split(":")[1].strip())

                # Parse seizure times
                for j in range(n_seizures):
                    i += 1
                    # Look for seizure start time
                    while i < len(lines) and not lines[i].strip().startswith("Seizure"):
                        i += 1

                    if i < len(lines) - 1:
                        i += 1  # Move to start time line
                        start_line = lines[i].strip()
                        start_time = float(start_line.split(":")[1].strip().split()[0])

                        i += 1  # Move to end time line
                        end_line = lines[i].strip()
                        end_time = float(end_line.split(":")[1].strip().split()[0])

                        if current_file is not None:
                            seizure_info[current_file].append((start_time, end_time))

            i += 1

        return seizure_info

    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """Apply additional preprocessing to loaded data."""
        # Data is already preprocessed during loading
        # This method can be used for additional preprocessing if needed

        # Example: Standardization
        if self.config.preprocessing_params.get("standardize", True):
            # Standardize per channel
            mean = np.mean(data, axis=(0, 2), keepdims=True)
            std = np.std(data, axis=(0, 2), keepdims=True)
            data = (data - mean) / (std + 1e-8)

        return data

    def validate(self, data: np.ndarray) -> bool:
        """Validate data quality."""
        # Check for NaN or Inf values
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            logger.error("Data contains NaN or Inf values")
            return False

        # Check data range
        max_amplitude = np.max(np.abs(data))
        if max_amplitude > 1e6:  # Unrealistic amplitude
            logger.error(f"Data amplitude too high: {max_amplitude}")
            return False

        # Check for flat channels
        channel_vars = np.var(data, axis=(0, 2))
        flat_channels = np.where(channel_vars < 1e-10)[0]
        if len(flat_channels) > 0:
            logger.warning(f"Found {len(flat_channels)} flat channels")

        # Check sampling rate consistency
        expected_shape = (
            data.shape[0],  # n_epochs
            len(self._channel_names),  # n_channels
            int(
                self.config.window_size
                * (self.config.sampling_rate or self._original_sampling_rate)
            ),
        )

        if data.shape[2] != expected_shape[2]:
            logger.warning(
                f"Unexpected number of samples: {data.shape[2]} vs {expected_shape[2]}"
            )

        return True

    def get_channel_info(self) -> Dict[str, Any]:
        """Get detailed channel information."""
        return {
            "channel_names": self._channel_names,
            "n_channels": len(self._channel_names),
            "sampling_rate": self.config.sampling_rate or self._original_sampling_rate,
            "reference": self.config.reference,
            "filters": {
                "bandpass": self.config.bandpass_freq,
                "notch": self.config.notch_freq,
            },
        }

    def export_to_lsl(self, data: np.ndarray, labels: np.ndarray) -> None:
        """Export dataset as LSL stream for real-time testing."""
        try:
            from pylsl import StreamInfo, StreamOutlet

            # Create LSL stream info
            n_channels = data.shape[1]
            srate = self.config.sampling_rate or self._original_sampling_rate

            info = StreamInfo(
                name=f"PhysioNet-{self.config.dataset_type.value}",
                type="EEG",
                channel_count=n_channels,
                nominal_srate=srate,
                channel_format="float32",
                source_id=f"physionet_{self.config.dataset_type.value}",
            )

            # Add channel names
            channels = info.desc().append_child("channels")
            for ch_name in self._channel_names:
                ch = channels.append_child("channel")
                ch.append_child_value("label", ch_name)
                ch.append_child_value("unit", "microvolts")
                ch.append_child_value("type", "EEG")

            # Create outlet
            outlet = StreamOutlet(info)

            logger.info(f"Streaming {len(data)} epochs via LSL...")

            # Stream data
            for epoch_idx in range(len(data)):
                epoch = data[epoch_idx]  # (n_channels, n_samples)

                # Send sample by sample
                for sample_idx in range(epoch.shape[1]):
                    sample = epoch[:, sample_idx].tolist()
                    outlet.push_sample(sample)

                # Small delay between epochs
                import time

                time.sleep(0.1)

            logger.info("LSL streaming complete")

        except ImportError:
            logger.error("pylsl not installed. Install with: pip install pylsl")
            raise

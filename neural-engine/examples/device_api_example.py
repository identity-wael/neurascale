"""Example usage of the Device Management REST API."""

import requests
import json
import time
from typing import Dict, Any


class DeviceAPIClient:
    """Simple client for the Device Management API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """Initialize API client."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/devices"

    def list_devices(self) -> Dict[str, Any]:
        """List all devices."""
        response = requests.get(f"{self.api_url}/")
        return response.json()

    def add_device(self, device_id: str, device_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a new device."""
        data = {
            "device_id": device_id,
            "device_type": device_type,
            "device_config": config or {}
        }
        response = requests.post(f"{self.api_url}/", json=data)
        return response.json()

    def connect_device(self, device_id: str) -> Dict[str, Any]:
        """Connect to a device."""
        response = requests.post(f"{self.api_url}/{device_id}/connect")
        return response.json()

    def start_streaming(self, device_id: str) -> Dict[str, Any]:
        """Start streaming from a device."""
        response = requests.post(f"{self.api_url}/{device_id}/stream/start")
        return response.json()

    def stop_streaming(self, device_id: str) -> Dict[str, Any]:
        """Stop streaming from a device."""
        response = requests.post(f"{self.api_url}/{device_id}/stream/stop")
        return response.json()

    def disconnect_device(self, device_id: str) -> Dict[str, Any]:
        """Disconnect from a device."""
        response = requests.post(f"{self.api_url}/{device_id}/disconnect")
        return response.json()

    def remove_device(self, device_id: str) -> Dict[str, Any]:
        """Remove a device."""
        response = requests.delete(f"{self.api_url}/{device_id}")
        return response.json()

    def discover_devices(self, timeout: float = 10.0) -> Dict[str, Any]:
        """Discover available devices."""
        response = requests.get(f"{self.api_url}/discover", params={"timeout": timeout})
        return response.json()

    def get_health(self, device_id: str = None) -> Dict[str, Any]:
        """Get device health information."""
        params = {"device_id": device_id} if device_id else {}
        response = requests.get(f"{self.api_url}/health", params=params)
        return response.json()

    def start_health_monitoring(self) -> Dict[str, Any]:
        """Start health monitoring."""
        response = requests.post(f"{self.api_url}/health/monitoring/start")
        return response.json()

    def check_impedance(self, device_id: str) -> Dict[str, Any]:
        """Check impedance for a device."""
        response = requests.get(f"{self.api_url}/{device_id}/impedance")
        return response.json()

    def get_signal_quality(self, device_id: str) -> Dict[str, Any]:
        """Get signal quality for a device."""
        response = requests.get(f"{self.api_url}/{device_id}/signal-quality")
        return response.json()


def main():
    """Example usage of the Device API."""
    # Create API client
    client = DeviceAPIClient()

    print("=== Device Management API Example ===\n")

    # 1. List current devices
    print("1. Listing current devices...")
    devices = client.list_devices()
    print(f"   Found {len(devices)} devices")

    # 2. Add a synthetic device
    print("\n2. Adding synthetic EEG device...")
    result = client.add_device(
        device_id="synthetic_eeg_001",
        device_type="synthetic",
        config={
            "n_channels": 8,
            "sampling_rate": 256.0,
            "signal_type": "EEG"
        }
    )
    print(f"   Device added: {result['device_name']} (state: {result['state']})")

    # 3. Connect to device
    print("\n3. Connecting to device...")
    result = client.connect_device("synthetic_eeg_001")
    print(f"   Connected: {result['connected']}")

    # 4. Start health monitoring
    print("\n4. Starting health monitoring...")
    result = client.start_health_monitoring()
    print(f"   Monitoring: {result['monitoring']}")

    # 5. Start streaming
    print("\n5. Starting data streaming...")
    result = client.start_streaming("synthetic_eeg_001")
    print(f"   Streaming: {result['streaming']}")
    print(f"   Session ID: {result['session_id']}")

    # 6. Wait a bit and check health
    print("\n6. Waiting 3 seconds and checking health...")
    time.sleep(3)
    health = client.get_health("synthetic_eeg_001")
    print(f"   Health status: {health['status']}")
    if health.get('metrics'):
        metrics = health['metrics']
        print(f"   Data rate: {metrics['data']['data_rate_hz']:.1f} Hz")
        print(f"   Connection uptime: {metrics['connection']['uptime_seconds']:.1f} seconds")

    # 7. Try to get signal quality
    print("\n7. Getting signal quality...")
    try:
        quality = client.get_signal_quality("synthetic_eeg_001")
        if 'signal_quality' in quality:
            for ch_id, ch_quality in quality['signal_quality'].items():
                print(f"   Channel {ch_id}: {ch_quality['quality_level']} (SNR: {ch_quality['snr_db']:.1f} dB)")
    except Exception as e:
        print(f"   Signal quality not available: {e}")

    # 8. Stop streaming
    print("\n8. Stopping streaming...")
    result = client.stop_streaming("synthetic_eeg_001")
    print(f"   Streaming: {result['streaming']}")

    # 9. Disconnect device
    print("\n9. Disconnecting device...")
    result = client.disconnect_device("synthetic_eeg_001")
    print(f"   Connected: {result['connected']}")

    # 10. Remove device
    print("\n10. Removing device...")
    result = client.remove_device("synthetic_eeg_001")
    print(f"    {result['message']}")

    # 11. Discover devices
    print("\n11. Discovering available devices...")
    discovered = client.discover_devices(timeout=5.0)
    print(f"    Found {len(discovered)} devices:")
    for device in discovered:
        print(f"    - {device['name']} ({device['device_type']}) on {device['protocol']}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()

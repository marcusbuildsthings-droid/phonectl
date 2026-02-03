"""Device interaction layer wrapping pymobiledevice3."""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class DeviceError(Exception):
    """Base exception for device errors."""
    pass


class NoDeviceError(DeviceError):
    """No device connected."""
    pass


class Device:
    """Wrapper for iOS device operations via pymobiledevice3."""
    
    def __init__(self, udid: Optional[str] = None):
        self.udid = udid
        self._check_pymobiledevice3()
    
    def _check_pymobiledevice3(self):
        """Verify pymobiledevice3 is installed."""
        try:
            subprocess.run(
                ["pymobiledevice3", "--version"],
                capture_output=True,
                check=True
            )
        except FileNotFoundError:
            raise DeviceError(
                "pymobiledevice3 not found. Install with: pip install pymobiledevice3"
            )
    
    def _run(self, *args, **kwargs) -> subprocess.CompletedProcess:
        """Run pymobiledevice3 command."""
        cmd = ["pymobiledevice3"] + list(args)
        if self.udid:
            cmd.extend(["--udid", self.udid])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            **kwargs
        )
        return result
    
    def _run_json(self, *args) -> Any:
        """Run command and parse JSON output."""
        result = self._run(*args)
        if result.returncode != 0:
            raise DeviceError(result.stderr or result.stdout)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout
    
    @staticmethod
    def list_devices() -> List[Dict[str, Any]]:
        """List connected iOS devices."""
        result = subprocess.run(
            ["pymobiledevice3", "usbmux", "list", "--no-color"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        # Parse output - each line is a device
        devices = []
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('─'):
                # Try to extract device info
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({
                        "udid": parts[0] if len(parts[0]) > 20 else None,
                        "name": " ".join(parts[1:]) if len(parts) > 1 else "Unknown",
                        "raw": line
                    })
        
        return devices
    
    @staticmethod
    def get_first_device() -> Optional[str]:
        """Get UDID of first connected device."""
        devices = Device.list_devices()
        if devices and devices[0].get("udid"):
            return devices[0]["udid"]
        return None
    
    def screenshot(self, output_path: str = "screenshot.png") -> str:
        """Take a screenshot and save to file."""
        output = Path(output_path).resolve()
        result = self._run("developer", "dvt", "screenshot", str(output))
        
        if result.returncode != 0:
            raise DeviceError(f"Screenshot failed: {result.stderr}")
        
        return str(output)
    
    def list_apps(self, user_only: bool = True) -> List[Dict[str, Any]]:
        """List installed applications."""
        args = ["apps", "list"]
        if user_only:
            args.append("--user")
        
        result = self._run(*args)
        if result.returncode != 0:
            raise DeviceError(f"Failed to list apps: {result.stderr}")
        
        # Parse app list
        apps = []
        for line in result.stdout.strip().split('\n'):
            if line and '.' in line:  # Bundle IDs contain dots
                parts = line.strip().split(maxsplit=1)
                if parts:
                    apps.append({
                        "bundle_id": parts[0],
                        "name": parts[1] if len(parts) > 1 else parts[0]
                    })
        
        return apps
    
    def launch_app(self, bundle_id: str) -> bool:
        """Launch an application by bundle ID."""
        result = self._run("developer", "dvt", "launch", bundle_id)
        return result.returncode == 0
    
    def kill_app(self, bundle_id: str) -> bool:
        """Kill a running application."""
        result = self._run("developer", "dvt", "kill", bundle_id)
        return result.returncode == 0
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        result = self._run("lockdown", "info")
        if result.returncode != 0:
            raise DeviceError(f"Failed to get device info: {result.stderr}")
        
        # Parse key-value pairs
        info = {}
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                info[key.strip()] = value.strip()
        
        return info
    
    def list_files(self, path: str = "/", service: str = "afc") -> List[str]:
        """List files on device."""
        result = self._run("afc", "ls", path)
        if result.returncode != 0:
            raise DeviceError(f"Failed to list files: {result.stderr}")
        
        return [f for f in result.stdout.strip().split('\n') if f]
    
    def pull_file(self, remote_path: str, local_path: str) -> str:
        """Pull a file from device."""
        output = Path(local_path).resolve()
        result = self._run("afc", "pull", remote_path, str(output))
        
        if result.returncode != 0:
            raise DeviceError(f"Failed to pull file: {result.stderr}")
        
        return str(output)
    
    def push_file(self, local_path: str, remote_path: str) -> bool:
        """Push a file to device."""
        local = Path(local_path).resolve()
        if not local.exists():
            raise DeviceError(f"Local file not found: {local}")
        
        result = self._run("afc", "push", str(local), remote_path)
        return result.returncode == 0
    
    def start_tunnel(self) -> bool:
        """Start tunneld for iOS 17+ devices (requires sudo)."""
        # Note: This typically needs to run as a daemon
        result = subprocess.run(
            ["sudo", "pymobiledevice3", "remote", "tunneld"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

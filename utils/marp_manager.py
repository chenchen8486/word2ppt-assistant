import os
import sys
import zipfile
import requests
import subprocess
import shutil
from pathlib import Path

class MarpManager:
    MARP_VERSION = "latest"  # Or specific version like "3.4.0"
    GITHUB_REPO = "marp-team/marp-cli"
    
    def __init__(self, install_dir="bin"):
        self.install_dir = Path(install_dir)
        self.executable_name = "marp.exe" if sys.platform == "win32" else "marp"
        self.executable_path = self.install_dir / self.executable_name
        
    def ensure_marp_cli(self):
        """
        Check if Marp CLI is installed. If not, download and install it.
        Returns the path to the executable.
        """
        if self.executable_path.exists():
            print(f"Marp CLI found at: {self.executable_path}")
            return str(self.executable_path)
            
        print("Marp CLI not found. Starting download...")
        self._download_and_install()
        return str(self.executable_path)
    
    def _download_and_install(self):
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine download URL
        # For simplicity, we'll try to get the latest release from GitHub API
        try:
            api_url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            release_data = response.json()
            
            # Find the correct asset for Windows
            asset_url = None
            for asset in release_data.get("assets", []):
                name = asset["name"].lower()
                if "win" in name and name.endswith(".zip"):
                    asset_url = asset["browser_download_url"]
                    break
            
            if not asset_url:
                raise Exception("Could not find a suitable Marp CLI release for Windows.")
                
            # Download
            print(f"Downloading Marp CLI from {asset_url}...")
            zip_path = self.install_dir / "marp.zip"
            with requests.get(asset_url, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
            # Extract
            print("Extracting Marp CLI...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
                
            # Cleanup
            os.remove(zip_path)
            
            # Verify extraction (Marp CLI zip usually contains the exe at root or in a folder)
            # Sometimes it extracts into a folder. Let's check.
            # If marp.exe is not in install_dir, look for it in subdirectories
            if not self.executable_path.exists():
                found = list(self.install_dir.rglob(self.executable_name))
                if found:
                    # Move it to install_dir
                    shutil.move(str(found[0]), str(self.executable_path))
                    # Optional: clean up empty dirs?
                else:
                    raise Exception("marp.exe not found in downloaded archive.")
            
            print("Marp CLI installed successfully.")
            
        except Exception as e:
            print(f"Error installing Marp CLI: {e}")
            raise

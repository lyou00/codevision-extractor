import urllib.request
import json
import os
import subprocess

req = urllib.request.Request(
    'https://api.github.com/repos/UB-Mannheim/tesseract/releases/latest',
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        exe_asset = None
        for asset in data.get('assets', []):
            if asset['name'].endswith('.exe'):
                exe_asset = asset['browser_download_url']
                break
        print("Found asset URL:", exe_asset)
        if exe_asset:
            dest = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "tesseract_setup.exe")
            print("Downloading...")
            req_dl = urllib.request.Request(exe_asset, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_dl) as r_in, open(dest, 'wb') as f_out:
                f_out.write(r_in.read())
            print("Downloaded. Installing Tesseract OCR silently...")
            subprocess.run([dest, "/S"], check=True)
            print("Installed successfully!")
except Exception as e:
    print("Error:", e)

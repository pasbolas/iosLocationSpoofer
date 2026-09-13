# iPhone Location Simulation - Windows 11 Setup Guide

This guide covers everything required to set up and run the iPhone Location Simulator on Windows 11 using `pymobiledevice3`.

> [!NOTE]
> **Device & iOS Compatibility**:
> Fully compatible with **iPhone 12, iPhone 12 mini, iPhone 12 Pro, and iPhone 12 Pro Max** across all supported iOS versions:
> - **iOS 17 & iOS 18**: Uses Apple's modern CoreDevice RSD userspace tunnel and DVT `LocationSimulation`.
> - **iOS 14, 15, & 16**: Uses the classic lockdown developer service `DtSimulateLocation`.
> On iOS 16, 17, and 18, Developer Mode must be enabled on the iPhone.

---

## 1. Prerequisites on Windows 11

### A. Apple Mobile Device Support (USBMUXD)
On Windows, communication with an iOS device over USB requires Apple's `usbmuxd` daemon (**Apple Mobile Device Service**), which listens locally on TCP port `127.0.0.1:27015`.

**Installation Options:**
* **Option 1 (Recommended via winget):**
  Open PowerShell as Administrator and run:
  ```powershell
  winget install Apple.iTunes --accept-source-agreements --accept-package-agreements
  ```
* **Option 2 (Microsoft Store):**
  Install **iTunes** or **Apple Devices** directly from the Microsoft Store:
  - [iTunes on Microsoft Store](https://apps.microsoft.com/detail/9pb2mz1zmb1s)

* **Verify the Service is Running:**
  After installation, verify that the Apple Mobile Device Service is active:
  ```powershell
  Get-Service -Name "Apple Mobile Device Service"
  ```
  Status should display as `Running`. If not, start it:
  ```powershell
  Start-Service -Name "Apple Mobile Device Service"
  ```

---

### B. Python 3.11 or 3.12
`pymobiledevice3` requires Python 3.9+. We recommend **Python 3.12**.

* **Install via winget:**
  ```powershell
  winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
  ```
* **Verify Python is in PATH:**
  Open a new PowerShell terminal and check:
  ```powershell
  python --version
  pip --version
  ```
  *(If `python` is not recognized, ensure `C:\Users\<User>\AppData\Local\Programs\Python\Python312` and its `Scripts` directory are added to your user `PATH` environment variable).*

---

## 2. iPhone Configuration

Before simulating locations, your iPhone must meet three preconditions:

### 1. Trust This Computer
1. Connect your iPhone to your Windows PC using an official or MFi-certified USB cable (direct USB port preferred over unpowered hubs).
2. Unlock your iPhone screen.
3. When the alert **"Trust This Computer?"** appears on your iPhone, tap **Trust**.
4. Enter your iPhone passcode to confirm the pairing record.

### 2. Enable Developer Mode (iOS 16 & iOS 17+)
Apple requires Developer Mode to run DVT instrumentation and location simulation services:
1. Open **Settings** on your iPhone.
2. Scroll down and select **Privacy & Security**.
3. Scroll to the very bottom to find **Developer Mode** (under the "Security" heading).
4. Toggle **Developer Mode** to **ON**.
5. An alert will ask you to restart your device. Tap **Restart**.
6. After your iPhone reboots, unlock your device. A system dialog **"Turn on Developer Mode?"** will appear.
7. Tap **Turn On** and enter your passcode.

> [!TIP]
> **Can't see the "Developer Mode" toggle in Settings?**
> Apple hides this toggle by default until a developer handshake is triggered over USB.
> To make it appear immediately:
> 1. Double-click [reveal_dev_mode.bat](file:///c:/Users/Akshat%20Pasbola/Desktop/spoof/reveal_dev_mode.bat) (or in the web app, click **⚡ Reveal Toggle on iPhone**).
> 2. Force close and re-open the **Settings** app on your iPhone.
> 3. Go to **Privacy & Security** > scroll to the bottom > **Developer Mode** is now visible!

---

## 3. Project Setup & Running the Proof of Concept

### Step 1: Create a Virtual Environment
From the project root (`c:\Users\Akshat Pasbola\Desktop\spoof`):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script activation, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`)*

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Phase 1 Proof of Concept
Ensure your iPhone is connected via USB, unlocked, and has Developer Mode enabled, then run:
```powershell
python poc.py
```

### What Happens:
1. The script checks for the `usbmuxd` listener on `127.0.0.1:27015`.
2. It detects your connected iPhone and outputs:
   - Device Name (e.g. *Akshat's iPhone*)
   - Model (e.g. *iPhone 15 Pro*)
   - iOS Version (e.g. *17.5.1*)
   - UDID
   - Pairing Status
   - Developer Mode Status
3. It creates the required connection:
   - For **iOS 17+**: Establishes a no-root in-process RSD tunnel (`PreferredRsdTunnel`), mounts the DVT provider, and creates the `LocationSimulation` service.
   - For **iOS < 17**: Establishes a lockdown connection and uses `DtSimulateLocation`.
4. It sets the device's GPS to **Dublin, Ireland** (`53.3498, -6.2603`).
5. Terminal shows:
   ```
   [SUCCESS] SIMULATED LOCATION ACTIVE: Dublin, Ireland (53.3498, -6.2603)
   Press Enter to stop simulation and restore real location...
   ```
6. Open **Apple Maps**, **Google Maps**, or **Find My** on your iPhone — your blue location dot will be in Dublin!
7. Press **Enter** (or `Ctrl+C`) in your terminal to cleanly terminate the simulation and restore your real GPS location.

---

## 4. Troubleshooting & Error Codes

| Error Code | Cause | Solution |
| :--- | :--- | :--- |
| `USBMUXD_NOT_FOUND` / `ConnectionFailedToUsbmuxdError` | Apple Mobile Device Service is not running on Windows port 27015. | Install iTunes or Apple Devices, and run `Start-Service "Apple Mobile Device Service"`. |
| `DEVICE_NOT_FOUND` / `NoDeviceConnectedError` | No iPhone detected over USB. | Re-plug the USB cable, ensure the cable is data-capable, and avoid loose adapters. |
| `DEVICE_LOCKED` / `PasswordRequiredError` | iPhone screen is locked with passcode. | Unlock your iPhone and keep the screen active. |
| `PAIRING_REQUIRED` / `NotTrustedError` | Computer is not trusted by the iPhone. | Unlock iPhone, tap "Trust This Computer" on the popup, and enter your passcode. |
| `DEVELOPER_MODE_DISABLED` | Developer Mode is off on iOS 16+. | Go to *Settings > Privacy & Security > Developer Mode*, turn ON, and restart phone. |
| `TUNNEL_FAILED` | In-process RSD tunnel failed (iOS 17+). | Ensure phone is unlocked, trusted, and has Developer Mode enabled. Re-run `poc.py`. |
| `LOCATION_SIMULATION_FAILED` | DVT LocationSimulation service failed to engage. | Reboot iPhone, re-pair USB connection, and re-run. |

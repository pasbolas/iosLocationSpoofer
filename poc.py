#!/usr/bin/env python3
"""
Proof of Concept: Windows-first local iPhone location simulator using pymobiledevice3.
Sets device location to Dublin (53.3498, -6.2603), waits for Enter, and clears on exit.
"""

import asyncio
import socket
import sys
from typing import Optional, Dict, Any

# Well-known iPhone model mapping for friendly display
DEVICE_MODEL_NAMES: Dict[str, str] = {
    # iPhone X / XR / XS series
    "iPhone10,3": "iPhone X",
    "iPhone10,6": "iPhone X",
    "iPhone11,2": "iPhone XS",
    "iPhone11,4": "iPhone XS Max",
    "iPhone11,6": "iPhone XS Max",
    "iPhone11,8": "iPhone XR",
    # iPhone 11 series
    "iPhone12,1": "iPhone 11",
    "iPhone12,3": "iPhone 11 Pro",
    "iPhone12,5": "iPhone 11 Pro Max",
    # iPhone SE (2nd Gen)
    "iPhone12,8": "iPhone SE (2nd generation)",
    # iPhone 12 series
    "iPhone13,1": "iPhone 12 mini",
    "iPhone13,2": "iPhone 12",
    "iPhone13,3": "iPhone 12 Pro",
    "iPhone13,4": "iPhone 12 Pro Max",
    # iPhone 13 series
    "iPhone14,2": "iPhone 13 Pro",
    "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,4": "iPhone 13 mini",
    "iPhone14,5": "iPhone 13",
    # iPhone SE (3rd Gen)
    "iPhone14,6": "iPhone SE (3rd generation)",
    # iPhone 14 series
    "iPhone14,7": "iPhone 14",
    "iPhone14,8": "iPhone 14 Plus",
    "iPhone15,2": "iPhone 14 Pro",
    "iPhone15,3": "iPhone 14 Pro Max",
    # iPhone 15 series
    "iPhone15,4": "iPhone 15",
    "iPhone15,5": "iPhone 15 Plus",
    "iPhone16,1": "iPhone 15 Pro",
    "iPhone16,2": "iPhone 15 Pro Max",
    # iPhone 16 series
    "iPhone17,1": "iPhone 16 Pro",
    "iPhone17,2": "iPhone 16 Pro Max",
    "iPhone17,3": "iPhone 16",
    "iPhone17,4": "iPhone 16 Plus",
}

# Dublin, Ireland coordinates specified in requirements
TARGET_LATITUDE = 53.3498
TARGET_LONGITUDE = -6.2603
TARGET_NAME = "Dublin, Ireland"


def check_usbmuxd_running(host: str = "127.0.0.1", port: int = 27015) -> bool:
    """Check if Apple Mobile Device Service (usbmuxd) is listening on localhost."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False


def get_model_name(product_type: str, marketing_name: Optional[str] = None) -> str:
    """Resolve marketing name or fallback to dictionary / product type."""
    if marketing_name:
        return marketing_name
    return DEVICE_MODEL_NAMES.get(product_type, product_type or "Unknown iPhone")


async def main() -> None:
    print("=" * 60)
    print("  iPhone Location Simulator - Phase 1 Windows PoC")
    print("=" * 60)
    print()

    # 1. Check if Apple Mobile Device Service (usbmuxd) is available
    print("[1/5] Checking Apple Mobile Device Service (usbmuxd:27015)...")
    if not check_usbmuxd_running():
        print()
        print("  [ERROR] USBMUXD_NOT_FOUND")
        print("  Cannot connect to Apple Mobile Device Service on 127.0.0.1:27015.")
        print("  Please install iTunes or Apple Devices for Windows and ensure")
        print("  the 'Apple Mobile Device Service' is running.")
        print("  See SETUP.md for installation instructions.")
        print()
        sys.exit(1)
    print("  -> Apple Mobile Device Service is running.")

    # Lazy import pymobiledevice3 modules
    try:
        from pymobiledevice3 import usbmux
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.exceptions import (
            NoDeviceConnectedError,
            ConnectionFailedToUsbmuxdError,
            PasswordRequiredError,
            PasscodeRequiredError,
            NotTrustedError,
            NotPairedError,
            PairingDialogResponsePendingError,
            UserDeniedPairingError,
            DeveloperModeIsNotEnabledError,
            PyMobileDevice3Exception,
        )
    except ImportError:
        print()
        print("  [ERROR] pymobiledevice3 is not installed.")
        print("  Please run: pip install -r requirements.txt")
        print()
        sys.exit(1)

    # 2. Detect connected iPhones
    print("[2/5] Detecting connected iPhones over USB...")
    try:
        devices = await usbmux.list_devices()
        usb_devices = [d for d in devices if d.is_usb]
    except ConnectionFailedToUsbmuxdError:
        print("  [ERROR] Connection failed to usbmuxd service.")
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Failed to query USB devices: {e}")
        sys.exit(1)

    if not usb_devices:
        print()
        print("  [ERROR] DEVICE_NOT_FOUND")
        print("  No iPhone detected over USB.")
        print("  Please connect your iPhone via USB, ensure it is unlocked, and try again.")
        print()
        sys.exit(1)

    print(f"  -> Found {len(usb_devices)} connected USB device(s).")
    selected_device = usb_devices[0]
    if len(usb_devices) > 1:
        print("\nMultiple devices connected:")
        for idx, dev in enumerate(usb_devices):
            print(f"  [{idx + 1}] Serial/UDID: {dev.serial}")
        choice = input("Select device number [default 1]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(usb_devices):
            selected_device = usb_devices[int(choice) - 1]

    # 3. Retrieve device details and check preconditions
    print(f"[3/5] Querying device information for UDID: {selected_device.serial}...")
    try:
        lockdown = await create_using_usbmux(serial=selected_device.serial)
    except (PasswordRequiredError, PasscodeRequiredError):
        print()
        print("  [ERROR] DEVICE_LOCKED")
        print("  The iPhone screen is locked. Unlock your iPhone and enter passcode.")
        print()
        sys.exit(1)
    except (NotTrustedError, NotPairedError, PairingDialogResponsePendingError, UserDeniedPairingError):
        print()
        print("  [ERROR] PAIRING_REQUIRED")
        print("  The computer is not trusted. Unlock your iPhone, tap 'Trust This Computer',")
        print("  enter your passcode, and run this script again.")
        print()
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Failed to connect to device lockdown: {e}")
        sys.exit(1)

    # Query lockdown properties
    device_name = lockdown.all_values.get("DeviceName") or lockdown.device_name or "Unknown Device"
    product_type = lockdown.product_type or lockdown.all_values.get("ProductType") or "Unknown"
    marketing_name = lockdown.all_values.get("MarketingName")
    model_name = get_model_name(product_type, marketing_name)
    ios_version = lockdown.product_version or "Unknown"
    udid = lockdown.udid or selected_device.serial
    is_paired = lockdown.paired

    # Developer mode check
    dev_mode_status = "Unknown"
    is_dev_mode_ready = False
    try:
        is_dev_mode_ready = await lockdown.get_developer_mode_status()
        dev_mode_status = "Ready (Enabled)" if is_dev_mode_ready else "Disabled"
    except Exception:
        # On iOS < 16, Developer Mode toggle does not exist; developer services are ready once mounted
        dev_mode_status = "Not Applicable (iOS < 16)"
        is_dev_mode_ready = True

    print("\n" + "-" * 40)
    print(f"  Device Name:          {device_name}")
    print(f"  Model:                {model_name} ({product_type})")
    print(f"  iOS Version:          {ios_version}")
    print(f"  UDID:                 {udid}")
    print(f"  Pairing Status:       {'Paired' if is_paired else 'Unpaired'}")
    print(f"  Developer Mode:       {dev_mode_status}")
    print("-" * 40 + "\n")

    # Pre-condition check for Developer Mode
    if dev_mode_status == "Disabled":
        print("  [WARNING] DEVELOPER_MODE_DISABLED")
        print("  Apple requires Developer Mode to be enabled for location simulation on iOS 16+.")
        print("  Please enable it on your device:")
        print("    1. Go to Settings > Privacy & Security")
        print("    2. Scroll to bottom and tap 'Developer Mode'")
        print("    3. Toggle ON and restart the device")
        print("    4. Unlock after restart and tap 'Turn On'")
        print()
        sys.exit(1)

    # 4. Establish location simulation connection based on iOS version
    try:
        major_version = int(ios_version.split(".")[0])
    except (ValueError, IndexError):
        major_version = 17

    print(f"[4/5] Establishing location simulation connection (iOS {ios_version})...")

    if major_version >= 17:
        # iOS 17+ CoreDevice / RemoteXPC RSD tunnel mechanism
        from pymobiledevice3.remote.rsd_tunnel import PreferredRsdTunnel
        from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
        from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

        print("  -> Initializing PreferredRsdTunnel (userspace tunnel)...")
        try:
            async with PreferredRsdTunnel(serial=udid) as rsd:
                print("  -> Mounting DVT Provider...")
                async with DvtProvider(rsd) as dvt:
                    async with LocationSimulation(dvt) as loc_sim:
                        print(f"  -> Setting simulated location to {TARGET_NAME} ({TARGET_LATITUDE}, {TARGET_LONGITUDE})...")
                        await loc_sim.set(TARGET_LATITUDE, TARGET_LONGITUDE)
                        print()
                        print("*" * 60)
                        print(f"  [SUCCESS] SIMULATED LOCATION ACTIVE")
                        print(f"  Coordinates: Latitude {TARGET_LATITUDE}, Longitude {TARGET_LONGITUDE}")
                        print(f"  Location:    {TARGET_NAME}")
                        print("*" * 60)
                        print()
                        print("Open Apple Maps or Google Maps on your iPhone to verify.")
                        print()
                        try:
                            await asyncio.to_thread(input, "Press [Enter] to STOP simulation and restore real location: ")
                        except (KeyboardInterrupt, asyncio.CancelledError):
                            print("\nInterrupted.")
                        finally:
                            print("\n[5/5] Stopping location simulation and restoring real GPS...")
                            try:
                                await loc_sim.clear()
                                print("  -> [SUCCESS] Real location restored.")
                            except Exception as e:
                                print(f"  -> [WARNING] Failed to clear location on exit: {e}")
        except DeveloperModeIsNotEnabledError:
            print("\n  [ERROR] DEVELOPER_MODE_DISABLED: Location simulation rejected by device.")
            sys.exit(1)
        except Exception as e:
            print(f"\n  [ERROR] TUNNEL_FAILED / LOCATION_SIMULATION_FAILED: {e}")
            sys.exit(1)

    else:
        # iOS < 17 lockdown service mechanism
        from pymobiledevice3.services.simulate_location import DtSimulateLocation

        print("  -> Initializing DtSimulateLocation over lockdown...")
        try:
            loc_sim = DtSimulateLocation(lockdown)
            print(f"  -> Setting simulated location to {TARGET_NAME} ({TARGET_LATITUDE}, {TARGET_LONGITUDE})...")
            await loc_sim.set(TARGET_LATITUDE, TARGET_LONGITUDE)
            print()
            print("*" * 60)
            print(f"  [SUCCESS] SIMULATED LOCATION ACTIVE")
            print(f"  Coordinates: Latitude {TARGET_LATITUDE}, Longitude {TARGET_LONGITUDE}")
            print(f"  Location:    {TARGET_NAME}")
            print("*" * 60)
            print()
            print("Open Apple Maps or Google Maps on your iPhone to verify.")
            print()
            try:
                await asyncio.to_thread(input, "Press [Enter] to STOP simulation and restore real location: ")
            except (KeyboardInterrupt, asyncio.CancelledError):
                print("\nInterrupted.")
            finally:
                print("\n[5/5] Stopping location simulation and restoring real GPS...")
                try:
                    await loc_sim.clear()
                    print("  -> [SUCCESS] Real location restored.")
                except Exception as e:
                    print(f"  -> [WARNING] Failed to clear location on exit: {e}")
        except Exception as e:
            print(f"\n  [ERROR] LOCATION_SIMULATION_FAILED: {e}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting.")

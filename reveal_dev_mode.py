#!/usr/bin/env python3
"""
Helper script to force iOS to reveal the 'Developer Mode' menu under:
Settings > Privacy & Security > Developer Mode
"""

import asyncio
import sys


async def main():
    print("=" * 60)
    print("  iOS Developer Mode Reveal Helper")
    print("=" * 60)
    print()

    try:
        from pymobiledevice3 import usbmux
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.amfi import AmfiService
        from pymobiledevice3.exceptions import (
            NoDeviceConnectedError,
            ConnectionFailedToUsbmuxdError,
            PasswordRequiredError,
            NotTrustedError,
        )
    except ImportError:
        print("[ERROR] pymobiledevice3 is not installed in current environment.")
        print("Please run using .venv\\Scripts\\python.exe reveal_dev_mode.py")
        sys.exit(1)

    print("[1/3] Detecting iPhone via USB...")
    try:
        devices = await usbmux.list_devices()
        usb_devices = [d for d in devices if d.is_usb]
    except ConnectionFailedToUsbmuxdError:
        print("[ERROR] Cannot connect to Apple Mobile Device Service (usbmuxd on 127.0.0.1:27015).")
        print("Please make sure iTunes or Apple Devices is running.")
        sys.exit(1)

    if not usb_devices:
        print("[ERROR] No iPhone detected. Connect your iPhone via USB, unlock it, and retry.")
        sys.exit(1)

    selected = usb_devices[0]
    print(f"  -> Found device: {selected.serial}")

    print("[2/3] Connecting to device lockdown...")
    try:
        lockdown = await create_using_usbmux(serial=selected.serial)
    except PasswordRequiredError:
        print("[ERROR] iPhone screen is locked. Please unlock your iPhone with your passcode.")
        sys.exit(1)
    except NotTrustedError:
        print("[ERROR] Pairing untrusted. Tap 'Trust This Computer' on your iPhone.")
        sys.exit(1)

    print("[3/3] Sending AMFI command to reveal Developer Mode toggle in Settings...")
    try:
        amfi = AmfiService(lockdown)
        await amfi.reveal_developer_mode_option_in_ui()
        print()
        print("*" * 60)
        print("  [SUCCESS] Developer Mode menu has been revealed on your iPhone!")
        print("*" * 60)
        print()
        print("Now follow these simple steps on your iPhone:")
        print("  1. Open the 'Settings' app on your iPhone.")
        print("     (If Settings was already open, force close it and re-open it).")
        print("  2. Scroll down and tap 'Privacy & Security'.")
        print("  3. Scroll all the way to the bottom (under the 'Security' section).")
        print("  4. You will now see 'Developer Mode'!")
        print("  5. Tap 'Developer Mode', toggle it ON, and tap 'Restart'.")
        print("  6. After the phone restarts, unlock it and tap 'Turn On'.")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to reveal Developer Mode: {e}")
        print("Ensure your iPhone is unlocked, trusted, and reconnected.")


if __name__ == "__main__":
    asyncio.run(main())

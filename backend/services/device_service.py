import socket
import logging
from typing import Optional, Dict, List

from backend.models.schemas import Device

logger = logging.getLogger(__name__)

# Complete mapping for iPhone models
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


def check_usbmuxd_running(host: str = "127.0.0.1", port: int = 27015) -> bool:
    """Check if Apple Mobile Device Service (usbmuxd) is listening locally on port 27015."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False


def get_model_name(product_type: str, marketing_name: Optional[str] = None) -> str:
    """Resolve marketing name or fallback to model dictionary / product type."""
    if marketing_name:
        return marketing_name
    return DEVICE_MODEL_NAMES.get(product_type, product_type or "Unknown iPhone")


class DeviceService:
    """Handles USB discovery and device information querying using pymobiledevice3."""

    @staticmethod
    async def list_devices() -> List[Device]:
        if not check_usbmuxd_running():
            logger.warning("usbmuxd port 27015 is not reachable")
            return []

        try:
            from pymobiledevice3 import usbmux
            from pymobiledevice3.lockdown import create_using_usbmux
            from pymobiledevice3.exceptions import (
                PasswordRequiredError,
                PasscodeRequiredError,
                NotTrustedError,
                NotPairedError,
                PairingDialogResponsePendingError,
                UserDeniedPairingError,
            )
        except ImportError as e:
            logger.error(f"Failed to import pymobiledevice3: {e}")
            return []

        try:
            mux_devices = await usbmux.list_devices()
        except Exception as e:
            logger.error(f"Error listing usbmux devices: {e}")
            return []

        usb_devices = [d for d in mux_devices if d.is_usb]
        results: List[Device] = []

        for mux_dev in usb_devices:
            udid = mux_dev.serial
            device_name = "iPhone"
            product_type = "Unknown"
            model_name = "iPhone"
            ios_version = "Unknown"
            is_paired = False
            dev_mode_str = "Unknown"

            try:
                lockdown = await create_using_usbmux(serial=udid)
                device_name = lockdown.all_values.get("DeviceName") or lockdown.device_name or "iPhone"
                product_type = lockdown.product_type or lockdown.all_values.get("ProductType") or "Unknown"
                marketing = lockdown.all_values.get("MarketingName")
                model_name = get_model_name(product_type, marketing)
                ios_version = lockdown.product_version or "Unknown"
                is_paired = lockdown.paired

                try:
                    dev_mode_ready = await lockdown.get_developer_mode_status()
                    dev_mode_str = "Ready" if dev_mode_ready else "Disabled"
                except Exception:
                    # On iOS < 16, Developer Mode toggle does not exist
                    dev_mode_str = "Not Applicable (iOS < 16)"

            except (PasswordRequiredError, PasscodeRequiredError):
                device_name = "iPhone (Passcode Locked)"
                dev_mode_str = "Locked"
            except (NotTrustedError, NotPairedError, PairingDialogResponsePendingError, UserDeniedPairingError):
                device_name = "iPhone (Untrusted / Pairing Required)"
                dev_mode_str = "Pairing Required"
            except Exception as e:
                logger.debug(f"Failed to fetch detailed lockdown info for {udid}: {e}")

            results.append(
                Device(
                    udid=udid,
                    name=device_name,
                    model=model_name,
                    product_type=product_type,
                    ios_version=ios_version,
                    connected=True,
                    paired=is_paired,
                    developer_mode=dev_mode_str,
                )
            )

        return results

    @staticmethod
    async def reveal_developer_mode(udid: Optional[str] = None) -> bool:
        """Tell iOS AMFI to show the Developer Mode toggle in Settings > Privacy & Security."""
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.amfi import AmfiService

        lockdown = await create_using_usbmux(serial=udid)
        amfi = AmfiService(lockdown)
        await amfi.reveal_developer_mode_option_in_ui()
        return True

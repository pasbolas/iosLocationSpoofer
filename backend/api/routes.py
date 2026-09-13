import logging
import urllib.parse
from typing import List, Optional
import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import (
    Device,
    SetLocationRequest,
    LocationResponse,
    StatusResponse,
    GeocodeResult,
)
from backend.services.device_service import DeviceService, check_usbmuxd_running
from backend.services.location_service import location_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Return device connectivity and simulation status."""
    usbmuxd_up = check_usbmuxd_running()
    devices = await DeviceService.list_devices() if usbmuxd_up else []
    sim_status = location_service.get_status()

    active_device = None
    if sim_status.active and sim_status.udid:
        for d in devices:
            if d.udid == sim_status.udid:
                active_device = d
                break
    elif devices:
        active_device = devices[0]

    return StatusResponse(
        usbmuxd_running=usbmuxd_up,
        devices=devices,
        active_device=active_device,
        simulation=sim_status,
    )


@router.get("/devices", response_model=List[Device])
async def get_devices():
    """Return all connected iOS devices detected via USB."""
    if not check_usbmuxd_running():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "USBMUXD_NOT_FOUND",
                "message": "Apple Mobile Device Service is not reachable on 127.0.0.1:27015.",
                "solution": "Please ensure iTunes or Apple Devices is installed and running.",
            },
        )
    return await DeviceService.list_devices()


@router.post("/device/reveal-dev-mode")
async def reveal_developer_mode(udid: Optional[str] = None):
    """Force iOS to show the Developer Mode toggle in Settings > Privacy & Security."""
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        from pymobiledevice3.services.amfi import AmfiService

        target_udid = udid
        if not target_udid:
            devs = await DeviceService.list_devices()
            if not devs:
                raise HTTPException(
                    status_code=404,
                    detail={"code": "DEVICE_NOT_FOUND", "message": "No iPhone connected via USB over usbmuxd."},
                )
            target_udid = devs[0].udid

        lockdown = await create_using_usbmux(serial=target_udid)
        amfi = AmfiService(lockdown)
        await amfi.reveal_developer_mode_option_in_ui()
        return {
            "success": True,
            "message": "Developer Mode option is now visible in iPhone Settings > Privacy & Security!",
        }
    except Exception as e:
        logger.exception(f"Failed to reveal developer mode: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "REVEAL_FAILED",
                "message": f"Could not reveal Developer Mode: {str(e)}",
                "solution": "Make sure your iPhone is unlocked, trusted, and plugged in via USB.",
            },
        )



@router.post("/location", response_model=LocationResponse)
async def set_location(request: SetLocationRequest):
    """Set simulated GPS location for a specific iOS device."""
    if not check_usbmuxd_running():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "USBMUXD_NOT_FOUND",
                "message": "Apple Mobile Device Service is not reachable.",
                "solution": "Install iTunes or Apple Devices and ensure the service is running.",
            },
        )

    try:
        from pymobiledevice3.exceptions import (
            PasswordRequiredError,
            PasscodeRequiredError,
            NotTrustedError,
            NotPairedError,
            PairingDialogResponsePendingError,
            UserDeniedPairingError,
            DeveloperModeIsNotEnabledError,
            NoDeviceConnectedError,
        )
    except ImportError:
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": "pymobiledevice3 import failed"})

    try:
        result = await location_service.set_location(
            udid=request.udid,
            latitude=request.latitude,
            longitude=request.longitude,
            location_name=request.location_name,
        )
        return result

    except (PasswordRequiredError, PasscodeRequiredError):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "DEVICE_LOCKED",
                "message": "iPhone is passcode-locked.",
                "solution": "Please unlock your iPhone screen and enter your passcode.",
            },
        )
    except (NotTrustedError, NotPairedError, PairingDialogResponsePendingError, UserDeniedPairingError):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PAIRING_REQUIRED",
                "message": "Computer is not trusted by the iPhone.",
                "solution": "Tap 'Trust This Computer' on your iPhone and enter your passcode.",
            },
        )
    except DeveloperModeIsNotEnabledError:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "DEVELOPER_MODE_DISABLED",
                "message": "Developer Mode is disabled on iOS 16+.",
                "solution": "Go to Settings > Privacy & Security > Developer Mode, turn ON, and restart device.",
            },
        )
    except NoDeviceConnectedError:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "DEVICE_NOT_FOUND",
                "message": "The selected device was not found.",
                "solution": "Check the USB cable connection and unlock the device.",
            },
        )
    except Exception as e:
        logger.exception(f"Location simulation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LOCATION_SIMULATION_FAILED",
                "message": f"Failed to simulate location: {str(e)}",
                "solution": "Re-connect the USB cable or reboot the device, then try again.",
            },
        )


@router.delete("/location", response_model=LocationResponse)
async def stop_location(udid: Optional[str] = None):
    """Stop active location simulation and restore device's real GPS."""
    try:
        return await location_service.stop_simulation(udid=udid)
    except Exception as e:
        logger.exception(f"Error stopping simulation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LOCATION_STOP_FAILED",
                "message": f"Failed to stop location simulation: {str(e)}",
                "solution": "Rebooting the iPhone will also restore real GPS automatically.",
            },
        )


@router.get("/geocode", response_model=List[GeocodeResult])
async def geocode(q: str = Query(..., min_length=1)):
    """Search for locations using OpenStreetMap Nominatim with a dedicated User-Agent."""
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=5"
    headers = {"User-Agent": "iPhoneLocationSimulator/1.0 (local-desktop-tool)"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = []
            for item in data:
                results.append(
                    GeocodeResult(
                        name=item.get("name") or item.get("display_name", "").split(",")[0],
                        display_name=item.get("display_name", ""),
                        latitude=float(item.get("lat")),
                        longitude=float(item.get("lon")),
                    )
                )
            return results
    except Exception as e:
        logger.warning(f"Geocoding error for '{q}': {e}")
        return []


@router.post("/device/reveal-dev-mode")
async def reveal_developer_mode(udid: Optional[str] = None):
    """Force iOS to reveal the Developer Mode menu in Settings > Privacy & Security."""
    try:
        await DeviceService.reveal_developer_mode(udid=udid)
        return {
            "status": "success",
            "message": "Developer Mode toggle revealed! Open Settings > Privacy & Security > Developer Mode on your iPhone.",
        }
    except Exception as e:
        logger.exception(f"Error revealing developer mode: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DEV_MODE_REVEAL_FAILED",
                "message": f"Failed to reveal Developer Mode: {str(e)}",
                "solution": "Ensure your iPhone is connected via USB, screen is unlocked, and you tapped 'Trust This Computer'.",
            },
        )

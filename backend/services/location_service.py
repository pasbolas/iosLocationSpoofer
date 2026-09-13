import datetime
import logging
from typing import Optional

from backend.models.schemas import LocationResponse
from backend.services.tunnel_service import tunnel_service

logger = logging.getLogger(__name__)


class LocationService:
    """
    Coordinates device location simulation across iOS versions (iOS 17+ via
    PreferredRsdTunnel DVT LocationSimulation and iOS < 17 via DtSimulateLocation).
    """

    def __init__(self) -> None:
        self.is_active: bool = False
        self.active_udid: Optional[str] = None
        self.active_latitude: Optional[float] = None
        self.active_longitude: Optional[float] = None
        self.active_location_name: Optional[str] = None
        self.started_at: Optional[str] = None

    def get_status(self) -> LocationResponse:
        return LocationResponse(
            active=self.is_active,
            latitude=self.active_latitude,
            longitude=self.active_longitude,
            udid=self.active_udid,
            location_name=self.active_location_name,
            started_at=self.started_at,
        )

    async def set_location(
        self,
        udid: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
    ) -> LocationResponse:
        from pymobiledevice3.lockdown import create_using_usbmux

        logger.info(f"Setting location for UDID {udid} to ({latitude}, {longitude}) - {location_name}")

        # Query lockdown to inspect device and iOS version
        lockdown = await create_using_usbmux(serial=udid)
        ios_version = lockdown.product_version or "17.0"
        try:
            major_version = int(ios_version.split(".")[0])
        except (ValueError, IndexError):
            major_version = 17

        if major_version >= 17:
            # iOS 17+ DVT LocationSimulation over RSD tunnel
            loc_sim = await tunnel_service.get_or_create_simulation(udid)
            await loc_sim.set(latitude, longitude)
        else:
            # iOS < 17 lockdown service
            from pymobiledevice3.services.simulate_location import DtSimulateLocation

            loc_sim = DtSimulateLocation(lockdown)
            await loc_sim.set(latitude, longitude)

        # Update tracking state
        self.is_active = True
        self.active_udid = udid
        self.active_latitude = latitude
        self.active_longitude = longitude
        self.active_location_name = location_name or f"{latitude:.4f}, {longitude:.4f}"
        if not self.started_at:
            self.started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return self.get_status()

    async def stop_simulation(self, udid: Optional[str] = None) -> LocationResponse:
        target_udid = udid or self.active_udid

        if not target_udid and not self.is_active:
            return LocationResponse(active=False)

        logger.info(f"Stopping location simulation for UDID: {target_udid}")

        try:
            from pymobiledevice3.lockdown import create_using_usbmux

            lockdown = await create_using_usbmux(serial=target_udid)
            ios_version = lockdown.product_version or "17.0"
            try:
                major_version = int(ios_version.split(".")[0])
            except (ValueError, IndexError):
                major_version = 17

            if major_version >= 17:
                loc_sim = await tunnel_service.get_or_create_simulation(target_udid)
                await loc_sim.clear()
                await tunnel_service.close_simulation(target_udid)
            else:
                from pymobiledevice3.services.simulate_location import DtSimulateLocation

                loc_sim = DtSimulateLocation(lockdown)
                await loc_sim.clear()

        except Exception as e:
            logger.warning(f"Error while stopping simulation for {target_udid}: {e}")
            if target_udid:
                await tunnel_service.close_simulation(target_udid)

        # Reset active state
        self.is_active = False
        self.active_udid = None
        self.active_latitude = None
        self.active_longitude = None
        self.active_location_name = None
        self.started_at = None

        return self.get_status()

    async def shutdown(self) -> None:
        """Emergency cleanup on server termination."""
        if self.is_active and self.active_udid:
            logger.info("Shutdown detected: attempting clean restore of real location...")
            try:
                await self.stop_simulation(self.active_udid)
            except Exception as e:
                logger.error(f"Failed to clear location on shutdown: {e}")
        await tunnel_service.close_all()


location_service = LocationService()

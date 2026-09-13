import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TunnelService:
    """
    Manages Remote Service Discovery (RSD) tunnels and DVT LocationSimulation
    connections for iOS 17+ devices using pymobiledevice3's PreferredRsdTunnel.
    """

    def __init__(self) -> None:
        self._tunnels: Dict[str, object] = {}
        self._dvt_providers: Dict[str, object] = {}
        self._loc_sims: Dict[str, object] = {}

    async def get_or_create_simulation(self, udid: str):
        """
        Get existing active LocationSimulation service or establish a new
        PreferredRsdTunnel + DvtProvider + LocationSimulation pipeline.
        """
        if udid in self._loc_sims:
            return self._loc_sims[udid]

        from pymobiledevice3.remote.rsd_tunnel import PreferredRsdTunnel
        from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
        from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

        logger.info(f"Opening PreferredRsdTunnel for UDID: {udid}")
        tunnel = PreferredRsdTunnel(serial=udid)
        rsd = await tunnel.aopen()

        logger.info(f"Connecting DvtProvider over RSD for UDID: {udid}")
        dvt = DvtProvider(rsd)
        await dvt.connect()

        logger.info(f"Connecting LocationSimulation channel for UDID: {udid}")
        loc_sim = LocationSimulation(dvt)
        await loc_sim.connect()

        self._tunnels[udid] = tunnel
        self._dvt_providers[udid] = dvt
        self._loc_sims[udid] = loc_sim

        return loc_sim

    async def close_simulation(self, udid: str) -> None:
        """Cleanly close LocationSimulation, DvtProvider, and RSD tunnel for a device."""
        if udid in self._loc_sims:
            try:
                await self._loc_sims[udid].close()
            except Exception as e:
                logger.debug(f"Error closing LocationSimulation for {udid}: {e}")
            del self._loc_sims[udid]

        if udid in self._dvt_providers:
            try:
                await self._dvt_providers[udid].close()
            except Exception as e:
                logger.debug(f"Error closing DvtProvider for {udid}: {e}")
            del self._dvt_providers[udid]

        if udid in self._tunnels:
            try:
                await self._tunnels[udid].aclose()
            except Exception as e:
                logger.debug(f"Error closing PreferredRsdTunnel for {udid}: {e}")
            del self._tunnels[udid]

    async def close_all(self) -> None:
        """Teardown all active tunnels and simulation connections."""
        active_udids = list(self._tunnels.keys())
        for udid in active_udids:
            await self.close_simulation(udid)


tunnel_service = TunnelService()

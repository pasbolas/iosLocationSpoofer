from typing import Optional
from pydantic import BaseModel, Field


class Device(BaseModel):
    udid: str
    name: str
    model: str
    product_type: str
    ios_version: str
    connected: bool = True
    paired: bool = False
    developer_mode: str = "Unknown"  # "Ready", "Disabled", "Not Applicable (iOS < 16)"


class SetLocationRequest(BaseModel):
    udid: str = Field(..., description="Target device UDID")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    location_name: Optional[str] = Field(None, description="Optional human-readable location name")


class LocationResponse(BaseModel):
    active: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    udid: Optional[str] = None
    location_name: Optional[str] = None
    started_at: Optional[str] = None


class StatusResponse(BaseModel):
    usbmuxd_running: bool
    devices: list[Device] = []
    active_device: Optional[Device] = None
    simulation: LocationResponse


class GeocodeResult(BaseModel):
    name: str
    display_name: str
    latitude: float
    longitude: float


class ErrorDetail(BaseModel):
    code: str
    message: str
    solution: Optional[str] = None

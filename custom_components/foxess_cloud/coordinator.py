"""Data update coordinator for FoxESS integration."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONFIG_API_KEY,
    CONFIG_DEVICE_SN,
    DATA_DEVICE_DETAIL,
    DATA_DEVICE_DETAIL_STATUS,
    DATA_DEVICE_GENERATION,
    DATA_DEVICE_RT_DATA,
    DEVICE_RT_DATA_VARIABLES,
    DOMAIN,
)
from .foxess_cloud_api import FoxESSCloud

_LOGGER = logging.getLogger(__name__)

DEVICE_STATUS_ONLINE = 1
DEVICE_STATUS_BREAKDOWN = 2
DEVICE_STATUS_OFFLINE = 3

GET_RT_DATA_INTERVAL = 2
GET_DEVICE_DETAIL_INTERVAL = 15
GET_GENERATION_INTERVAL = 5


class FoxESSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to retrieve FoxESS status."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        self.device_sn = config_entry.data[CONFIG_DEVICE_SN]
        self.next_update_device = 0
        self.next_update_rt_data = 0
        self.next_update_generation = 0
        self.client = FoxESSCloud(
            config_entry.data[CONFIG_API_KEY], async_get_clientsession(hass)
        )
        self.current_data = {
            DATA_DEVICE_DETAIL: {DATA_DEVICE_DETAIL_STATUS: DEVICE_STATUS_OFFLINE},
            DATA_DEVICE_GENERATION: {},
            DATA_DEVICE_RT_DATA: {},
        }

    def get_pv_count(self) -> int:
        """Get PV count from current data."""
        return self.client.detect_pv_count(self.current_data[DATA_DEVICE_RT_DATA])

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""

        self.next_update_device = self.next_update_device - 1
        self.next_update_rt_data = self.next_update_rt_data - 1
        self.next_update_generation = self.next_update_generation - 1

        if self.next_update_device <= 0:
            _LOGGER.debug("Updating device detail data")
            device_detail = await self.client.get_device_detail(self.device_sn)
            self.current_data[DATA_DEVICE_DETAIL] = device_detail
            self.next_update_device = GET_DEVICE_DETAIL_INTERVAL
            _LOGGER.debug(
                "Device detail data updated successfully. Got: %s", device_detail
            )

        if self.next_update_generation <= 0:
            _LOGGER.debug("Updating device generation data")
            device_generation = await self.client.get_device_generation(self.device_sn)
            self.current_data[DATA_DEVICE_GENERATION] = device_generation
            self.next_update_generation = GET_GENERATION_INTERVAL
            _LOGGER.debug(
                "Device generation data updated successfully. Got: %s",
                device_generation,
            )

        if self.next_update_rt_data <= 0:
            _LOGGER.debug("Updating device real-time data")
            try:
                real_time_data = await self.client.get_device_real_time_data(
                    self.device_sn, DEVICE_RT_DATA_VARIABLES
                )
                _LOGGER.debug(
                    "Device real-time data updated successfully. Got: %s",
                    real_time_data,
                )
            except Exception as e:
                _LOGGER.error("Error updating device real-time data: %s", e)
                # Data must me marked as unavailable if error occurs, otherwise old data will be shown
                real_time_data = {}
            self.current_data[DATA_DEVICE_RT_DATA] = real_time_data
            self.next_update_rt_data = GET_RT_DATA_INTERVAL

        return self.current_data

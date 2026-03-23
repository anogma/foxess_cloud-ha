"""Config flow for the FoxESS Cloud integration."""

import logging
from typing import Any

from aiohttp.client_exceptions import ClientResponseError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONFIG_API_KEY, CONFIG_DEVICE_NAME, CONFIG_DEVICE_SN, DOMAIN
from .foxess_cloud import FoxESSCloud, FoxESSCloudException

_LOGGER = logging.getLogger(__name__)


class FoxESSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for FoxESS integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_sn = user_input[CONFIG_DEVICE_SN].strip().upper()
            api_key = user_input[CONFIG_API_KEY].strip()
            device_name = user_input[CONFIG_DEVICE_NAME].strip()

            await self.async_set_unique_id(device_sn, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            try:
                session = async_get_clientsession(self.hass)
                await FoxESSCloud(api_key, session).get_device_detail(
                    device_sn
                )  # Test API key

            except FoxESSCloudException as e:
                errors["base"] = e.args[1] or "api_error"
            except ClientResponseError as e:
                if e.message == "Unauthorized":
                    errors[CONFIG_API_KEY] = "invalid_api_key"
                else:
                    _LOGGER.error("Error while connecting to FoxESS Cloud API: %s", e)
                    errors["base"] = "unknown"
            else:
                entry_data = {
                    CONFIG_DEVICE_SN: device_sn,
                    CONFIG_API_KEY: api_key,
                    CONFIG_DEVICE_NAME: device_name,
                }

                return self.async_create_entry(
                    title=f"{device_name} ({device_sn})", data=entry_data
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONFIG_API_KEY): str,
                    vol.Required(CONFIG_DEVICE_SN): str,
                    vol.Required(CONFIG_DEVICE_NAME): str,
                }
            ),
            errors=errors,
        )

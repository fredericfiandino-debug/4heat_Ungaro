"""Config flow for the 4heatlite integration."""
import json
import logging
import socket

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    DATA_QUERY,
    SOCKET_BUFFER,
    SOCKET_TIMEOUT,
    TCP_PORT,
    RESULT_DATA,
)

_LOGGER = logging.getLogger(__name__)


@callback
def four_heat_entries(hass: HomeAssistant):
    """Return the hosts already configured for this domain."""
    return set(
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    )


class FourHeatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """4heatlite config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors = {}

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if this host is already configured."""
        return host in four_heat_entries(self.hass)

    def _check_host(self, host) -> bool:
        """Check if we can connect and get a valid 2WL response from the module."""
        try:
            data = json.dumps(DATA_QUERY, separators=(",", ":")).encode()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(SOCKET_TIMEOUT)
            s.connect((host, TCP_PORT))
            s.send(data)
            raw = s.recv(SOCKET_BUFFER).decode()
            s.close()
            response = json.loads(raw)
            return bool(response) and response[0] == RESULT_DATA
        except Exception as ex:
            _LOGGER.error("Impossible de se connecter au module 4heatlite : %s", ex)
            self._errors[CONF_HOST] = "could_not_connect"
            return False

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            if self._host_in_configuration_exists(user_input[CONF_HOST]):
                self._errors[CONF_HOST] = "host_exists"
            else:
                name = user_input[CONF_NAME]
                host = user_input[CONF_HOST]
                can_connect = await self.hass.async_add_executor_job(
                    self._check_host, host
                )
                if can_connect:
                    return self.async_create_entry(
                        title=name,
                        data={CONF_HOST: host},
                    )
        else:
            user_input = {}

        setup_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, "Poêle")): str,
                vol.Required(
                    CONF_HOST, default=user_input.get(CONF_HOST, "192.168.1.72")
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=setup_schema, errors=self._errors
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        if self._host_in_configuration_exists(user_input[CONF_HOST]):
            return self.async_abort(reason="host_exists")
        return await self.async_step_user(user_input)

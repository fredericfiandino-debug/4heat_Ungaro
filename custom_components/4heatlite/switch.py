"""The 4heatlite integration - switch."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import FourHeatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Codes d'etat (table lingue_stati / MODE_NAMES) consideres comme "poele en marche".
# Testes en conditions reelles : 0 (Off) et 7 (Extinguishing) -> off ; 1 (Check Up) -> on.
# Les autres (2 Ignition, 3 Stabilization, 4 Retry Ignition, 5 Run, 6 Modulation,
# 10 Recover Ignition, 11 Standby) sont deduits de la table du FileMap mais pas
# encore observes chez vous -> a ajuster si besoin une fois testes.
STATES_ON = {1, 2, 3, 4, 5, 6, 10, 11}


async def async_setup_entry(hass, entry, async_add_entities):
    """Add the 4heatlite on/off switch."""
    coordinator: FourHeatDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([FourHeatLiteSwitch(coordinator, entry.title)])


class FourHeatLiteSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of the 4heatlite on/off switch."""

    def __init__(self, coordinator, name):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._name = name
        self.serial_number = coordinator.serial_number
        self.model = coordinator.model

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._name} Marche/Arrêt"

    @property
    def icon(self):
        """Return icon."""
        return "mdi:radiator"

    @property
    def is_on(self):
        """Return true if the stove is running (etat dans STATES_ON)."""
        if not self.coordinator.data or "mode_code" not in self.coordinator.data:
            return False
        return self.coordinator.data["mode_code"] in STATES_ON

    async def async_turn_on(self, **kwargs):
        """Turn the stove on."""
        await self.coordinator.async_turn_on()
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the stove off."""
        await self.coordinator.async_turn_off()
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return unique id based on device name."""
        return f"{self._name}_switch"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._name,
            "manufacturer": "Tiemme",
            "model": self.model,
        }

    @property
    def extra_state_attributes(self):
        """Return the current mode (texte + code) as attributes."""
        if not self.coordinator.data:
            return None
        return {
            "mode": self.coordinator.data.get("mode"),
            "mode_code": self.coordinator.data.get("mode_code"),
        }

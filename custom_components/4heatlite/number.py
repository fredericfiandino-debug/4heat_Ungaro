"""The 4heatlite integration - number (consigne de température réglable)."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    PARAM_ROOM_SETPOINT,
)
from .coordinator import FourHeatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add the 4heatlite temperature setpoint number entity."""
    coordinator: FourHeatDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([FourHeatLiteSetpointNumber(coordinator, entry.title)])


class FourHeatLiteSetpointNumber(CoordinatorEntity, NumberEntity):
    """Representation of the 4heatlite room temperature setpoint (paramètre 005a)."""

    # Bornes observées dans les trames du poêle (10.0 - 40.0°C).
    _attr_native_min_value = 10.0
    _attr_native_max_value = 40.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator, name):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._name = name
        self.serial_number = coordinator.serial_number
        self.model = coordinator.model

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{self._name} Consigne température"

    @property
    def native_value(self):
        """Return the current setpoint in °C (la trame stocke des dixièmes de degré)."""
        if not self.coordinator.data or PARAM_ROOM_SETPOINT not in self.coordinator.data:
            return None
        return self.coordinator.data[PARAM_ROOM_SETPOINT] / 10

    async def async_set_native_value(self, value: float) -> None:
        """Change la consigne de température sur le poêle."""
        await self.coordinator.async_set_temperature(PARAM_ROOM_SETPOINT, value)
        await self.coordinator.async_request_refresh()

    @property
    def unique_id(self):
        """Return unique id based on device name and parameter id."""
        return f"{self._name}_{PARAM_ROOM_SETPOINT}_setpoint"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._name,
            "manufacturer": "Tiemme",
            "model": self.model,
        }

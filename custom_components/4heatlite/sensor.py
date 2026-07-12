"""The 4heatlite integration - sensors."""

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .const import (
    SENSOR_TYPES,
    PARAM_VALUE_MAPS,
    DOMAIN,
    DATA_COORDINATOR,
    ATTR_STOVE_ID,
    ATTR_READING_ID,
)
from .coordinator import FourHeatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add 4heatlite sensor entities."""
    coordinator: FourHeatDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    entities = [
        FourHeatLiteSensor(coordinator, param_id, entry.title) for param_id in SENSOR_TYPES
    ]
    entities.append(FourHeatLiteModeSensor(coordinator, entry.title))

    async_add_entities(entities)


class FourHeatLiteSensor(CoordinatorEntity, SensorEntity):
    """Representation of a 4heatlite numeric sensor (temperature/puissance/etc.)."""

    def __init__(self, coordinator, param_id, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.type = param_id
        self._name = name
        self._last_value = None

        sensor_name, unit, icon, device_class, state_class, divisor = SENSOR_TYPES[param_id]
        self._sensor_name = sensor_name
        self._unit_of_measurement = unit
        self._icon = icon
        self._device_class = device_class
        self._state_class = state_class
        self._divisor = divisor

        self.serial_number = coordinator.serial_number
        self.model = coordinator.model

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._sensor_name}"

    @property
    def native_value(self):
        """Return the value : traduit via table (puissances) ou divise (temperatures)."""
        if not self.coordinator.data or self.type not in self.coordinator.data:
            return self._last_value

        raw = self.coordinator.data[self.type]

        if self.type in PARAM_VALUE_MAPS:
            value = PARAM_VALUE_MAPS[self.type].get(raw, f"Unknown ({raw})")
        else:
            value = raw / self._divisor if self._divisor != 1 else raw

        self._last_value = value
        return value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement for templating and statistics."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return icon."""
        return self._icon

    @property
    def device_class(self):
        """Return device-class."""
        return self._device_class

    @property
    def state_class(self):
        """Return state-class."""
        return self._state_class

    @property
    def unique_id(self):
        """Return unique id based on device name and parameter id."""
        return f"{self._name}_{self.type}"

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
        """Return additional attributes for the entity."""
        if not self.coordinator.data or self.type not in self.coordinator.data:
            return None
        return {
            ATTR_READING_ID: self.type,
            ATTR_STOVE_ID: self.coordinator.stove_id,
        }


class FourHeatLiteModeSensor(CoordinatorEntity, SensorEntity):
    """Representation of the 4heatlite operating state (Off/Ignition/Run/...)."""

    def __init__(self, coordinator, name):
        """Initialize the mode sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._name = name
        self._last_value = None
        self.serial_number = coordinator.serial_number
        self.model = coordinator.model

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} État"

    @property
    def native_value(self):
        """Return the current mode name (Off, Ignition, Run, Extinguishing, ...)."""
        if not self.coordinator.data or "mode" not in self.coordinator.data:
            return self._last_value
        value = self.coordinator.data["mode"]
        self._last_value = value
        return value

    @property
    def icon(self):
        """Return icon."""
        return "mdi:radiator"

    @property
    def unique_id(self):
        """Return unique id."""
        return f"{self._name}_mode"

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
        """Return the raw mode code as an attribute."""
        if not self.coordinator.data or "mode_code" not in self.coordinator.data:
            return None
        return {
            ATTR_STOVE_ID: self.coordinator.stove_id,
            "mode_code": self.coordinator.data["mode_code"],
        }

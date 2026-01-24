"""The 4Heat integration."""

import logging
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .const import (
    MODE_NAMES, ERROR_NAMES, POWER_NAMES,
    MODE_TYPE, ERROR_TYPE, POWER_TYPE,
    SENSOR_TYPES, DOMAIN, DATA_COORDINATOR,
    ATTR_MARKER, ATTR_NUM_VAL, ATTR_READING_ID, ATTR_STOVE_ID
)
from .coordinator import FourHeatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add an FourHeat entry."""
    coordinator: FourHeatDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    entities = []
    sensorIds = entry.data[CONF_MONITORED_CONDITIONS]

    for sensorId in sensorIds:
        if len(sensorId) > 5:
            try:
                sId = sensorId[1:6]
                entities.append(FourHeatDevice(coordinator, sId, entry.title))
            except:
                _LOGGER.debug(f"Error adding {sensorId}")

    async_add_entities(entities)


class FourHeatDevice(CoordinatorEntity, SensorEntity):
    """Representation of a 4Heat device."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        if sensor_type not in SENSOR_TYPES:
            _LOGGER.error(f"Sensor '{sensor_type}' unkonwn, notify maintainer.")
            SENSOR_TYPES[sensor_type] = [f"UN {sensor_type}", None, ""]
        self._sensor = SENSOR_TYPES[sensor_type][0]
        self._name = name
        self.type = sensor_type
        self.coordinator = coordinator
        self._last_value = None
        self.serial_number = coordinator.serial_number
        self.model = coordinator.model
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._device_class = SENSOR_TYPES[self.type][3]
        self._state_class = SENSOR_TYPES[self.type][4]
        _LOGGER.debug(self.coordinator)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._sensor}"

    @property
    def state(self):
        """Return the state of the device."""
        if self.type not in self.coordinator.data: 
            return None
        try:
            if self.type == MODE_TYPE:
                state = MODE_NAMES[self.coordinator.data[self.type][0]]
            elif self.type == ERROR_TYPE:
                state = ERROR_NAMES[self.coordinator.data[self.type][0]]
            elif self.type == POWER_TYPE:
                state = POWER_NAMES[self.coordinator.data[self.type][0]]
            else:
                state = self.coordinator.data[self.type][0]

            self._last_value = state
        except Exception as ex:
            _LOGGER.error(ex)
            state = self._last_value
        return state

    @property
    def native_value(self):
        """Return the native value (numeric) of the sensor for statistics."""
        if self.type not in self.coordinator.data:
            return None
        try:
            # native_value MUST be numeric for Home Assistant statistics/recorder.
            # Return the raw numeric code for all sensor types so statistics work.
            return self.coordinator.data[self.type][0]
        except Exception:
            return self._last_value

    @property
    def maker(self):
        """Maker information"""
        return self.coordinator.data[self.type][1]

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
        """Return device-class"""
        return self._device_class

    @property
    def state_class(self):
        """Return state-class"""
        return self._state_class


    @property
    def unique_id(self):
        """Return unique id based on device serial and variable."""
        return f"{self._name}_{self.type}"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._name,
            "manufacturer": "4Heat",
            "model": self.model,
        }

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the entity."""
        try:
            if self.type not in self.coordinator.data:
                return None

            attrs = {
                ATTR_MARKER: self.coordinator.data[self.type][1],
                ATTR_READING_ID: self.type,
                ATTR_STOVE_ID: self.coordinator.stove_id,
            }

            # include numeric raw value for modes/errors/power as an attribute too
            if self.type in (MODE_TYPE, ERROR_TYPE, POWER_TYPE):
                attrs[ATTR_NUM_VAL] = self.coordinator.data[self.type][0]

            return attrs

        except Exception as ex:
            _LOGGER.error(ex)
            return None
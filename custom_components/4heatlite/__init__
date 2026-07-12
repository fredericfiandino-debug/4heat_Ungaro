"""Integration for 4heatlite."""
import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant, valid_entity_id
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.exceptions import ConfigEntryNotReady

import homeassistant.helpers.config_validation as cv

from .const import ATTR_READING_ID, ATTR_STOVE_ID, DOMAIN, DATA_COORDINATOR
from .coordinator import FourHeatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_HOST): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config[DOMAIN])
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Load the saved entities."""
    coordinator = FourHeatDataUpdateCoordinator(
        hass,
        config=entry.data,
        options=entry.options,
        id=entry.entry_id,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    async def async_handle_set_temperature(call):
        """Handle the service call to set a temperature setpoint (parametre type 0x12).

        Contrairement a l'ancien protocole (marqueur 'B' + valeur brute), on
        ecrit maintenant via l'algorithme confirme dans coordinator.async_set_temperature,
        qui a besoin de la derniere trame lue (bornes min/max) pour ce parametre.
        """
        entity_id = call.data.get("entity_id", "")
        value = call.data.get("value")

        if not valid_entity_id(entity_id):
            _LOGGER.error('"%s" n\'est pas un entity_id valide', entity_id)
            return

        state = hass.states.get(entity_id)
        if state is None or ATTR_READING_ID not in state.attributes:
            _LOGGER.error(
                '"%s" n\'a pas d\'attribut %s, impossible d\'ecrire une valeur',
                entity_id,
                ATTR_READING_ID,
            )
            return

        reading_id = state.attributes[ATTR_READING_ID]
        stove_id = state.attributes.get(ATTR_STOVE_ID, entry.entry_id)
        coord = hass.data[DOMAIN][stove_id][DATA_COORDINATOR]

        await coord.async_set_temperature(reading_id, float(value))
        await coord.async_request_refresh()

    hass.services.async_register(DOMAIN, "set_temperature", async_handle_set_temperature)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])
    return True

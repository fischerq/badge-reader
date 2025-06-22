"""Binary sensors for the Badge Reader integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BadgeReaderDataUpdateCoordinator
from .const import DOMAIN, BINARY_SENSOR_HOUSEKEEPER_PRESENT, BINARY_SENSOR_NFC_READER_STATUS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator: BadgeReaderDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HousekeeperPresentBinarySensor(coordinator, entry),
        NFCReaderStatusBinarySensor(coordinator, entry),
    ]

    async_add_entities(entities)


class HousekeeperPresentBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for housekeeper presence."""

    def __init__(self, coordinator, config_entry):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = "Housekeeper Present"
        self._attr_unique_id = f"{config_entry.entry_id}_{BINARY_SENSOR_HOUSEKEEPER_PRESENT}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Badge Reader",
            "manufacturer": "Badge Reader Integration",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        # This will be updated based on the coordinator state in later steps
        return self.coordinator.data.get("housekeeper_present")


class NFCReaderStatusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for NFC reader status."""

    def __init__(self, coordinator, config_entry):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = "NFC Reader Status"
        self._attr_unique_id = f"{config_entry.entry_id}_{BINARY_SENSOR_NFC_READER_STATUS}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Badge Reader",
            "manufacturer": "Badge Reader Integration",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (online)."""
        # This will be updated based on the coordinator state in later steps
        return self.coordinator.data.get("reader_online")
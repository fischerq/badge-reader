"""Sensor platform for badgereader."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BadgereaderDataUpdateCoordinator
from .const import DOMAIN, HOUSEKEEPER_STATUS_SENSOR_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: BadgereaderDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[SensorEntity] = []
    sensors.append(HousekeeperStatusSensor(coordinator))

    async_add_entities(sensors)


class HousekeeperStatusSensor(CoordinatorEntity, SensorEntity):
    """Defines a housekeeper status sensor."""

    _attr_name = HOUSEKEEPER_STATUS_SENSOR_NAME

    def __init__(self, coordinator: BadgereaderDataUpdateCoordinator) -> None:
        """Initialize the housekeeper status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_status"
        self._attr_device_info = coordinator.device_info

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        # This state will be updated by the coordinator based on webhook data
        return self.coordinator.data.get("status")
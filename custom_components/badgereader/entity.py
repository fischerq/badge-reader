"""Base entity for the Badge Reader component."""
from homeassistant.helpers.entity import Entity


class BadgeReaderEntity(Entity):
    """Base entity for the Badge Reader component."""

    _attr_should_poll = False

    def __init__(self, coordinator):
        """Initialize the entity."""
        self.coordinator = coordinator

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        # This will be overridden by subclasses
        raise NotImplementedError

    @property
    def device_info(self):
        """Return the device info."""
        # Define a shared device for all entities of this component
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                ("badgereader", self.coordinator.config_entry.unique_id)
            },
            "name": "Badge Reader",
            "manufacturer": "Your Manufacturer",  # Replace with your manufacturer name
            "model": "uFR Nano Online",
            "configuration_url": f"http://{self.coordinator.reader_ip}",
        }
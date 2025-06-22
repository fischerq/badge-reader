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
        config_entry_unique_id = "unknown_reader"
        if hasattr(self.coordinator, 'config_entry') and self.coordinator.config_entry and hasattr(self.coordinator.config_entry, 'unique_id') and self.coordinator.config_entry.unique_id:
            config_entry_unique_id = self.coordinator.config_entry.unique_id

        reader_name = "Badge Reader"
        reader_ip = "unknown_ip"
        if hasattr(self.coordinator, 'reader_ip') and self.coordinator.reader_ip:
            reader_ip = self.coordinator.reader_ip
            # Potentially use reader_ip or a part of it in the name if config_entry.name is not available
            # For now, let's assume a generic name if specific config name isn't easily accessible
            # reader_name = self.coordinator.config_entry.data.get("name", "Badge Reader") # Example if name was in data

        return {
            "identifiers": {
                ("badgereader", config_entry_unique_id)
            },
            "name": reader_name,
            "manufacturer": "Your Name or Project Name",  # Updated to match test
            "model": "NFC Badge Reader",  # Updated to match test
            "configuration_url": f"http://{reader_ip}",
        }
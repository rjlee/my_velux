"""Support for Velux lights."""
from __future__ import annotations
import logging

from pyvlx import Intensity, LighteningDevice
from pyvlx.node import Node

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    COLOR_MODE_BRIGHTNESS,
    LightEntity,
)

from .const import DOMAIN
from . import VeluxEntity

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    for node in gateway.nodes:
        if isinstance(node, LighteningDevice):
            _LOGGER.debug("Light will be added: %s", node.name)
            entities.append(VeluxLight(node))
    async_add_entities(entities)


class VeluxLight(VeluxEntity, LightEntity):
    """Representation of a Velux light."""

    def __init__(self, node: Node) -> None:
        """Initialize the Velux light."""
        super().__init__(node)

        self._attr_supported_color_modes = {COLOR_MODE_BRIGHTNESS}
        self._attr_color_mode = COLOR_MODE_BRIGHTNESS

    @property
    def brightness(self):
        """Return the current brightness."""
        return int((100 - self.node.intensity.intensity_percent) * 255 / 100)

    @property
    def is_on(self):
        """Return true if light is on."""
        return not self.node.intensity.off and self.node.intensity.known

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            intensity_percent = int(100 - kwargs[ATTR_BRIGHTNESS] / 255 * 100)
            await self.node.set_intensity(
                Intensity(intensity_percent=intensity_percent),
                wait_for_completion=True,
            )
        else:
            await self.node.turn_on(wait_for_completion=True)

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        await self.node.turn_off(wait_for_completion=True)
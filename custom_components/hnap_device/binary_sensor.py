# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

"""Binary sensor for HNAP device integration."""

import logging
from typing import Optional

import hnap
import requests.exceptions
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType


from .const import DOMAIN, PLATFORM_BINARY_SENSOR
from .entity import HNapEntity

PLATFORM = PLATFORM_BINARY_SENSOR

_LOGGER = logging.getLogger(__name__)


class HNAPMotion(HNapEntity, BinarySensorEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name="motion")

        self._attr_device_class = BinarySensorDeviceClass.MOTION

    def update(self):
        try:
            self._attr_is_on = self._api.is_active()
            self.hnap_update_success()

        except (
            hnap.soapclient.MethodCallError,
            requests.exceptions.ConnectionError,
        ) as e:
            _LOGGER.error(e)
            self._attr_is_on = None
            self.hnap_update_failure()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,  # noqa DiscoveryInfoType | None
):
    api = hass.data[DOMAIN][config_entry.entry_id]
    device_info = await hass.async_add_executor_job(api.client.device_info)

    add_entities(
        [
            HNAPMotion(
                unique_id=f"{config_entry.entry_id}-{PLATFORM}",
                device_info=device_info,
                api=api,
            )
        ],
        update_before_add=True,
    )

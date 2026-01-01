"""Tests for the number platform."""

from unittest.mock import patch

import pytest

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from .common import ENTITY_HUMIDIFIER_MIST_LEVEL, ENTITY_HUMIDIFIER_WARM_LEVEL

from tests.common import MockConfigEntry


async def test_set_mist_level_bad_range(
    hass: HomeAssistant, humidifier_config_entry: MockConfigEntry
) -> None:
    """Test set_mist_level invalid value."""
    with (
        pytest.raises(ServiceValidationError),
        patch(
            "pyvesync.devices.vesynchumidifier.VeSyncHumid200300S.set_mist_level",
            return_value=True,
        ) as method_mock,
    ):
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: ENTITY_HUMIDIFIER_MIST_LEVEL, ATTR_VALUE: "10"},
            blocking=True,
        )
    await hass.async_block_till_done()
    method_mock.assert_not_called()


async def test_set_mist_level(
    hass: HomeAssistant, humidifier_config_entry: MockConfigEntry
) -> None:
    """Test set_mist_level usage."""

    with patch(
        "pyvesync.devices.vesynchumidifier.VeSyncHumid200300S.set_mist_level",
        return_value=True,
    ) as method_mock:
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: ENTITY_HUMIDIFIER_MIST_LEVEL, ATTR_VALUE: "3"},
            blocking=True,
        )
    await hass.async_block_till_done()
    method_mock.assert_called_once()


async def test_mist_level(
    hass: HomeAssistant, humidifier_config_entry: MockConfigEntry
) -> None:
    """Test the state of mist_level number entity."""

    assert hass.states.get(ENTITY_HUMIDIFIER_MIST_LEVEL).state == "6"


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_set_warm_level_bad_range(
    hass: HomeAssistant, install_humidifier_device
) -> None:
    """Test set_warm_level invalid value."""
    with (
        pytest.raises(ServiceValidationError),
        patch(
            "pyvesync.devices.vesynchumidifier.VeSyncHumid200300S.set_warm_level",
            return_value=True,
        ) as method_mock,
    ):
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: ENTITY_HUMIDIFIER_WARM_LEVEL, ATTR_VALUE: "10"},
            blocking=True,
        )
    await hass.async_block_till_done()
    method_mock.assert_not_called()


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_set_warm_level(
    hass: HomeAssistant, install_humidifier_device
) -> None:
    """Test set_warm_level usage."""

    with patch(
        "pyvesync.devices.vesynchumidifier.VeSyncHumid200300S.set_warm_level",
        return_value=True,
    ) as method_mock:
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: ENTITY_HUMIDIFIER_WARM_LEVEL, ATTR_VALUE: "2"},
            blocking=True,
        )
    await hass.async_block_till_done()
    method_mock.assert_called_once()


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_warm_level(
    hass: HomeAssistant, install_humidifier_device
) -> None:
    """Test the state of warm_level number entity."""

    assert hass.states.get(ENTITY_HUMIDIFIER_WARM_LEVEL).state == "2"

"""Tests for the number platform."""

from unittest.mock import AsyncMock, patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from tests.common import MockConfigEntry, snapshot_platform
from tests.test_util.aiohttp import AiohttpClientMocker


@pytest.fixture
def platforms() -> list[Platform]:
    """Fixture to specify platforms to test."""
    return [Platform.NUMBER]


@pytest.mark.parametrize("install_humidifier_device", ["humidifier"], indirect=True)
async def test_number_state(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    install_humidifier_device,
    config_entry: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test the number entities for mist_level."""

    await snapshot_platform(hass, entity_registry, snapshot, config_entry.entry_id)


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_number_warm_level_state(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    install_humidifier_device,
    config_entry: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test the number entities for warm_level."""

    await snapshot_platform(hass, entity_registry, snapshot, config_entry.entry_id)


async def test_set_mist_level(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    config: dict,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test set_mist_level usage."""
    from .common import mock_multiple_device_responses

    config_entry = MockConfigEntry(
        title="VeSync",
        domain="vesync",
        data=config["vesync"],
    )
    config_entry.add_to_hass(hass)

    device_name = "Humidifier 200s"
    mock_multiple_device_responses(aioclient_mock, [device_name])
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Get the actual entity_id from the registry
    # Mist level entity has max=6 (or 9 depending on fixture data)
    entities = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)
    mist_level_entity = next(
        (
            e
            for e in entities
            if e.domain == NUMBER_DOMAIN
            and hass.states.get(e.entity_id)
            and hass.states.get(e.entity_id).attributes.get("max") in (6, 9)
        ),
        None,
    )
    assert mist_level_entity is not None

    with patch(
        "pyvesync.devices.vesynchumidifier.VeSyncHumid200300S.set_mist_level",
        return_value=True,
    ) as method_mock:
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: mist_level_entity.entity_id, ATTR_VALUE: "3"},
            blocking=True,
        )
    await hass.async_block_till_done()
    method_mock.assert_called_once()


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_set_warm_level(
    hass: HomeAssistant,
    install_humidifier_device,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    humidifier_300s,
) -> None:
    """Test set_warm_level usage."""
    # Get the actual entity_id from the registry
    # Warm level entity has max=3, mist level has max=6
    entities = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)
    warm_level_entity = next(
        (
            e
            for e in entities
            if e.domain == NUMBER_DOMAIN
            and hass.states.get(e.entity_id)
            and hass.states.get(e.entity_id).attributes.get("max") == 3
        ),
        None,
    )
    assert warm_level_entity is not None

    # Mock the set_warm_level method on the device instance
    humidifier_300s.set_warm_level = AsyncMock(return_value=True)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: warm_level_entity.entity_id, ATTR_VALUE: "2"},
        blocking=True,
    )
    await hass.async_block_till_done()
    humidifier_300s.set_warm_level.assert_called_once_with(2.0)

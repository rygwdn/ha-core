"""Tests for the number platform."""

from unittest.mock import AsyncMock

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry, snapshot_platform


@pytest.fixture
def platforms() -> list[Platform]:
    """Fixture to specify platforms to test."""
    return [Platform.NUMBER]


@pytest.mark.parametrize(
    "install_humidifier_device", ["humidifier", "humidifier_300s"], indirect=True
)
async def test_number_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    install_humidifier_device,
    config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test the number entities."""
    await snapshot_platform(hass, entity_registry, snapshot, config_entry.entry_id)


@pytest.mark.parametrize("install_humidifier_device", ["humidifier"], indirect=True)
async def test_set_mist_level(
    hass: HomeAssistant,
    install_humidifier_device,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    humidifier,
) -> None:
    """Test set_mist_level usage."""
    # Get mist_level entity by translation_key
    entities = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)
    mist_level_entity = next(
        e for e in entities if e.translation_key == "mist_level"
    )

    humidifier.set_mist_level = AsyncMock(return_value=True)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: mist_level_entity.entity_id, ATTR_VALUE: "3"},
        blocking=True,
    )
    await hass.async_block_till_done()
    humidifier.set_mist_level.assert_called_once_with(3.0)


@pytest.mark.parametrize("install_humidifier_device", ["humidifier_300s"], indirect=True)
async def test_set_warm_level(
    hass: HomeAssistant,
    install_humidifier_device,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
    humidifier_300s,
) -> None:
    """Test set_warm_level usage."""
    # Get warm_level entity by translation_key
    entities = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)
    warm_level_entity = next(
        e for e in entities if e.translation_key == "warm_level"
    )

    humidifier_300s.set_warm_level = AsyncMock(return_value=True)

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: warm_level_entity.entity_id, ATTR_VALUE: "2"},
        blocking=True,
    )
    await hass.async_block_till_done()
    humidifier_300s.set_warm_level.assert_called_once_with(2.0)

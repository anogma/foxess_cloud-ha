"""Sensor platform for FoxESS Cloud."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONFIG_DEVICE_NAME,
    CONFIG_DEVICE_SN,
    DATA_DEVICE_DETAIL,
    DATA_DEVICE_GENERATION,
    DATA_DEVICE_RT_DATA,
    DOMAIN,
)
from .coordinator import FoxESSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor set up."""

    coordinator = FoxESSDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    pv_count = coordinator.get_pv_count()
    entities = [
        FoxESSInverterStatus(coordinator, "status", "Status"),
        FoxESSPower(coordinator, "pv_power", "PV Power", "pvPower"),
        FoxESSRunningState(coordinator, "running_state", "Running State"),
        # Temperatures
        FoxESSTemperature(
            coordinator,
            "ambient_temperature",
            "Ambient Temperature",
            "ambientTemperation",
        ),
        FoxESSTemperature(
            coordinator, "boot_temperature", "Boost Temperature", "boostTemperation"
        ),
        FoxESSTemperature(
            coordinator, "inv_temperature", "Inverter Temperature", "invTemperation"
        ),
        FoxESSPower(coordinator, "load_power", "Load Power", "loads"),
        FoxESSPower(coordinator, "output_power", "Output Power", "generationPower"),
        FoxESSPower(
            coordinator,
            "grid_consumption_power",
            "Grid Consumption Power",
            "gridConsumptionPower",
        ),
        FoxESSKVar(coordinator, "reactive_power", "Reactive Power", "ReactivePower"),
        FoxESSEnergy(
            coordinator,
            "generation",
            "Cumulative Energy Generation",
            "generation",
        ),
        FoxESSEnergy(
            coordinator,
            "grid_consumption",
            "Grid Consumption Energy",
            "gridConsumption",
        ),
        FoxESSEnergy(
            coordinator,
            "grid_consumption_2",
            "Grid Consumption Energy 2",
            "gridConsumption2",
        ),
        FoxESSEnergy(coordinator, "load_energy", "Load Energy", "loadsPower"),
        FoxESSEnergy(
            coordinator,
            "feedin_power",
            "FeedIn Energy",
            "feedin",
        ),
        FoxESSEnergy(
            coordinator,
            "feedin_power2",
            "FeedIn Energy 2",
            "feedin2",
        ),
        FoxESSEnergy(
            coordinator,
            "pv_energy_total",
            "PV Energy Generation",
            "PVEnergyTotal",
        ),
        FoxESSEnergy(
            coordinator,
            "pv_energy_cumulative",
            "PV Energy Generation Cumulative",
            "cumulative",
            data_key=DATA_DEVICE_GENERATION,
        ),
        FoxESSEnergy(
            coordinator,
            "pv_energy_today",
            "PV Energy Generation Today",
            "today",
            data_key=DATA_DEVICE_GENERATION,
        ),
        FoxESSEnergy(
            coordinator,
            "pv_energy_month",
            "PV Energy Generation Month",
            "month",
            data_key=DATA_DEVICE_GENERATION,
        ),
        # R
        FoxESSCurrent(coordinator, "r_current", "R Current", "RCurrent"),
        FoxESSFrequency(coordinator, "r_frequency", "R Frequency", "RFreq"),
        FoxESSPower(coordinator, "r_power", "R Power", "RPower"),
        FoxESSVoltage(coordinator, "r_voltage", "R Voltage", "RVolt"),
        # T
        FoxESSCurrent(coordinator, "t_current", "T Current", "TCurrent"),
        FoxESSFrequency(coordinator, "t_frequency", "T Frequency", "TFreq"),
        FoxESSPower(coordinator, "t_power", "T Power", "TPower"),
        FoxESSVoltage(coordinator, "t_voltage", "T Voltage", "TVolt"),
        # S
        FoxESSCurrent(coordinator, "s_current", "S Current", "SCurrent"),
        FoxESSFrequency(coordinator, "s_frequency", "S Frequency", "SFreq"),
        FoxESSPower(coordinator, "s_power", "S Power", "SPower"),
        FoxESSVoltage(coordinator, "s_voltage", "S Voltage", "SVolt"),
    ]
    for index in range(1, pv_count + 1):
        entities.extend(
            [
                FoxESSPower(
                    coordinator,
                    f"pv{index}_power",
                    f"PV{index} Power",
                    f"pv{index}Power",
                ),
                FoxESSVoltage(
                    coordinator,
                    f"pv{index}_-voltage",
                    f"PV{index} Voltage",
                    f"pv{index}Volt",
                ),
                FoxESSCurrent(
                    coordinator,
                    f"pv{index}_current",
                    f"PV{index} Current",
                    f"pv{index}Current",
                ),
            ]
        )

    async_add_entities(entities)
    return True


class FoxESSEntity(CoordinatorEntity, SensorEntity):
    """Base class for FoxESSCloud entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, id: str, attr_name: str, context=None) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, context)
        self.device_sn = coordinator.config_entry.data[CONFIG_DEVICE_SN]
        self._attr_name = attr_name
        self._attr_unique_id = f"{self.device_sn}_{id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""

        device_detail = self.coordinator.current_data[DATA_DEVICE_DETAIL]
        master_version = device_detail["masterVersion"]
        hardware_version = device_detail["hardwareVersion"]

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.data[CONFIG_DEVICE_NAME],
            manufacturer="FoxESS",
            model=device_detail["deviceType"],
            serial_number=device_detail["deviceSN"],
            sw_version=master_version
            if master_version and master_version != "--"
            else None,
            hw_version=hardware_version
            if hardware_version and hardware_version != "--"
            else None,
        )


class FoxESSFloatVariableEntity(FoxESSEntity):
    """Base class for FoxESSCloud entities representing float variables."""

    def __init__(
        self,
        coordinator,
        id,
        attr_name,
        variable,
        data_key=DATA_DEVICE_RT_DATA,
        context=None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, id, attr_name, context)
        self.variable = variable
        self.data_key = data_key

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.current_data.get(self.data_key, {}).get(
            self.variable, None
        )

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.current_data.get(self.data_key) is not None


class FoxESSInverterStatus(FoxESSEntity):
    """Sensor representing the inverter status (online, fault, offline)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["online", "fault", "offline"]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        code = self.coordinator.current_data.get(DATA_DEVICE_DETAIL, {}).get("status")
        return (
            self._attr_options[code - 1]
            if code and 0 < code <= len(self._attr_options)
            else "unknown"
        )

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.current_data.get(DATA_DEVICE_DETAIL) is not None


RUNNING_STATE_MAP = {
    "160": "self-test",
    "161": "waiting",
    "162": "checking",
    "163": "on-grid",
    "164": "off-grid",
    "165": "fault",
    "166": "permanent-fault",
    "167": "standby",
    "168": "upgrading",
    "169": "fct",
    "170": "illegal",
}


class FoxESSRunningState(FoxESSEntity):
    """Sensor representing the running state of the device (self-test, waiting, checking, on-grid, off-grid, fault, permanent-fault, standby, upgrading, fct, illegal)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(RUNNING_STATE_MAP.values())

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        code = self.coordinator.current_data.get(DATA_DEVICE_RT_DATA, {}).get(
            "runningState", None
        )
        return RUNNING_STATE_MAP.get(code, "unknown")

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.current_data.get(DATA_DEVICE_RT_DATA) is not None


class FoxESSEnergy(FoxESSFloatVariableEntity):
    """Sensor representing energy values, with state class TOTAL_INCREASING and device class ENERGY."""

    _attr_state_class: SensorStateClass = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR


class FoxESSPower(FoxESSFloatVariableEntity):
    """Sensor representing power values, with state class MEASUREMENT and device class POWER."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT


class FoxESSVoltage(FoxESSFloatVariableEntity):
    """Sensor representing voltage values, with state class MEASUREMENT and device class VOLTAGE."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT


class FoxESSCurrent(FoxESSFloatVariableEntity):
    """Sensor representing current values, with state class MEASUREMENT and device class CURRENT."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE


class FoxESSFrequency(FoxESSFloatVariableEntity):
    """Sensor representing frequency values, with state class MEASUREMENT and device class FREQUENCY."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ


class FoxESSTemperature(FoxESSFloatVariableEntity):
    """Sensor representing temperature values, with state class MEASUREMENT and device class TEMPERATURE."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class FoxESSKVar(FoxESSFloatVariableEntity):
    """Sensor representing reactive power values, with state class MEASUREMENT and device class REACTIVE_POWER."""

    _attr_state_class: SensorStateClass = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.REACTIVE_POWER
    _attr_native_unit_of_measurement = UnitOfReactivePower.KILO_VOLT_AMPERE_REACTIVE

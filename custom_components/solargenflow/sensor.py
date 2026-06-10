from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower, UnitOfEnergy, PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .flow_engine import SolarGenflowEngine


DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, "solargenflow_core")},
    name="SolarGenflow Core",
    manufacturer="SolarGenflow",
    model="Energy Flow Engine",
)


SENSOR_MAPPING = {
    "pv_power": {
        "engine_attr": "pv_power",
        "name": "PV Power",
        "icon": "mdi:solar-power",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "pv1_power": {
        "engine_attr": "pv1_power",
        "name": "PV1 Power",
        "icon": "mdi:solar-power",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "pv2_power": {
        "engine_attr": "pv2_power",
        "name": "PV2 Power",
        "icon": "mdi:solar-power",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "pv3_power": {
        "engine_attr": "pv3_power",
        "name": "PV3 Power",
        "icon": "mdi:solar-power",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "pv4_power": {
        "engine_attr": "pv4_power",
        "name": "PV4 Power",
        "icon": "mdi:solar-power",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    
    "solarvault_ac_power": {
    "engine_attr": "solarvault_ac_power",
    "name": "SolarVault AC Power",
    "icon": "mdi:transmission-tower",
    "unit": UnitOfPower.WATT,
    "device_class": "power",
    "state_class": "measurement",
    },
    "solarvault_ac_output": {
        "engine_attr": "solarvault_ac_output",
        "name": "SolarVault AC Output",
        "icon": "mdi:home-import-outline",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "solarvault_ac_input": {
        "engine_attr": "solarvault_ac_input",
        "name": "SolarVault AC Input",
        "icon": "mdi:home-export-outline",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "home_power": {
        "engine_attr": "home_power",
        "name": "Home Power",
        "icon": "mdi:home-import-outline",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "domestic_load_power": {
        "engine_attr": "domestic_load_power",
        "name": "Domestic Load Power",
        "icon": "mdi:home-lightning-bolt",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "home_load_total": {
        "engine_attr": "home_load_total",
        "name": "Home Load Total",
        "icon": "mdi:home-lightning-bolt-outline",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_charge_power": {
        "engine_attr": "battery_charge_power",
        "name": "Battery Charge Power",
        "icon": "mdi:battery-charging",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_discharge_power": {
        "engine_attr": "battery_discharge_power",
        "name": "Battery Discharge Power",
        "icon": "mdi:battery-minus",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    # Capteur net signé utile pour l'énergie dashboard
    "battery_net_power": {
        "engine_attr": "battery_net_power",
        "name": "Battery Net Power",
        "icon": "mdi:battery-arrow-up-outline",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "grid_import_power": {
        "engine_attr": "grid_import_power",
        "name": "Grid Import Power",
        "icon": "mdi:transmission-tower-import",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "grid_export_power": {
        "engine_attr": "grid_export_power",
        "name": "Grid Export Power",
        "icon": "mdi:transmission-tower-export",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "backup_output_power": {
        "engine_attr": "backup_output_power",
        "name": "Backup Output Power",
        "icon": "mdi:power-socket-eu",
        "unit": UnitOfPower.WATT,
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_soc": {
        "engine_attr": "battery_soc",
        "name": "Battery SOC",
        "icon": "mdi:battery",
        "unit": PERCENTAGE,
        "device_class": "battery",
        "state_class": "measurement",
    },
    "solar_energy_total": {
        "engine_attr": "solar_energy_total",
        "name": "Solar Energy Total",
        "icon": "mdi:solar-power",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": "energy",
        "state_class": "total_increasing",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    engine = SolarGenflowEngine(hass, entry)

    entities = [SolarGenflowStatusSensor()]
    for key, config in SENSOR_MAPPING.items():
        entities.append(SolarGenflowEngineSensor(engine, key, config))

    async_add_entities(entities, update_before_add=True)

    # FIX: rechargement automatique si les options changent
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))


async def _async_update_listener(hass, entry):
    """Recharge l'intégration quand les options sont modifiées."""
    await hass.config_entries.async_reload(entry.entry_id)


class SolarGenflowBaseEntity(SensorEntity):
    @property
    def device_info(self) -> DeviceInfo:
        return DEVICE_INFO


class SolarGenflowStatusSensor(SolarGenflowBaseEntity):
    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_unique_id = "solargenflow_status"
    _attr_native_value = "Running"
    _attr_icon = "mdi:solar-power"


class SolarGenflowEngineSensor(SolarGenflowBaseEntity):
    _attr_has_entity_name = True

    def __init__(self, engine, key, config):
        self.engine = engine
        self.config = config

        self._attr_unique_id = f"solargenflow_{key}"
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        self._attr_native_unit_of_measurement = config["unit"]
        self._attr_device_class = config["device_class"]
        self._attr_state_class = config["state_class"]

    @property
    def native_value(self):
        return getattr(self.engine, self.config["engine_attr"], 0)

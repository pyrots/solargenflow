import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN


CONF_PV_ENTITY = "pv_entity"
CONF_HOME_ENTITY = "home_entity"
CONF_EDF_POWER_ENTITY = "edf_power_entity"
CONF_BATTERY_SOC_ENTITY = "battery_soc_entity"
CONF_BATTERY_CHARGE_ENTITY = "battery_charge_entity"
CONF_BATTERY_DISCHARGE_ENTITY = "battery_discharge_entity"
CONF_BATTERY_NET_ENTITY = "battery_net_entity"
CONF_GRID_IMPORT_ENTITY = "grid_import_entity"
CONF_GRID_EXPORT_ENTITY = "grid_export_entity"
CONF_BACKUP_ENTITY = "backup_entity"
CONF_SOLAR_ENERGY_ENTITY = "solar_energy_entity"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="SolarGenflow", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SolarGenflowOptionsFlowHandler(config_entry)


class SolarGenflowOptionsFlowHandler(config_entries.OptionsFlow):
    # FIX: suppression de __init__ avec self._config_entry (déprécié HA 2024.x)
    # La classe parente expose self.config_entry automatiquement

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        sensor_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_PV_ENTITY, default=options.get(CONF_PV_ENTITY)): sensor_selector,
                vol.Optional(CONF_EDF_POWER_ENTITY, default=options.get(CONF_EDF_POWER_ENTITY)): sensor_selector,
                vol.Optional(CONF_BATTERY_SOC_ENTITY, default=options.get(CONF_BATTERY_SOC_ENTITY)): sensor_selector,
                vol.Optional(CONF_BATTERY_CHARGE_ENTITY, default=options.get(CONF_BATTERY_CHARGE_ENTITY)): sensor_selector,
                vol.Optional(CONF_BATTERY_DISCHARGE_ENTITY, default=options.get(CONF_BATTERY_DISCHARGE_ENTITY)): sensor_selector,
                vol.Optional(CONF_BATTERY_NET_ENTITY, default=options.get(CONF_BATTERY_NET_ENTITY)): sensor_selector,
                vol.Optional(CONF_GRID_IMPORT_ENTITY, default=options.get(CONF_GRID_IMPORT_ENTITY)): sensor_selector,
                vol.Optional(CONF_GRID_EXPORT_ENTITY, default=options.get(CONF_GRID_EXPORT_ENTITY)): sensor_selector,
                vol.Optional(CONF_BACKUP_ENTITY, default=options.get(CONF_BACKUP_ENTITY)): sensor_selector,
                vol.Optional(CONF_SOLAR_ENERGY_ENTITY, default=options.get(CONF_SOLAR_ENERGY_ENTITY)): sensor_selector,
                vol.Optional(CONF_HOME_ENTITY, default=options.get(CONF_HOME_ENTITY)): sensor_selector,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)

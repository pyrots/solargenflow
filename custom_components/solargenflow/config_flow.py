import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="SolarGenflow", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SolarGenflowOptionsFlowHandler(config_entry)


class SolarGenflowOptionsFlowHandler(config_entries.OptionsFlow):

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        sensor_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        )

        schema = vol.Schema({
            vol.Optional("pv_entity",               default=options.get("pv_entity", "")): sensor_selector,
            vol.Optional("pv1_entity",              default=options.get("pv1_entity", "")): sensor_selector,
            vol.Optional("pv2_entity",              default=options.get("pv2_entity", "")): sensor_selector,
            vol.Optional("pv3_entity",              default=options.get("pv3_entity", "")): sensor_selector,
            vol.Optional("pv4_entity",              default=options.get("pv4_entity", "")): sensor_selector,
            vol.Optional("edf_power_entity",        default=options.get("edf_power_entity", "")): sensor_selector,
            vol.Optional("battery_soc_entity",      default=options.get("battery_soc_entity", "")): sensor_selector,
            vol.Optional("battery_charge_entity",   default=options.get("battery_charge_entity", "")): sensor_selector,
            vol.Optional("battery_discharge_entity",default=options.get("battery_discharge_entity", "")): sensor_selector,
            vol.Optional("battery_net_entity",      default=options.get("battery_net_entity", "")): sensor_selector,
            vol.Optional("grid_import_entity",      default=options.get("grid_import_entity", "")): sensor_selector,
            vol.Optional("grid_export_entity",      default=options.get("grid_export_entity", "")): sensor_selector,
            vol.Optional("solarvault_output_entity",default=options.get("solarvault_output_entity", "")): sensor_selector,
            vol.Optional("solarvault_input_entity", default=options.get("solarvault_input_entity", "")): sensor_selector,
            vol.Optional("backup_entity",           default=options.get("backup_entity", "")): sensor_selector,
            vol.Optional("solar_energy_entity",     default=options.get("solar_energy_entity", "")): sensor_selector,
        })

        return self.async_show_form(step_id="init", data_schema=schema)

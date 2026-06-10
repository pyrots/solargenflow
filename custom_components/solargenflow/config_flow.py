import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN

OPTIONS_SCHEMA = {
    "pv_entity":              "sensor.jackery_solar_power",
    "pv1_entity":             "sensor.jackery_solar_power_pv1",
    "pv2_entity":             "sensor.jackery_solar_power_pv2",
    "pv3_entity":             "sensor.jackery_solar_power_pv3",
    "pv4_entity":             "sensor.jackery_solar_power_pv4",
    "edf_power_entity":       "sensor.shellypro3em_ac15187c8e84_phase_a_puissance",
    "battery_soc_entity":     "sensor.jackery_battery_soc",
    "battery_charge_entity":  "sensor.jackery_battery_charge_power_calc",
    "battery_discharge_entity": "sensor.jackery_battery_discharge_power_calc",
    "battery_net_entity":     "sensor.jackery_battery_net_power",
    "grid_import_entity":     "sensor.jackery_grid_import_power",
    "grid_export_entity":     "sensor.jackery_grid_export_power",
    "solarvault_output_entity": "sensor.jackery_home_power",
    "solarvault_input_entity":  "sensor.jackery_grid_import_power",
    "backup_entity":          "sensor.jackery_eps_output_power",
    "solar_energy_entity":    "sensor.jackery_solar_energy",
}


def _build_schema(defaults: dict) -> vol.Schema:
    return vol.Schema({
        vol.Optional(key, default=defaults.get(key, fallback)): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        )
        for key, fallback in OPTIONS_SCHEMA.items()
    })


class SolarGenflowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour SolarGenflow — crée une seule entrée."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="SolarGenflow", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    def async_get_options_flow(config_entry):
        return SolarGenflowOptionsFlow(config_entry)


class SolarGenflowOptionsFlow(config_entries.OptionsFlow):
    """Options flow — configure les capteurs sources."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = dict(self.config_entry.options)
        schema = _build_schema(current)

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

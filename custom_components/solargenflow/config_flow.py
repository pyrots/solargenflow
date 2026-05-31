import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN


OPTION_KEYS = [
    ("pv_entity",                "Production solaire (W)",              "sensor.jackery_solar_power"),
    ("edf_power_entity",         "Compteur réseau EDF / Shelly (W)",    "sensor.shellypro3em_ac15187c8e84_phase_a_puissance"),
    ("battery_soc_entity",       "État de charge batterie (%)",         "sensor.jackery_battery_soc"),
    ("battery_charge_entity",    "Puissance de charge batterie (W)",    "sensor.jackery_battery_charge_power"),
    ("battery_discharge_entity", "Puissance de décharge batterie (W)",  "sensor.jackery_battery_discharge_power"),
    ("battery_net_entity",       "Puissance nette batterie signée (W)", "sensor.jackery_battery_net_power"),
    ("grid_import_entity",       "Import réseau Jackery (W)",           "sensor.jackery_grid_import_power"),
    ("grid_export_entity",       "Export vers réseau Jackery (W)",      "sensor.jackery_grid_export_power"),
    ("solarvault_output_entity", "Sortie AC SolarVault → Maison (W)",   "sensor.jackery_home_power"),
    ("solarvault_input_entity",  "Entrée AC SolarVault ← EDF (W)",      "sensor.jackery_grid_import_power"),
    ("backup_entity",            "Puissance sortie EPS / backup (W)",   "sensor.jackery_eps_output_power"),
    ("solar_energy_entity",      "Énergie solaire totale (kWh)",        "sensor.jackery_solar_energy"),
]


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
            # Nettoyer les valeurs vides avant de sauvegarder
            cleaned = {k: v for k, v in user_input.items() if v}
            return self.async_create_entry(title="", data=cleaned)

        options = self.config_entry.options
        sensor_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        )

        schema_dict = {}
        for key, _label, _fallback in OPTION_KEYS:
            current = options.get(key)
            if current:
                schema_dict[vol.Optional(key, default=current)] = sensor_selector
            else:
                schema_dict[vol.Optional(key)] = sensor_selector

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )

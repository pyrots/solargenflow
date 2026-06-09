class SolarGenflowEngine:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

    def get_float_state(self, entity_id, default=0):
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable", None):
            return default
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return default

    def get_option_entity(self, key, fallback=None):
        return self.entry.options.get(key) or fallback

    # ─── Sources brutes ───────────────────────────────────────────────────────

    @property
    def pv_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "pv_entity",
                    "sensor.jackery_solar_power"
                )
            ),
            0,
        )

    @property
    def pv1_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "pv1_entity",
                    "sensor.jackery_solar_power_pv1"
                )
            ),
            0,
        )

    @property
    def pv2_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "pv2_entity",
                    "sensor.jackery_solar_power_pv2"
                )
            ),
            0,
        )

    @property
    def pv3_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "pv3_entity",
                    "sensor.jackery_solar_power_pv3"
                )
            ),
            0,
        )

    @property
    def pv4_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "pv4_entity",
                    "sensor.jackery_solar_power_pv4"
                )
            ),
            0,
        )

    @property
    def edf_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "edf_power_entity",
                    "sensor.shellypro3em_ac15187c8e84_phase_a_puissance",
                )
            ),
            0,
        )

    # ─── Batterie ────────────────────────────────────────────────────────────

    @property
    def battery_net_power(self):
        return self.get_float_state(
            self.get_option_entity(
                "battery_net_entity",
                "sensor.jackery_battery_net_power"
            )
        )

    @property
    def battery_charge_power(self):
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_charge_entity",
                "sensor.jackery_battery_charge_power_calc"
            )
        )

        if raw > 0:
            return raw

        return 0

    @property
    def battery_discharge_power(self):
        raw = self.get_float_state(
            self.get_option_entity(
                "battery_discharge_entity",
                "sensor.jackery_battery_discharge_power_calc"
            )
        )

        if raw > 0:
            return raw

        return 0

    @property
    def battery_soc(self):
        return self.get_float_state(
            self.get_option_entity(
                "battery_soc_entity",
                "sensor.jackery_battery_soc"
            )
        )

    # ─── Flux SolarVault ─────────────────────────────────────────────────────

    @property
    def solarvault_ac_output(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "solarvault_output_entity",
                    "sensor.jackery_home_power"
                )
            ),
            0,
        )

    @property
    def solarvault_ac_input(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "solarvault_input_entity",
                    "sensor.jackery_grid_import_power"
                )
            ),
            0,
        )

    @property
    def solarvault_ac_power(self):
        return self.solarvault_ac_output - self.solarvault_ac_input

    # ─── Réseau ──────────────────────────────────────────────────────────────

    @property
    def grid_import_power(self):
        return self.edf_power

    @property
    def grid_export_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "grid_export_entity",
                    "sensor.jackery_grid_export_power"
                )
            ),
            0,
        )

    # ─── Consommation maison ─────────────────────────────────────────────────

    @property
    def home_power(self):
        sv_out = self.solarvault_ac_output
        edf = self.edf_power

        if sv_out > 0:
            return sv_out + edf

        return max(
            self.pv_power
            - self.grid_export_power
            - self.battery_charge_power
            + self.battery_discharge_power
            + edf,
            0,
        )

    @property
    def home_load_total(self):
        return self.home_power

    # ─── Divers ──────────────────────────────────────────────────────────────

    @property
    def backup_output_power(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "backup_entity",
                    "sensor.jackery_eps_output_power"
                )
            ),
            0,
        )

    @property
    def solar_energy_total(self):
        return max(
            self.get_float_state(
                self.get_option_entity(
                    "solar_energy_entity",
                    "sensor.jackery_solar_energy"
                )
            ),
            0,
        )

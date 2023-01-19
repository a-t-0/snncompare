"""Verifies the Supported_experiment_settings object catches invalid
overwrite_sim_results specifications."""
# pylint: disable=R0801
import copy
import unittest

from typeguard import typechecked

from snncompare.exp_config.Supported_experiment_settings import (
    Supported_experiment_settings,
)
from snncompare.exp_config.verify_experiment_settings import verify_exp_config
from tests.exp_config.exp_config.test_generic_experiment_settings import (
    adap_sets,
    rad_sets,
    supp_exp_config,
    verify_invalid_config_sett_val_throws_error,
    with_adaptation_with_radiation,
)


class Test_overwrite_sim_results_settings(unittest.TestCase):
    """Tests whether the verify_exp_config_types function catches invalid
    overwrite_sim_results settings.."""

    # Initialize test object
    @typechecked
    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.supp_exp_config = Supported_experiment_settings()
        self.valid_overwrite_sim_results = (
            self.supp_exp_config.overwrite_sim_results
        )

        self.invalid_overwrite_sim_results_value = {
            "overwrite_sim_results": "invalid value of type string iso list of"
            + " floats",
        }

        self.supp_exp_config = supp_exp_config
        self.adap_sets = adap_sets
        self.rad_sets = rad_sets
        self.with_adaptation_with_radiation = with_adaptation_with_radiation

    @typechecked
    def test_error_is_thrown_if_overwrite_sim_results_key_is_missing(
        self,
    ) -> None:
        """Verifies an exception is thrown if the overwrite_sim_results key is
        missing from the configuration settings dictionary."""

        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.with_adaptation_with_radiation)

        # Remove key and value of m.
        exp_config.pop("overwrite_sim_results")

        with self.assertRaises(Exception) as context:
            verify_exp_config(
                self.supp_exp_config,
                exp_config,
                has_unique_id=False,
                allow_optional=False,
            )

        self.assertEqual(
            # "'overwrite_sim_results'",
            "Error:overwrite_sim_results is not in the configuration"
            + f" settings:{exp_config.keys()}",
            str(context.exception),
        )

    @typechecked
    def test_overwrite_sim_results_value_is_invalid_type(self) -> None:
        """Verifies an exception is thrown if the overwrite_sim_results
        dictionary value, is of invalid type.

        (Invalid types None, and string are tested, a list with floats
        is expected).
        """

        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.with_adaptation_with_radiation)
        expected_type = type(self.supp_exp_config.overwrite_sim_results)

        # Verify it throws an error on None and string.
        for invalid_config_setting_value in [None, ""]:
            exp_config["overwrite_sim_results"] = invalid_config_setting_value
            verify_invalid_config_sett_val_throws_error(
                invalid_config_setting_value,
                exp_config,
                expected_type,
                self,
                alternative_var_name="bool_setting",
            )

"""Parses the graph json files to recreate the graphs."""
from pprint import pprint
from typing import Dict

from typeguard import typechecked

from snncompare.exp_setts.run_config.Run_config import Run_config

from ..export_results.helper import run_config_to_filename
from ..export_results.load_json_to_nx_graph import dicts_are_equal
from ..export_results.verify_stage_1_graphs import assert_graphs_are_in_dict
from ..helper import get_extensions_list
from .read_json import load_results_from_json


@typechecked
def load_results_stage_1(
    run_config: Run_config,
) -> Dict:
    """Loads the experiment config, run config and graphs from the json file.

    # TODO: ensure it only loads the graphs of stage 1. OR: make all
    dict loading the same.
    """
    stage_index = 1

    # Get the json filename.
    filename = run_config_to_filename(run_config)
    relative_output_dir = "results/"
    extensions = get_extensions_list(run_config, stage_index)
    for extension in extensions:
        if extension == ".json":
            filepath = relative_output_dir + filename + extension

    stage_1_dict = load_results_from_json(filepath, run_config)

    # Split the dictionary into three separate dicts.
    # The ** loads the dict into the object.
    stage_1_dict["run_config"] = Run_config(**stage_1_dict["run_config"])

    # Verify the run_dict is valid.
    if not dicts_are_equal(
        run_config.__dict__,
        stage_1_dict["run_config"].__dict__,
        without_unique_id=True,
    ):
        print("Current run_config:")
        pprint(run_config)
        print("Loaded run_config:")
        pprint(stage_1_dict["run_config"].__dict__)
        raise Exception("Error, difference in run configs, see above.")

    # Verify the graph names are as expected for the graph name.
    assert_graphs_are_in_dict(run_config, stage_1_dict["graphs_dict"], 1)

    return stage_1_dict

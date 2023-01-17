"""Completes the tasks specified in the arg_parser."""
import argparse
import os
import shutil
from pprint import pprint
from typing import Dict

from snnbackends.plot_graphs import create_root_dir_if_not_exists
from typeguard import typechecked

from snncompare.exp_setts.Supported_experiment_settings import (
    Supported_experiment_settings,
)
from snncompare.exp_setts.verify_experiment_settings import (
    verify_experiment_config,
)
from snncompare.Experiment_runner import Experiment_runner

from ..exp_setts.custom_setts.run_configs.algo_test import (
    load_experiment_config_from_file,
)


@typechecked
def process_args(args: argparse.Namespace, custom_config_path: str) -> None:
    """Processes the arguments and ensures the accompanying tasks are executed.

    TODO: --graph-filepath
    TODO: --run-config
    TODO: list existing exp_configs
    TODO: list existing exp_configs
    """

    # mdsa_creation_only_size_3_4
    # mdsa_size3_5_m_0_5
    # mdsa_size3_m1
    # mdsa_size3_m0
    # mdsa_size5_m4
    # mdsa_size4_m0
    exp_setts: Dict = load_experiment_config_from_file(
        custom_config_path, args.experiment_settings_name
    )

    manage_export_parsing(args, exp_setts)
    manage_exp_setts_parsing(args, exp_setts)

    # if not args.overwrite_visualisation:
    #    exp_setts["export_images"] = True
    #    exp_setts["overwrite_images"] = True

    verify_experiment_config(
        Supported_experiment_settings(),
        exp_setts,
        has_unique_id=False,
        allow_optional=True,
    )

    # python -m src.snncompare -e mdsa_creation_only_size_3_4 -v
    Experiment_runner(exp_setts)
    # TODO: verify expected output results have been generated successfully.
    print("Done")


def manage_export_parsing(args: argparse.Namespace, exp_setts: Dict) -> None:
    """Performs the argument parsing related to data export settings."""
    create_root_dir_if_not_exists("latex/Images/graphs")
    supp_setts = Supported_experiment_settings()

    if args.delete_images and os.path.exists("latex"):
        shutil.rmtree("latex")

    if args.delete_results and os.path.exists("results"):
        shutil.rmtree("results")

    # By default export pdf, if exporting is on.
    if args.export_images == "export_images":
        exp_setts["export_images"] = True
        exp_setts["export_types"] = ["pdf"]
    # Don't export if it is not wanted.
    elif args.export_images is None:
        exp_setts["export_images"] = False
    # Allow user to specify image export types (and verify them).
    else:
        extensions = args.export_images.split(",")
        for extension in extensions:
            if extension in supp_setts.export_types:
                print(f"extensions={extensions}")
            else:
                raise Exception(
                    f"Error, image output extension:{extension} is"
                    " not supported."
                )
        exp_setts["export_images"] = True
        exp_setts["export_types"] = extensions

    # Determine whether user wants to pause computation to show images.
    if args.visualise_snn:
        exp_setts["show_snns"] = True
    else:
        exp_setts["show_snns"] = False


def manage_exp_setts_parsing(
    args: argparse.Namespace, exp_setts: Dict
) -> None:
    """Performs the argument parsing related to experiment settings."""
    # Process the graph_size argument.
    if args.graph_size is not None:
        if not isinstance(args.graph_size, int):
            raise TypeError("args.graphs_size should be int.")
        # Assume only one iteration is used if graph size is specified.
        exp_setts["size_and_max_graphs"] = [(args.graph_size, 1)]

    # Process the m_val argument.
    if args.m_val is not None:
        if not isinstance(args.m_val, int):
            raise TypeError("args.m_val should be int.")
        pprint(exp_setts)
        # Assume only one iteration is used if graph size is specified.
        exp_setts["algorithms"]["MDSA"] = [{"m_val": args.m_val}]

    # Process the m_val argument.
    if args.redundancy is not None:
        if not isinstance(args.redundancy, int):
            raise TypeError("args.redundancy should be int.")
        pprint(exp_setts)
        # Assume only one iteration is used if graph size is specified.
        exp_setts["adaptations"] = {"redundancy": [args.redundancy]}
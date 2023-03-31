"""Contains helper functions that are used throughout this repository."""
import copy
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import networkx as nx
import pylab as plt
from networkx.classes.graph import Graph
from simsnn.core.simulators import Simulator
from typeguard import typechecked

from snncompare.export_plots.plot_graphs import export_plot

if TYPE_CHECKING:
    pass


@typechecked
def generate_list_of_n_random_nrs(
    *, G: Graph, max_val: Optional[int] = None, seed: Optional[int] = None
) -> List[int]:
    """Generates list of numbers in range of 1 to (and including) len(G), or:

    Generates list of numbers in range of 1 to (and including) max, or:
    TODO: Verify list does not contain duplicates, throw error if it does.

    :param G: The original graph on which the MDSA algorithm is ran.
    :param max_val:  (Default value = None)
    :param seed: The value of the random seed used for this test.  (Default
    value = None)
    """
    if max_val is None:
        # Return the consecutive numbers in len(G) by default.
        return list(range(0, len(G)))
    if max_val == len(G) - 1:
        # TODO: remove this artifact.
        return list(range(0, len(G)))
    if max_val >= len(G):
        # Generate a too large list with numbers in range 0 to max_val.
        large_list = list(range(0, max_val))
        if seed is not None:
            random.seed(seed)
        # Return a random (with seed) sampling of len (G) from the previously
        # created large range within [0, max_val).
        return random.sample(large_list, len(G))
    raise ValueError(
        f"The max_val={max_val} is smaller than the graph size:{len(G)}."
    )


@typechecked
def compute_mark(*, input_graph: nx.Graph, rand_ceil: float) -> None:
    """Computes the mark at the counter neurons after the simulation is
    completed.

    TODO: move into algorithms module.
    """
    # Compute the mark based on degree+randomness=weight
    for node in input_graph.nodes:
        max_weight = max(
            input_graph.nodes[n]["weight"]
            for n in nx.all_neighbors(input_graph, node)
        )

        nr_of_max_weights = 0
        for n in nx.all_neighbors(input_graph, node):
            if (
                input_graph.nodes[n]["weight"] == max_weight
            ):  # Should all max weight neurons be marked or only one of them?
                # Read of the score from countermarks, not marks.
                input_graph.nodes[n]["marks"] += rand_ceil + 1
                input_graph.nodes[n]["countermarks"] += 1
                nr_of_max_weights = nr_of_max_weights + 1
                # Verify there is only one max weight neuron.
                if nr_of_max_weights > 1:
                    raise ValueError("Two numbers with identical max weight.")


@typechecked
def plot_alipour(
    *,
    configuration: str,
    seed: int,
    size: int,
    m: int,
    G: nx.DiGraph,
    export: bool = True,
    show: bool = False,
) -> None:
    """

    :param configuration:
    param iteration: The initialisation iteration that is used.
    :param seed: The value of the random seed used for this test.
    :param size: Nr of nodes in the original graph on which test is ran.
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    :param G: The original graph on which the MDSA algorithm is ran.
    :param export:  (Default value = True)
    :param show:  (Default value = False)

    """
    # pylint: disable=R0913
    # TODO: reduce 8/5 input arguments to at most 5/5.
    the_labels = get_alipour_labels(G=G, configuration=configuration)
    # nx.draw_networkx_labels(G, pos=None, labels=the_labels)
    npos = nx.circular_layout(
        G,
        scale=1,
    )
    nx.draw(G, npos, labels=the_labels, with_labels=True)
    if show:
        plt.show()
    if export:
        export_plot(
            plt,
            f"alipour_{seed}_size{size}_m{m}_iter_combined_"
            + f"{configuration}",
            extensions=["png"],  # TODO: include run_config extensions.
        )

    plt.clf()
    plt.close()


@typechecked
def get_alipour_labels(*, G: nx.DiGraph, configuration: str) -> Dict[str, str]:
    """

    :param G: The original graph on which the MDSA algorithm is ran.
    :param configuration:

    """
    labels = {}
    for node_name in G.nodes:
        if configuration == "0rand_mark":
            labels[node_name] = (
                f'{node_name},R:{G.nodes[node_name]["random_number"]}, M:'
                + f'{G.nodes[node_name]["marks"]}'
            )
        elif configuration == "1weight":
            labels[
                node_name
            ] = f'{node_name}, W:{G.nodes[node_name]["weight"]}'
        else:
            raise NotImplementedError("Unsupported configuration.")
    return labels


# checks if file exists
@typechecked
def file_exists(*, filepath: str) -> bool:
    """

    :param string:

    """
    # TODO: Execute Path(string).is_file() directly instead of calling this
    # function.
    my_file = Path(filepath)
    return my_file.is_file()


@typechecked
def compute_marks_for_m_larger_than_one(
    *,
    input_graph: nx.Graph,
    m: int,
    seed: int,
    size: int,
    rand_ceil: int,
    export: bool = False,
    show: bool = False,
) -> None:
    """Stores the marks in the counter nodes of the graph.."""
    # pylint: disable=R0913
    # TODO: reduce 10/5 arguments to at most 5/5.
    # Don't compute for m=0
    for loop in range(1, m + 1):
        for node in input_graph.nodes:
            # Compute the weights for this round of m.
            input_graph.nodes[node]["weight"] = (
                input_graph.nodes[node]["marks"]
                + input_graph.nodes[node]["random_number"]
            )

            # Reset marks.
            input_graph.nodes[node]["marks"] = 0
            input_graph.nodes[node]["countermarks"] = 0

        for node in input_graph.nodes:
            max_weight = max(
                input_graph.nodes[n]["weight"]
                for n in nx.all_neighbors(input_graph, node)
            )
            for n in nx.all_neighbors(input_graph, node):
                if input_graph.nodes[n]["weight"] == max_weight:
                    # Always raise mark always by (rand_ceil + 1) * delta
                    # (not by 1).
                    input_graph.nodes[n]["marks"] += rand_ceil + 1
                    input_graph.nodes[n]["countermarks"] += 1
        if show or export:
            plot_alipour(
                configuration="0rand_mark",
                seed=seed,
                size=size,
                m=loop,
                G=input_graph,
                show=show,
            )
            plot_alipour(
                configuration="1weight",
                seed=seed,
                size=size,
                m=loop,
                G=input_graph,
                show=show,
            )
            plot_alipour(
                configuration="2inhib_weight",
                seed=seed,
                size=size,
                m=loop,
                G=input_graph,
                show=show,
            )


@typechecked
def set_node_default_values(
    *,
    input_graph: nx.Graph,
    node: int,
    rand_ceil: float,
    uninhibited_spread_rand_nrs: List[float],
) -> None:
    """Initialises the starting values of the node attributes."""
    # pylint: disable=R0913
    # TODO: reduce 6/5 arguments to at most 5/5.
    # Initialise values.
    # G.nodes[node]["marks"] = 0
    input_graph.nodes[node]["marks"] = input_graph.degree(node) * (
        rand_ceil + 1
    )
    input_graph.nodes[node]["countermarks"] = 0
    input_graph.nodes[node]["random_number"] = (
        1 * uninhibited_spread_rand_nrs[node]
    )
    input_graph.nodes[node]["weight"] = (
        input_graph.degree(node) * (rand_ceil + 1)
        + input_graph.nodes[node]["random_number"]
    )


@typechecked
def add_stage_completion_to_graph(
    *, snn: Union[nx.Graph, Simulator], stage_index: int
) -> None:
    """Adds the completed stage to the list of completed stages for the
    incoming graph."""
    if isinstance(snn, Simulator):
        graph = snn.network.graph
    else:
        graph = snn
    # Initialise the completed_stages key.
    if stage_index == 1:
        if "completed_stages" in graph.graph:
            raise ValueError(
                "Error, the completed_stages parameter is"
                + f"already created for stage 1{graph.graph}:"
            )
        graph.graph["completed_stages"] = []
    # After stage 1, the completed_stages key should already be a list.
    elif not isinstance(graph.graph["completed_stages"], list):
        raise TypeError(
            "Error, the completed_stages parameter is not of type"
            + "list. instead, it is of type:"
            + f'{type(graph.graph["completed_stages"])}'
        )
    # At this point, the completed_stages key should not contain the current
    # stage index already..
    if stage_index in graph.graph["completed_stages"]:
        raise ValueError(
            f"Error, the stage:{stage_index} is already in the completed_stage"
            f's: {graph.graph["completed_stages"]}'
        )

    # Add the completed stages key to the snn graph.
    graph.graph["completed_stages"].append(stage_index)


@typechecked
def get_max_sim_duration(  # type:ignore[misc]
    *,
    input_graph: nx.Graph,
    run_config: Any,
) -> int:
    """Compute the simulation duration for a given algorithm and graph."""
    for algo_name, algo_settings in run_config.algorithm.items():
        if algo_name == "MDSA":
            # TODO: Move into stage_1 get input graphs.
            sim_time: int = int(
                len(input_graph)
                * (len(input_graph) + 1)
                * ((algo_settings["m_val"]) + 1)  # +_6 for delay
            )
            return sim_time
        raise NotImplementedError(
            f"Error, algo_name:{algo_name} is not (yet) supported."
        )
    raise ValueError("Error, the simulation time was not found.")


@typechecked
def get_some_duration(
    *,
    simulator: str,
    snn_graph: Union[nx.DiGraph, Simulator],
    duration_name: str,
) -> int:
    """Compute the simulation duration for a given algorithm and graph."""
    if simulator == "simsnn":
        if duration_name not in snn_graph.network.graph.graph:
            if duration_name == "actual_duration":
                return len(snn_graph.multimeter.V)
            raise ValueError(
                f"Error, {duration_name} not found in simsnn graph."
            )
        return snn_graph.network.graph.graph[duration_name]
    if simulator == "nx":
        return snn_graph.graph[duration_name]
    raise NotImplementedError(f"Error, simulator:{simulator} not implemented.")


@typechecked
def get_expected_stages(
    *,
    stage_index: int,
) -> List[int]:
    """Computes which stages should be expected at this stage of the
    experiment."""
    expected_stages = list(range(1, stage_index + 1))
    # stage 3 is checked on completeness by looking if image files exist.
    if 3 in expected_stages:
        expected_stages.remove(3)

    # Sort and remove dupes.
    return list(set(sorted(expected_stages)))


@typechecked
def dicts_are_equal(
    *, left: Dict, right: Dict, without_unique_id: bool
) -> bool:
    """Determines whether two run configurations are equal or not."""
    if without_unique_id:
        left_copy = copy.deepcopy(left)
        right_copy = copy.deepcopy(right)
        if "unique_id" in left_copy:
            left_copy.pop("unique_id")
        if "unique_id" in right_copy:
            right_copy.pop("unique_id")
        return left_copy == right_copy
    return left == right


@typechecked
def get_with_adaptation_bool(*, graph_name: str) -> bool:
    """Returns True if the graph name belongs to a graph that has adaptation,
    returns False otherwise."""
    if graph_name in ["adapted_snn_graph", "rad_adapted_snn_graph"]:
        return True
    if graph_name in ["snn_algo_graph", "rad_snn_algo_graph"]:
        return False
    raise NotImplementedError(f"Error, {graph_name} is not supported.")


@typechecked
def get_with_radiation_bool(*, graph_name: str) -> bool:
    """Returns True if the graph name belongs to a graph that has radiation,
    returns False otherwise."""
    if graph_name in ["rad_snn_algo_graph", "rad_adapted_snn_graph"]:
        return True
    if graph_name in ["snn_algo_graph", "adapted_snn_graph"]:
        return False
    raise NotImplementedError(f"Error, {graph_name} is not supported.")


def get_snn_graph_from_graphs_dict(
    with_adaptation: bool,
    with_radiation: bool,
    graphs_dict: Dict[str, Union[nx.DiGraph, Simulator]],
) -> Union[nx.DiGraph, Simulator]:
    """Returns the snn graph corresponding to the adaptation and radiation
    configuration."""
    graph_name: str = get_snn_graph_name(
        with_adaptation=with_adaptation, with_radiation=with_radiation
    )
    return graphs_dict[graph_name]


def get_snn_graph_name(
    with_adaptation: bool, with_radiation: bool
) -> Union[nx.DiGraph, Simulator]:
    """Returns the snn graph name corresponding to the adaptation and radiation
    configuration."""
    if with_adaptation:
        if with_radiation:
            return "rad_adapted_snn_graph"
        return "adapted_snn_graph"

    if with_radiation:
        return "rad_snn_algo_graph"
    return "snn_algo_graph"


def get_snn_graph_names() -> List[str]:
    """Returns the 4 graph names: rad_adapted_snn_graph adapted_snn_graph
    rad_snn_algo_graph snn_algo_graph.

    in some order.
    """
    graph_names: List[str] = []
    for with_adaptation in [False, True]:
        for with_radiation in [False, True]:
            graph_name: str = get_snn_graph_name(
                with_adaptation=with_adaptation, with_radiation=with_radiation
            )
            graph_names.append(graph_name)
    return graph_names

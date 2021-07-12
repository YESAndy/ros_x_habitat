import numpy as np
from habitat.config import Config
from habitat.config.default import get_config
from typing import List, Tuple, Dict
from collections import defaultdict
from src.evaluators.evaluator import Evaluator
from src.utils import utils_logging


class HabitatSimEvaluator(Evaluator):
    r"""Abstract class for evaluating an agent in a Habitat simulation
    environment either with or without physics.

    Users should instantiate subclasses to 'HabitatSimEvaluator' for
    evaluation.
    """

    def __init__(
        self,
        config_paths: str,
        input_type: str,
        model_path: str,
        enable_physics: bool = False,
    ):
        # store experiment settings
        self.config = get_config(config_paths)
        self.input_type = input_type
        self.model_path = model_path
        self.enable_physics = enable_physics

    @classmethod
    def overwrite_simulator_config(cls, config):
        r"""
        Overwrite simulator and task configurations when physics is enabled.
        :param config: environment config to be overwritten.
        """
        for k in config.PHYSICS_SIMULATOR.keys():
            if isinstance(config.PHYSICS_SIMULATOR[k], Config):
                for inner_k in config.PHYSICS_SIMULATOR[k].keys():
                    config.SIMULATOR[k][inner_k] = config.PHYSICS_SIMULATOR[k][inner_k]
            else:
                config.SIMULATOR[k] = config.PHYSICS_SIMULATOR[k]
        try:
            from habitat.sims.habitat_simulator.habitat_simulator import (
                HabitatSim,
            )
            from src.sims.habitat_physics_simulator import HabitatPhysicsSim
            from src.tasks.habitat_physics_task import PhysicsNavigationTask
            from habitat.sims.habitat_simulator.actions import (
                HabitatSimV1ActionSpaceConfiguration,
            )
        except ImportError as e:
            print("Import HSIM failed")
            raise e

        return

    @classmethod
    def compute_avg_metrics(
        cls,
        dict_of_metrics: Dict[str, Dict[str, float]],
    ) -> Dict:
        r"""
        Compute average metrics from a list of metrics.
        :param dict_of_metrics: a collection of metrics for which a key
            identifies an episode, a value contains a dictionary of metrics
            from that episode. Each metrics dictionary should contain only
            numerically-valued metrics.
        :returns: average metrics as a dictionary.
        """
        agg_metrics: Dict = defaultdict(float)
        for _, metrics in dict_of_metrics.items():
            for m, v in metrics.items():
                agg_metrics[m] += v
        avg_metrics = {k: v/len(dict_of_metrics) for k, v in agg_metrics.items()}
        return avg_metrics

    @classmethod
    def extract_metrics(
        cls,
        dict_of_metrics: Dict[str, Dict[str, float]],
        metric_names: List[str],
    ) -> Dict[str, Dict[str, float]]:
        r"""
        Extract specified metrics from dict_of_metrics and return.
        :param dict_of_metrics: A dictionary of metrics from many episodes.
        :param metric_names: Names of metrics to extract. Each metric must
            have already been collected.
        :return: A dictionary of metrics from the same episodes, but contains
            only metrics with names specified in `metric_names`.
        """
        new_dict_of_metrics = {}
        for episode_identifier, episode_metrics in dict_of_metrics.items():
            new_dict_of_metrics[episode_identifier] = {
                metric_name: episode_metrics[metric_name] for metric_name in metric_names
            }
        return new_dict_of_metrics

    def generate_video(
        self, episode_id: str, scene_id: str, agent_seed: int = 7, *args, **kwargs
    ) -> None:
        r"""
        Evaluate the episode of given episode ID and scene ID, and save the video to <video_dir>/.

        :param episode_id: ID of the episode
        :param scene_id: ID of the scene
        :param agent_seed: seed for initializing agent
        """
        raise NotImplementedError

    def generate_map(
        self,
        episode_id: str,
        scene_id: str,
        agent_seed: int,
        map_height: int,
        *args,
        **kwargs
    ) -> np.ndarray:
        r"""
        Evaluate the episode of given episode ID and scene ID, with agent initialized by the
        given seed. Return the top-down map.

        :param episode_id: ID of the episode
        :param scene_id: ID of the scene
        :param agent_seed: seed for initializing agent
        :param map_height: desired height of the map

        :returns: Top-down map with initial/goal position, shortest path and actual path.
        """
        raise NotImplementedError

    def evaluate_and_get_maps(
        self,
        episode_id_last: str = "-1",
        scene_id_last: str = "data/scene_datasets/habitat-test-scenes/skokloster-castle.glb",
        log_dir: str = "logs/",
        map_height: int = 200,
        *args,
        **kwargs,
    )-> Dict[str, Dict[str, float]]:
        r"""..
        Evaluate over episodes, starting from the last episode evaluated. Return evaluation
        metrics and top-down maps from the episodes.

        :param episode_id_last: ID of the last episode evaluated; -1 for evaluating
            from start
        :param scene_id_last: Scene ID of the last episode evaluated
        :param log_dir: logging directory
        :param map_height: height of top-down maps
        :return: a dictionary where each key is an episode's unique identifier as
            <episode-id>,<scene-id>; each value is the set of metrics (including top-down maps)
            from the episode.
        """
        raise NotImplementedError
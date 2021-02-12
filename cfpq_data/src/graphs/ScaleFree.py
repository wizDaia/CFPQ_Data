from itertools import product
from pathlib import Path
from typing import Tuple

import rdflib
import numpy as np
from tqdm import tqdm

from cfpq_data.src.graphs.RDF import RDF
from cfpq_data.src.tools.CmdParser import CmdParser
from cfpq_data.src.utils import add_graph_dir, add_rdf_edge, write_to_rdf

SCALEFREE_GRAPH_TO_GEN = list(product(
    [100, 500, 2500, 10000]
    , [1, 3, 5, 10]
))


class ScaleFree(RDF, CmdParser):
    """
    ScaleFree — graphs generated by using the Barab'asi-Albert model of scale-free networks

    - graphs: already builded graphs
    """

    graphs = {}

    @classmethod
    def build(cls, vertices_number: int, vertices_degree: int):
        """
        Builds ScaleFree graph instance by number of vertices and degree of vertex

        :param vertices_number: number of vertices in the graph
        :type vertices_number: int
        :param vertices_degree: degree of the vertex in the graph
        :type vertices_degree: int
        :return: ScaleFree graph instance
        :rtype: ScaleFree
        """

        path_to_graph = gen_scale_free_graph(add_graph_dir('ScaleFree'), vertices_number, vertices_degree)

        return ScaleFree.load_from_rdf(path_to_graph)

    @staticmethod
    def init_cmd_parser(parser):
        """
        Initialize command line parser

        :param parser: ScaleFree subparser of command line parser
        :type parser: ArgumentParser
        :return: None
        :rtype: None
        """

        parser.add_argument(
            '-p'
            , '--preset'
            , action='store_true'
            , help='Load preset ScaleFree graphs from dataset'
        )
        parser.add_argument(
            '-n'
            , '--vertices_number'
            , required=False
            , type=int
            , help='Number of vertices of ScaleFree graph'
        )
        parser.add_argument(
            '-k'
            , '--vertices_degree'
            , required=False
            , type=int
            , help='Degree of vertices in a graph'
        )

    @staticmethod
    def eval_cmd_parser(args):
        """
        Evaluate command line parser

        :param args: command line arguments
        :type args: Namespace
        :return: None
        :rtype: None
        """

        if args.preset is False and \
                (args.vertices_number is None or args.vertices_degree is None):
            print("One of -p/--preset, (-n/--vertices_number and necessarily -k/--vertices_degree) required")
            exit()

        if args.preset is True:
            for n, k in tqdm(SCALEFREE_GRAPH_TO_GEN, desc='ScaleFree graphs generation'):
                ScaleFree.build(n, k).save_metadata()

        if args.vertices_number is not None and args.vertices_degree is not None:
            graph = ScaleFree.build(args.vertices_number, args.vertices_degree)
            graph.save_metadata()
            print(f'Generated {graph.basename} to {graph.dirname}')


def gen_scale_free_graph(
        destination_folder: Path
        , vertices_number: int
        , vertices_degree: int
        , labels: Tuple[str, ...] = ('A', 'B', 'C', 'D')
) -> Path:
    """
    Generates scale free graph
    
    :param destination_folder: directory to save the graph
    :type destination_folder: Path
    :param vertices_number: number of vertices in the graph
    :type vertices_number: int
    :param vertices_degree: degree of a vertex in the graph
    :type vertices_degree: int
    :param labels: edge labels in the graph
    :type labels: Tuple[str, ...]
    :return: path to generated graph
    :rtype: Path
    """

    g = {
        i: [(j, np.random.choice(labels)) for j in range(vertices_degree)]
        for i in range(vertices_degree)
    }

    degree = [3] * vertices_degree

    for i in range(vertices_degree, vertices_number):
        to_vertices = np.random.choice(
            range(i)
            , size=vertices_degree
            , replace=False
            , p=np.array(degree) / sum(degree)
        )

        g[i] = []
        degree.append(0)
        for to in to_vertices:
            label = np.random.choice(labels)
            g[i].append((to, label))
            degree[to] += 1
            degree[i] += 1

    output_graph = rdflib.Graph()

    edges = list()

    for v in g:
        for to in g[v]:
            edges.append((v, to[1], to[0]))

    for subj, pred, obj in tqdm(edges, desc=f'scale_free_graph_{vertices_number}_{vertices_degree} generation'):
        add_rdf_edge(subj, pred, obj, output_graph)

    target = destination_folder / f'scale_free_graph_{vertices_number}_{vertices_degree}.xml'

    write_to_rdf(target, output_graph)

    return target

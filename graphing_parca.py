import json
import networkx as nx

with open("reconstruction/ecoli/parca_map.json", "r") as file:
    parca_map = json.load(file)

G = nx.Graph()
DG = nx.DiGraph()

DG.add_nodes_from([("input_adjustments", {"type": "outer"})])


for func, simdict in parca_map["input_adjustments"].items():
    DG.add_nodes_from([(func, {"type": "inner"})])
    DG.add_edge(func, "input_adjustments")
    for simd in simdict.keys():
        broken = simd.split('.')
        for i in range(len(broken)-1):
            if broken[i] != "sim_data" and broken[i] != "*sim_data":
                DG.add_nodes_from([(broken[i], {"type": "simd"}), (broken[i+1], {"type": "simd"})])
            else:
                DG.add_nodes_from([(broken[i], {"type": "simdata"}), (broken[i+1], {"type": "simd"})])
            DG.add_edge(broken[i], broken[i+1])
        DG.add_edge(broken[-1], func)
nx.write_graphml(DG, "runscripts/di_input_adjustments_graph.graphml")


# G = nx.Graph()


# for outer, value in parca_map.items():
#     G.add_nodes_from([(outer, {"type": "outer"})])
#     for inner, val in value.items():
#         G.add_nodes_from([(inner, {"type": "inner"})])
#         if inner != "EXTERNAL":
#             G.add_edge(inner, outer)
#             for simd in val.keys():
#                 G.add_nodes_from([(simd, {"type": "simd"})])
#                 G.add_edge(simd, inner)
#         else:
#             for simd in val.keys():
#                 G.add_nodes_from([(simd, {"type": "simd"})])
#                 G.add_edge(simd, outer)
# nx.write_graphml(G, "runscripts/parca_graph.graphml")

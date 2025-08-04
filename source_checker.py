import ast 
import _pickle as pickle
from pprint import pprint
import json

with open("reconstruction/ecoli/fit_sim_data_1.py", "r") as file:
    parca_data = file.read()

with open("ecoli/library/initial_conditions.py", "r") as file:
    bulk_data = file.read().split("def initialize_bulk_counts")[0]

iodict = dict()
lines_visited = dict()

class VarTracker(ast.NodeVisitor):
    def visit_name(self, node, lines_visited):
        if node.id == "sim_data":
            broken = parca_data.split('\n')
            data_attrs = broken[node.lineno-1].split('sim_data.')
            if len(data_attrs) > 1:
                if node.lineno not in lines_visited:
                    lines_visited[node.lineno] = 1
                    member = data_attrs[1].split(' ')[0]
                else:
                    lines_visited[node.lineno] += 1
                    member = data_attrs[lines_visited[node.lineno]].split(' ')[0]
                if isinstance(node.ctx, ast.Load):
                    if member in iodict.keys():
                        iodict[member].add("Read")
                    else:
                        iodict[member] = set(["Read"])
                elif isinstance(node.ctx, ast.Store):
                    if member in iodict.keys():
                        iodict[member].add("Write")
                    else:
                        iodict[member] = set(["Write"])
        self.generic_visit(node)

    def visit_Attribute(self, node, func=False):
        if node.attr in set(["items", "keys", "get", "dot"]):
            self.visit(node.value)
        else:
            ourpath = [node.attr]
            locval = node.value
            while isinstance(locval, ast.Attribute):
                ourpath.insert(0, locval.attr)
                locval = locval.value
            if isinstance(locval, ast.Name):
                if locval.id == "sim_data":
                    tostr = ""
                    for i in range(len(ourpath)):
                        tostr += ourpath[i]
                        if i != len(ourpath) - 1:
                            tostr += "."
                    if func:
                        iodict[tostr] = set(["Method"])
                    else:
                        if isinstance(node.ctx, ast.Load):
                            if tostr in iodict.keys():
                                iodict[tostr].add("Read")
                            else:
                                iodict[tostr] = set(["Read"])
                        elif isinstance(node.ctx, ast.Store):
                            if tostr in iodict.keys():
                                iodict[tostr].add("Write")
                            else:
                                iodict[tostr] = set(["Write"])
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in set(["get", "astype", "dot"]):
                self.visit(node.func.value)
            else:
                self.visit_Attribute(node.func, func=True)
        else:
            self.generic_visit(node)

    def visit(self, node):
        if isinstance(node, ast.Call):
            if node.lineno == 775:
                pass
            self.visit_Call(node)
        if isinstance(node, ast.Attribute):
            if node.lineno == 2368:
                pass
            self.visit_Attribute(node)
        # if isinstance(node, ast.Name):
        #     if node.lineno > 244:
        #         pass
        #     self.visit_name(node, lines_visited)
        else:
            self.generic_visit(node)



data = """
x=1
y=2
print(x+y)
def hello():
    z=2
    y = z+5
"""

bulk_tree = ast.parse(bulk_data)

tree = ast.parse(parca_data)
tracker = VarTracker()
tracker.visit(tree)
tracker.visit(bulk_tree)
# pprint(iodict)

with open("reconstruction/ecoli/parca_map.json", "r") as file:
    data = json.load(file)



ourset = set()

for outer, innercol in data.items():
    for inner, simlist in innercol.items():
        thisdict = dict()
        for val in simlist:
            ourset.add(val.split("sim_data.")[1])
            try: 
                thisdict[val] = list(iodict[val.split("sim_data.")[1]])
            except KeyError:
                print(f"{val} not found in AST map.")
        innercol[inner] = thisdict

# with open("reconstruction/ecoli/parca_map.json", "w") as file:
#     json.dump(data, file)

print(f"ParcaMap total set length: {len(ourset)}")

print(f"AST map total set length: {len(iodict)}")

print("\n" + "-"*50 + "\n")

print("Items in ParcaMap not in AST map:")
pprint(ourset.difference(set(iodict.keys())))
print("\n" + "-"*50 + "\n")

print("Items in AST map not in ParcaMap:")
pprint(set(iodict.keys()).difference(ourset))

# import json
# import sys
# import os
# from pprint import pprint
# import _pickle as pickle
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# with open("reconstruction/ecoli/simulation_data.py", "r") as file:
#     contents = file.read().split('def calculate_ppgpp_expression')[0]

# with open("reconstruction/sim_data/kb/simData.cPickle", "rb") as file:
#     unpick = pickle.Unpickler(file)
#     data = unpick.load()

# attrs = contents.split('self.')
# attrs.pop(0)
# attr_set = set()

# for portion in attrs:
#     attr = portion.split(' ')[0]
#     if not "(" in attr:
#         attr_set.add(attr.strip().split('[')[0].strip(']').strip(')').strip(':'))

# simkeys = set()
# for key in dir(data):
#     if not key.startswith("__"):
#         simkeys.add(key)


# pprint(simkeys.difference(attr_set))
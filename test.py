from subdiv import HalfEdgeStructure
from obj_parser import *

hs = HalfEdgeStructure()

vs, fs = load_obj_to_vflist("./model/Manifold/menger1.obj")
print(len(vs), len(fs))
hs.parse_vf(vs, fs)
hs.subdiv()
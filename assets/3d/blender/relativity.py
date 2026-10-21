import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from common import *
OUT = sys.argv[-1]
reset(); random.seed(7)
# units: 1 Blender unit = 1 km

ground = mat("GroundTop", (0.05,0.10,0.16,1), rough=0.75)
rock   = mat("Rock", (0.025,0.045,0.07,1), rough=0.85)
stra   = mat("Strata", (0.06,0.13,0.22,1), rough=0.6, emit=(0.05,0.25,0.6,1), emit_str=0.25)
air    = mat("Air", (0.3,0.6,1,1), rough=0.3, alpha=0.07, emit=(0.0,0.5,1,1), emit_str=0.15)
prim   = mat("Primary", (1,0.8,0.5,1), emit=(1.0,0.72,0.32,1), emit_str=4)
shower = mat("Shower", (0.6,0.7,1,1), emit=(0.55,0.65,1.0,1), emit_str=2.5)
muRel  = mat("MuonRel", (0,0.66,0.96,1), emit=(0.0,0.66,0.96,1), emit_str=4)
muCls  = mat("MuonClassical", (0.7,0.75,0.8,1), emit=(0.75,0.8,0.86,1), emit_str=2.2)
decay  = mat("Decay", (1,0.71,0.28,1), emit=(1.0,0.71,0.28,1), emit_str=7)
det    = mat("DetectorGlow", (0.13,0.32,1,1), emit=(0.13,0.32,1.0,1), emit_str=5)
tick   = mat("Ruler", (0.55,0.65,0.78,1), rough=0.4, emit=(0.4,0.55,0.75,1), emit_str=0.6)

W, D = 10.0, 6.0
# ── earth block with strata ──
box("Earth", (W,D,1.56), (0,0,-0.82), rock, bevel=0.06)
box("Surface", (W+0.02,D+0.02,0.08), (0,0,-0.04), ground, bevel=0.03)
for i,z in enumerate((-0.45,-0.9,-1.3)):
    box(f"Stratum{i}", (W+0.03,D+0.03,0.035), (0,0,z), stra)

# ── atmosphere slabs ──
for i,z in enumerate((3,6,9,12,15)):
    box(f"Air{i}", (W,D,0.02), (0,0,z), air)

# ── primary + shower ──
birth = (0.0,0.0,15.0)
tube_curve("PrimaryRay", [(-0.9,0.3,19.5), birth], 0.05, prim)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=birth, segments=24, ring_count=12)
s = bpy.context.active_object; s.name = "Collision"; s.data.materials.append(prim)
bpy.ops.object.shade_smooth()
for k in range(9):
    a = random.uniform(0, 2*math.pi); r = random.uniform(1.0, 2.6); L = random.uniform(2.0, 4.0)
    end = (birth[0]+r*math.cos(a), birth[1]+r*math.sin(a)*0.6, birth[2]-L)
    tube_curve(f"Shower{k}", [birth, end], 0.018, shower)

# ── muon paths ──
detp  = (1.6,0.0,0.06)
# classical: travels c·τ ≈ 0.66 km and decays
dirv = [detp[i]-birth[i] for i in range(3)]; Ln = math.sqrt(sum(v*v for v in dirv))
u = [v/Ln for v in dirv]
cls_dir = (-0.12, 0.0, -1.0); n = math.sqrt(sum(c*c for c in cls_dir)); cls_dir=[c/n for c in cls_dir]
decp = tuple(birth[i] + 0.66*cls_dir[i]*1.0 for i in range(3))
tube_curve("MuonClassical", [birth, decp], 0.035, muCls)
for k,(dx,dz) in enumerate(((-0.5,-0.25),(0.3,-0.45),(-0.15,0.35))):
    tube_curve(f"DecayProd{k}", [decp, (decp[0]+dx, decp[1]+0.1*k, decp[2]+dz)], 0.014, decay)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.16, location=decp, subdivisions=2)
x = bpy.context.active_object; x.name="DecayPoint"; x.data.materials.append(decay)
# relativistic: reaches the ground detector
tube_curve("MuonRel", [birth, detp], 0.05, muRel)

# ── detector on the surface ──
box("DetectorBase", (0.9,0.9,0.08), (detp[0],0,0.04), rock, bevel=0.02)
box("DetectorA", (0.62,0.62,0.06), (detp[0],0,0.22), det, bevel=0.01)
box("DetectorB", (0.62,0.62,0.06), (detp[0],0,0.12), det, bevel=0.01)

# ── altitude ruler ──
rx, ry = -W/2+0.35, -D/2+0.35
cyl("Ruler", 0.025, 15.0, (rx,ry,7.5), tick, 12)
for zk in (0,5,10,15):
    box(f"Tick{zk}", (0.35,0.03,0.03), (rx+0.17,ry,zk), tick)

for nm,p in (("P_birth",birth),("P_decay",decp),("P_det",(detp[0],0,0.28)),
             ("P_top",(-0.9,0.3,19.5)),("LBL_r0",(rx,ry,0)),("LBL_r5",(rx,ry,5)),
             ("LBL_r10",(rx,ry,10)),("LBL_r15",(rx,ry,15))):
    empty(nm, p)

export_glb(os.path.join(OUT,"relativity.glb"))

world((0.005,0.016,0.03), 0.5)
area_light("Key",  (-14,-16,24), (0,0,6), 9000, 10, (1,0.96,0.9))
area_light("Rim",  (10,14,18),   (0,0,6), 6000, 10, (0.3,0.55,1))
camera((22,-26,15), (0.4,0,7.6), lens=42)
render(os.path.join(OUT,"relativity.png"), 900, 1100, samples=int(os.environ.get("SAMPLES","64")))

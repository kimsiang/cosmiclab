import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from common import *
OUT = sys.argv[-1]
reset()

alu   = mat("Aluminium", (0.62,0.66,0.72,1), metal=1.0, rough=0.32)
anod  = mat("Anodised", (0.035,0.05,0.075,1), metal=0.85, rough=0.38)
scint = mat("Scintillator", (0.30,0.62,1.0,1), rough=0.06, transmission=0.85, ior=1.58,
            emit=(0.0,0.45,1.0,1), emit_str=1.1)
wrap  = mat("Wrap", (0.02,0.03,0.05,1), rough=0.7)
pcb   = mat("PCB", (0.02,0.09,0.07,1), rough=0.45, coat=0.6)
sipm  = mat("SiPM", (0.75,0.78,0.82,1), metal=0.9, rough=0.18, emit=(0.4,0.7,1,1), emit_str=0.0)
cable = mat("Cable", (0.012,0.014,0.02,1), rough=0.55)
unit  = mat("Housing", (0.03,0.06,0.11,1), rough=0.42, coat=0.4)
screen= mat("Screen", (0,0,0,1), rough=0.2, emit=(0.0,0.62,0.96,1), emit_str=3.0)
ledOn = mat("LED_on", (0.1,0.3,1,1), emit=(0.13,0.32,1.0,1), emit_str=12.0)
ledOff= mat("LED_off", (0.2,0.22,0.25,1), rough=0.3)
lapS  = mat("LaptopScreen", (0,0,0,1), rough=0.15, emit=(0.02,0.12,0.30,1), emit_str=2.5)

# ── frame ──
box("BasePlate", (0.27,0.27,0.012), (0,0,0.006), anod, bevel=0.003)
for i,(x,y) in enumerate([(-.115,-.115),(.115,-.115),(.115,.115),(-.115,.115)]):
    box(f"Post{i}", (0.02,0.02,0.34), (x,y,0.012+0.17), alu, bevel=0.002)
box("TopPlate", (0.27,0.27,0.008), (0,0,0.356), anod, bevel=0.003)
for i,(x,y) in enumerate([(-.115,-.115),(.115,-.115),(.115,.115),(-.115,.115)]):
    cyl(f"Foot{i}", 0.014, 0.008, (x,y,-0.002), cable, 24)

# ── scintillator planes ──
for tag,z in (("A",0.235),("B",0.125)):
    box(f"Scint{tag}", (0.15,0.15,0.012), (0,0,z), scint, bevel=0.0015)
    for s in (-1,1):   # holder rails between posts, with tabs under the tile
        box(f"Rail{tag}{s}", (0.21,0.012,0.006), (0, s*0.115, z-0.009), alu, bevel=0.001)
        for x in (-0.05,0.05):
            box(f"Tab{tag}{s}{x}", (0.016,0.05,0.004), (x, s*0.094, z-0.008), alu, bevel=0.0008)
    # SiPM readout board on +x edge
    box(f"PCB{tag}", (0.006,0.05,0.026), (0.082,0,z), pcb, bevel=0.0008)
    box(f"SiPM{tag}", (0.0015,0.008,0.008), (0.0782,0,z), sipm)
    tube_curve(f"Cable{tag}", [(0.086,0,z),(0.13,0.02,z+0.02),(0.1,0.05,0.30),(0.06,0.04,0.375)], 0.0022, cable)

# ── control unit on top ──
box("ControlUnit", (0.17,0.1,0.048), (0,0,0.36+0.024), unit, bevel=0.006, segs=4)
box("Screen", (0.07,0.002,0.022), (0.025,-0.0505,0.386), screen, bevel=0.0006)
cyl("LED0", 0.004, 0.004, (-0.055,-0.0505,0.386), ledOn, 16, rot=(math.pi/2,0,0))
cyl("LED1", 0.004, 0.004, (-0.04,-0.0505,0.386), ledOff, 16, rot=(math.pi/2,0,0))

# ── USB cable to a laptop data logger ──
lx, ly = 0.34, 0.10
tube_curve("USB", [(0.085,0.01,0.39),(0.2,0.02,0.40),(0.29,0.06,0.15),(lx-0.06,ly,0.01)], 0.003, cable)
box("LaptopBase", (0.16,0.11,0.008), (lx,ly,0.004), anod, bevel=0.002)
lid = box("LaptopLid", (0.16,0.006,0.105), (lx, ly+0.058, 0.06), anod, bevel=0.002)
lid.rotation_euler = (math.radians(-12),0,0)
scr = box("LaptopScreen", (0.148,0.001,0.092), (lx, ly+0.054, 0.061), lapS)
scr.rotation_euler = (math.radians(-12),0,0)

# label anchors (three.js reads these)
empty("LBL_ctrl", (-0.085,0,0.41))
empty("LBL_scA",  (-0.075,-0.075,0.235))
empty("LBL_scB",  (-0.075,-0.075,0.125))
empty("LBL_sipm", (0.085,0,0.235))
empty("LBL_log",  (lx,ly,0.12))

export_glb(os.path.join(OUT,"detector.glb"))

# ── poster render ──
bpy.ops.mesh.primitive_plane_add(size=4, location=(0,0,-0.006))
g = bpy.context.active_object; g.name="Ground"; g.is_shadow_catcher = True
world((0.005,0.016,0.03), 0.6)
area_light("Key",  (-0.6,-0.7,0.9), (0,0,0.2), 60, 0.6, (1,0.97,0.92))
area_light("Rim",  (0.4,0.8,0.7),  (0,0,0.2), 45, 0.5, (0.3,0.6,1))
area_light("Fill", (0.9,-0.3,0.3), (0,0,0.2), 14, 0.8, (0.4,0.6,1))
camera((0.78,-0.92,0.62), (0.07,0.02,0.19), lens=55)
render(os.path.join(OUT,"detector.png"), 1000, 1000, samples=int(os.environ.get("SAMPLES","64")))

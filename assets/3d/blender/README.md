# 3D figure sources

The two rotatable figures on the landing page are modelled in Blender 5.2 from these scripts.
Each script exports a `.glb` (loaded by three.js on the page) and renders a Cycles poster
(`.png`, converted to `.webp`) that shows before the live model loads or when WebGL is off.

    pip install bpy              # Blender as a Python module (Python 3.13)
    SAMPLES=96 python detector.py   -- ../    # → detector.glb, detector.png
    SAMPLES=96 python relativity.py -- ../    # → relativity.glb, relativity.png

Object and material names (`ScintA`, `LED0`, `Scintillator`, `MuonRel`, `P_birth`, `LBL_*` …)
are read by the viewer script in `index.html`, so keep them stable when editing.

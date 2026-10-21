import bpy, math, mathutils

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, base=(0.8,0.8,0.8,1), metal=0.0, rough=0.5, emit=None, emit_str=0.0,
        alpha=1.0, transmission=0.0, ior=1.5, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = base
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["IOR"].default_value = ior
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if emit:
        p.inputs["Emission Color"].default_value = emit
        p.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m

def box(name, size, loc, material, bevel=0.0, segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("bev", 'BEVEL'); b.width = bevel; b.segments = segs
        b.limit_method = 'ANGLE'
        bpy.ops.object.modifier_apply(modifier="bev")
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    return o

def cyl(name, r, depth, loc, material, verts=32, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    return o

def tube_curve(name, pts, radius, material, res=24):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.bevel_depth = radius; cu.bevel_resolution = 4; cu.resolution_u = res
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o.select_set(False)
    return o

def empty(name, loc):
    e = bpy.data.objects.new(name, None); e.location = loc
    bpy.context.collection.objects.link(e); return e

def world(color=(0.004,0.014,0.025), strength=1.0):
    w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1); bg.inputs[1].default_value = strength

def area_light(name, loc, target, energy, size, color=(1,1,1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = color
    o = bpy.data.objects.new(name, l); o.location = loc
    bpy.context.collection.objects.link(o)
    d = mathutils.Vector(target) - mathutils.Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
    return o

def camera(loc, target, lens=50):
    c = bpy.data.cameras.new("Cam"); c.lens = lens
    o = bpy.data.objects.new("Cam", c); o.location = loc
    bpy.context.collection.objects.link(o)
    d = mathutils.Vector(target) - mathutils.Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera = o
    return o

def render(path, w, h, samples=48):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
    s.cycles.samples = samples; s.cycles.use_denoising = True
    s.render.resolution_x = w; s.render.resolution_y = h; s.render.resolution_percentage = 100
    s.render.film_transparent = True
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)

def export_glb(path, exclude=("Cam",)):
    bpy.ops.object.select_all(action='SELECT')
    for o in bpy.context.scene.objects:
        if o.type in ('LIGHT','CAMERA'): o.select_set(False)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_extras=True,
                              export_lights=False, export_cameras=False)

"""CadQuery helpers + the part registry shared by the model builders.

Every part is registered with metadata (tag, title, system, spec, source, status, note) so the STEP tree,
the GLB node names, the BOM and the viewer inspector all agree.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq

V = cq.Vector


# ------------------------------------------------------------------------------ primitives (mm)
def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def cyl(p0, p1, r):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, d.Length, p0, d.normalized()))


def tube(p0, p1, r_out, r_in):
    return cyl(p0, p1, r_out).cut(cyl(p0, p1, r_in))


def sph(p, r):
    return cq.Workplane("XY").add(cq.Solid.makeSphere(r, V(*p), angleDegrees1=-90, angleDegrees2=90))


def pipe(points, r, elbows=True):
    """Pipe along a polyline: straight cylinders + spheres at the bends (robust, fast)."""
    w = None
    for a, b in zip(points, points[1:]):
        if math.dist(a, b) < 1e-6:
            continue
        s = cyl(a, b, r)
        w = s if w is None else w.union(s)
    if elbows:
        for p in points[1:-1]:
            w = w.union(sph(p, r))
    return w


def duct(points, w, h, up=(0, 0, 1)):
    """Rectangular duct (w across, h vertical) along an axis-aligned polyline, as boxes with corner overlap."""
    out = None
    for a, b in zip(points, points[1:]):
        (x0, y0, z0), (x1, y1, z1) = a, b
        if abs(x1 - x0) > 1e-6:      # along X
            s = box(min(x0, x1) - w / 2, max(x0, x1) + w / 2, y0 - w / 2, y0 + w / 2, z0 - h / 2, z0 + h / 2)
        elif abs(y1 - y0) > 1e-6:    # along Y
            s = box(x0 - w / 2, x0 + w / 2, min(y0, y1) - w / 2, max(y0, y1) + w / 2, z0 - h / 2, z0 + h / 2)
        else:                        # vertical
            s = box(x0 - w / 2, x0 + w / 2, y0 - h / 2, y0 + h / 2, min(z0, z1) - h / 2, max(z0, z1) + h / 2)
        out = s if out is None else out.union(s)
    return out


def rrect(L, W, r, z0, z1, cx=0, cy=0):
    """Rounded rectangle prism (L along Y, W along X)."""
    s = cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(W, L).extrude(z1 - z0)
    if r > 0:
        s = s.edges("|Z").fillet(r)
    return s


def rring(L, W, r, off_in, off_out, z0, z1):
    """Ring around a rounded rect L x W (radius r): from offset off_in to off_out outward."""
    o = rrect(L + 2 * off_out, W + 2 * off_out, r + off_out, z0, z1)
    if off_in <= 0 and r + off_in <= 0:
        i = rrect(L + 2 * off_in, W + 2 * off_in, 0, z0 - 1, z1 + 1)
    else:
        i = rrect(L + 2 * off_in, W + 2 * off_in, max(r + off_in, 0.5), z0 - 1, z1 + 1)
    return o.cut(i)


def frame(x0, x1, y0, y1, xi0, xi1, yi0, yi1, z0, z1):
    return box(x0, x1, y0, y1, z0, z1).cut(box(xi0, xi1, yi0, yi1, z0 - 1, z1 + 1))


def ibeam(p0, p1, h=150, b=80, tw=4.8, tf=7.6, up=(0, 0, 1)):
    """I-section between two points (horizontal members along X or Y; web vertical)."""
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    if abs(x1 - x0) > abs(y1 - y0):
        xa, xb = sorted((x0, x1))
        fl = lambda zc: box(xa, xb, y0 - b / 2, y0 + b / 2, zc - tf / 2, zc + tf / 2)
        web = box(xa, xb, y0 - tw / 2, y0 + tw / 2, z0 - h / 2, z0 + h / 2)
    else:
        ya, yb = sorted((y0, y1))
        fl = lambda zc: box(x0 - b / 2, x0 + b / 2, ya, yb, zc - tf / 2, zc + tf / 2)
        web = box(x0 - tw / 2, x0 + tw / 2, ya, yb, z0 - h / 2, z0 + h / 2)
    return web.union(fl(z0 - h / 2 + tf / 2)).union(fl(z0 + h / 2 - tf / 2))


def quarter_ring(cx, cy, r_in, r_out, z0, z1, quad):
    """Quarter annulus centred (cx, cy); quad = (sx, sy) picks the quadrant."""
    sx, sy = quad
    ring = cyl((cx, cy, z0), (cx, cy, z1), r_out).cut(cyl((cx, cy, z0 - 1), (cx, cy, z1 + 1), r_in))
    q = box(cx, cx + sx * (r_out + 5), cy, cy + sy * (r_out + 5), z0 - 2, z1 + 2)
    return ring.intersect(q)


def merge(*ws):
    out = None
    for w in ws:
        if w is None:
            continue
        out = w if out is None else out.union(w)
    return out


def compound(*ws):
    """Fast non-boolean grouping of many solids into one shape."""
    shapes = []
    for w in ws:
        if w is None:
            continue
        shapes += [o for o in w.vals() if isinstance(o, cq.Shape)]
    return cq.Workplane("XY").add(cq.Compound.makeCompound(shapes))


# ------------------------------------------------------------------------------ registry
SYSTEMS = {
    # key: (title, order)
    "civil": ("Civil: foundation, pits, trenches", 1),
    "casing": ("Furnace casing and structure", 2),
    "lining": ("Refractory lining and insulation", 3),
    "kettle": ("Kettle, zinc and support ring", 4),
    "topclose": ("Top closure, band and corner shields", 5),
    "burner": ("Burners and burner blocks", 6),
    "gas": ("Gas train and piping", 7),
    "air": ("Combustion air", 8),
    "pitvent": ("Burner pits: fans, rails, ladders", 9),
    "instr": ("Instruments and controls", 10),
    "flue": ("Flue duct", 11),
    "loop": ("Heat-recovery loop", 12),
    "dryer": ("Four-position dryer", 13),
    "stack": ("Bleed and stack", 14),
    "load": ("Sample loads (jigs)", 15),
    "enclosure": ("Zinc enclosure (optional)", 16),
}

COL = {  # RGB 0-1; palette continues the SH-INS 3D viewer where the part is the same
    "concrete": (0.62, 0.64, 0.66), "concrete2": (0.52, 0.54, 0.56), "rccpit": (0.58, 0.60, 0.63),
    "steel": (0.29, 0.33, 0.39), "steel2": (0.38, 0.43, 0.50), "deck": (0.45, 0.49, 0.54), "galv": (0.70, 0.73, 0.76),
    "module": (0.85, 0.80, 0.70), "mpi": (0.93, 0.93, 0.88), "casi": (0.80, 0.84, 0.86), "castable": (0.66, 0.55, 0.45),
    "B1": (0.03, 0.39, 0.43), "B2": (0.06, 0.64, 0.69), "B3": (0.36, 0.88, 0.91), "T1": (0.88, 0.54, 0.0),
    "T2": (1.0, 0.70, 0.0), "T3": (1.0, 0.85, 0.35), "band": (0.91, 0.25, 0.17), "shf": (0.61, 0.30, 0.79),
    "ss": (0.79, 0.82, 0.86), "hdb": (0.61, 0.88, 0.36), "lip": (0.22, 0.25, 0.32), "kettle": (0.18, 0.42, 0.66),
    "zinc": (0.80, 0.85, 0.90), "graphite": (0.12, 0.12, 0.13), "support": (0.50, 0.66, 0.82),
    "burner": (0.80, 0.10, 0.12), "gas": (1.0, 0.82, 0.0), "valve": (0.85, 0.12, 0.12), "solenoid": (0.16, 0.20, 0.26),
    "air": (0.40, 0.69, 0.90), "airduct": (0.53, 0.75, 0.93), "motor": (0.13, 0.36, 0.60), "fan": (0.14, 0.45, 0.70),
    "yellow": (1.0, 0.76, 0.0), "panel": (0.85, 0.87, 0.89), "black": (0.06, 0.06, 0.07), "rubber": (0.10, 0.10, 0.10),
    "flue": (0.55, 0.12, 0.10), "fluesteel": (0.35, 0.22, 0.20), "retn": (0.91, 0.77, 0.42), "suct": (0.91, 0.45, 0.23),
    "supp": (0.95, 0.65, 0.25), "fresh": (0.16, 0.62, 0.96), "bleed": (0.54, 0.56, 0.60), "alu": (0.82, 0.84, 0.86),
    "insul": (0.92, 0.88, 0.78), "chain": (0.10, 0.10, 0.11), "gear": (0.55, 0.57, 0.60), "red": (0.80, 0.10, 0.10),
    "work": (0.35, 0.37, 0.40), "glass": (0.70, 0.85, 0.95), "grating": (0.55, 0.58, 0.62),
}


@dataclass
class Part:
    name: str
    shape: cq.Workplane
    system: str
    color: str
    tag: str = ""
    title: str = ""
    spec: str = ""
    material: str = ""
    src: str = ""
    status: str = "C"
    note: str = ""
    qty: str = "1"
    hidden: bool = False
    alpha: float = 1.0
    layer: str = ""


@dataclass
class Registry:
    parts: list = field(default_factory=list)

    def add(self, name, shape, system, color, **meta):
        if shape is None:
            return
        assert system in SYSTEMS, system
        assert color in COL, color
        assert all(p.name != name for p in self.parts), f"duplicate part name {name}"
        self.parts.append(Part(name, shape, system, color, **meta))

    def assembly(self):
        root = cq.Assembly(name="SHV-FUR-6700")
        for key, (title, _o) in sorted(SYSTEMS.items(), key=lambda kv: kv[1][1]):
            members = [p for p in self.parts if p.system == key]
            if not members:
                continue
            sub = cq.Assembly(name=key)
            for p in members:
                r, g, b = COL[p.color]
                sub.add(p.shape, name=p.name, color=cq.Color(r, g, b, p.alpha))
            root.add(sub, name=key)
        return root

    def meta(self):
        return {p.name: {"tag": p.tag, "title": p.title or p.name, "system": p.system, "spec": p.spec,
                         "material": p.material, "src": p.src, "status": p.status, "note": p.note, "qty": p.qty,
                         "hidden": p.hidden, "alpha": p.alpha, "layer": p.layer, "color": COL[p.color]} for p in self.parts}

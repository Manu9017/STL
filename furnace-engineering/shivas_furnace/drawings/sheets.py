"""GA drawings SHV-FUR-6700-GA-001..006 from the CAD model.

Views are hidden-line projections (OpenCascade HLRBRep) of the model, optionally cut by a half-space; cut faces
are filled by material. Dimensions are true values (dimlfac = scale). Output: DXF (paper space in mm at 1:1
of the sheet), PDF (all sheets) and SVG previews.
"""
from __future__ import annotations

import datetime as dt
import math
from pathlib import Path

import cadquery as cq
import ezdxf
from ezdxf.enums import TextEntityAlignment
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape

from ..basis import B, G, ROOT
from ..cad import combustion, furnace, loop
from ..cad.lib import COL, Registry

OUT = ROOT / "out" / "drawings"
A1 = (841.0, 594.0)
TODAY = dt.date(2026, 11, 20).isoformat()

# view frames: (eye direction toward the viewer, x direction on paper)
VIEWS = {
    "top": ((0, 0, 1), (1, 0, 0)),          # plan, north up
    "south": ((0, -1, 0), (1, 0, 0)),       # elevation looking north, east to the right
    "west": ((-1, 0, 0), (0, -1, 0)),       # elevation looking east, south to the right
}


def frame_vectors(view):
    n, x = VIEWS[view]
    n = cq.Vector(*n)
    x = cq.Vector(*x)
    y = n.cross(x)
    return n, x, y


# ------------------------------------------------------------------------------ model access
_REG = None


def registry():
    global _REG
    if _REG is None:
        R = Registry()
        furnace.build(R)
        combustion.build(R)
        loop.build(R)
        _REG = R
    return _REG


def parts(include=None, exclude=("load", "enclosure"), skip_layers=("flow",), bbox=None):
    out = []
    for p in registry().parts:
        if include and p.system not in include:
            continue
        if p.system in exclude or p.layer in skip_layers or p.hidden:
            continue
        if bbox is not None:
            bb = p.shape.val().BoundingBox()
            (x0, x1), (y0, y1), (z0, z1) = bbox
            if bb.xmax < x0 or bb.xmin > x1 or bb.ymax < y0 or bb.ymin > y1 or bb.zmax < z0 or bb.zmin > z1:
                continue
        out.append(p)
    return out


def halfspace(axis, value, keep):
    """Big box keeping coordinate `axis` <= value (keep='-') or >= value (keep='+')."""
    big = 60000
    c = [0, 0, 0]
    c[axis] = value + (big / 2 if keep == "+" else -big / 2)
    return cq.Workplane().box(big, big, big).translate(tuple(c)).val()


def cut_parts(ps, cut):
    if cut is None:
        return [(p, p.shape.val()) for p in ps]
    axis, value, keep = cut
    hs = halfspace(axis, value, keep)
    out = []
    for p in ps:
        try:
            s = p.shape.val().intersect(hs)
            if s.isValid() and s.Volume() > 1:
                out.append((p, s))
        except Exception:
            pass
    return out


def section_faces(ps, cut):
    """Faces of each part on the cut plane."""
    axis, value, _keep = cut
    n = [0, 0, 0]
    n[axis] = 1
    base = [0, 0, 0]
    base[axis] = value
    plane = cq.Face.makePlane(80000, 80000, basePnt=tuple(base), dir=tuple(n))
    out = []
    for p in ps:
        try:
            s = p.shape.val().intersect(plane)
            for f in s.Faces():
                if f.Area() > 1:
                    out.append((p, f))
        except Exception:
            pass
    return out


def hlr_edges(shapes, view):
    n, x, _y = frame_vectors(view)
    algo = HLRBRep_Algo()
    for s in shapes:
        algo.Add(s.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(n.x, n.y, n.z), gp_Dir(x.x, x.y, x.z))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    edges = []
    for comp in (h.VCompound(), h.OutLineVCompound()):
        if comp is None or comp.IsNull():
            continue
        for e in cq.Shape.cast(comp).Edges():
            edges.append(e)
    return edges


def edge_pts(e, step=25.0):
    if e.geomType() == "LINE":
        a, b = e.startPoint(), e.endPoint()
        return [(a.x, a.y), (b.x, b.y)]
    L = e.Length()
    n = max(6, min(200, int(L / step)))
    return [(p.x, p.y) for p in e.positions([i / n for i in range(n + 1)])]


def _wire_chain(w, x, y):
    """Points of a wire in loop order (edges chained by matching end points, reversed where needed)."""
    segs = []
    for e in w.Edges():
        if e.geomType() == "LINE":
            ps = [e.startPoint(), e.endPoint()]
        else:
            k = max(6, min(120, int(e.Length() / 15)))
            ps = e.positions([i / k for i in range(k + 1)])
        segs.append([(p.dot(x), p.dot(y)) for p in ps])
    if not segs:
        return []
    chain = segs.pop(0)
    d = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    while segs:
        last = chain[-1]
        best = min(range(len(segs)), key=lambda i: min(d(last, segs[i][0]), d(last, segs[i][-1])))
        sg = segs.pop(best)
        if d(last, sg[-1]) < d(last, sg[0]):
            sg = sg[::-1]
        chain += sg[1:]
    return chain


def face_loops(f, view):
    _n, x, y = frame_vectors(view)
    return [lp for lp in (_wire_chain(w, x, y) for w in [f.outerWire()] + f.innerWires()) if len(lp) >= 3]


# ------------------------------------------------------------------------------ sheet
def rgb(c, lighten=0.0):
    r, g, b = c
    return tuple(int(255 * (v + (1 - v) * lighten)) for v in (r, g, b))


class Sheet:
    def __init__(self, number, title, subtitle=""):
        self.number, self.title, self.subtitle = number, title, subtitle
        self.doc = ezdxf.new("R2018", setup=True, units=4)
        self.doc.header["$INSUNITS"] = 4
        self.msp = self.doc.modelspace()
        for name, color, lw in (("FRAME", 7, 50), ("VISIBLE", 7, 35), ("CUT", 7, 50), ("FILL", 8, 0), ("DIM", 1, 18),
                                ("TEXT", 7, 25), ("CALLOUT", 5, 18), ("CENTER", 3, 13), ("LEVEL", 30, 18)):
            self.doc.layers.add(name, color=color, lineweight=lw)
        self.doc.layers.get("CENTER").dxf.linetype = "CENTER"
        st = self.doc.styles.get("Standard")
        st.dxf.font = "DejaVuSans.ttf"
        self.dimstyles = {}
        self._frame()

    # -- annotation helpers (paper mm)
    def text(self, s, p, h=2.5, layer="TEXT", align=TextEntityAlignment.LEFT, color=None, rot=0):
        t = self.msp.add_text(s, height=h, dxfattribs={"layer": layer, "rotation": rot})
        if color:
            t.dxf.true_color = ezdxf.colors.rgb2int(color)
        t.set_placement(p, align=align)
        return t

    def line(self, a, b, layer="FRAME"):
        self.msp.add_line(a, b, dxfattribs={"layer": layer})

    def rect(self, x0, y0, x1, y1, layer="FRAME"):
        self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})

    def _frame(self):
        W, H = A1
        self.rect(0, 0, W, H)
        self.rect(20, 10, W - 10, H - 10)
        # title block 190 x 70 bottom right
        x0, y0, x1, y1 = W - 10 - 190, 10, W - 10, 80
        self.rect(x0, y0, x1, y1)
        for y in (24, 38, 52, 66):
            self.line((x0, y), (x1, y))
        self.line((x0 + 95, y0), (x0 + 95, 52))
        self.line((x0 + 140, y0), (x0 + 140, 38))
        self.text("SHIVAS TECHNOLOGY LTD", (x0 + 4, 70.5), 5.0, color=(227, 0, 15))
        self.text("A-1/270 Swadeshi Compound, Kavi Nagar Industrial Area, Ghaziabad 201002", (x0 + 4, 67.5), 1.8)
        self.text(self.title, (x0 + 4, 59.5), 3.6)
        self.text(self.subtitle, (x0 + 4, 54.5), 2.2)
        self.text("DRAWING No.", (x0 + 2, 49), 1.6); self.text(self.number, (x0 + 2, 42), 3.4)
        self.text("REV", (x0 + 97, 49), 1.6); self.text("A", (x0 + 97, 42), 3.4)
        self.text("SHEET", (x0 + 142, 49), 1.6); self.text("A1", (x0 + 142, 42), 3.4)
        self.text("DRAWN", (x0 + 2, 35), 1.6); self.text("Claude Code (draft) " + TODAY, (x0 + 2, 28), 2.2)
        self.text("CHECKED", (x0 + 97, 35), 1.6)
        self.text("APPROVED", (x0 + 142, 35), 1.6)
        self.text("UNITS  mm · LEVELS m from FFL ±0.000 · X east, Y north", (x0 + 2, 19.5), 1.9)
        self.text("BASIS  SHV-FUR-6700-DB Rev A · CALC SHV-FUR-6700-CR Rev A", (x0 + 2, 15.5), 1.9)
        self.text("PRELIMINARY — NOT FOR CONSTRUCTION", (x0 + 2, 11.5), 2.4, color=(200, 0, 0))
        # first-angle projection symbol (ISO 128): cone frustum + circles
        cx, cy = x1 - 22, 18
        self.msp.add_circle((cx + 9, cy), 4, dxfattribs={"layer": "FRAME"})
        self.msp.add_circle((cx + 9, cy), 2, dxfattribs={"layer": "FRAME"})
        self.msp.add_lwpolyline([(cx - 8, cy - 4), (cx - 1, cy - 2), (cx - 1, cy + 2), (cx - 8, cy + 4)], close=True, dxfattribs={"layer": "FRAME"})
        self.text("1st ANGLE", (cx - 8, cy + 6), 1.6)

    def notes(self, lines, x=24, y=None, w=250):
        y = y if y is not None else 80
        self.text("NOTES", (x, y + 4.5 * (len(lines)) + 4), 3.0)
        for i, s in enumerate(lines):
            self.text(f"{i + 1}. {s}", (x, y + 4.5 * (len(lines) - 1 - i)), 2.1)

    # -- views
    def view(self, title, view, origin, scale, cut=None, include=None, bbox=None, exclude=("load", "enclosure"), clip=None, title_dy=12):
        """Project parts. origin: paper point for model (u=0, v=0). clip: (umin, umax, vmin, vmax) model limits."""
        ps = parts(include=include, bbox=bbox, exclude=exclude)
        cp = cut_parts(ps, cut)
        cbox = None
        if clip is not None:   # 3-D window box aligned with the view axes: clipped solids give clean break lines
            n, x, y = frame_vectors(view)
            c = x * ((clip[0] + clip[1]) / 2) + y * ((clip[2] + clip[3]) / 2)
            sz = [abs(x.x) * (clip[1] - clip[0]) + abs(y.x) * (clip[3] - clip[2]) + abs(n.x) * 60000,
                  abs(x.y) * (clip[1] - clip[0]) + abs(y.y) * (clip[3] - clip[2]) + abs(n.y) * 60000,
                  abs(x.z) * (clip[1] - clip[0]) + abs(y.z) * (clip[3] - clip[2]) + abs(n.z) * 60000]
            cbox = cq.Workplane().box(*sz).translate((c.x, c.y, c.z)).val()
            cc = []
            for p, sh in cp:
                try:
                    k = sh.intersect(cbox)
                    if k.isValid() and k.Volume() > 0.5:
                        cc.append((p, k))
                except Exception:
                    pass
            cp = cc
        edges = hlr_edges([s for _p, s in cp], view)
        ox, oy = origin
        T = lambda u, v: (ox + u / scale, oy + v / scale)
        inside = (lambda u, v: True) if clip is None else (lambda u, v: clip[0] - 1 <= u <= clip[1] + 1 and clip[2] - 1 <= v <= clip[3] + 1)
        if cut is not None:
            fills = section_faces([p for p, _s in cp], cut) if cbox is None else [(p, f) for p, f in section_faces([p for p, _s in cp], cut)]
            for p, f in fills:
                if cbox is not None:
                    try:
                        f = f.intersect(cbox)
                        fs = f.Faces()
                        if not fs:
                            continue
                        f = fs[0]
                    except Exception:
                        continue
                loops = face_loops(f, view)
                if not loops:
                    continue
                h = self.msp.add_hatch(dxfattribs={"layer": "FILL"})
                h.set_solid_fill(rgb=rgb(COL[p.color], 0.35))
                for i, lp in enumerate(loops):
                    h.paths.add_polyline_path([T(*q) for q in lp], is_closed=True, flags=1 if i == 0 else 16)
                for lp in loops:
                    self.msp.add_lwpolyline([T(*q) for q in lp], close=True, dxfattribs={"layer": "CUT"})
        umin = vmin = 1e18
        umax = vmax = -1e18
        for e in edges:
            pts = edge_pts(e, step=12 * scale / 10)
            if clip is not None:
                pts = [q for q in pts if inside(*q)]
                if len(pts) < 2:
                    continue
            for u, v in pts:
                umin, umax, vmin, vmax = min(umin, u), max(umax, u), min(vmin, v), max(vmax, v)
            self.msp.add_lwpolyline([T(*q) for q in pts], dxfattribs={"layer": "VISIBLE"})
        tx, ty = T(umin, vmax)
        self.text(title, (tx, ty + title_dy), 4.0)
        self.text(f"SCALE 1:{scale:g}", (tx, ty + title_dy - 4.5), 2.4)
        self.extent = (umin, umax, vmin, vmax)
        return T

    def dim(self, T, scale, p1, p2, offset, vertical=False):
        """Linear dimension between model points (u, v); offset in paper mm."""
        key = scale
        if key not in self.dimstyles:
            name = f"SHV{int(scale)}"
            ds = self.doc.dimstyles.duplicate_entry("EZDXF", name)
            ds.dxf.dimlfac = scale
            ds.dxf.dimtxt = 2.2
            ds.dxf.dimasz = 2.0
            ds.dxf.dimexe = 1.2
            ds.dxf.dimexo = 1.0
            ds.dxf.dimdec = 0
            ds.dxf.dimgap = 0.8
            ds.dxf.dimclrd = 1
            ds.dxf.dimclre = 1
            ds.dxf.dimclrt = 7
            ds.dxf.dimtad = 1
            ds.dxf.dimtih = 0
            ds.dxf.dimtoh = 0
            ds.dxf.dimzin = 8
            ds.dxf.dimtxsty = "Standard"
            self.dimstyles[key] = name
        a, b = T(*p1), T(*p2)
        if vertical:
            base = (min(a[0], b[0]) + offset, a[1])
            d = self.msp.add_linear_dim(base=base, p1=a, p2=b, angle=90, dimstyle=self.dimstyles[key], dxfattribs={"layer": "DIM"})
        else:
            base = (a[0], min(a[1], b[1]) + offset)
            d = self.msp.add_linear_dim(base=base, p1=a, p2=b, angle=0, dimstyle=self.dimstyles[key], dxfattribs={"layer": "DIM"})
        d.render()

    def levels(self, T, u, items, length=10, right=True, gap=3.4):
        """Level marks at model x=u for [(z, label)], labels staggered so they never overlap."""
        s = 1 if right else -1
        last = None
        for z, label in sorted(items, key=lambda t: -t[0]):
            x, y = T(u, z)
            ty = y if last is None else min(y, last - gap)
            last = ty
            self.msp.add_line((x, y), (x + s * length, y), dxfattribs={"layer": "LEVEL"})
            self.msp.add_lwpolyline([(x + s * length, y), (x + s * (length - 1.4), y + 1.9), (x + s * (length + 1.4), y + 1.9)], close=True, dxfattribs={"layer": "LEVEL"})
            self.msp.add_line((x + s * (length + 1.6), y), (x + s * (length + 5), ty), dxfattribs={"layer": "LEVEL"})
            self.text(label, (x + s * (length + 6), ty - 0.7), 2.0, align=TextEntityAlignment.LEFT if right else TextEntityAlignment.RIGHT)

    def level(self, T, u, v, label, length=14, right=True):
        self.levels(T, u, [(v, label)], length, right)

    def callout(self, T, u, v, text, dx, dy):
        x, y = T(u, v)
        self.msp.add_circle((x, y), 0.6, dxfattribs={"layer": "CALLOUT"})
        self.msp.add_line((x, y), (x + dx, y + dy), dxfattribs={"layer": "CALLOUT"})
        self.msp.add_line((x + dx, y + dy), (x + dx + (6 if dx >= 0 else -6), y + dy), dxfattribs={"layer": "CALLOUT"})
        self.text(text, (x + dx + (7 if dx >= 0 else -7), y + dy - 0.8), 2.1,
                  align=TextEntityAlignment.LEFT if dx >= 0 else TextEntityAlignment.RIGHT)

    def table(self, x, y, cols, rows, widths, h=5.0, size=2.0, head=None):
        yy = y
        allrows = ([head] if head else []) + rows
        for r, row in enumerate(allrows):
            xx = x
            for c, (cell, w) in enumerate(zip(row, widths)):
                self.rect(xx, yy - h, xx + w, yy, layer="TEXT")
                s = str(cell)
                maxc = int(w / (size * 0.62))
                if len(s) > maxc:
                    s = s[: maxc - 1] + "…"
                self.text(s, (xx + 1.2, yy - h + 1.4), size if not (head and r == 0) else size + 0.2)
                xx += w
            yy -= h
        return yy

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / f"{name}.dxf"
        self.doc.saveas(p)
        return p

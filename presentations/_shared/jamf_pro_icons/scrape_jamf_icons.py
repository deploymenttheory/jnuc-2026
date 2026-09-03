#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.40"]
# ///
"""
Scrape the Jamf Pro web UI icon set from a Jamf Pro instance.

No login is needed: every artefact this script touches is a public static
asset of the Angular front end.  How it works (worked out by reading the
running app in Chrome):

  1. GET  /angular/upgrade-module/en/index.html
        -> names of the hashed entry bundle (main-*.js) and stylesheet.
  2. The stylesheet declares an icon font, /assets/fonts/icons/jamf-icons.woff,
     with ~740 glyphs whose glyph names are the real icon names
     (e.g. "cog-8-tooth-outline").  Every glyph is converted to a 24x24 SVG.
        -> font/<name>.svg
  3. main-*.js is crawled through its ESM import graph.  One chunk is the
     inline icon library used by <jamf-icon>: ~130 objects shaped
     {height,width,viewBox,path:'<path d=.../>'}.  Their export names are
     minified, so real names are recovered two ways: (a) `this.xMarkOutline=X`
     style assignments in importing chunks, (b) geometric matching against the
     font glyphs.  The exact original SVG markup is written out.
        -> inline/<name>.svg
  4. settings.module-*.js lists every Settings tile as
     {cardTitle, cardDescription, cardIcon:{icon:X,color:p.ORANGE}}.  Those are
     rebuilt as the coloured 32x32 tiles you see on /view/settings.
        -> settings/<slug>.svg
  5. Any assets/icons/**.svg referenced by the bundles (product logos such as
     Self Service+, Jamf Parent, Jamf Teacher) is downloaded verbatim.
        -> assets/<path>
  6. manifest.json + contact-sheet.html describe everything that was written.

Usage:
    python3 scrape_jamf_icons.py                       # defaults below
    python3 scrape_jamf_icons.py --base-url https://your.jamfcloud.com --out ./icons

Dependencies:  pip install fonttools   (or run with `uv run scrape_jamf_icons.py`)
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from fontTools.pens.basePen import BasePen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.svgLib.path import parse_path
    from fontTools.ttLib import TTFont
except ImportError:  # pragma: no cover
    sys.exit("fonttools is required:  pip install fonttools   (or: uv run scrape_jamf_icons.py)")

DEFAULT_BASE_URL = "https://tfproviderdev.jamfcloud.com"
APP_INDEX = "/angular/upgrade-module/en/index.html"
USER_AGENT = "jamf-pro-icon-scraper/1.0 (+https://github.com/deploymenttheory/jnuc-2026)"

# Tile geometry observed on /view/settings: jamf-icon is 32x32, padding 6px,
# border-radius 8px, icon drawn at 20px.
TILE_SIZE, TILE_PAD, TILE_RADIUS = 32, 6, 8
ICON_SUFFIXES = ("outline", "solid", "branded", "android")


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------
class Fetcher:
    def __init__(self, base_url: str, delay: float = 0.0, verbose: bool = False):
        self.base = base_url.rstrip("/")
        self.delay = delay
        self.verbose = verbose
        self.cache: dict[str, bytes] = {}

    def url(self, path: str) -> str:
        return path if path.startswith("http") else self.base + "/" + path.lstrip("/")

    def get(self, path: str, retries: int = 3) -> bytes:
        url = self.url(path)
        if url in self.cache:
            return self.cache[url]
        last: Exception | None = None
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                if self.verbose:
                    print(f"  GET {url} ({len(data)} bytes)")
                self.cache[url] = data
                if self.delay:
                    time.sleep(self.delay)
                return data
            except urllib.error.HTTPError as e:
                if e.code in (404, 403):
                    raise
                last = e
            except Exception as e:  # network hiccup
                last = e
            time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"failed to fetch {url}: {last}")

    def text(self, path: str) -> str:
        return self.get(path).decode("utf-8", errors="replace")


# ----------------------------------------------------------------------------
# Step 1: discover the Angular app's hashed bundles
# ----------------------------------------------------------------------------
def discover_app(f: Fetcher) -> dict:
    index = f.text(APP_INDEX)
    app_dir = APP_INDEX.rsplit("/", 1)[0] + "/"
    mains = re.findall(r'src="([^"]*?main-[A-Z0-9]+\.js)"', index)
    styles = re.findall(r'href="([^"]*?styles-[A-Z0-9]+\.css)"', index)
    if not mains or not styles:
        raise RuntimeError("could not find main-*.js / styles-*.css in " + APP_INDEX)
    norm = lambda p: "/" + p.lstrip("/")
    return {"app_dir": app_dir, "main": norm(mains[0]), "styles": norm(styles[0])}


# ----------------------------------------------------------------------------
# Step 2: the icon font
# ----------------------------------------------------------------------------
def parse_stylesheet(css: str) -> dict:
    m = re.search(r"@font-face\{[^}]*font-family:jamf-icons;src:url\(([^)]+)\)", css)
    if not m:
        raise RuntimeError("jamf-icons @font-face not found in stylesheet")
    font_url = m.group(1).strip("'\"")
    codepoints = {
        name: int(cp, 16)
        for name, cp in re.findall(r'\.icon-([a-z0-9-]+):+before\{content:"\\([0-9a-fA-F]+)"\}', css)
    }
    # Design tokens for the coloured Settings tiles (first = light theme).
    colors: dict[str, dict[str, str]] = {}
    for c, kind, val in re.findall(r"--color-([a-z]+)-(background|font):\s*([^;]+);", css):
        colors.setdefault(c, {}).setdefault(kind, val.strip())
    colors = {c: v for c, v in colors.items() if "background" in v and "font" in v}
    return {"font_url": font_url, "codepoints": codepoints, "colors": colors}


class FlattenPen(BasePen):
    """Flattens a glyph/path outline into polyline points in 24x24 icon space."""

    def __init__(self, scale: float = 1.0, flip_y: bool = False, steps: int = 8):
        super().__init__(None)
        self.scale, self.flip_y, self.steps = scale, flip_y, steps
        self.points: list[tuple[float, float]] = []
        self.contours: list[list[tuple[float, float]]] = []
        self._cur = (0.0, 0.0)

    def _map(self, p):
        x, y = p[0] * self.scale, p[1] * self.scale
        if self.flip_y:
            y = 24 - y
        return (x, y)

    def _add(self, p):
        q = self._map(p)
        self.points.append(q)
        self.contours[-1].append(q)

    def _moveTo(self, p):
        self.contours.append([])
        self._cur = p
        self._add(p)

    def _lineTo(self, p):
        self._sample(lambda t: (self._cur[0] + (p[0] - self._cur[0]) * t, self._cur[1] + (p[1] - self._cur[1]) * t))
        self._cur = p

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur
        self._sample(
            lambda t: (
                (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t**3 * p3[0],
                (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t**3 * p3[1],
            )
        )
        self._cur = p3

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur
        self._sample(
            lambda t: (
                (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
            )
        )
        self._cur = p2

    def _sample(self, fn):
        for i in range(1, self.steps + 1):
            self._add(fn(i / self.steps))

    def _closePath(self):
        pass

    def _endPath(self):
        pass

    # --- shape signature -----------------------------------------------------
    def signature(self, grid: int = 16) -> tuple[list[int], float]:
        occ = [0] * (grid * grid)
        for x, y in self.points:
            i = min(grid - 1, max(0, int(x / 24 * grid)))
            j = min(grid - 1, max(0, int(y / 24 * grid)))
            occ[j * grid + i] = 1
        # |sum of signed contour areas| distinguishes outline from solid variants
        area = 0.0
        for c in self.contours:
            a = 0.0
            for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
                a += x0 * y1 - x1 * y0
            area += a / 2
        return occ, abs(area) / (24 * 24)


def extract_font_glyphs(woff: bytes, tmp_path: Path) -> dict[str, dict]:
    tmp_path.write_bytes(woff)
    font = TTFont(str(tmp_path))
    upm = font["head"].unitsPerEm
    scale = 24 / upm
    glyph_set = font.getGlyphSet()
    reverse_cmap = {g: cp for cp, g in font.getBestCmap().items()}
    out: dict[str, dict] = {}
    for name in font.getGlyphOrder():
        if not name.endswith(ICON_SUFFIXES) or "-" not in name:
            continue
        glyph = glyph_set[name]
        # font space (y up, UPM units) -> SVG icon space (24x24, y down)
        svg_pen = SVGPathPen(glyph_set, ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
        glyph.draw(TransformPen(svg_pen, (scale, 0, 0, -scale, 0, 24)))
        d = svg_pen.getCommands()
        flat = FlattenPen(scale=scale, flip_y=True)
        glyph.draw(flat)
        occ, area = flat.signature()
        out[name] = {
            "svg": (
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="currentColor">'
                f'<path d="{d}"/></svg>'
            ),
            "codepoint": reverse_cmap.get(name),
            "sig": occ,
            "area": area,
        }
    return out


# ----------------------------------------------------------------------------
# Step 3: crawl the JS bundles and pull the inline icon library
# ----------------------------------------------------------------------------
IMPORT_RE = re.compile(r'''(?:from|import\()\s*["']\./([\w.\-]+\.js)["']''')
ICON_OBJ_RE = re.compile(r"""([A-Za-z_$][\w$]*)=\{height:(\d*),width:(\d*),viewBox:"([^"]*)",path:'((?:[^'\\]|\\.)*)'\}""")


def crawl_chunks(f: Fetcher, app_dir: str, main: str) -> dict[str, str]:
    chunks: dict[str, str] = {}
    queue = [os.path.basename(main)]
    while queue:
        name = queue.pop()
        if name in chunks:
            continue
        try:
            chunks[name] = f.text(app_dir + name)
        except urllib.error.HTTPError as e:
            print(f"  ! {name}: HTTP {e.code} (skipped)")
            chunks[name] = ""
            continue
        for dep in IMPORT_RE.findall(chunks[name]):
            if dep not in chunks:
                queue.append(dep)
    return chunks


def find_icon_module(chunks: dict[str, str]) -> tuple[str, dict, dict]:
    best, best_n = None, 0
    for name, text in chunks.items():
        n = len(ICON_OBJ_RE.findall(text))
        if n > best_n:
            best, best_n = name, n
    if best is None or best_n < 20:
        raise RuntimeError("inline icon module not found")
    text = chunks[best]
    icons = {
        m.group(1): {"height": m.group(2), "width": m.group(3), "viewBox": m.group(4), "path": m.group(5)}
        for m in ICON_OBJ_RE.finditer(text)
    }
    exp_m = re.search(r"export\{([^}]+)\}", text)
    var_to_export = dict(re.findall(r"([\w$]+) as ([\w$]+)", exp_m.group(1))) if exp_m else {}
    export_to_var = {e: v for v, e in var_to_export.items() if v in icons}
    return best, icons, export_to_var


def camel_to_kebab(s: str) -> str:
    s = re.sub(r"(?<=[a-z])(?=[A-Z0-9])|(?<=[0-9])(?=[A-Z])", "-", s)
    return s.lower()


def recover_usage_names(chunks: dict[str, str], icon_module: str, exports: set[str]) -> dict[str, collections.Counter]:
    """Look at every chunk importing the icon module for `this.xMarkOutline=LOCAL`
    or `xMarkOutline=LOCAL` assignments, which leak the original identifier."""
    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    imp_re = re.compile(r'import\{([^}]*)\}from"\./%s"' % re.escape(icon_module))
    for text in chunks.values():
        for im in imp_re.finditer(text):
            for part in im.group(1).split(","):
                bits = [b.strip() for b in part.strip().split(" as ")]
                exp, local = bits[0], bits[-1]
                if exp not in exports or not local:
                    continue
                L = re.escape(local)
                # Angular:  this.xMarkOutline=X   /  const xMarkOutline=X
                for m in re.finditer(r"(?:this\.|(?<![\w$.]))([A-Za-z][\w]{3,}(?:Outline|Solid|Icon|Branded))=%s(?![\w$])" % L, text):
                    votes[exp][camel_to_kebab(m.group(1))] += 1
                # Vue data():  {chevronUpSolid:X, ...}
                for m in re.finditer(r"(?<![\w$.])([A-Za-z][\w]{3,}(?:Outline|Solid|Branded)):%s(?![\w$])" % L, text):
                    votes[exp][camel_to_kebab(m.group(1))] += 1
    return votes


def inline_signature(icon: dict) -> tuple[list[int], float]:
    vb = (icon["viewBox"] or "0 0 24 24").split()
    scale = 24 / float(vb[2]) if len(vb) == 4 and float(vb[2]) > 0 else 1.0
    pen = FlattenPen(scale=scale)
    for d in re.findall(r'\sd="([^"]+)"', icon["path"]):
        parse_path(d, pen)
    return pen.signature()


def match_inline_to_font(icons: dict, export_to_var: dict, glyphs: dict, usage: dict) -> dict[str, dict]:
    """Return {export: {name, method, confidence, candidates, usage_names}}.

    Priority: strong usage name (…Outline/…Solid/…Branded identifier found in
    app code) > unambiguous geometric match > weak usage name (…Icon) >
    ambiguous geometric match > unnamed.  Collisions are resolved afterwards
    in favour of the stronger claim.
    """
    norm = lambda n: n.replace("-", "")
    font_by_norm = {norm(n): n for n in glyphs}
    results: dict[str, dict] = {}
    for exp, var in export_to_var.items():
        icon = icons[var]
        occ, area = inline_signature(icon)
        scored = []
        for gname, g in glyphs.items():
            d = sum(a != b for a, b in zip(occ, g["sig"]))
            d += 40 * abs(area - g["area"])  # outline vs solid disambiguation
            scored.append((d, gname))
        # near-ties (visually identical glyphs) -> prefer the -outline variant
        # (what the Angular app uses almost everywhere), then the simpler name
        scored.sort(key=lambda t: (int(t[0] // 3), not t[1].endswith("-outline"), len(t[1]), t[1]))
        best = scored[0]
        gap = (scored[1][0] - best[0]) if len(scored) > 1 else math.inf
        used = usage.get(exp) or collections.Counter()

        strong = weak = None
        for uname, _ in used.most_common():
            if uname.endswith("-icon"):
                for suffix in ("-outline", "-solid"):
                    key = norm(uname[: -len("-icon")] + suffix)
                    if key in font_by_norm and weak is None:
                        weak = font_by_norm[key]
            elif norm(uname) in font_by_norm and strong is None:
                strong = font_by_norm[norm(uname)]

        ranked: list[tuple[int, str, str, str]] = []  # (priority, name, method, confidence)
        if strong:
            ranked.append((0, strong, "usage", "high"))
        if best[0] <= 14 and gap >= 3:
            ranked.append((1, best[1], "geometry", "high" if best[0] <= 6 else "medium"))
        if weak:
            ranked.append((2, weak, "usage", "medium"))
        if best[0] <= 24:
            ranked.append((3, best[1], "geometry", "low"))
        for s, n in scored[1:3]:
            if s <= 24:
                ranked.append((4, n, "geometry", "low"))
        digest = hashlib.sha1(icon["path"].encode()).hexdigest()[:8]
        ranked.append((9, f"unnamed-{digest}", "none", "none"))

        results[exp] = {
            "ranked": ranked,
            "candidates": [{"name": n, "score": round(s, 1)} for s, n in scored[:3]],
            "usage_names": [n for n, _ in used.most_common(3)],
        }

    # resolve collisions: stronger claims are assigned first; a weaker claim on
    # an already-taken name falls through to its next unclaimed candidate and
    # only duplicates (suffixed later) when it has nothing else.
    claimed: dict[str, str] = {}
    for exp in sorted(results, key=lambda e: results[e]["ranked"][0][0]):
        ranked = results[exp]["ranked"]
        free = [r for r in ranked if r[1] not in claimed]
        prio, name, method, conf = free[0] if free and free[0][0] < 9 else ranked[0]
        if name in claimed:
            results[exp]["duplicate_of"] = claimed[name]
        else:
            claimed[name] = exp
        results[exp].update(name=name, method=method, confidence=conf)
        results[exp].pop("ranked", None)
    return results


def inline_svg(icon: dict) -> str:
    vb = icon["viewBox"] or "0 0 24 24"
    w = icon["width"] or "24"
    h = icon["height"] or "24"
    path = icon["path"].replace("\\'", "'")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" fill="currentColor">'
        f"{path}</svg>"
    )


# ----------------------------------------------------------------------------
# Step 4: Settings tiles
# ----------------------------------------------------------------------------
CARD_RE = re.compile(
    r'this\.cardTitle="((?:[^"\\]|\\.)*)",this\.cardDescription="((?:[^"\\]|\\.)*)",'
    r"this\.cardIcon=\{(icon:([\w$]+),color:[\w$]+\.([A-Z_]+)|svgUrl:\"([^\"]+)\")\}"
    r'(?:,this\.cardPagePath="([^"]*)")?'
    r'.*?selectors:\[\["([\w-]+)"\]\]',
    re.S,
)


def parse_settings_cards(chunks: dict[str, str], icon_module: str, export_to_var: dict) -> list[dict]:
    cards: list[dict] = []
    imp_re = re.compile(r'import\{([^}]*)\}from"\./%s"' % re.escape(icon_module))
    for fname, text in chunks.items():
        if "this.cardIcon=" not in text:
            continue
        local_to_export: dict[str, str] = {}
        for im in imp_re.finditer(text):
            for part in im.group(1).split(","):
                bits = [b.strip() for b in part.strip().split(" as ")]
                local_to_export[bits[-1]] = bits[0]
        for m in CARD_RE.finditer(text):
            title, desc, _, icon_local, color, svg_url, page_path, selector = m.groups()
            card = {
                "selector": selector,
                "title": title.encode().decode("unicode_escape"),
                "description": desc.encode().decode("unicode_escape"),
                "page_path": page_path,
                "module": fname,
            }
            if svg_url:
                card["svg_url"] = svg_url
            else:
                exp = local_to_export.get(icon_local)
                card["icon_export"] = exp
                card["color"] = color.lower() if color else None
            cards.append(card)
    return cards


def rgba_to_svg_fill(value: str) -> tuple[str, str]:
    """'rgba(255, 59, 48, .16)' -> ('#ff3b30', '0.16'); '#C30001' -> ('#C30001','1')."""
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)", value)
    if m:
        r, g, b, a = m.groups()
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}", (a or "1")
    return value, "1"


def tile_svg(icon: dict, color_tokens: dict[str, str]) -> str:
    bg, bg_alpha = rgba_to_svg_fill(color_tokens["background"])
    fg, _ = rgba_to_svg_fill(color_tokens["font"])
    inner = TILE_SIZE - 2 * TILE_PAD
    vb = icon["viewBox"] or "0 0 24 24"
    vb_w = float(vb.split()[2]) if len(vb.split()) == 4 else 24.0
    scale = inner / vb_w
    path = icon["path"].replace("\\'", "'")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE_SIZE} {TILE_SIZE}" width="{TILE_SIZE}" height="{TILE_SIZE}">'
        f'<rect width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{TILE_RADIUS}" fill="{bg}" fill-opacity="{bg_alpha}"/>'
        f'<g transform="translate({TILE_PAD} {TILE_PAD}) scale({scale:.4f})" fill="{fg}">{path}</g></svg>'
    )


def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "untitled"


# ----------------------------------------------------------------------------
# Step 5: static SVG assets referenced by the bundles
# ----------------------------------------------------------------------------
def collect_asset_svgs(chunks: dict[str, str]) -> list[str]:
    found: set[str] = set()
    for text in chunks.values():
        for p in re.findall(r"[\w./-]*assets/icons/[\w./@-]+\.svg", text):
            found.add("/" + p.lstrip("./"))
    return sorted(found)


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)


def contact_sheet(manifest: dict) -> str:
    def cell(src: str, label: str, sub: str = "") -> str:
        return (
            f'<figure title="{html.escape(label)}"><img src="{html.escape(src)}" loading="lazy">'
            f"<figcaption>{html.escape(label)}{'<small>' + html.escape(sub) + '</small>' if sub else ''}</figcaption></figure>"
        )

    sections = []
    font_cells = "".join(cell(f"font/{n}.svg", n) for n in sorted(manifest["font"]))
    sections.append(("Icon font glyphs", len(manifest["font"]), font_cells))
    inline_cells = "".join(
        cell(f"inline/{e['file']}", e["name"], f"{e['method']} · {e['confidence']}")
        for e in sorted(manifest["inline"], key=lambda x: x["name"])
    )
    sections.append(("Inline <jamf-icon> library", len(manifest["inline"]), inline_cells))
    tile_cells = "".join(
        cell(c["file"], c["title"], c.get("icon_name") or c.get("svg_url", ""))
        for c in manifest["settings"] if c.get("file")
    )
    sections.append(("Settings tiles", len(manifest["settings"]), tile_cells))
    asset_cells = "".join(cell(a["file"], a["url"].rsplit("/", 1)[-1]) for a in manifest["assets"])
    sections.append(("Static SVG assets", len(manifest["assets"]), asset_cells))

    body = "".join(
        f"<h2>{html.escape(t)} <span>{n}</span></h2><div class=grid>{cells}</div>" for t, n, cells in sections
    )
    return f"""<!doctype html><meta charset="utf-8"><title>Jamf Pro icons</title>
<style>
body{{font:14px/1.4 -apple-system,Inter,sans-serif;margin:24px;color:#222;background:#fff}}
h1{{font-size:22px}} h2{{font-size:16px;margin:32px 0 12px}} h2 span{{color:#888;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}
figure{{margin:0;padding:10px;border:1px solid #e5e5e5;border-radius:8px;text-align:center;background:#fafafa}}
figure img{{width:32px;height:32px;display:block;margin:0 auto 6px}}
figcaption{{font-size:11px;word-break:break-all}} figcaption small{{display:block;color:#999;font-size:10px}}
input{{width:320px;padding:6px 8px;font-size:14px}}
</style>
<h1>Jamf Pro icons <small style="color:#888;font-weight:400">from {html.escape(manifest['source']['base_url'])} · build {html.escape(manifest['source']['build'])} · {html.escape(manifest['source']['scraped_at'])}</small></h1>
<input id=q placeholder="filter by name…" oninput="for(const f of document.querySelectorAll('figure'))f.hidden=!f.title.toLowerCase().includes(this.value.toLowerCase())">
{body}"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Jamf Pro instance URL")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent), help="output directory")
    ap.add_argument("--delay", type=float, default=0.0, help="seconds to sleep between requests")
    ap.add_argument("--no-tiles", action="store_true", help="skip coloured Settings tiles")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    f = Fetcher(args.base_url, delay=args.delay, verbose=args.verbose)

    print(f"[1/6] discovering app bundles at {args.base_url}{APP_INDEX}")
    app = discover_app(f)
    print(f"      main={app['main'].rsplit('/',1)[-1]}  styles={app['styles'].rsplit('/',1)[-1]}")

    print("[2/6] icon font")
    css = f.text(app["styles"])
    style = parse_stylesheet(css)
    woff = f.get(style["font_url"])
    write(out / "raw" / "jamf-icons.woff", woff)
    write(out / "raw" / os.path.basename(app["styles"]), css)
    glyphs = extract_font_glyphs(woff, out / "raw" / "jamf-icons.woff")
    for name, g in glyphs.items():
        write(out / "font" / f"{name}.svg", g["svg"])
    print(f"      {len(glyphs)} glyphs -> font/   ({len(style['codepoints'])} CSS classes)")

    print("[3/6] crawling JS import graph")
    chunks = crawl_chunks(f, app["app_dir"], app["main"])
    print(f"      {len(chunks)} chunks")
    icon_module, icons, export_to_var = find_icon_module(chunks)
    write(out / "raw" / icon_module, chunks[icon_module])
    print(f"      inline icon library: {icon_module} ({len(export_to_var)} icons)")
    usage = recover_usage_names(chunks, icon_module, set(export_to_var))
    matches = match_inline_to_font(icons, export_to_var, glyphs, usage)

    inline_entries = []
    taken: dict[str, int] = collections.Counter()
    export_to_name: dict[str, str] = {}
    for exp in sorted(export_to_var, key=lambda e: (len(e), e)):
        m = matches[exp]
        base = m["name"]
        taken[base] += 1
        fname = f"{base}.svg" if taken[base] == 1 else f"{base}-{taken[base]}.svg"
        write(out / "inline" / fname, inline_svg(icons[export_to_var[exp]]))
        export_to_name[exp] = base
        inline_entries.append(
            {
                "name": base,
                "file": fname,
                "export": exp,
                "method": m["method"],
                "confidence": m["confidence"],
                "usage_names": m["usage_names"],
                "font_candidates": m["candidates"],
                "viewBox": icons[export_to_var[exp]]["viewBox"],
            }
        )
    by_method = collections.Counter(e["method"] for e in inline_entries)
    print(f"      named via usage={by_method['usage']} geometry={by_method['geometry']} unnamed={by_method['none']} -> inline/")

    print("[4/6] Settings tiles")
    cards = parse_settings_cards(chunks, icon_module, export_to_var)
    for c in cards:
        slug = slugify(c["selector"].replace("jp-settings-page-", "").replace("jp-settings-", ""))
        c["slug"] = slug
        if "icon_export" in c and c["icon_export"] in export_to_var:
            c["icon_name"] = export_to_name[c["icon_export"]]
            c["icon_file"] = f"inline/{c['icon_name']}.svg"
            tok = style["colors"].get(c["color"] or "")
            if tok and not args.no_tiles:
                c["file"] = f"settings/{slug}.svg"
                c["colors"] = tok
                write(out / c["file"], tile_svg(icons[export_to_var[c["icon_export"]]], tok))
    print(f"      {len(cards)} cards, {sum(1 for c in cards if c.get('file'))} tiles -> settings/")

    print("[5/6] static SVG assets")
    assets = []
    for path in collect_asset_svgs(chunks):
        try:
            data = f.get(path)
        except Exception as e:
            print(f"      ! {path}: {e}")
            continue
        rel = "assets/" + path.split("assets/", 1)[1]
        write(out / rel, data)
        assets.append({"url": path, "file": rel})
        for c in cards:
            if c.get("svg_url") and path.endswith("/" + c["svg_url"].split("/", 1)[-1]):
                c["file"] = rel
    print(f"      {len(assets)} files -> assets/")

    print("[6/6] manifest + contact sheet")
    # The Jamf Pro version is only exposed behind auth; the hashed bundle names
    # uniquely identify the front-end build instead.
    build_id = f"{os.path.basename(app['main'])} / {os.path.basename(style['font_url']).split('?')[0]}"
    manifest = {
        "source": {
            "base_url": args.base_url,
            "app_index": APP_INDEX,
            "main": app["main"],
            "styles": app["styles"],
            "font_url": style["font_url"],
            "icon_module": icon_module,
            "build": build_id,
            "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "tile_style": {"size": TILE_SIZE, "padding": TILE_PAD, "radius": TILE_RADIUS, "colors": style["colors"]},
        "font": {n: {"file": f"font/{n}.svg", "codepoint": g["codepoint"]} for n, g in glyphs.items()},
        "inline": inline_entries,
        "settings": cards,
        "assets": assets,
    }
    write(out / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    write(out / "contact-sheet.html", contact_sheet(manifest))
    print(f"done -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

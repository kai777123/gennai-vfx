"""Rebuild site/index.html and site/README.md from shop_footer.json and each pack.

Run:  python -I site/tools/build_site.py
Facts come from the catalog (live packs only), pack.json (preset counts, Godot
versions, renderers) and the READMEs (sprite packs). Nothing is guessed: a value
that cannot be read is left out and printed as MISSING.
"""
import json, re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # C:\gennai
SITE = ROOT / "site"
CATALOG = ROOT / "tools/vfxpack/listing/shop_footer.json"
WHICH = ROOT / "ユーザ用/39_WhichPack_1020/which_pack.md"
BASE = "https://kai777123.github.io/gennai-vfx/"
SHOP = "https://gennai.itch.io"
BLUESKY = "https://bsky.app/profile/gennaivfx.bsky.social"
UTM = "?utm_source=github_pages&utm_medium=catalog"
H1 = "Godot 4 VFX Packs by gennai"
# itch public titles that differ from the catalog name (catalog starts with a coined word)
TITLE_OVERRIDE = {"fx2": "Pixel Art Laser Beam & Lightning VFX (ARCBIT)"}
# sprite packs without a pack.json: README that states Godot / Unity support
SPRITE_README = {"fx2": "fx2/docs/README_full.md",
                 "px_explosion": "px_explosion/pack/full/ARCBIT_Explosion/README.md"}
missing = []


def read_use_texts():
    """slug -> short use phrase from which_pack.md ('Fire, explosions: [..](url), 49 presets')."""
    out = {}
    if not WHICH.exists():
        missing.append("which_pack.md not found: use-phrases come from catalog blurbs")
        return out
    for line in WHICH.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(.+?):\s*\[.+?\]\(https://gennai\.itch\.io/([^)]+)\)", line)
        if m:
            out[m.group(2)] = m.group(1).strip()
    return out


def lc_first(s):
    return s[0].lower() + s[1:] if s and not s[:2].isupper() else s


def load():
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    uses = read_use_texts()
    packs = []
    for c in cat["catalog"]:
        if not c.get("live"):
            continue
        k = c["key"]
        p = {"key": k, "name": TITLE_OVERRIDE.get(k, c["name"]), "slug": c["slug"],
             "lite": c.get("lite_slug"), "blurb": c.get("blurb", "")}
        p["use"] = uses.get(c["slug"])
        if not p["use"]:
            missing.append(f"{k}: no use phrase in which_pack.md")
            p["use"] = p["blurb"].split(",")[0] if p["blurb"] else p["name"]
        pj = ROOT / k / "pack.json"
        if pj.exists() and not c.get("no_pack_json") and k not in SPRITE_README:
            d = json.loads(pj.read_text(encoding="utf-8"))
            cn = d.get("counts", {})
            p["presets"] = cn.get("presets")
            p["p3d"], p["p2d"] = cn.get("presets_3d"), cn.get("presets_2d")
            g = d.get("godot", {})
            p["tested"] = g.get("versions", [])
            p["renderers"] = g.get("renderers", [])
            p["sprite"] = False
            if p["presets"] is None:
                missing.append(f"{k}: counts.presets missing")
        else:
            p["sprite"] = True
            rd = ROOT / SPRITE_README[k] if k in SPRITE_README else None
            txt = rd.read_text(encoding="utf-8") if rd and rd.exists() else ""
            m = re.search(r"^(\d+)\s+(?:pixel-art|effects)", c.get("blurb", "")) or re.search(r"\b(\d+) effects", txt)
            p["effects"] = int(m.group(1)) if m else None
            if p["effects"] is None:
                missing.append(f"{k}: effect count not found")
            gm = re.search(r"Godot (4\.\d+)\+", txt)
            p["godot_min"] = gm.group(1) if gm else None
            tm = re.search(r"tested on (4\.\d+\.\d+) and (4\.\d+\.\d+)", txt)
            p["tested"] = list(tm.groups()) if tm else []
            p["unity"] = bool(re.search(r"Unity 20\d\d", txt))
            if not p["godot_min"]:
                missing.append(f"{k}: Godot minimum not found in README")
        packs.append(p)
    # Sales order (best sellers first), then the rest in catalog order.
    order = ["set_a_1004", "volt", "ice", "weather", "set_b_1004", "gun",
             "earth", "ambient", "px_explosion", "fx2"]
    packs.sort(key=lambda q: order.index(q["key"]) if q["key"] in order else len(order))
    return cat, packs


def count_text(p):
    if p["sprite"]:
        return f"{p['effects']} sprite effects" if p["effects"] else ""
    return f"{p['presets']} presets" if p["presets"] else ""


def desc_lines(p):
    """Two fact lines per pack (the third line is the link line)."""
    if p["sprite"]:
        l1 = re.sub(r",? (?:Godot|Unity)[^,]* included$", "", p["blurb"])
        l1 = l1[0].upper() + l1[1:] + "."
        eng = []
        if p.get("godot_min"):
            eng.append(f"a Godot {p['godot_min']}+ project")
        if p.get("unity"):
            eng.append("a Unity package")
        l2 = "Sprite sheets for any engine" + (", with " + " and ".join(eng) + " included." if eng else ".")
        return [l1, l2]
    blurb = p["blurb"] or f"{lc_first(p['use'])}, 3D + 2D, {p['presets']} presets"
    l1 = blurb[0].upper() + blurb[1:] + "."
    l2 = f"{p['p3d']} 3D and {p['p2d']} 2D presets, all made in code."
    return [l1, l2]


def url(slug):
    return f"{SHOP}/{slug}{UTM}"


def faq(packs):
    godot_packs = [p for p in packs if not p["sprite"]]
    common = set(godot_packs[0]["tested"])
    for p in godot_packs:
        common &= set(p["tested"])
    extra = sorted({v for p in godot_packs for v in p["tested"]} - common)
    tested = " and ".join(sorted(common))
    a1 = (f"The Godot packs need Godot 4.4 or newer and are tested on {tested}. "
          + (f"Ice & Frost was also tested on {', '.join(extra)}. " if extra and len([p for p in godot_packs if set(p['tested']) - common]) == 1 else (f"Some were also tested on {', '.join(extra)}. " if extra else ""))
          + "Versions in between should work too.")
    a2 = ("They're tested on Forward+, Mobile and Compatibility, and Web exports use Compatibility. "
          "The itch pages have browser demos you can try first.")
    a3 = ("You can use a pack in commercial or non-commercial games, apps and videos. It's royalty-free and needs no credit, "
          "and exported builds that contain it are fine. You can't resell or redistribute the pack itself. "
          "LICENSE.txt in the download has the full text.")
    a4 = ("A free version is a small slice of its pack, enough to try the look and the setup. "
          "The paid pack has the whole preset list and all the demo scenes. The itch page of each free version says what's in it.")
    uni = [p for p in packs if p.get("unity")]
    names = "; ".join(p["name"] for p in uni)
    a5 = (f"These ship with a Unity package: {names}. " if uni else "")
    a5 += "The other packs are Godot 4 only."
    return [("Godot 4.4 to 4.7", a1),
            ("Web exports and Compatibility", a2),
            ("License", a3),
            ("Free and paid versions", a4),
            ("Unity support", a5)]


def build():
    cat, packs = load()
    ngod = sum(1 for p in packs if not p["sprite"])
    nspr = len(packs) - ngod
    intro = (f"I make VFX packs for Godot 4 and sell them on itch.io. {ngod} of them are made entirely in code, "
             "without textures. They're tested on Forward+, Mobile and Compatibility, which also covers Web exports. "
             f"The other {nspr} are pixel-art sprite packs with a Godot project and a Unity package. "
             "Below is what each pack is for and where to get it.")
    desc = (f"Catalog of {len(packs)} VFX packs for Godot 4 by gennai: fire, lightning, weather, ice, guns, "
            "sword trails, ground, light shafts and pixel-art sprites. What each one is for, preset counts, free versions.")
    q = faq(packs)
    e = html.escape

    items = []
    for i, p in enumerate(packs, 1):
        prod = {"@type": "Product", "name": p["name"], "url": f"{SHOP}/{p['slug']}",
                "brand": {"@type": "Brand", "name": "gennai"}, "description": p["use"]}
        items.append({"@type": "ListItem", "position": i, "item": prod})
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": H1,
          "url": BASE, "itemListElement": items}

    rows = ""
    for p in packs:
        free = f'<a href="{e(url(p["lite"]))}">Free version</a>' if p["lite"] else ""
        rows += (f'<tr><td>{e(p["use"])}</td><td><a href="{e(url(p["slug"]))}">{e(p["name"])}</a></td>'
                 f'<td>{e(count_text(p))}</td><td>{free}</td></tr>\n')
    secs = ""
    for p in packs:
        lines = "".join(f"<p>{e(x)}</p>" for x in desc_lines(p))
        if p["lite"]:
            lines += f'<p><a href="{e(url(p["slug"]))}">Get the pack</a> or <a href="{e(url(p["lite"]))}">try the free version</a>.</p>'
        else:
            lines += f'<p><a href="{e(url(p["slug"]))}">Get the pack</a>.</p>'
        secs += f'<section><h3 id="{e(p["slug"])}">{e(p["name"])}</h3>{lines}</section>\n'
    faqh = "".join(f"<h3>{e(a)}</h3><p>{e(b)}</p>\n" for a, b in q)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(H1)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(H1)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}">
<style>
:root{{--bg:#fff;--fg:#1c1c20;--muted:#5b5b66;--link:#0b5cd5;--line:#d9d9e0;--head:#f2f2f6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16161a;--fg:#e8e8ee;--muted:#a0a0ad;--link:#7db2ff;--line:#34343c;--head:#22222a}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:60rem;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:1.9rem;line-height:1.25;margin:0 0 .6em}}
h2{{font-size:1.35rem;margin:2em 0 .5em}}
h3{{font-size:1.05rem;margin:1.4em 0 .3em}}
p{{margin:.4em 0}}
a{{color:var(--link)}}
.t{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;min-width:34rem}}
th,td{{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}}
th{{background:var(--head)}}
footer{{margin-top:2.5em;color:var(--muted)}}
</style>
<script type="application/ld+json">
{json.dumps(ld, indent=1, ensure_ascii=False)}
</script>
</head>
<body>
<main>
<h1>{e(H1)}</h1>
<p>{e(intro)}</p>
<h2>Which pack do I need?</h2>
<div class="t"><table>
<thead><tr><th>You need</th><th>Pack</th><th>Size</th><th>Free version</th></tr></thead>
<tbody>
{rows}</tbody>
</table></div>
<h2>The packs</h2>
{secs}<h2>FAQ</h2>
{faqh}<h2>Bundles</h2>
<p>Bundles and sales are on the author page: <a href="{SHOP}/{UTM}">{SHOP.replace('https://', '')}</a>.</p>
<footer>
<p>By gennai. <a href="{SHOP}/{UTM}">itch.io author page</a> | <a href="{BLUESKY}">Bluesky @gennaivfx.bsky.social</a></p>
</footer>
</main>
</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8", newline="\n")

    md = [f"# {H1}", "", intro, "", "## Which pack do I need?", "",
          "| You need | Pack | Size | Free version |", "|---|---|---|---|"]
    for p in packs:
        free = f"[Free version]({url(p['lite'])})" if p["lite"] else ""
        md.append(f"| {p['use']} | [{p['name']}]({url(p['slug'])}) | {count_text(p)} | {free} |")
    md += ["", "## The packs", ""]
    for p in packs:
        md += [f"### {p['name']}", ""] + [x + "  " for x in desc_lines(p)]
        if p["lite"]:
            md.append(f"[Get the pack]({url(p['slug'])}) or [try the free version]({url(p['lite'])}).")
        else:
            md.append(f"[Get the pack]({url(p['slug'])}).")
        md.append("")
    md += ["## FAQ", ""]
    for a, b in q:
        md += [f"### {a}", "", b, ""]
    md += ["## Bundles", "",
           f"Bundles and sales are on the author page: [{SHOP.replace('https://', '')}]({SHOP}/{UTM}).", "",
           f"By gennai. [itch.io author page]({SHOP}/{UTM}) | [Bluesky @gennaivfx.bsky.social]({BLUESKY})", ""]
    (SITE / "README.md").write_text("\n".join(md), encoding="utf-8", newline="\n")

    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8", newline="\n")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{BASE}</loc></url>\n</urlset>\n", encoding="utf-8", newline="\n")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {len(packs)} packs")
    for m in missing:
        print("MISSING:", m)


if __name__ == "__main__":
    build()

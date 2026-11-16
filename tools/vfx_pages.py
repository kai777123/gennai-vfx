"""Effect pages (site/vfx/*.html) and their list page (site/vfx/index.html).

Loaded by build_site.py. One static page per effect: an English title, a 100-150 word answer,
one GIF, the real call (1-5 lines from the pack's README / addon code), a button that loads the
pack's browser demo into an iframe only when pressed, and one link to the paid pack on itch.
Facts (preset counts, Godot versions, renderers) come from pack.json; nothing is guessed.
"""
import gzip, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
BASE = "https://kai777123.github.io/gennai-vfx/"
SHOP = "https://gennai.itch.io"
BUNDLE = "godot-4-vfx-complete-collection"
DATE = "2026-11-16"
PACK_DIR = {"dissolve": "gemini/dissolve"}          # packs whose folder is not <key>
ENGINE_GROUP = {"a": 29226613, "b": 39514754}
e = html.escape

# slot = which scene of the pack's showcase the demo opens on (None = its first scene, with the
# demo's own loading screen). "scene" is what the visitor sees there.
EFFECTS = [
    dict(file="burn-any-mesh-godot-4", key="set_a_1004", brand="PYROLUX", demo="pyrolux", slot=10, nscenes=15,
         scene="Set anything on fire", gif="pyrolux_burning_objects.gif",
         alt="PyroluxBurn3D spreading fire over crates and barrels in Godot 4, charring the surface",
         cap="Fire spreads from the hit point over a crate, a barrel and a figure, chars the surface, and the small crate burns away.",
         h1="Burn any mesh in Godot 4", short="Set a crate, barrel or character on fire from the point it was hit.",
         lead="If you want a crate, a barrel or a character to catch fire in Godot 4, you don't have to park a particle emitter on top of it. Add a PyroluxBurn3D node under the MeshInstance3D and call ignite() with the hit position. The fire starts at that point and spreads across the surface. It chars whatever it covers, and it can burn the object away, with a burned_out signal when it's finished. I built it to work on any mesh you give it. It's part of PYROLUX, which has {presets} fire, explosion, smoke and lava presets for Godot 4.4 and newer. It makes its look in code and needs no texture files, and it runs in a Web export. Read the code below, then press the button to run the demo right here.",
         code=['$Crate/PyroluxBurn3D.ignite(hit.position)          # fire spreads over the mesh from the hit point',
               '$Crate/PyroluxBurn3D.burned_out.connect(_on_crate_burned)',
               'Pyrolux.wind = Vector3(2, 0, 0)                    # flames, smoke and embers lean with it'],
         code_note="PyroluxBurn3D sits under the MeshInstance3D you want to burn. The wind line is global: every flame, smoke column and ember in the scene leans the same way.",
         more="The pack also has campfires, torches, walls of fire, explosions, smoke, sparks, lava, a flamethrower and a meteor strike, in 3D with a 2D side-view set and a pixel-art mode. I made the hit position the only thing you have to pass in."),
    dict(file="blow-up-anything-godot-4", key="blast", brand="BLASTLUX", demo="blastlux", slot=None, nscenes=None,
         scene="Everything in range reacts", gif="blastlux_everything_reacts.gif",
         alt="A grenade going off between crates, barrels and a figure in Godot 4: the crates scorch and one breaks apart",
         cap="A grenade goes off between barrels, crates and a figure: the meshes buckle and scorch on the blast side and the near crate breaks apart.",
         h1="Blow up anything in Godot 4", short="One call detonates a blast and every mesh in range reacts.",
         lead="One call sets off an explosion in Godot 4, and everything near it reacts. Blastlux.detonate(self, \"blast_frag_medium\", hit_point) draws a flash, a fireball, dust, a shock ring, sparks and debris, then leaves a crater in the floor. Meshes inside the blast radius get a pressure wave that runs through their vertices and springs back. The side facing the blast turns sooty and glows for a moment. A RigidBody3D gets pushed. If you've marked a mesh as breakable and it's close, it flies apart into pieces of itself. This is BLASTLUX, which has {presets} presets in 20 blast families for Godot 4.4 and newer, built without textures or imported meshes. Below are the call itself and a demo you can run in the page.",
         code=['Blastlux.detonate(self, "blast_frag_medium", hit_point)',
               '$Crate/Mesh.add_to_group("blastlux_targets")     # reacts even without a collider',
               '$Crate/Mesh.add_to_group("blastlux_breakable")   # flies apart when the blast is close'],
         code_note="detonate() returns the BlastluxBlast3D and frees it when it's done. Connect its detonated and shocked signals if you want to know what it hit.",
         more="The pack has 20 blast families, from grenades, fuel, barrels and vehicles to plasma, electric, cryo, flashbangs, mushroom clouds, cluster bombs and flak. Craters, smoke columns and debris can also be spawned on their own."),
    dict(file="lightning-bolt-godot-4", key="volt", brand="ARCFLUX", demo="arcflux", slot=None, nscenes=None,
         scene="Lightning Bolt", gif="arcflux_bolt.gif",
         alt="A branching lightning bolt striking between two points in Godot 4 with a flash",
         cap="Three bolt presets in blue, purple and gold. Every strike has a new shape.",
         h1="Strike lightning between any two points in Godot 4", short="Draw a branching bolt, a chain or a laser from code.",
         lead="Lightning in Godot 4 doesn't need a texture or an animated sprite. With ARCFLUX you create an ArcfluxBolt3D, add it to the scene and call strike(from, to). A branching bolt appears between the two points, flashes and fades, and each strike gets a new shape. Lasers and other continuous effects take set_active() instead, which turns a held button into one line. The pack has {presets} presets, {p3d} in 3D and {p2d} in 2D: bolts, sky strikes, chain lightning, arcs that stay attached to moving points, auras that crawl over a mesh, tesla coils, beams and an EMP ring, in six colour palettes. It's all generated at runtime in code and needs Godot 4.4 or newer. The code is below, along with a demo that runs in the page.",
         code=['var bolt := ArcfluxBolt3D.new()',
               'add_child(bolt)',
               'bolt.strike($Hand.global_position, $Enemy.global_position)',
               '$Laser.set_active(Input.is_action_pressed("fire"))     # a continuous beam'],
         code_note="Glow in a WorldEnvironment makes bolts look better, but each effect draws its own soft halo and reads fine without it.",
         more="Scaling a node scales everything in it: the geometry, the glow, the sparks and the light."),
    dict(file="freeze-and-shatter-godot-4", key="ice", brand="GLACILUX", demo="glacilux", slot=None, nscenes=None,
         scene="Freeze anything", gif="ice_freeze_and_thaw.gif",
         alt="A mesh freezing from the hit point, thawing and dripping in Godot 4",
         cap="Frost spreads from the hit point, then the ice melts, drips and leaves a wet sheen.",
         h1="Freeze and shatter any mesh in Godot 4", short="Frost that spreads from the hit point, then thaws or breaks into shards.",
         lead="To freeze a mesh in Godot 4, put a GlaciluxFreeze3D under the MeshInstance3D and call freeze() with the hit position. Frost spreads over the surface from that point. After that you have three ways out. thaw() melts the ice with drips and leaves a wet sheen. shatter() breaks it into shards of the mesh itself. reset() puts everything back exactly as it was. It also follows an animated character once you point the node at the AnimationPlayer. This is GLACILUX, which has {presets} ice and frost presets for Godot 4.4 and newer and uses no textures. The code is below, and the demo runs in the page when you press the button.",
         code=['$Crate/Freeze.freeze(hit.position)                 # frost spreads from the hit point',
               '$Crate/Freeze.thaw()                              # melts, drips, leaves a wet sheen',
               '$Crate/Freeze.shatter(hit.position, 1.4)          # breaks into shards of itself',
               '$Crate/Freeze.reset()                             # back to exactly how it started'],
         code_note="Freeze is a GlaciluxFreeze3D under the MeshInstance3D. Give it a shatter_delay and it breaks by itself that many seconds after it's fully frozen.",
         more="The rest of the pack covers ice spikes, frost novas, freeze rays, blizzards, walls of ice, ice projectiles and frozen ground. I kept the main calls for one mesh to those four."),
    dict(file="rain-and-weather-godot-4", key="weather", brand="NIMBLUX", demo="nimblux", slot=None, nscenes=None,
         scene="Rain", gif="nimblux_rain.gif",
         alt="Rain falling in a Godot 4 scene, with ripples and splash crowns on the ground",
         cap="Rain whose drops stay put in the world while the camera moves, with ripples and splashes on the ground.",
         h1="Add rain, snow and storms to a Godot 4 scene", short="Rain that follows the camera, and weather you can blend from code.",
         lead="Rain that stays put in the world while the camera moves takes one node in Godot 4. Create a NimbluxRain3D, add it to the scene and call set_amount_smooth(1.0, 5.0), and a drizzle becomes a downpour over five seconds. For a whole sky there's NimbluxWeather3D, which blends between weather profiles with transition_to(profile, seconds). The pack ships twelve profiles, from drizzle and downpour to thunderstorm, blizzard and sandstorm. Rain makes ripples and splash crowns on the ground, and roofs and tunnels can shelter whatever is under them. Snow, fog and wind work the same way. This is NIMBLUX: {presets} weather presets for Godot 4.4 and newer, 3D and 2D, with no textures. The code is below, and so is a demo that runs in the page.",
         code=['var rain := NimbluxRain3D.new()',
               'add_child(rain)',
               'rain.set_amount_smooth(1.0, 5.0)                   # drizzle to downpour over 5 seconds',
               '$Weather.transition_to(load("res://addons/nimblux_fx/profiles/blizzard.tres"), 20.0)   # $Weather is a NimbluxWeather3D'],
         code_note="Profiles are resources in addons/nimblux_fx/profiles. transition_to() takes any of them.",
         more="Beyond rain there's snow, fog banks, ground fog, wind with leaves and petals, sandstorms, cloud shadows, thunderstorms and drops on the camera lens. I made the drops live in the world, not on the screen."),
    dict(file="sword-trail-and-slash-godot-4", key="set_b_1004", brand="EDGEFLUX", demo="edgeflux", slot=None, nscenes=None,
         scene="Weapon Trails", gif="edgeflux_weapon_trails.gif",
         alt="Sword trails in five looks following a swinging blade in Godot 4",
         cap="A trail that follows the blade, in five looks, and stays smooth on fast swings.",
         h1="Add sword trails and slashes to any weapon in Godot 4", short="A trail that follows the blade, slash arcs and hit sparks.",
         lead="A sword trail in Godot 4 is a ribbon that follows two points on the blade and fades out behind them. With EDGEFLUX you add an EdgefluxWeaponTrail3D under the weapon and set base_offset and tip_offset. After that it draws itself. Set auto_emit_speed and it only draws while the blade is moving fast. A slash arc is one call, slash(), and slash(true) sweeps the other way for combo strings. hit() puts sparks where the blade lands. The pack has {presets} presets, {p3d} in 3D and {p2d} in 2D: trails, slashes, thrusts, claws, parries, energy shields, ground slams and dashes. It's for Godot 4.4 and newer and uses no textures. The code and a demo that runs in the page follow.",
         code=['$Sword/WeaponTrail.base_offset = Vector3(0, 0.2, 0)',
               '$Sword/WeaponTrail.tip_offset = Vector3(0, 1.1, 0)',
               '$Sword/WeaponTrail.auto_emit_speed = 4.0           # only draws while the blade moves fast',
               '$Slash.slash()                                     # slash(true) sweeps the other way',
               '$Hit.hit(point, normal)'],
         code_note="The trail node goes under the blade. Slash and hit nodes can stay in the scene, or you can spawn a preset that frees itself when it's done.",
         more="You also get four hit styles, parry and clash flashes, shields that ripple where they're hit, and a cel-shaded look. I set it up so an idle sword leaves nothing behind."),
    dict(file="dissolve-to-ash-godot-4", key="dissolve", brand="CINELUX", demo="cinelux", slot=None, nscenes=None,
         scene="Ash from where it was hit", gif="cinelux_ash_and_ember_dissolve.gif",
         alt="A walking figure turning to ash in Godot 4, with cracks glowing red and the ash blowing downwind",
         cap="A cinder bolt hits a walking figure's chest: cracks glow red, the body chars, and the ash blows downwind and heaps up at its feet.",
         h1="Dissolve any mesh to ash or stone in Godot 4", short="Turn a mesh to ash, stone, acid or dust from the point it was hit.",
         lead="Turning a mesh to ash in Godot 4 is one call to Cinelux.apply, passing the mesh and the style \"ash\". Change the style to \"petrify\" and the mesh turns to stone, then shatters. \"acid\" melts it into a puddle, and \"dust\" crumbles it to sand that blows away on the wind. The effect starts at the point you pass in. A hit on the chest makes the ash spread from the chest. The restore method on the CineluxDissolve3D node puts the original materials back. It works on any MeshInstance3D, including a walking character. This is CINELUX: {presets} presets for death, dissolve and petrify effects, with shatter bursts, rising souls and reaper slashes, for Godot 4.4 and newer, without textures. The code and a demo you can run in the page are below.",
         code=['Cinelux.apply($Enemy/Mesh, "ash", hit_point)         # or "petrify", "acid", "dust"',
               'var fx := CineluxDissolve3D.new()',
               '$Statue/Mesh.add_child(fx)',
               'fx.dissolve(hit_point)',
               'fx.restore()                                        # puts the original materials back'],
         code_note="Cinelux.apply is the one-line form. Keep a CineluxDissolve3D node around if you want its dissolved signal or need to restore the mesh later.",
         more="There are also 2D sprite dissolves and a pixel-art mode. Rocks and crates burst into debris, souls lift off fallen bodies, and doom marks and miasma clouds fill out the set. I added a restore method so you can bring a mesh back."),
    dict(file="status-effects-godot-4", key="status", brand="NOXALUX", demo="noxalux", slot=1, nscenes=11,
         scene="Five attributes", gif="noxalux_five_attributes.gif",
         alt="Burn, freeze, shock, poison and petrify each on its own figure in Godot 4",
         cap="Burn, Freeze, Shock, Poison and Petrify, each on its own target, named at its feet.",
         h1="Put burn, freeze, shock, poison and petrify on any mesh in Godot 4", short="Status effects that crawl over a mesh from the hit and stay on it as it moves.",
         lead="Burning, freezing, shock, poison and petrify can crawl over a mesh from the point of impact in Godot 4. With NOXALUX you call Noxalux.afflict($Enemy, Noxalux.Kind.BURN, hit_point, 4.0), and the effect spreads out from the hit for four seconds. If you want more control, add a NoxaluxStatus3D to the MeshInstance3D. apply() starts an effect or stacks it up to three times, and cleanse() removes one kind or all of them. The status stays on the mesh, which means a walking character carries it along. Effects also react to each other: a freeze bolt into a fire makes steam and puts it out. The pack has {presets} presets in 3D and 2D for Godot 4.4 and newer, with no textures. The code is below, plus a demo that runs in the page.",
         code=['Noxalux.afflict($Enemy, Noxalux.Kind.BURN, hit_point, 4.0)     # from the hit point, for four seconds',
               'var status := NoxaluxStatus3D.new()',
               '$Enemy/Body.add_child(status)                                # a MeshInstance3D',
               'status.apply(Noxalux.Kind.SHOCK, hit_point, 5.0, 2)           # crawls out from the hit; 2 = a second stack',
               'status.cleanse(Noxalux.Kind.ALL)                              # or one kind, or let it expire'],
         code_note="Stacks go from 1 to 3. The ticked signal reports the kind and the stack count on each tick, and the health you take off is up to you.",
         more="You get two palettes per kind and a 2D version. Bolts carry a status to a target, arcs jump from one body to the next, and burning patches sit on the floor. I kept a one-line form for the common case."),
]
CSS = """:root{--bg:#fff;--fg:#1c1c20;--muted:#5b5b66;--link:#0b5cd5;--line:#d9d9e0;--head:#f2f2f6;--code:#f5f5f8;--btn:#0b5cd5;--btnfg:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#16161a;--fg:#e8e8ee;--muted:#a0a0ad;--link:#7db2ff;--line:#34343c;--head:#22222a;--code:#1f1f26;--btn:#3d7fe0;--btnfg:#fff}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:46rem;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.9rem;line-height:1.25;margin:0 0 .4em}
h2{font-size:1.35rem;margin:2em 0 .5em}
p{margin:.6em 0}
a{color:var(--link)}
img{max-width:100%;height:auto;display:block;border-radius:6px}
figure{margin:1.2em 0}
figcaption{color:var(--muted);font-size:.9rem;margin-top:.4em}
pre{background:var(--code);border:1px solid var(--line);border-radius:6px;padding:12px 14px;overflow-x:auto;font-size:.88rem;line-height:1.45}
code{font-family:ui-monospace,Consolas,"SF Mono",monospace}
p code{background:var(--code);padding:1px 4px;border-radius:3px;font-size:.9em}
.t{overflow-x:auto}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line)}
th{background:var(--head)}
.meta{color:var(--muted);font-size:.9rem;margin:0 0 1.5em}
.demo{position:relative;width:100%;aspect-ratio:16/9;background:#101014;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:.6rem;padding:12px;text-align:center}
.demo iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.demo button{font:600 1.05rem system-ui,sans-serif;background:var(--btn);color:var(--btnfg);border:0;border-radius:8px;padding:.8rem 1.4rem;cursor:pointer}
.demo button:focus-visible{outline:3px solid #fff;outline-offset:2px}
.demo .note{color:#b8b8c4;font-size:.85rem;margin:0;max-width:30rem}
.cta{border:1px solid var(--line);border-radius:8px;padding:14px 16px;background:var(--head);margin:1.2em 0}
.cta p{margin:.3em 0}
ul.list{padding-left:1.2rem}
ul.list li{margin:.5em 0}
footer{margin-top:2.5em;color:var(--muted);border-top:1px solid var(--line);padding-top:1em}"""
GA = ('<script async src="https://www.googletagmanager.com/gtag/js?id=G-439CSY86RJ"></script>\n'
      "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-439CSY86RJ');</script>")


def utm(slug, campaign):
    return f"{SHOP}/{slug}?utm_source=github_pages&utm_medium=vfx&utm_campaign={campaign}"


def gz_mb(path, cache={}):
    """gzip size (level 6, like a CDN) of a file, in MB."""
    if path not in cache:
        cache[path] = len(gzip.compress(Path(path).read_bytes(), 6)) / 1e6
    return cache[path]


def pack_info(key, catalog):
    c = next(x for x in catalog["catalog"] if x["key"] == key)
    pj = ROOT / PACK_DIR.get(key, key) / "pack.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    cn = d.get("counts", {})
    g = d.get("godot", {})
    return dict(c=c, presets=cn.get("presets"), p3d=cn.get("presets_3d"), p2d=cn.get("presets_2d"),
                tested=g.get("versions", []), renderers=g.get("renderers", []))


def words(s):
    return len(re.findall(r"[A-Za-z0-9_$.()'\"-]+", s))


def build(catalog, missing, live_only_nav=True):
    out = SITE / "vfx"
    out.mkdir(exist_ok=True)
    pages = []
    for ef in EFFECTS:
        info = pack_info(ef["key"], catalog)
        ef["info"] = info
        ef["live"] = bool(info["c"].get("live"))
        ef["url"] = f"{BASE}vfx/{ef['file']}.html"
    for ef in EFFECTS:
        info = ef["info"]
        c = info["c"]
        lead = ef["lead"].format(presets=info["presets"], p3d=info["p3d"], p2d=info["p2d"])
        n = words(lead)
        if not 100 <= n <= 150:
            missing.append(f"vfx {ef['file']}: lead is {n} words (want 100-150)")
        ef["lead_text"] = lead
        name = c["name"]
        itch = utm(c["slug"], ef["file"])
        engine = "a" if ef["demo"] not in ("edgeflux", "noxalux") else "b"
        demo_dir = SITE / "demo" / ef["demo"]
        pck_mb = gz_mb(demo_dir / "index.pck")
        wasm_mb = gz_mb(SITE / "demo" / "_engine" / engine / "index.wasm")
        total_mb = max(1, round(wasm_mb + pck_mb + 0.65))
        q = f"?slot={ef['slot']}" if ef["slot"] is not None else ""
        demo_url = f"../demo/{ef['demo']}/index.html{q}"
        if ef["slot"] is not None:
            where = f"opens on scene {ef['slot'] + 1} of {ef['nscenes']}, “{ef['scene']}”"
        else:
            where = f"opens on its first scene, “{ef['scene']}”"
        tv = info["tested"]
        tested = tv[0] if len(tv) == 1 else ", ".join(tv[:-1]) + " and " + tv[-1]
        rend = {"forward_plus": "Forward+", "mobile": "Mobile", "gl_compatibility": "Compatibility"}
        rends = ", ".join(rend.get(r, r) for r in info["renderers"])
        facts = [("Pack", f'<a href="{e(itch)}">{e(name)}</a>'), ("Presets", f"{info['presets']} ({info['p3d']} 3D, {info['p2d']} 2D)"),
                 ("Godot", f"4.4 or newer, tested on {e(tested)}"), ("Renderers", e(rends) + " (Web exports use Compatibility)"),
                 ("Textures", "none: everything is made in code")]
        frows = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in facts)
        code = "\n".join(ef["code"])
        title = ef["h1"]
        desc = f"{ef['short']} {len(ef['code'])} lines of GDScript, a demo that runs in the page, and the {ef['brand']} pack for Godot 4.4+."
        desc = desc if len(desc) <= 200 else desc[:197] + "..."
        ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc,
              "url": ef["url"], "image": f"{BASE}img/{ef['gif']}", "datePublished": DATE, "dateModified": DATE,
              "author": {"@type": "Person", "name": "gennai", "url": SHOP + "/"}, "dependencies": "Godot 4.4 or newer",
              "mentions": {"@type": "Product", "name": name, "url": f"{SHOP}/{c['slug']}", "brand": {"@type": "Brand", "name": "gennai"}}}
        robots = "" if ef["live"] else '<meta name="robots" content="noindex">\n'
        others = "".join(f'<li><a href="{o["file"]}.html">{e(o["h1"])}</a></li>' for o in EFFECTS if o is not ef and o["live"])
        page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{ef['url']}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{ef['url']}">
<meta property="og:image" content="{BASE}img/{e(ef['gif'])}">
<style>
{CSS}
</style>
<script type="application/ld+json">
{json.dumps(ld, indent=1, ensure_ascii=False)}
</script>
</head>
<body>
<main>
<p class="meta"><a href="../">Godot 4 VFX Packs by gennai</a> › <a href="./">Try the effects</a></p>
<h1>{e(title)}</h1>
<p class="meta">Updated {DATE}. Tested on Godot {e(tested)}, Forward+ and Compatibility.</p>

<p>{e(lead)}</p>

<figure>
<img src="../img/{e(ef['gif'])}" alt="{e(ef['alt'])}" width="960" height="540">
<figcaption>{e(ef['cap'])}</figcaption>
</figure>

<h2>The code</h2>
<pre><code>{e(code)}
</code></pre>
<p>{e(ef['code_note'])}</p>

<h2>Try it in your browser</h2>
<div class="demo" id="demo" data-src="{e(demo_url)}">
<button type="button" id="demo-go">Try it in your browser</button>
<p class="note">It loads the pack's own demo, about {total_mb} MB the first time, and it {where}. Left and right arrow keys, or the on-screen buttons, move to other scenes. A desktop browser works best; the first start can take up to a minute while the shaders compile.</p>
</div>
<noscript><p><a href="{e(demo_url)}">Open the demo in its own page</a>.</p></noscript>
<script>
(function(){{var b=document.getElementById('demo-go'),d=document.getElementById('demo');
b.addEventListener('click',function(){{var f=document.createElement('iframe');f.src=d.getAttribute('data-src');
f.title='{e(ef["brand"])} demo';f.allow='autoplay; fullscreen';f.setAttribute('allowfullscreen','');
d.textContent='';d.appendChild(f);if(window.gtag)gtag('event','demo_start',{{page:'{e(ef['file'])}'}});}});}})();
</script>

<h2>What is in the pack</h2>
<p>{e(ef['more'])}</p>
<div class="t"><table>
<tbody>
{frows}</tbody>
</table></div>

<div class="cta">
<p><a href="{e(itch)}">Get {e(name)} on itch.io</a></p>
<p>There's also a bundle of my Godot 4 packs: <a href="{e(utm(BUNDLE, ef['file']))}">the complete collection</a>.</p>
</div>

<h2>More effects to try</h2>
<ul class="list">
{others}</ul>

<footer>
<p>All packs and guides: <a href="../">Godot 4 VFX Packs by gennai</a>. <a href="{SHOP}/?utm_source=github_pages&amp;utm_medium=vfx">itch.io author page</a></p>
</footer>
</main>
</body>
</html>
"""
        (out / f"{ef['file']}.html").write_text(page, encoding="utf-8", newline="\n")
        pages.append(ef)
    # list page
    live = [ef for ef in EFFECTS if ef["live"]]
    items = "".join(f'<li><a href="{ef["file"]}.html">{e(ef["h1"])}</a>. {e(ef["short"])} ({e(ef["brand"])})</li>\n' for ef in live)
    ldl = {"@context": "https://schema.org", "@type": "ItemList", "name": "Godot 4 VFX you can try in your browser",
           "url": f"{BASE}vfx/", "itemListElement": [{"@type": "ListItem", "position": i, "url": ef["url"], "name": ef["h1"]}
                                                      for i, ef in enumerate(live, 1)]}
    lt = "Godot 4 VFX you can try in your browser"
    ld_desc = (f"{len(live)} effects for Godot 4 (fire, explosions, lightning, ice, weather, sword trails, dissolve, status effects), "
               "each with the GDScript call and a demo that runs in the page.")
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(lt)}</title>
<meta name="description" content="{e(ld_desc)}">
<link rel="canonical" href="{BASE}vfx/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(lt)}">
<meta property="og:description" content="{e(ld_desc)}">
<meta property="og:url" content="{BASE}vfx/">
<style>
{CSS}
</style>
<script type="application/ld+json">
{json.dumps(ldl, indent=1, ensure_ascii=False)}
</script>
</head>
<body>
<main>
<p class="meta"><a href="../">Godot 4 VFX Packs by gennai</a> › Try the effects</p>
<h1>{e(lt)}</h1>
<p>Each page below is one effect for Godot 4: the call that makes it happen, a GIF, and a button that runs the pack's own demo in the page. Nothing downloads until you press the button. Every pack is made in code, without textures, and is tested on Forward+, Mobile and Compatibility.</p>
<ul class="list">
{items}</ul>
<p>The full list of packs, with free versions, is on <a href="../">the main page</a>.</p>
<footer>
<p><a href="{SHOP}/?utm_source=github_pages&amp;utm_medium=vfx">itch.io author page</a></p>
</footer>
</main>
</body>
</html>
"""
    (out / "index.html").write_text(page, encoding="utf-8", newline="\n")
    return live

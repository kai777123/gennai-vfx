"""Copy each pack's Web demo into site/demo/<name>/ and share the engine.

Run:  python -I site/tools/prep_demos.py
Reads (never changes) <pack>/web/. Two Godot web engines exist (identical bytes in every
pack of a group), so site/demo/_engine/a|b/ hold one copy each; every demo keeps only its
own index.pck, its page and its loading-screen files. The page's GODOT_CONFIG is rewritten
to load the engine from ../_engine/<group>/ (executable) and its own index.pck (mainPack).
"""
import hashlib, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DEMO = SITE / "demo"
# demo name -> (pack web folder, engine group)
DEMOS = {"pyrolux": ("set_a_1004", "a"), "blastlux": ("blast", "a"), "arcflux": ("volt", "a"),
         "glacilux": ("ice", "a"), "nimblux": ("weather", "a"), "cinelux": ("gemini/dissolve", "a"),
         "edgeflux": ("set_b_1004", "b"), "noxalux": ("status", "b")}
ENGINE_FILES = ["index.js", "index.wasm", "index.audio.worklet.js", "index.audio.position.worklet.js"]


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def main():
    groups = {}
    for name, (pack, g) in DEMOS.items():
        web = ROOT / pack / "web"
        sig = tuple(md5(web / f) for f in ENGINE_FILES)
        if g in groups and groups[g][0] != sig:
            raise SystemExit(f"engine of {pack} differs from group {g}: not sharing")
        groups.setdefault(g, (sig, web))
    for g, (sig, web) in groups.items():
        out = DEMO / "_engine" / g
        out.mkdir(parents=True, exist_ok=True)
        for f in ENGINE_FILES:
            if not (out / f).exists() or md5(out / f) != md5(web / f):
                shutil.copy2(web / f, out / f)
    report = {}
    for name, (pack, g) in DEMOS.items():
        web = ROOT / pack / "web"
        out = DEMO / name
        out.mkdir(parents=True, exist_ok=True)
        for f in web.iterdir():
            if f.name in ENGINE_FILES:
                continue
            if f.name == "index.html":
                t = f.read_text(encoding="utf-8")
                t = t.replace('<script src="index.js"></script>', f'<script src="../_engine/{g}/index.js"></script>')
                m = re.search(r"const GODOT_CONFIG = (\{.*?\});", t)
                cfg = json.loads(m.group(1))
                wasm = (web / "index.wasm").stat().st_size
                pck = (web / "index.pck").stat().st_size
                cfg["executable"] = f"../_engine/{g}/index"
                cfg["mainPack"] = "index.pck"
                cfg["fileSizes"] = {"index.pck": pck, f"../_engine/{g}/index.wasm": wasm}
                # ?slot=N[&hold=1] starts the demo on scene N (the showcase reads --slot=N / --hold itself)
                pre = ("(function(){var q=new URLSearchParams(location.search),s=q.get('slot');"
                       "if(s!==null&&/^\\d+$/.test(s)){var a=['--','--slot='+s];if(q.get('hold'))a.push('--hold');"
                       "GODOT_CONFIG.args=a;"
                       "}})();")
                # --slot skips the demo's own 'ready' call: lift the loading clip 4 s after the engine is up
                t = t.replace("setTimeout(window.fxPreviewDone, 75000);", "setTimeout(window.fxPreviewDone, GODOT_CONFIG.args.length ? 4000 : 75000);")

                if "web_note.js" in t:  # demos without the loading clip: drop the start note when --slot skips the demo's own call
                    pre += "if(GODOT_CONFIG.args.length)window.addEventListener('load',function(){setTimeout(function(){window.fxNoteDone&&window.fxNoteDone();},15000);});"
                t = t.replace(m.group(0), "const GODOT_CONFIG = " + json.dumps(cfg, separators=(",", ":")) + ";\n" + pre)
                (out / "index.html").write_text(t, encoding="utf-8", newline="\n")
            else:
                shutil.copy2(f, out / f.name)
        report[name] = (pack, g, (web / "index.pck").stat().st_size)
    for k, v in report.items():
        print(k, v)


if __name__ == "__main__":
    main()

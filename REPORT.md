# site report (2026-10-20)

Files: index.html, README.md, robots.txt, sitemap.xml, .nojekyll, tools/build_site.py, REPORT.md (git repo in site/, branch main).
Rebuild: python -I site/tools/build_site.py (run twice, output byte-identical).

Publishing: NOT published. gh CLI is not installed on this PC (coordinator: do not install). Local git init + commit only.
Steps for the coordinator: create public repo gennai-vfx under kai777123 (description "Godot 4 VFX packs by gennai: catalog and FAQ"), push main, then Settings -> Pages -> Deploy from branch main, folder / (or gh api -X POST repos/kai777123/gennai-vfx/pages -f build_type=legacy -f source[branch]=main -f source[path]=/). Expected URL: https://kai777123.github.io/gennai-vfx/

human_lint (reddit_post kind, body text of index.html): FAIL, AI degree 74% (threshold 54%). Remaining: 2 strong flags that come from the catalog itself
(comma lists without "and" in the table's "You need" column, taken from which_pack.md and the catalog blurbs; spec-style repetition of preset counts), plus length 825 words
(Reddit-post norm 420). Not 0; cutting them would remove the table content the task asks for. Needs a coordinator decision.

Values not available in pack.json / READMEs (not guessed):
- price: in no pack.json -> no offers.price in JSON-LD
- fx2 has no pack.json: effect count 16 from the catalog blurb, Godot 4.4+ / Unity 2022.3+ from fx2/docs/README_full.md
- px_explosion pack.json has no counts: 16 from the catalog blurb; Godot 4.4+ and Unity from its README
- bundle URL (itch.io/s/...): several different bundle URLs in notes, none confirmed current -> links to the author page
- fx2 title: catalog name "ARCBIT - Pixel Beams & Lightning" starts with a coined word; used the itch spec title prefix "Pixel Art Laser Beam & Lightning VFX (ARCBIT)" (same as which_pack.md). Please confirm
- px_explosion pack.json says its itch page was "Not published"; the catalog has live:true, so it is listed. Confirm it is public
- "browser demo on the itch pages" is inferred from web/ folders and pack.json web settings, not from live pages
- use phrases come from ユーザ用/39_WhichPack_1020/which_pack.md (found, used)

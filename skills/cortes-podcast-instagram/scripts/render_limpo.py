"""Render do vertical LIMPO de cada clipe com o motor da skill (render_clip) +
a decupagem padrão (captions.srt/.ass, timing por palavra) para a motion-vox.

A legenda no estilo da referência é queimada depois, por queimar_legenda.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

SK = Path(r"C:\Users\NOT - LIVE\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin"
          r"\9120283d-e4e9-43b8-9f03-34432aeed1ad\01aa1494-2237-435c-a60d-cb968be6d887\skills\corte-viral")
sys.path.insert(0, str(SK))
from scripts.render import render_clip  # noqa: E402
from scripts.subtitles import build_caption_files  # noqa: E402

RUN = Path(__file__).resolve().parent.parent
VIDEO = RUN.parent.parent / "EXECUTORIA CAST - METAL GLASS.mp4"

cfg = yaml.safe_load((SK / "config" / "default.yaml").read_text(encoding="utf-8"))
render_cfg = dict(cfg["render"])
render_cfg["make_captioned_version"] = False      # a legenda da referência entra depois
caption_cfg = dict(cfg["captions"])
style = dict(yaml.safe_load((SK / "config" / "caption_styles" / "clean.yaml").read_text(encoding="utf-8")))
style.update({"play_res_x": 1080, "play_res_y": 1920})

cands = {c["id"]: c for c in json.loads((RUN / "06-candidates.json").read_text(encoding="utf-8"))["clips"]}
plans = json.loads((RUN / "11-edit-plans.json").read_text(encoding="utf-8"))["plans"]
only = set(sys.argv[1:])

for plan in plans:
    cid = plan["clip_id"]
    if only and not any(cid.startswith(o) for o in only):
        continue
    out = RUN / "output" / "final-clips" / plan["primary_context"] / plan["output_slug"]
    meta = render_clip(VIDEO, cands[cid], plan, out, render_cfg)
    caps = build_caption_files(RUN / "02-transcript.json", plan["timeline"], out,
                               caption_config=caption_cfg, style=style)
    dur = meta["rendered_media"]["duration_seconds"]
    print(f"{plan['output_slug']}: {dur:.2f}s, {caps['count']} legendas de decupagem -> {out}", flush=True)

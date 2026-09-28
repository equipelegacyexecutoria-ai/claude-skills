"""Monta 11-edit-plans.json a partir de 06-candidates.json + enquadramento.json.

Edição simples (pedido do usuário): layout cover, sem punch-in, sem card, sem
B-roll, sem corte de respiro (as pausas medidas vão de 0,7 a 1,4s e várias são
retóricas). A única lógica editorial nova é o enquadramento por locutor.
"""
from __future__ import annotations

import json
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
cands = json.loads((RUN / "06-candidates.json").read_text(encoding="utf-8"))["clips"]
enq = json.loads((RUN / "assets" / "enquadramento.json").read_text(encoding="utf-8"))

NOMES = {"jane": "Jane (direita no plano das convidadas)",
         "fernanda": "Fernanda (esquerda no plano das convidadas)"}

plans = []
for c in cands:
    runs = enq[c["id"]]["runs"]
    timeline = []
    for i, r in enumerate(runs, start=1):
        quem = NOMES.get(r["quem"], r["quem"])
        timeline.append({
            "source_start": r["source_start"],
            "source_end": r["source_end"],
            "crop_anchor_x": r["crop_anchor_x"],
            "zoom": r["zoom"],
            "layout": "cover",
            "transition_in": "cut",
            "order": i,
            "framing_reason": f"locutor centralizado: {quem} — {r['motivo']}; enquadramento manual-assistido (voz+YuNet), não autoframe",
        })
    n = int(c.get("user_number") or 0)
    plans.append({
        "clip_id": c["id"],
        "output_slug": f"{n:02d}-{c['id'].split('-', 1)[1]}",
        "primary_context": c.get("primary_context") or "outro",
        "timeline": timeline,
        "captions": {
            "burn": True,
            "style": "referencia-sf-pro-black",
            "font": "SF Pro Text Black",
            "generator": "assets/legenda_ref.py",
            "notes": "caixa-alta branca, linha pequena + linha grande de destaque, palavra a palavra com desfoque",
        },
        "audio": {"mix": "original", "loudness_lufs": -14, "true_peak_db": -1.0},
        "cards": [],
        "optional_assets": [],
        "editor_notes": ("Edição simples só com legenda (pedido do usuário). Sem corte de respiro, sem punch-in. "
                         "Troca de enquadramento só onde a voz muda de pessoa ou a câmera do bruto corta."),
    })

out = {"schema_version": "1.0", "plans": plans}
(RUN / "11-edit-plans.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(plans), "planos;", sum(len(p["timeline"]) for p in plans), "trechos")

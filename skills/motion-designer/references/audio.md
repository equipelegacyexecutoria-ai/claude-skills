# Áudio: narração, trilha e efeitos

## Narração (Magnific / ElevenLabs)

- Vozes BR aprovadas: **Duarte Queiroz** (masculina, firme, anúncio). Outras boas: Rafael Valente,
  Catarina Cordeiro (feminina enérgica), Lívia Moreira (feminina leve).
- Escrever o texto com uma tag curta por trecho (`[serious]`, `[softly]`, `[confident]`, `[energetic]`,
  `[warm]`). Reticências criam pausa.
- Se passar do tempo, acelerar na mixagem (`atempo` 1,05–1,07) em vez de gerar de novo.
- Conferir pronúncia transcrevendo (`scripts/transcrever.py <audio> pt`).

## Trilha e efeitos (Artlist pelo Chrome)

- Não há conector: usar o Chrome logado do usuário. Busca de música:
  `https://artlist.io/royalty-free-music/search?terms=<termos>`; efeitos: `https://artlist.io/sfx/search?terms=<termos>`.
- A página só monta quando a aba está visível: tirar um print antes de procurar elementos.
- Baixar: botão de download da linha/página → "WAV". Os arquivos caem em `~/Downloads`.
- Termos que funcionaram: sombria "dark tension suspense cinematic" (ex.: "Coming Soon" — Jonathan
  Guerstein); rock "energetic rock driving drums" (ex.: "Shockwave - Instrumental version" — Ikoliks);
  corporativo "tech product launch upbeat" (ex.: "Beyond the Algorithm" — 331Music).
  Efeitos: "lightning strike", "whoosh transition", "ui click", "cinematic impact boom".
- Narração por cima: escolher versão instrumental / "No Backing Vocals".

## Encaixe na batida

- `python scripts/analisar_audio.py musica.wav` → BPM, batidas, energia por segundo e os picos (viradas).
- Escolher o ponto do arquivo onde a música "vira" e alinhar com o momento-chave do vídeo:
  `inicio_no_arquivo = pico_no_arquivo - momento_no_video`.
- Efeitos: `analisar_audio.py --picos efeito.wav` dá onde está o pico de cada efeito; o `mix_audio.py`
  posiciona cada efeito pelo pico, não pelo começo do arquivo.

## Mixagem (`scripts/mix_audio.py config.json`)

Exemplo de `config.json`:

```json
{
  "duracao": 44.5,
  "saida": "assets/audio/mix_final.wav",
  "voz": {"arquivo": "assets/audio/narracao.mp3", "atempo": 1.07, "inicio": 0.3, "volume": 1.0},
  "trilhas": [
    {"arquivo": "assets/audio/musicas/sombria.wav", "inicio_no_arquivo": 40.9, "entra": 0, "sai": 12.1, "volume": 0.95, "fade_saida": 0.5},
    {"arquivo": "assets/audio/musicas/rock.wav", "inicio_no_arquivo": 9.75, "entra": 13.85, "sai": 44.5, "volume": 0.62, "fade_saida": 1.4}
  ],
  "abaixar_musica_sob_voz": {"threshold": 0.05, "ratio": 3},
  "efeitos": [
    {"arquivo": "assets/audio/artlist/trovao.wav", "momento": 12.1, "pico": 0.30, "volume": 1.0}
  ],
  "loudness": -14
}
```

- Volume final: -14 LUFS (Instagram/TikTok). A música abaixa sozinha sob a voz e vai até o fim.

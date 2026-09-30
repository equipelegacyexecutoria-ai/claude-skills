// Gêmeo do medir.py para quando só houver Node (ex.: Claude Code no Windows sem Python).
// Mesmos comandos e mesma saída:  node scripts/medir.mjs manchete|capa|pag3|pag2|titulo|corpo "texto" ...
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const M = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), "..", "references", "metricas.json"), "utf8"));
const ALVO_CAPA = 975, BASE_CAPA = 1250;
// Capa aprovada em 28/09/2026 (DAHWgdFSrXw): círculo de 462 px a y 330. Desde 29/09/2026 o logo
// (logo + confete) já vem no template como um GRUPO: só se reposiciona, topo 150 px acima da H1.
const CIRC_LADO = 462.15, CIRC_TOP = 330.14;
const LOGO_LEFT = 477.21, LOGO_ACIMA = 150;
const ESC = M.degrade.escuro, H_FADE = M.degrade.altura_img;
const r1 = (x) => Math.round(x * 10) / 10;

// Páginas-modelo LEGACY (template, 2026-09-27): [top, left, altura] da foto e do degradê;
// ib = topo e altura da imagem FADE dentro do retângulo; ref = escuridão no topo do texto.
const PAG = {
  capa: { foto: [-10.0, -10.8, 1142.42], degrade: [386.8, -51.39, 747.62], ib: [-467.71, 1447.38], ref: 0.7 },
  pag2: { foto: [-17.47, -14.3, 1210.46], degrade: [472.23, -13.19, 769.05], ib: [-608.4, 1433.93], ref: null },
  pag3: { foto: [-17.47, -14.3, 942.88], degrade: [333.65, 0.0, 813.45], ib: [-620.47, 1433.93], ref: null },
};
const TITULO_TOP = 776.6, CORPO_TOP = 884.6, CORPO_BASE = 1317, TOPO_MINIMO = 350, PAG2_BASE = 1290.3, FOTO_MINIMA = 250;

function larguraEm(texto, fonte, espaco = 0) {
  const tab = M[fonte], padrao = fonte === "bebas" ? 400 : 600;
  let t = 0;
  for (const c of texto) t += tab[c] ?? (c.codePointAt(0) > 0x2fff ? 1200 : padrao);
  return t / 1000 + espaco * [...texto].length;
}

// ---------- degradê e foto ----------
function linhaDoEscuro(d) {
  const n = ESC.length;
  for (let i = 1; i < n; i++) {
    if (ESC[i] >= d) {
      const a = ESC[i - 1], b = ESC[i];
      const f = b > a ? (d - a) / (b - a) : 0;
      return ((i - 1 + f) * H_FADE) / (n - 1);
    }
  }
  return H_FADE;
}
const yDoEscuro = (p, gTop, d) => gTop + PAG[p].ib[0] + (linhaDoEscuro(d) * PAG[p].ib[1]) / H_FADE;
function escuroEm(p, gTop, y) {
  const i = ((y - gTop - PAG[p].ib[0]) / PAG[p].ib[1]) * (ESC.length - 1);
  if (i <= 0) return ESC[0];
  if (i >= ESC.length - 1) return ESC[ESC.length - 1];
  const a = Math.floor(i);
  return ESC[a] + (ESC[a + 1] - ESC[a]) * (i - a);
}
PAG.pag2.ref = PAG.pag3.ref = escuroEm("pag3", PAG.pag3.degrade[0], TITULO_TOP);

function encaixe(p, topoTexto) {
  const [g0, gl, gh] = PAG[p].degrade, [f0, fl, fh] = PAG[p].foto;
  let g = Math.min(g0, topoTexto - yDoEscuro(p, 0, PAG[p].ref));
  if (g0 - g < 3) g = g0;
  let f = f0 - Math.max(0, f0 + fh - (g + gh)); // a foto nunca passa do fim do degradê
  if (f0 - f < 1) f = f0;
  const y50 = yDoEscuro(p, g, 0.5);
  if (y50 < FOTO_MINIMA)
    return [{ foto_util: false, foto_visivel_ate_y: Math.round(y50), sujeito_entre_pct: null }, [{ op: "delete_element", elemento: "FOTO" }]];
  const res = {
    foto_util: true,
    degrade_top: r1(g),
    foto_top: r1(f),
    foto_visivel_ate_y: Math.round(y50),
    sujeito_entre_pct: [Math.round((100 * Math.max(0, -f)) / fh), Math.round((100 * (y50 - f)) / fh)],
  };
  const ops = [];
  if (g !== g0) ops.push({ op: "position_element", elemento: "DEGRADE", top: r1(g), left: gl });
  if (f !== f0) ops.push({ op: "position_element", elemento: "FOTO", top: r1(f), left: fl });
  return [res, ops];
}

// ---------- textos ----------
function dividirManchete(texto) {
  // Quebra H1 + H2 onde a menor das duas linhas fica com a maior fonte (vírgula ganha bônus);
  // manchete com duas frases ou com "|" quebra ali.
  if (texto.includes("|")) { const [x, ...y] = texto.split("|"); return [x.trim(), y.join("|").trim()]; }
  const fim = /[.!?]\s+(?=\S+\s+\S)/.exec(texto);
  if (fim && texto.slice(0, fim.index).split(/\s+/).length >= 2) {
    const corte = fim.index + fim[0].length;
    return [texto.slice(0, corte).trim(), texto.slice(corte).trim()];
  }
  const p = texto.split(/\s+/);
  let melhor = null;
  for (let i = 2; i < p.length - 1; i++) {
    const a = p.slice(0, i).join(" "), b = p.slice(i).join(" ");
    const pa = ALVO_CAPA / larguraEm(a.toUpperCase(), "bebas", -0.02);
    const pb = ALVO_CAPA / larguraEm(b.toUpperCase(), "bebas", -0.02);
    const nota = Math.min(pa, pb) + (a.endsWith(",") ? 6 : 0);
    if (!melhor || nota > melhor[0]) melhor = [nota, a, b];
  }
  return melhor ? [melhor[1], melhor[2]] : [texto, ""];
}

function capa(linhas, circulo = "direita") {
  if (linhas.length !== 3) throw new Error("capa: passe exatamente 3 linhas");
  const res = linhas.map((t) => {
    const em = larguraEm(t.toUpperCase(), "bebas", -0.02);
    const px = Math.floor(ALVO_CAPA / em); // format_text só aceita inteiro: para baixo, a linha nunca quebra
    return { texto: t, px, ui: r1(px * 0.75), largura: Math.round(em * px) };
  });
  const s = res.map((r) => r.px);
  const altura = 0.95 * (s[0] + s[1] + s[2]) + 0.149 * s[0] + 0.088 * s[2];
  const top = BASE_CAPA - altura;
  // H1, H2 e H3 são 3 caixas (uma por linha) com o mesmo espaçamento de uma caixa só com lh 0.95
  const tops = [top];
  tops.push(tops[0] + 1.099 * s[0] - 0.149 * s[1]);
  tops.push(tops[1] + 1.099 * s[1] - 0.149 * s[2]);
  const [enc, ops] = encaixe("capa", top);
  const manchete = ["H1", "H2", "H3"].flatMap((nome, i) => [
    { op: "format_text", elemento: nome, font_size: s[i] },
    { op: "position_element", elemento: nome, top: r1(tops[i]), left: 50.64 },
  ]);
  const logoTop = tops[0] - LOGO_ACIMA;
  const cTop = Math.min(CIRC_TOP, logoTop - 12 - CIRC_LADO);
  const cLeft = circulo === "esquerda" ? 50.64 : Math.round((1080 - 50.64 - CIRC_LADO) * 100) / 100;
  const extras = [
    { op: "resize_element", elemento: "CIRCULO", width: CIRC_LADO, height: CIRC_LADO },
    { op: "position_element", elemento: "CIRCULO", top: r1(cTop), left: cLeft },
    { op: "position_element", elemento: "LOGO", top: r1(logoTop), left: LOGO_LEFT, nota: "LOGO = o grupo (logo + confete) que já vem na capa do template" },
  ];
  const out = {
    linhas: res,
    altura_bloco: r1(altura),
    ...enc,
    circulo: { lado: circulo, x: [cLeft, Math.round(cLeft + CIRC_LADO)], y: [Math.round(cTop), Math.round(cTop + CIRC_LADO)] },
    operacoes: [...manchete, ...extras, ...ops],
    nota: "sujeito / ponto de fuga da foto principal do lado oposto ao círculo; nada importante atrás do logo",
  };
  if (cTop < 150) out.aviso = "manchete alta demais (linha curta = fonte enorme): círculo e logo apertados; conferir na miniatura";
  return out;
}

function titulo(texto, px = 80.0355, caixa = 931) {
  texto = texto.replaceAll("\n", " ");
  const w = (t) => larguraEm(t.toUpperCase(), "bebas") * px;
  const larg = w(texto);
  const out = { largura: Math.round(larg), linhas: larg <= caixa - 6 ? 1 : 2 };
  if (out.linhas === 1) { out.altura = 96; return out; }
  const p = texto.split(" ");
  let melhor = null;
  for (let i = 1; i < p.length; i++) {
    const a = p.slice(0, i).join(" "), b = p.slice(i).join(" ");
    const wa = w(a), wb = w(b);
    if (Math.max(wa, wb) > caixa - 6) continue;
    const nota = Math.abs(wa - wb) - (a.endsWith(",") ? 200 : 0);
    if (!melhor || nota < melhor[0]) melhor = [nota, a + "\n" + b];
  }
  if (!melhor) { // nem em 2 linhas: 3 linhas equilibradas
    out.linhas = 3;
    for (let i = 1; i < p.length - 1; i++)
      for (let j = i + 1; j < p.length; j++) {
        const partes = [p.slice(0, i).join(" "), p.slice(i, j).join(" "), p.slice(j).join(" ")];
        const ws = partes.map(w);
        if (Math.max(...ws) > caixa - 6) continue;
        const nota = Math.max(...ws) - Math.min(...ws);
        if (!melhor || nota < melhor[0]) melhor = [nota, partes.join("\n")];
      }
  }
  out.quebra = melhor ? melhor[1] : null;
  out.altura = 96 + 80 * (out.linhas - 1);
  return out;
}

function quebrar(par, px, larg) {
  const linhas = [];
  let atual = "";
  for (const w of par.split(" ")) {
    const tent = atual ? atual + " " + w : w;
    if (larguraEm(tent, "poppins_bold") * px * 1.011 <= larg || !atual) atual = tent; // 1,1%: calibrado com a quebra real do Canva
    else { linhas.push(atual); atual = w; }
  }
  linhas.push(atual);
  return linhas;
}

function corpo(pars, px = 40, larg = 974) {
  const medir = (l) => {
    const ls = pars.map((p) => quebrar(p, px, l));
    const n = ls.reduce((a, x) => a + x.length, 0) + pars.length - 1;
    const orf = ls.filter((x) => x.length > 1 && !x[x.length - 1].includes(" ")).map((x) => x[x.length - 1]);
    return [n, orf, ls];
  };
  const [n, orf, ls] = medir(larg);
  const out = { linhas: n, orfas: orf };
  if (orf.length) for (const l of [960, 945, 930, 920, 900, 880, 860, 850]) {
    const [n2, o2] = medir(l);
    if (!o2.length && n2 <= n) { out.sugestao_largura = l; break; }
  }
  const altura = 1.175 * px + (n - 1) * 1.375 * px;
  out.altura = r1(altura);
  out.corpo_top_pag3 = CORPO_TOP + altura <= CORPO_BASE ? CORPO_TOP : r1(CORPO_BASE - altura);
  out.linhas_texto = ls.flat();
  return out;
}

function pag3(tituloTxt, pars, larg = 974) {
  const t = titulo(tituloTxt);
  let px, c, l, cTop, tTop;
  for (px of [40, 36]) {
    c = corpo(pars, px, larg);
    l = c.sugestao_largura ?? larg;
    if (l !== larg) c = corpo(pars, px, l);
    cTop = c.corpo_top_pag3;
    tTop = r1(cTop - 12 - t.altura);
    if (tTop >= TOPO_MINIMO) break;
  }
  const [enc, opsEnc] = encaixe("pag3", tTop);
  const ops = [];
  if (tTop !== TITULO_TOP) ops.push({ op: "position_element", elemento: "TITULO", top: tTop, left: 64.22 });
  if (px !== 40) ops.push({ op: "format_text", elemento: "CORPO", font_size: Math.floor(px) });
  if (l !== larg) ops.push({ op: "resize_element", elemento: "CORPO", width: l });
  if (cTop !== CORPO_TOP) ops.push({ op: "position_element", elemento: "CORPO", top: cTop, left: 68.22 });
  const out = {
    titulo: { texto: t.quebra || tituloTxt, linhas: t.linhas, top: tTop },
    corpo: { px, linhas: c.linhas, orfas: c.orfas, largura: l, top: cTop },
    ...enc,
    operacoes: [...ops, ...opsEnc],
  };
  const avisos = [];
  if (tTop < TOPO_MINIMO) avisos.push("card muito longo: mesmo com o corpo em 36 px o título passa do limite");
  if (!enc.foto_util) avisos.push("texto ocupa o card: sem foto (não buscar imagem; a foto de exemplo é apagada)");
  if (avisos.length) out.aviso = avisos.join("; ") + ". Contar na entrega.";
  return out;
}

function pag2(pars, larg = 974) {
  let c = corpo(pars, 53.333, larg), px = 53.333;
  if (c.linhas > 6) { px = c.linhas <= 9 ? 44 : 40; c = corpo(pars, px, larg); }
  const l = c.sugestao_largura ?? larg;
  if (l !== larg) c = corpo(pars, px, l);
  const topo = r1(PAG2_BASE - c.altura);
  const [enc, opsEnc] = encaixe("pag2", topo);
  const ops = px !== 53.333 ? [{ op: "format_text", elemento: "CORPO", font_size: Math.floor(px) }] : [];
  if (l !== larg) ops.push({ op: "resize_element", elemento: "CORPO", width: l });
  const out = { corpo: { px, linhas: c.linhas, orfas: c.orfas, largura: l, top_calculado: topo }, ...enc, operacoes: [...ops, ...opsEnc] };
  if (!enc.foto_util) out.aviso = "texto ocupa o card: sem foto (não buscar imagem; a foto de exemplo é apagada). Contar na entrega.";
  return out;
}

const [cmd, ...args] = process.argv.slice(2);
const opts = { "--tam": 40, "--larg": 974, "--circulo": "direita" };
const textos = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] in opts) opts[args[i]] = args[i] === "--circulo" ? args[++i] : Number(args[++i]);
  else textos.push(args[i]);
}
const cmds = {
  manchete: () => { const [h1, h2] = dividirManchete(textos[0]); return capa([h1, h2, textos[1]], opts["--circulo"]); },
  capa: () => capa(textos, opts["--circulo"]),
  pag3: () => pag3(textos[0], textos.slice(1), opts["--larg"]),
  pag2: () => pag2(textos, opts["--larg"]),
  titulo: () => titulo(textos.join(" ")),
  corpo: () => corpo(textos, opts["--tam"], opts["--larg"]),
};
if (!cmds[cmd]) { console.error('uso: node scripts/medir.mjs manchete|capa|pag3|pag2|titulo|corpo "texto" ...'); process.exit(1); }
console.log(JSON.stringify(cmds[cmd](), null, 1));

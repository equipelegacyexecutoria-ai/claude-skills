// Confere um Playbook Legacy: dados da capa, ordem dos capítulos, componentes do catálogo,
// links internos, capturas, design travado e escrita.
// Uso: node verificar.mjs "<pasta>\Playbook X.html"     (código de saída 1 se houver ERRO)
// O montar.mjs já chama esta conferência no fim; rode sozinho só para conferir um arquivo.
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
export const TEMPLATE = path.join(AQUI, '..', 'assets', 'template.html');
export const MARCA_INICIO = '<!-- playbook:secoes:inicio -->';
export const MARCA_FIM = '<!-- playbook:secoes:fim -->';
export const RE_DADOS = /<script type="application\/json" id="playbook-dados">([\s\S]*?)<\/script>/;
export const RE_SHOTS = /const SHOTS = (\{.*\});/;

// ---------- dados da capa ----------
const ARTIGOS = ['do', 'da', 'de', 'dos', 'das'];
export function validarDados(d) {
  const e = [];
  if (!d || typeof d !== 'object') return ['bloco de dados ausente ou inválido'];
  const txt = (k, max) => {
    if (typeof d[k] !== 'string' || !d[k].trim()) e.push(`dados: falta "${k}"`);
    else if (max && d[k].length > max) e.push(`dados: "${k}" tem ${d[k].length} caracteres (máximo ${max})`);
  };
  txt('nome', 40);
  txt('area', 40);
  txt('lead', 320);
  if (!ARTIGOS.includes(d.artigo)) e.push(`dados: "artigo" deve ser um de ${ARTIGOS.join(', ')} (ex.: "Playbook do JEV Lab")`);
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(d.atualizado || '');
  if (!m || new Date(`${m[3]}-${m[2]}-${m[1]}T12:00:00`).getDate() !== Number(m[1])) e.push('dados: "atualizado" precisa ser uma data dd/mm/aaaa');
  if (!Array.isArray(d.faixa) || d.faixa.length !== 2 || d.faixa.some((f) => typeof f !== 'string' || !f.trim())) e.push('dados: "faixa" precisa ter exatamente 2 frases curtas');
  else d.faixa.forEach((f) => f.length > 38 && e.push(`dados: frase da faixa longa demais (${f.length} caracteres, máximo 38): "${f}"`));
  for (const k of ['contexto', 'ajuda']) if (d[k] != null && typeof d[k] !== 'string') e.push(`dados: "${k}" precisa ser texto`);
  const extras = Object.keys(d).filter((k) => !['nome', 'artigo', 'area', 'atualizado', 'lead', 'faixa', 'contexto', 'ajuda'].includes(k));
  if (extras.length) e.push(`dados: campos desconhecidos: ${extras.join(', ')}`);
  return e;
}

// ---------- leitor de HTML mínimo (suficiente para o conteúdo dos playbooks) ----------
const VAZIOS = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
const decode = (s) =>
  s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) =>
    e[0] === '#' ? String.fromCodePoint(/x/i.test(e[1]) ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10)) : (ENT[e.toLowerCase()] ?? m),
  );

export function parse(html, linhaBase = 1) {
  const quebras = [];
  for (let i = html.indexOf('\n'); i !== -1; i = html.indexOf('\n', i + 1)) quebras.push(i);
  const linhaDe = (idx) => {
    let lo = 0;
    let hi = quebras.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (quebras[mid] < idx) lo = mid + 1;
      else hi = mid;
    }
    return lo + linhaBase;
  };
  const raiz = { tag: '#raiz', attrs: {}, filhos: [], pai: null, linha: linhaBase };
  let atual = raiz;
  const re = /<!--[\s\S]*?-->|<(\/?)([a-zA-Z][\w-]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*(\/?)>|[^<]+|</g;
  let m;
  while ((m = re.exec(html))) {
    const [tudo, fecha, tag, attrsTxt = '', auto] = m;
    if (tudo.startsWith('<!--')) continue;
    if (!tag) {
      atual.filhos.push({ texto: decode(tudo) });
      continue;
    }
    const t = tag.toLowerCase();
    if (fecha) {
      let e = atual;
      while (e && e.tag !== t) e = e.pai;
      if (e && e.pai) atual = e.pai;
      continue;
    }
    const attrs = {};
    for (const a of attrsTxt.matchAll(/([^\s=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) attrs[a[1].toLowerCase()] = decode(a[2] ?? a[3] ?? a[4] ?? '');
    const el = { tag: t, attrs, filhos: [], pai: atual, linha: linhaDe(m.index) };
    atual.filhos.push(el);
    if (!VAZIOS.has(t) && !auto) atual = el;
  }
  return raiz;
}

const els = (el) => {
  const out = [];
  const walk = (e) => {
    for (const f of e.filhos) {
      if (!f.tag) continue;
      out.push(f);
      walk(f);
    }
  };
  walk(el);
  return out;
};
const filhos = (el) => el.filhos.filter((f) => f.tag);
const texto = (el) => (el.texto != null ? el.texto : el.filhos.map(texto).join(''));
const limpo = (s) => s.replace(/\s+/g, ' ').trim();
const cls = (el) => (el.attrs?.class || '').split(/\s+/).filter(Boolean);
const tem = (el, c) => cls(el).includes(c);
const BLOCOS = new Set(['p', 'ul', 'ol', 'li', 'div', 'table', 'figure', 'pre', 'details', 'dl', 'section', 'code', 'kbd']);
const textoProprio = (el) => el.filhos.map((f) => (f.texto != null ? f.texto : BLOCOS.has(f.tag) ? ' ' : textoProprio(f))).join('');
const trecho = (s, n = 70) => {
  const t = limpo(s);
  return t.length > n ? t.slice(0, n - 1) + '…' : t;
};

// ---------- catálogo: tudo o que o conteúdo pode usar ----------
const TAGS = new Set(
  'section span h2 h3 h4 p b strong a ul ol li div figure img figcaption table thead tbody tr th td code kbd pre details summary dl dt dd br hr'.split(' '),
);
const CLASSES = new Set(
  'chapter eyebrow title hl lead steps plain sep ui go ok cmd note tip info warn danger h shot browser road cards card main tag praticas check tree d c faq gloss table a'.split(' '),
);
const ATRIBUTOS = new Set(['id', 'class', 'href', 'alt', 'colspan', 'rowspan', 'open', 'target', 'rel', 'width', 'height']);
const TIPOS_AVISO = ['tip', 'info', 'warn', 'danger'];
const INICIO = ['comece', 'o-que-e', 'antes'];
const FIM = ['boas-praticas', 'problemas', 'glossario'];

export function verificar(html, template) {
  const erros = [];
  const avisos = [];
  const info = {};
  const onde = (el, sec) => `[${sec?.attrs?.id || '?'}] linha ${el.linha}`;

  // design travado: CSS, JS e ícones iguais aos do template
  if (template) {
    const bloco = (s, re) => (s.match(re)?.[1] || '').replace(/\r\n/g, '\n').replace(/const SHOTS = [^\n]*;/, 'const SHOTS = {};').trim();
    for (const [nome, re] of [
      ['CSS', /<style id="playbook-legacy-css">([\s\S]*?)<\/style>/],
      ['JavaScript', /<script id="playbook-legacy-js">([\s\S]*?)<\/script>/],
      ['logo e ícones', /(<svg class="sprite"[\s\S]*?<\/svg>)/],
    ]) {
      if (bloco(html, re) !== bloco(template, re)) erros.push(`O ${nome} do arquivo é diferente do template: o design foi mexido à mão ou o template mudou. Rode o montar.mjs neste arquivo.`);
    }
  }

  // sobras de rascunho
  const semShots = html.replace(RE_SHOTS, '');
  for (const [re, nome] of [
    [/@@[A-Z_0-9]+@@/, 'marcador @@…@@ do template'],
    [/PREENCHER/, 'PREENCHER'],
    [/\bTODO\b/, 'TODO'],
    [/\bXXX\b/, 'XXX'],
    [/lorem ipsum/i, 'lorem ipsum'],
  ]) {
    const m = re.exec(semShots);
    if (m) erros.push(`Sobrou "${nome}" do rascunho perto de: "${trecho(semShots.slice(Math.max(0, m.index - 40), m.index + 40))}"`);
  }

  // dados da capa
  let dados = null;
  const md = RE_DADOS.exec(html);
  if (!md) erros.push('Falta o bloco de dados (<script type="application/json" id="playbook-dados">).');
  else {
    try {
      dados = JSON.parse(md[1]);
      erros.push(...validarDados(dados));
    } catch (e) {
      erros.push(`Bloco de dados não é um JSON válido: ${e.message}`);
    }
  }

  // capítulos
  const i0 = html.indexOf(MARCA_INICIO);
  const i1 = html.indexOf(MARCA_FIM);
  if (i0 === -1 || i1 === -1) {
    erros.push('Arquivo sem as marcas dos capítulos: ele ainda não passou pelo montar.mjs.');
    return { erros, avisos, info };
  }
  const conteudo = html.slice(i0 + MARCA_INICIO.length, i1);
  const linhaBase = html.slice(0, i0 + MARCA_INICIO.length).split('\n').length;
  const raiz = parse(conteudo, linhaBase);
  const todos = els(raiz);

  for (const [re, nome] of [
    [/<style[\s>]/i, '<style>'],
    [/<script[\s>]/i, '<script>'],
    [/<link[\s>]/i, '<link>'],
    [/<iframe[\s>]/i, '<iframe>'],
  ])
    if (re.test(conteudo)) erros.push(`Os capítulos não podem ter ${nome}: o design e o código ficam só no template.`);

  const secoes = filhos(raiz).filter((e) => e.tag === 'section');
  const soltos = filhos(raiz).filter((e) => e.tag !== 'section');
  if (soltos.length) erros.push(`Há conteúdo fora de <section class="chapter"> (linha ${soltos[0].linha}, <${soltos[0].tag}>).`);
  const secDe = (el) => {
    let e = el;
    while (e && e.tag !== 'section') e = e.pai;
    return e;
  };

  // componentes: só o que está no catálogo
  for (const el of todos) {
    const sec = secDe(el);
    if (!TAGS.has(el.tag)) erros.push(`${onde(el, sec)}: <${el.tag}> não faz parte do catálogo de componentes.`);
    for (const c of cls(el)) if (!CLASSES.has(c)) erros.push(`${onde(el, sec)}: classe "${c}" não existe no catálogo (não invente componentes).`);
    for (const a of Object.keys(el.attrs)) {
      if (a === 'style') erros.push(`${onde(el, sec)}: atributo style não é permitido (o visual vem do template).`);
      else if (a === 'src' && el.tag === 'img') {
        if (!/^data:image\//.test(el.attrs.src)) erros.push(`${onde(el, sec)}: imagem por link ("${trecho(el.attrs.src, 40)}"). Use data-shot e embuta com --capturas.`);
      } else if (!ATRIBUTOS.has(a) && !a.startsWith('data-')) erros.push(`${onde(el, sec)}: atributo "${a}" não é permitido.`);
    }
  }

  // ordem fixa dos capítulos
  let k = 0;
  const pega = (cond) => (k < secoes.length && cond(secoes[k]) ? secoes[k++] : null);
  for (const id of INICIO) if (!pega((s) => s.attrs.id === id)) erros.push(`Falta o capítulo #${id} no lugar certo. Ordem fixa: comece, o-que-e, antes, passo-1…N, extras, custos (opcional), boas-praticas, problemas, glossario.`);
  let n = 0;
  while (pega((s) => s.attrs.id === `passo-${n + 1}`)) n++;
  if (!n) erros.push('Nenhum passo: depois de #antes vêm os capítulos passo-1, passo-2… (com data-passo="1", "2"…).');
  while (pega((s) => s.attrs['data-tipo'] === 'extra'));
  pega((s) => s.attrs.id === 'custos');
  for (const id of FIM) if (!pega((s) => s.attrs.id === id)) erros.push(`Falta o capítulo #${id} (ou está fora do lugar). Os três últimos são sempre boas-praticas, problemas e glossario.`);
  if (k < secoes.length) erros.push(`Capítulo fora do lugar: #${secoes[k].attrs.id || '(sem id)'}. Capítulo extra precisa de data-tipo="extra" e fica entre o último passo e custos/boas-praticas.`);
  if (n > 10) avisos.push(`${n} passos é muito: junte passos ou divida em dois playbooks (o ideal é de 3 a 8).`);
  else if (n && n < 3) avisos.push(`Só ${n} passo(s): confira se o processo não merece ser quebrado em mais etapas.`);

  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  const vistos = new Set();
  let grupoAtual = null;
  const gruposVistos = new Set();
  const grupoDe = {};
  secoes.forEach((s, idx) => {
    const id = s.attrs.id;
    grupoDe[id] = s.attrs['data-grupo'] || grupoAtual;
    if (!tem(s, 'chapter')) erros.push(`[${id}] linha ${s.linha}: a <section> precisa de class="chapter".`);
    if (!id) erros.push(`linha ${s.linha}: capítulo sem id.`);
    if (vistos.has(id)) erros.push(`[${id}] id repetido.`);
    vistos.add(id);
    const g = s.attrs['data-grupo'];
    if (idx === 0 && !g) erros.push('[comece] o primeiro capítulo precisa de data-grupo (ex.: data-grupo="Comece aqui").');
    if (g && g !== grupoAtual) {
      if (gruposVistos.has(g)) avisos.push(`[${id}] o grupo "${g}" aparece de novo depois de outro grupo: o sumário fica com o título repetido.`);
      gruposVistos.add(g);
      grupoAtual = g;
    }
    const f = filhos(s);
    const eyebrow = f.find((e) => e.tag === 'span' && tem(e, 'eyebrow'));
    const titulo = f.find((e) => e.tag === 'h2' && tem(e, 'title'));
    if (!eyebrow) erros.push(`[${id}] falta o <span class="eyebrow"> no começo do capítulo.`);
    if (!titulo) erros.push(`[${id}] falta o <h2 class="title">.`);
    const m = /^passo-(\d+)$/.exec(id || '');
    if (m) {
      if (s.attrs['data-passo'] !== m[1]) erros.push(`[${id}] precisa de data-passo="${m[1]}".`);
      if (eyebrow && !new RegExp(`^passo ${m[1]}(\\b|$)`, 'i').test(limpo(texto(eyebrow)))) erros.push(`[${id}] a etiqueta precisa começar com "passo ${m[1]}" (achei "${limpo(texto(eyebrow))}").`);
    }
    if (titulo) {
      const hls = els(titulo).filter((e) => tem(e, 'hl'));
      if (hls.length !== 1) avisos.push(`[${id}] o título tem ${hls.length} destaques (<span class="hl">); o padrão é exatamente 1.`);
      hls.forEach((h) => limpo(texto(h)).split(' ').length > 3 && avisos.push(`[${id}] destaque do título longo demais: "${limpo(texto(h))}" (máximo 3 palavras).`));
      const rotulo = s.attrs['data-toc'] || limpo(texto(titulo));
      if (rotulo.length > 34) avisos.push(`[${id}] nome no sumário longo (${rotulo.length} caracteres): use data-toc com até 34.`);
    }
    const nNotas = f.filter((e) => tem(e, 'note')).length;
    if (nNotas > 3) avisos.push(`[${id}] ${nNotas} avisos seguidos no capítulo: deixe no máximo 3 (aviso demais vira ruído).`);
  });

  // grupos do sumário: "Comece aqui" → nome do fluxo → "Mais"
  if (grupoDe.comece && grupoDe.comece !== 'Comece aqui') avisos.push('[comece] o primeiro grupo do sumário se chama "Comece aqui" (data-grupo="Comece aqui").');
  if (grupoDe['passo-1'] && ['Comece aqui', 'Mais'].includes(grupoDe['passo-1'])) avisos.push('[passo-1] os passos abrem um grupo com o nome do fluxo (ex.: data-grupo="Passo a passo").');
  if (grupoDe['boas-praticas'] && grupoDe['boas-praticas'] !== 'Mais') avisos.push('[boas-praticas] os capítulos finais ficam no grupo "Mais": ponha data-grupo="Mais" no primeiro capítulo depois do fluxo principal.');

  // o caminho: um cartão por passo, na ordem
  const comece = secoes.find((s) => s.attrs.id === 'comece');
  const road = comece && els(comece).find((e) => tem(e, 'road'));
  if (comece && !road) erros.push('[comece] falta o <div class="road"> com um cartão por passo.');
  if (road) {
    const as = filhos(road).filter((e) => e.tag === 'a');
    if (as.length !== n) erros.push(`[comece] o caminho tem ${as.length} cartões, mas há ${n} passos.`);
    as.forEach((a, i) => {
      if (a.attrs.href !== `#passo-${i + 1}`) erros.push(`[comece] o cartão ${i + 1} do caminho aponta para "${a.attrs.href}" (esperado #passo-${i + 1}).`);
      const st = filhos(a).find((e) => e.tag === 'strong');
      const sp = filhos(a).find((e) => e.tag === 'span');
      if (!st || !sp) erros.push(`[comece] o cartão ${i + 1} precisa de <strong>título</strong> e <span>dica curta</span>.`);
      else if (limpo(texto(sp)).length > 60) avisos.push(`[comece] dica do cartão ${i + 1} longa (${limpo(texto(sp)).length} caracteres, ideal até 60).`);
    });
  }

  // componentes com forma fixa
  for (const el of todos) {
    const sec = secDe(el);
    if (tem(el, 'note')) {
      const tipos = cls(el).filter((c) => TIPOS_AVISO.includes(c));
      if (tipos.length !== 1) erros.push(`${onde(el, sec)}: o aviso precisa de um tipo: note tip, note info, note warn ou note danger.`);
      const p = filhos(el)[0];
      if (!p || p.tag !== 'b' || !tem(p, 'h')) erros.push(`${onde(el, sec)}: o aviso começa com <b class="h">título</b>.`);
    }
    if (el.tag === 'details') {
      if (!tem(el, 'faq')) erros.push(`${onde(el, sec)}: <details> só como pergunta (class="faq").`);
      if (filhos(el)[0]?.tag !== 'summary') erros.push(`${onde(el, sec)}: a pergunta começa com <summary>.`);
    }
    if (el.tag === 'figure') {
      const imgs = els(el).filter((e) => e.tag === 'img');
      if (!tem(el, 'shot') || imgs.length !== 1) erros.push(`${onde(el, sec)}: <figure class="shot"> com exatamente uma imagem.`);
    }
    if (el.tag === 'img') {
      if (!limpo(el.attrs.alt || '')) erros.push(`${onde(el, sec)}: imagem sem alt (descreva o que aparece na tela).`);
      if (!el.attrs['data-shot'] && !el.attrs.src) erros.push(`${onde(el, sec)}: imagem sem data-shot.`);
    }
    if (el.tag === 'ol' && tem(el, 'steps')) {
      for (const li of filhos(el)) {
        const b = filhos(li)[0];
        const antes = li.filhos[0]?.texto != null && li.filhos[0].texto.trim();
        if (!b || b.tag !== 'b' || antes) {
          avisos.push(`${onde(li, sec)}: o passo começa com o título em negrito (<b>Faça isso.</b>): "${trecho(texto(li), 50)}"`);
          continue;
        }
        const t = limpo(texto(b));
        if (!/[.:?!]$/.test(t)) avisos.push(`${onde(li, sec)}: título do passo sem ponto final: "${trecho(t, 60)}"`);
      }
    }
    if (el.tag === 'a' && (el.attrs.href || '').startsWith('#')) {
      const alvo = el.attrs.href.slice(1);
      if (alvo && !ids.has(alvo)) erros.push(`${onde(el, sec)}: link para #${alvo}, que não existe.`);
    }
  }

  // capturas embutidas
  let shots = {};
  try {
    shots = JSON.parse(RE_SHOTS.exec(html)?.[1] || '{}');
  } catch {
    erros.push('A linha "const SHOTS = {...};" está quebrada: rode o montar.mjs de novo.');
  }
  const usadas = todos.filter((e) => e.tag === 'img' && e.attrs['data-shot']).map((e) => [e, e.attrs['data-shot']]);
  for (const [el, key] of usadas) if (!shots[key]) erros.push(`${onde(el, secDe(el))}: a captura "${key}" não foi embutida (rode o montar.mjs com --capturas <pasta> e um arquivo NN-${key}.jpg).`);

  // mínimos dos capítulos fixos
  const conta = (id, pred) => {
    const s = secoes.find((x) => x.attrs.id === id);
    return s ? els(s).filter(pred).length : 0;
  };
  const faq = conta('problemas', (e) => e.tag === 'details');
  const termos = conta('glossario', (e) => e.tag === 'dt');
  const praticas = conta('boas-praticas', (e) => tem(e, 'card') && tem(e.pai, 'praticas'));
  if (secoes.some((s) => s.attrs.id === 'antes') && !conta('antes', (e) => tem(e, 'check'))) avisos.push('[antes] falta o checklist (<ul class="check">).');
  if (faq < 5) avisos.push(`[problemas] só ${faq} perguntas: o ideal é de 5 a 12.`);
  if (termos < 5) avisos.push(`[glossario] só ${termos} termos: o ideal é de 5 a 16.`);
  if (praticas < 3 || praticas > 8) avisos.push(`[boas-praticas] ${praticas} cartões em <div class="cards praticas">: o ideal é de 3 a 8.`);

  // escrita
  const blocos = todos.filter((e) => ['p', 'li', 'dd', 'dt', 'figcaption', 'summary', 'td', 'th', 'h2', 'h3', 'h4'].includes(e.tag) || (e.tag === 'a' && e.pai?.tag === 'div'));
  const ja = new Set();
  const avisar = (el, msg) => {
    const chave = el.linha + msg;
    if (!ja.has(chave)) {
      ja.add(chave);
      avisos.push(`${onde(el, secDe(el))}: ${msg}`);
    }
  };
  const PROIBIDAS = /(?<!\p{L})(simplesmente|basicamente|obviamente|óbvio|facilmente|fácil|basta)(?!\p{L})/iu;
  for (const el of blocos) {
    const t = limpo(textoProprio(el));
    if (!t) continue;
    if (/—/.test(t.replace(/\(—\)/g, '')) && t !== '—') avisar(el, `travessão (—) no texto: troque por dois-pontos, vírgula ou ponto: "${trecho(t, 60)}"`);
    if (/[\u{1F000}-\u{1FAFF}]/u.test(t)) avisar(el, `emoji no texto: "${trecho(t, 50)}"`);
    const p = PROIBIDAS.exec(t);
    if (p) avisar(el, `evite "${p[1]}" (soa como se fosse óbvio para quem está aprendendo): "${trecho(t, 60)}"`);
    if (/clique aqui/i.test(t)) avisar(el, 'evite "clique aqui": o link deve dizer para onde leva.');
    for (const frase of t.split(/(?<=[.!?;:])\s+/)) {
      const w = frase.split(' ').length;
      if (w > 40) avisar(el, `frase com ${w} palavras (máximo 40): "${trecho(frase, 60)}"`);
    }
  }

  const palavras = (limpo(texto(raiz)).match(/\S+/g) || []).length;
  Object.assign(info, {
    nome: dados?.nome,
    capitulos: secoes.length,
    passos: n,
    duvidas: faq,
    termos,
    capturas: Object.keys(shots).length,
    palavras,
    minutos: Math.max(1, Math.round(palavras / 220)),
    kb: Math.round(Buffer.byteLength(html) / 1024),
  });
  return { erros, avisos, info };
}

export function relatorio({ erros, avisos, info }) {
  const l = [];
  if (info.capitulos != null)
    l.push(
      `Playbook ${info.nome || '?'} · ${info.capitulos} capítulos · ${info.passos} passos · ${info.duvidas} dúvidas · ${info.termos} termos · ${info.capturas} capturas · ~${info.palavras} palavras (~${info.minutos} min) · ${info.kb} KB`,
    );
  if (erros.length) l.push(`\nERROS (${erros.length}): corrija todos`, ...erros.map((e) => `  ✗ ${e}`));
  if (avisos.length) l.push(`\nAVISOS (${avisos.length}): corrija o que fizer sentido`, ...avisos.map((a) => `  ! ${a}`));
  l.push(erros.length ? '\nResultado: COM ERROS' : `\nResultado: OK${avisos.length ? ' (com avisos)' : ''}`);
  return l.join('\n');
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  const arquivo = process.argv[2];
  if (!arquivo) {
    console.error('Uso: node verificar.mjs "<Playbook X.html>"');
    process.exit(2);
  }
  const [html, template] = await Promise.all([readFile(arquivo, 'utf8'), readFile(TEMPLATE, 'utf8')]);
  const r = verificar(html, template);
  console.log(relatorio(r));
  process.exit(r.erros.length ? 1 : 0);
}

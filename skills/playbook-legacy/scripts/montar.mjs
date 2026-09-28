// Monta (ou atualiza) um Playbook Legacy: junta o bloco de dados e os capítulos com o template
// travado, embute as capturas de tela e confere o resultado (verificar.mjs).
//
// Criar:     escreva "<pasta>\Playbook X.html" só com o bloco de dados + os capítulos e rode
//              node montar.mjs "<pasta>\Playbook X.html" [--capturas "<pasta com 01-nome.jpg…>"]
//            O mesmo arquivo vira o playbook completo (um arquivo só, que abre sozinho).
// Atualizar: edite o bloco de dados ou os capítulos no próprio arquivo e rode o mesmo comando.
//            As capturas já embutidas são mantidas; --capturas acrescenta ou troca.
// Opcional:  --saida "<outro arquivo.html>" para gravar em outro lugar.
// Antes de sobrescrever, guarda uma cópia em %TEMP%\playbook-legacy-backups.
import { copyFile, mkdir, readdir, readFile, stat, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { MARCA_FIM, MARCA_INICIO, RE_DADOS, RE_SHOTS, TEMPLATE, relatorio, validarDados, verificar } from './verificar.mjs';

const args = process.argv.slice(2);
const opt = (nome) => {
  const i = args.indexOf(nome);
  return i === -1 ? null : args[i + 1];
};
const entrada = args.find((a, i) => !a.startsWith('--') && !['--capturas', '--saida'].includes(args[i - 1]));
if (!entrada) {
  console.error('Uso: node montar.mjs "<Playbook X.html>" [--capturas <pasta>] [--saida <arquivo.html>]');
  process.exit(2);
}
const saida = path.resolve(opt('--saida') || entrada);
const pastaCapturas = opt('--capturas');

const fonte = (await readFile(entrada, 'utf8')).replace(/^﻿/, '');
const template = await readFile(TEMPLATE, 'utf8');

// 1) dados da capa
const md = RE_DADOS.exec(fonte);
if (!md) sair('Não achei o bloco de dados: o arquivo precisa começar com <script type="application/json" id="playbook-dados">{…}</script>.');
let dados;
try {
  dados = JSON.parse(md[1]);
} catch (e) {
  sair(`O bloco de dados não é um JSON válido: ${e.message}`);
}
const errosDados = validarDados(dados);
if (errosDados.length) sair(errosDados.join('\n'));

// 2) capítulos: entre as marcas (arquivo já montado) ou tudo depois do bloco de dados (rascunho)
const i0 = fonte.indexOf(MARCA_INICIO);
const i1 = fonte.indexOf(MARCA_FIM);
const secoes = (i0 !== -1 && i1 > i0 ? fonte.slice(i0 + MARCA_INICIO.length, i1) : fonte.replace(RE_DADOS, '')).trim();
if (!/<section\b/.test(secoes)) sair('Não achei nenhum <section class="chapter"> no arquivo.');

// 3) capturas: as que já estavam no arquivo + as da pasta (a pasta vence)
let shots = {};
const ms = RE_SHOTS.exec(fonte);
if (ms && i0 !== -1) shots = JSON.parse(ms[1]);
if (pastaCapturas) {
  const MIME = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp' };
  for (const f of await readdir(pastaCapturas)) {
    const ext = path.extname(f).toLowerCase();
    if (!MIME[ext]) continue;
    const chave = path.basename(f, path.extname(f)).toLowerCase().replace(/^\d+[\s._-]*/, '');
    const buf = await readFile(path.join(pastaCapturas, f));
    if (buf.length > 450 * 1024) console.log(`! captura grande: ${f} (${Math.round(buf.length / 1024)} KB). Prefira JPEG qualidade ~84 e 1440 px de largura.`);
    shots[chave] = `data:${MIME[ext]};base64,${buf.toString('base64')}`;
  }
}
const usadas = [...new Set([...secoes.matchAll(/data-shot="([^"]+)"/g)].map((m) => m[1]))];
const sobrando = Object.keys(shots).filter((k) => !usadas.includes(k));
shots = Object.fromEntries(usadas.filter((k) => shots[k]).map((k) => [k, shots[k]]));

// 4) preenche o template (uma passada só: o texto dos capítulos nunca é reprocessado)
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const rodape = [];
if (dados.contexto) rodape.push(`<p>Contexto técnico: <b>${esc(dados.contexto)}</b>.</p>`);
if (dados.ajuda) rodape.push(`<p>Dúvida que este guia não resolve: fale com <b>${esc(dados.ajuda)}</b>.</p>`);
const valores = {
  NOME: esc(dados.nome),
  ARTIGO: esc(dados.artigo),
  AREA: esc(dados.area),
  LEAD: esc(dados.lead),
  DESCRICAO: esc(dados.lead),
  FAIXA_1: esc(dados.faixa[0]),
  FAIXA_2: esc(dados.faixa[1]),
  ATUALIZADO: esc(dados.atualizado),
  RODAPE_EXTRA: rodape.join('\n  '),
  DADOS_JSON: JSON.stringify(dados, null, 2).replace(/</g, '\\u003c'),
  SHOTS: JSON.stringify(shots),
  SECOES: secoes,
};
const html = template.replace(/@@([A-Z_0-9]+)@@/g, (m, k) => (k in valores ? valores[k] : m));

// 5) grava (com cópia de segurança do que existia)
try {
  await stat(saida);
  const dir = path.join(os.tmpdir(), 'playbook-legacy-backups');
  await mkdir(dir, { recursive: true });
  const carimbo = new Date().toISOString().replace(/[:T]/g, '-').slice(0, 19);
  await copyFile(saida, path.join(dir, `${path.basename(saida, '.html')} ${carimbo}.html`));
} catch {}
await mkdir(path.dirname(saida), { recursive: true });
await writeFile(saida, html);

// 6) confere
console.log(`Montado: ${saida}`);
if (sobrando.length) console.log(`(capturas não usadas no texto e deixadas de fora: ${sobrando.join(', ')})`);
const r = verificar(html, template);
console.log(relatorio(r));
process.exit(r.erros.length ? 1 : 0);

function sair(msg) {
  console.error(`ERRO: ${msg}`);
  process.exit(1);
}

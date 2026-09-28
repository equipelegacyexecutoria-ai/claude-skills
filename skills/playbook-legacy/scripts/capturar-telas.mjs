// Capturas de tela para um Playbook Legacy (app web que roda em localhost).
// Como usar: copie este arquivo para uma pasta de rascunho do projeto onde o playwright-core esteja
// instalado (ex.: .scratch\), edite SÓ a parte ROTEIRO no fim e rode:
//   node capturar-telas.mjs "<pasta de saída>"
// Saem arquivos 01-chave.jpg, 02-chave.jpg… prontos para: montar.mjs "<playbook>" --capturas "<pasta>".
// Usa o Chrome instalado, sem janela, e bloqueia tudo que não for localhost (nada sai da máquina).
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright-core';

const saida = process.argv[2] || 'capturas';
await mkdir(saida, { recursive: true });

const browser = await chromium.launch({ channel: 'chrome', headless: true });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'pt-BR', timezoneId: 'America/Sao_Paulo' });
const LOCAL = new Set(['localhost', '127.0.0.1']);
await ctx.route('**/*', (route) => {
  const u = new URL(route.request().url());
  return u.protocol === 'data:' || u.protocol === 'blob:' || LOCAL.has(u.hostname) ? route.continue() : route.abort();
});
const page = await ctx.newPage();
const erros = [];
page.on('pageerror', (e) => erros.push(e.message));

let n = 0;
// Salva a tela visível, a página inteira ou um recorte em volta de um ou mais seletores.
async function capturar(chave, seletores = null, { margem = 16, inteira = false } = {}) {
  const arquivo = path.join(saida, `${String(++n).padStart(2, '0')}-${chave}.jpg`);
  const opts = { path: arquivo, type: 'jpeg', quality: 84 };
  if (seletores) {
    const caixas = [];
    for (const s of [].concat(seletores)) {
      const b = await page
        .locator(s)
        .first()
        .evaluate((el) => {
          const r = el.getBoundingClientRect();
          return { x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height };
        })
        .catch(() => null);
      if (b) caixas.push(b);
    }
    if (!caixas.length) throw new Error(`nada encontrado para: ${[].concat(seletores).join(', ')}`);
    const x = Math.max(0, Math.min(...caixas.map((b) => b.x)) - margem);
    const y = Math.max(0, Math.min(...caixas.map((b) => b.y)) - margem);
    const dir = Math.min(1440, Math.max(...caixas.map((b) => b.x + b.w)) + margem);
    const baixo = Math.max(...caixas.map((b) => b.y + b.h)) + margem;
    Object.assign(opts, { fullPage: true, clip: { x, y, width: dir - x, height: baixo - y } });
  } else if (inteira) opts.fullPage = true;
  await page.screenshot(opts);
  console.log('ok', arquivo);
}

// ===================== ROTEIRO (edite daqui para baixo) =====================
// Exemplo de resposta simulada, para não gastar créditos nem mexer em contas reais:
// await ctx.route('**/api/status', (route) => route.fulfill({ json: { conectado: true } }));

await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
await page.waitForTimeout(800);
await capturar('inicio');

// await page.fill('#senha', process.env.SENHA_TESTE ?? '');   // senha de TESTE, nunca a real
// await page.click('text=Entrar');
// await page.waitForTimeout(1000);
// await capturar('formulario', ['#form', '#resumo']);        // recorte em volta dos dois
// ============================================================================

await browser.close();
console.log(erros.length ? `erros na página: ${erros.join(' | ')}` : 'sem erros na página');

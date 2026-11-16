(function () {
  const tlr = gsap.timeline({ paused: true });
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tlr;
  // voz antiga (v4) -> voz F; cada bloco antigo ainda leva o tempo da voz F para a voz G (mapaG)
  const ANC = __ANC__;
  const TTF = __TTF__;
  function interp(A, x) {
    if (x <= A[0][0]) return x + A[0][1] - A[0][0];
    const u = A[A.length - 1];
    if (x >= u[0]) return x + u[1] - u[0];
    for (let i = 1; i < A.length; i++) {
      const a = A[i - 1], b = A[i];
      if (x <= b[0]) return b[0] > a[0] ? a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]) : a[1];
    }
    return x;
  }
  let mapaF = false, mapaG = null;
  function bloco(f, g) { mapaF = f; mapaG = g; }
  function M(x) {
    if (typeof x !== "number") return x;
    if (x <= 0) return 0;
    let y = mapaF ? interp(ANC, x) : x;
    if (mapaG) y = interp(mapaG, y);
    return y;
  }
  const tl = { to: (a, b, q) => tlr.to(a, b, M(q)), fromTo: (a, b, c, q) => tlr.fromTo(a, b, c, M(q)), set: (a, b, q) => tlr.set(a, b, M(q)) };
  const DUR = __DUR__;
  const VAR = "__VAR__";
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));

  // tempos de cada palavra da voz nova (já com a voz começando em 0,25 s)
  const TX = __TX__;
  const TT = __TT__;
  // pares de âncoras: palavra i da voz F -> palavra j da voz G (mesmo texto)
  const par = (a0, a1, b0) => { const r = []; for (let i = a0; i <= a1; i++) r.push([TTF[i], TT[b0 + i - a0]]); return r; };

  // gerador fixo (mesmo resultado em todo render)
  let semente = 7;
  const rnd = () => { semente = (semente * 16807) % 2147483647; return (semente - 1) / 2147483646; };
  const br = (n) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  function contar(el, de, ate, t, dur, fmt, ease) {
    const o = { v: de };
    el.textContent = fmt(de);
    tl.fromTo(o, { v: de }, { v: ate, duration: dur, ease: ease || "power2.out", onUpdate: () => { el.textContent = fmt(o.v); } }, t);
  }
  function mostra(el, t, de, dur) {
    tl.fromTo(el, Object.assign({ autoAlpha: 0 }, de || {}), { autoAlpha: 1, x: 0, y: 0, z: 0, scale: 1, rotationX: 0, rotationY: 0, rotation: 0, filter: "blur(0px)", duration: dur || 0.6, ease: "expo.out" }, t);
  }
  function some(el, t, para, dur) {
    tl.to(el, Object.assign({ autoAlpha: 0, filter: "blur(16px)", duration: dur || 0.3, ease: "power2.in" }, para || {}), t);
  }

  // ---------- letreiro (palavra a palavra, no tempo da voz) ----------
  // saida/fim/risco já no tempo da voz nova (sem mapa)
  const letras = $("#letras");
  let nG = 0;
  function grupo(top, linhas, saida, opt) {
    opt = opt || {};
    const g = document.createElement("div");
    g.className = "grp";
    g.style.top = top + "px";
    letras.appendChild(g);
    let ini = 99, k = 0;
    linhas.forEach((ln) => {
      const L = document.createElement("span");
      L.className = "ln";
      g.appendChild(L);
      ln.forEach((p) => {
        const i = p[0], cls = p[1] || "";
        const w = document.createElement("span");
        w.className = "w " + cls;
        const tx = document.createElement("span");
        tx.className = "tx";
        tx.textContent = p[2] || TX[i];
        let marca = null, risco = null;
        if (cls.indexOf("hl") >= 0) { marca = document.createElement("span"); marca.className = "marca" + (cls.indexOf("cz") >= 0 ? " cz" : "") + (cls.indexOf("fg") >= 0 ? " fg" : ""); w.appendChild(marca); }
        w.appendChild(tx);
        if (cls.indexOf("rs") >= 0) { risco = document.createElement("span"); risco.className = "risco"; w.appendChild(risco); }
        L.appendChild(w);
        const t = TT[i];
        ini = Math.min(ini, t);
        const grande = cls.indexOf("big") >= 0 || cls.indexOf("xl") >= 0;
        tlr.fromTo(w, { opacity: 0, filter: "blur(18px)", y: grande ? 50 : 34, x: (k % 2 ? 1 : -1) * (grande ? 30 : 16), scale: grande ? 1.6 : 1.35 },
          { opacity: 1, filter: "blur(0px)", y: 0, x: 0, scale: 1, duration: 0.5, ease: "expo.out" }, t - 0.06);
        if (marca) {
          tlr.fromTo(marca, { scaleX: 0 }, { scaleX: 1, duration: 0.32, ease: "power3.out" }, t + 0.06);
          tlr.fromTo(tx, { color: "#0a1a33" }, { color: "#ffffff", duration: 0.2 }, t + 0.12);
        }
        if (risco) tlr.fromTo(risco, { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power3.inOut" }, opt.risco || t + 0.4);
        k++;
      });
    });
    const fim = opt.fim || saida;
    nG++;
    const lado = nG % 2 ? 1 : -1;
    // câmera orbita a frase na chegada e vai chegando perto enquanto ela fica na tela
    tlr.fromTo(g, { rotationY: lado * 22, rotationX: 8, z: -260 }, { rotationY: 0, rotationX: 0, z: 0, duration: 0.7, ease: "expo.out" }, ini - 0.06);
    tlr.fromTo(g, { scale: 1 }, { scale: 1.08, duration: Math.max(0.3, fim - ini), ease: "none" }, ini);
    tlr.to(g, { rotationY: -lado * 5, duration: Math.max(0.3, fim - ini - 0.7), ease: "sine.inOut" }, ini + 0.64);
    // palavra de destaque gigante e borrada lá atrás (profundidade)
    const hl = linhas.flat().find((p) => (p[1] || "").indexOf("hl") >= 0 && (p[1] || "").indexOf("cz") < 0);
    if (hl && !opt.semFantasma) {
      const f = document.createElement("div");
      f.className = "fant";
      f.textContent = (hl[2] || TX[hl[0]]).replace(/[.,?!]/g, "");
      f.style.top = (top - 40) + "px";
      letras.insertBefore(f, letras.firstChild);
      const t0 = TT[hl[0]];
      tlr.fromTo(f, { x: lado * 160, z: -300, scale: 0.9 }, { x: -lado * 120, z: -300, scale: 1.05, duration: Math.max(0.5, fim - t0), ease: "none" }, t0);
      tlr.fromTo(f, { opacity: 0 }, { opacity: 1, duration: 0.35 }, t0);
      tlr.to(f, { opacity: 0, duration: 0.25 }, Math.max(t0 + 0.4, fim - 0.14));
    }
    // saída: a câmera atravessa a frase
    if (saida < DUR) tlr.to(g, { opacity: 0, filter: "blur(16px)", scale: 1.7, z: 240, duration: 0.22, ease: "power2.in" }, saida - 0.14);
    return g;
  }
  // letreiro com a saída escrita no tempo da voz F (blocos do fim)
  const gF = (top, linhas, saida, opt) => grupo(top, linhas, M(saida), opt);

  // ======== S1 (0 a 4,45): gancho ========
  bloco(true, par(0, 11, 0).concat([[4.12, 4.45], [5.0, 4.9]]));
  grupo(560, [[[0, "sm dim"], [1, "sm dim"]], [[2, "xl"]]], 1.4);
  mostra("#c-receita", 0.68, { y: 260, z: -500, rotationX: 48, scale: 0.8, filter: "blur(20px)" }, 0.8);
  contar($("#rec-v"), 0, 82150, 0.8, 0.75, (v) => "R$ " + br(v));
  tl.fromTo("#rec-linha", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.8, ease: "power2.out" }, 0.85);
  tl.fromTo("#rec-area", { opacity: 0 }, { opacity: 1, duration: 0.6 }, 1.0);
  tl.to("#c-receita", { rotationY: -8, rotationX: 6, duration: 0.8, ease: "sine.inOut" }, 0.9);
  some("#c-receita", 1.48, { y: -420, z: -300, rotationX: -40, scale: 0.7 }, 0.32);
  grupo(600, [[[3, "sm"], [4, "sm"], [5, "sm"]], [[6, "big hl"], [7, "big hl"]], [[8], [9], [10], [11]]], 4.5);
  tl.set("#c-sobra", { autoAlpha: 0 }, 0);
  mostra("#c-sobra", 2.95, { y: 200, z: -400, rotationX: 40, filter: "blur(18px)" }, 0.6);
  (function () { const o = { v: 0 }; const el = $("#sobra-v"); const D = "0123456789?";
    tl.fromTo(o, { v: 0 }, { v: 30, duration: 1.2, ease: "none", onUpdate: () => {
      const f = Math.floor(o.v); let s = "R$ ";
      for (let j = 0; j < 4; j++) { s += D[(f * 7 + j * 3 + f * j) % D.length]; if (j === 0) s += "."; }
      el.textContent = f >= 29 ? "R$ ?.???" : s; } }, 3.0); })();
  tl.to("#c-sobra", { rotationY: 10, rotationX: -6, y: -20, duration: 1.2, ease: "sine.inOut" }, 3.0);
  some("#c-sobra", 5.0, {}, 0.2);

  // ======== N1 (4,45 a 10,3): três planilhas, sem controle ========
  bloco(false, null);
  const XLS = [
    ["Data", "Entrada", "Saída", "Saldo", "01/10", "12.400", "9.870", "#REF!", "08/10", "8.150", "???", "#N/D", "15/10", "=SOMA(", "11.230", "conferir"],
    ["Vendedor", "Out", "Meta", "%", "Ana", "32.100", "?", "#DIV/0!", "Bruno", "—", "40.000", "#REF!", "Carla", "18.900", "??", "rever"],
    ["Meta", "Dono", "Prazo", "Status", "Receita", "?", "?", "—", "Margem", "—", "dez?", "#N/D", "Clientes", "?", "—", "???"]];
  ["#xl1", "#xl2", "#xl3"].forEach((s, k) => {
    const g = $(s).querySelector(".xg");
    XLS[k].forEach((tx, j) => {
      const c = document.createElement("div");
      c.className = "xc" + (j < 4 ? " h" : "");
      c.style.left = (j % 4) * 170 + "px";
      c.style.top = Math.floor(j / 4) * 84 + "px";
      c.textContent = tx;
      if (j >= 4 && /^#|\?/.test(tx)) c.style.color = "#e11d48";
      g.appendChild(c);
    });
  });
  tl.set(["#xl1", "#xl2", "#xl3"], { autoAlpha: 0 }, 0);
  grupo(300, [[[12, "sm", "Se"], [13, "sm", "pra"], [14, "sm"]], [[15], [16], [17]]], 6.45);
  [["#xl1", 6.22, -1], ["#xl2", 6.5, 1], ["#xl3", 6.86, -1]].forEach((a) => {
    tlr.fromTo(a[0], { autoAlpha: 0, z: -900, y: 300, rotationX: 50, rotationY: a[2] * 25, rotation: 0, filter: "blur(18px)" },
      { autoAlpha: 1, z: 0, y: 0, rotationX: 8, rotationY: a[2] * -8, rotation: a[2] * -3, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, a[1]);
  });
  grupo(300, [[[18, "big hl"], [19, "big"]]], 7.72);
  tlr.to(["#xl1", "#xl2", "#xl3"], { z: -450, opacity: 0.3, filter: "blur(7px)", duration: 0.6, ease: "power3.out" }, 7.62);
  grupo(700, [[[20, "sm"], [21, "sm"], [22, "sm"], [23, "sm"]], [[24, "xl hl"]], [[25, "sm"], [26, "sm"], [27, "sm"]]], 10.3);

  // ======== N2 (10,3 a 15,4): caixa, vendas, metas na cabeça ========
  tl.set(["#k-caixa", "#k-vendas", "#k-metas"], { autoAlpha: 0 }, 0);
  [["#k-caixa", 10.58], ["#k-vendas", 12.34], ["#k-metas", 13.8]].forEach((a, i) => {
    const l = i % 2 ? 1 : -1;
    tlr.fromTo(a[0], { autoAlpha: 0, z: -700, x: l * 300, rotationY: -l * 40, filter: "blur(16px)" },
      { autoAlpha: 1, z: 0, x: 0, rotationY: l * 6, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }, a[1]);
  });
  tlr.to("#k-caixa", { opacity: 0.5, duration: 0.3 }, 12.34);
  tlr.to("#k-vendas", { opacity: 0.5, duration: 0.3 }, 13.8);
  tlr.fromTo("#k-q", { scale: 0, rotation: -30 }, { scale: 1, rotation: 0, duration: 0.5, ease: "back.out(2.4)" }, 14.5);
  tlr.fromTo("#k-metas", { x: 0 }, { x: 10, duration: 0.05, repeat: 3, yoyo: true, ease: "none", immediateRender: false }, 15.05);
  grupo(300, [[[28, "sm"], [29, "big hl"]], [[30, "sm"], [31, "sm"], [32, "sm"]]], 12.15);
  grupo(300, [[[33, "sm"], [34, "big hl"]], [[35, "sm"], [36, "big"]]], 13.65);
  grupo(1290, [[[37, "sm"], [38, "sm"], [39, "big hl"]], [[40, "sm"], [41], [42, "sm"], [43]]], 15.42);

  // ======== N3 (15,4 a 21,1): ninguém sabe quem faz, vira incêndio ========
  tl.set(["#tarefa", "#fogo"], { autoAlpha: 0 }, 0);
  mostra("#tarefa", 15.55, { z: -600, y: 200, rotationX: 40, filter: "blur(16px)" }, 0.7);
  $$("#tarefa .qav").forEach((q, i) => tlr.fromTo(q, { scale: 0 }, { scale: 1, duration: 0.4, ease: "back.out(2.4)" }, 16.5 + i * 0.12));
  tlr.fromTo("#tarefa .qav", { y: 0 }, { y: -14, duration: 0.16, yoyo: true, repeat: 3, ease: "power1.inOut", immediateRender: false }, 17.8);
  grupo(300, [[[44, "big"]], [[45, "sm"], [46, "sm"], [47, "sm"]], [[48, "sm"], [49, "sm"], [50, "sm"], [51, "hl"]]], 18.3);
  tlr.to("#tarefa", { z: -500, y: -120, opacity: 0.25, filter: "blur(8px)", duration: 0.6, ease: "power3.out" }, 18.2);
  [["🔔", "Boleto vencido hoje", "Fornecedor ligando de novo"], ["🔔", "Cliente cobrando entrega", "Pedido parado desde segunda"], ["🔔", "Vendedor sem meta", "Ninguém sabe quanto vendeu"]].forEach((a, i) => {
    const e = document.createElement("div");
    e.className = "alerta vidro p3";
    e.style.top = (700 + i * 160) + "px";
    e.innerHTML = '<div class="ic">' + a[0] + '</div><div class="tx1">' + a[1] + '</div><div class="tx2">' + a[2] + '</div>';
    $("#alertas0").appendChild(e);
    tlr.fromTo(e, { autoAlpha: 0, y: 80, scale: 0.85, filter: "blur(10px)" }, { autoAlpha: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "back.out(1.6)" }, [18.5, 19.18, 19.62][i]);
    tlr.fromTo(e, { x: 0 }, { x: 10, duration: 0.05, repeat: 5, yoyo: true, ease: "none", immediateRender: false }, 20.62 + i * 0.04);
  });
  tlr.fromTo("#fogo", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, immediateRender: false }, 20.55);
  grupo(1290, [[[52, "sm"], [53, "sm"], [54, "sm"], [55, "sm"], [56, "sm"]]], 19.62);
  grupo(1290, [[[57, "sm"], [58, "sm"], [59, "sm"]], [[60, "big hl fg"]]], 21.15);

  // ======== S2 (21,1 a 29,8): consultoria, 80 páginas, gaveta, problema sem solução ========
  bloco(true, [[4.0, 21.15]].concat(par(12, 27, 61), [[9.80, 27.28], [9.82, 29.62], [9.99, 29.95]]));
  const pilha = $("#pilha");
  const docs = [];
  for (let i = 0; i < 7; i++) {
    const d = document.createElement("div");
    d.className = "doc";
    d.innerHTML = '<div class="faixa"></div><div class="t1">PLANO ESTRATÉGICO</div><div class="t2">Consultoria · 2026</div>' +
      [170, 210, 250, 290, 350, 390, 430, 470].map((y, j) => '<div class="l" style="top:' + y + 'px; width:' + (j % 3 === 2 ? 240 : 380 - j * 8) + 'px;"></div>').join("") +
      '<div class="pg">PÁG. ' + (80 - (6 - i) * 13 > 0 ? String(Math.max(1, 80 - (6 - i) * 13)).padStart(2, "0") : "01") + ' / 80</div>';
    pilha.appendChild(d);
    docs.push(d);
  }
  grupo(300, [[[61, "sm dim"], [62, "sm dim"]], [[63], [64], [65]]], 23.45);
  tl.set(docs, { autoAlpha: 0 }, 0);
  docs.forEach((d, i) => {
    tl.fromTo(d, { autoAlpha: 0, y: 700, z: -200, rotationX: 60, rotation: -6 },
      { autoAlpha: 1, y: -i * 4, z: i * 6, rotationX: 0, rotation: (i - 3) * 0.6, duration: 0.8, ease: "expo.out" }, 4.55 + i * 0.03);
  });
  // abre em leque nas 80 páginas
  grupo(300, [[[66, "sm"], [67, "big hl"], [68, "big"]]], 24.62);
  docs.forEach((d, i) => {
    tl.to(d, { x: (i - 3) * 62, y: Math.abs(i - 3) * 22, rotation: (i - 3) * 7, rotationY: (i - 3) * -6, z: -Math.abs(i - 3) * 40, duration: 0.6, ease: "expo.out" }, 6.3 + i * 0.02);
  });
  tl.to(pilha, { rotationX: 14, rotationY: -12, duration: 1.4, ease: "sine.inOut" }, 6.3);
  // e vai embora
  grupo(1290, [[[69, "sm dim"], [70], [71, "big"]]], 25.45);
  tl.fromTo("#seta-sai", { autoAlpha: 0, x: -200 }, { autoAlpha: 1, x: 0, duration: 0.3, ease: "power2.out" }, 8.0);
  tl.fromTo("#seta-l", { strokeDashoffset: 0 }, { strokeDashoffset: -0.35, duration: 0.6, ease: "none" }, 8.0);
  tl.to("#seta-sai", { x: 700, autoAlpha: 0, filter: "blur(8px)", duration: 0.35, ease: "power3.in" }, 8.3);
  // fecha o leque e vai pra gaveta
  docs.forEach((d, i) => {
    tl.to(d, { x: 0, y: -i * 3, rotation: 0, rotationY: 0, z: i * 4, duration: 0.45, ease: "power3.inOut" }, 8.55);
  });
  tl.to(pilha, { rotationX: 0, rotationY: 0, scale: 0.86, duration: 0.45, ease: "power3.inOut" }, 8.55);
  grupo(300, [[[72, "sm"], [73, "sm"], [74, "sm"]], [[75, "big"], [76, "big hl cz"]]], 27.15);
  tl.set(["#gav-fundo", "#gav-frente"], { autoAlpha: 0 }, 0);
  mostra("#gav-fundo", 9.0, { y: 160 }, 0.5);
  mostra("#gav-frente", 9.0, { y: 200, rotationX: 30 }, 0.5);
  tl.to(pilha, { y: 640, scale: 0.8, duration: 0.5, ease: "power3.in" }, 9.42);
  tl.to(["#gav-frente", "#gav-fundo"], { y: -40, duration: 0.18, ease: "power2.out" }, 9.9);
  tl.to(["#gav-frente", "#gav-fundo"], { y: 0, duration: 0.25, ease: "power2.in" }, 10.08);
  tl.fromTo(["#gav-fundo", "#gav-frente", "#pilha"], { x: 0 }, { x: 8, duration: 0.05, repeat: 3, yoyo: true, ease: "none", immediateRender: false }, 9.9);
  some(["#pilha", "#gav-fundo", "#gav-frente"], 10.12, { scale: 0.9, y: 80 }, 0.25);
  tl.set(pilha, { autoAlpha: 0 }, 10.4);
  // e o seu problema continua sem solução (gaveta fechada, frase sobre ela)
  tlr.to(pilha, { autoAlpha: 0, duration: 0.1 }, 27.12);
  grupo(300, [[[77, "sm"], [78, "sm"], [79, "sm"], [80, "sm"]], [[81, "big"]], [[82, "big"], [83, "big hl"]]], 29.72);

  // ======== S3 (29,6 a 34,2): Na Legacy é diferente + executor entra ========
  bloco(true, [[9.77, 29.62], [9.95, 29.84], [10.74, 31.95], [11.38, 32.45], [11.80, 32.95], [12.37, 33.45], [13.15, 33.85], [13.9, 34.2]]);
  tl.fromTo("#azul", { opacity: 0, scaleY: 0, transformOrigin: "50% 100%" }, { opacity: 1, scaleY: 1, duration: 0.18, ease: "power3.in" }, 10.05);
  tl.to("#azul", { scaleY: 0, transformOrigin: "50% 0%", duration: 0.28, ease: "power3.out" }, 10.25);
  grupo(760, [[[84, "big"], [85, "big hl"]], [[86, "sm"], [87, "big"]]], 31.98);
  tl.set("#vcard", { autoAlpha: 0 }, 0);
  mostra("#vcard", 10.9, { scale: 0.55, y: 300, rotationX: 24, filter: "blur(20px)" }, 0.7);
  tl.to("#vcard", { rotationY: -6, rotationX: 4, duration: 2.4, ease: "sine.inOut" }, 11.0);
  const cortes = [["#vwA", 10.9], ["#vwC", 11.6], ["#vwB", 12.0], ["#vwG", 12.55], ["#vwE", 13.35]];
  $$("#vcard .vw").forEach((v) => tl.set(v, { autoAlpha: 0 }, 0));
  cortes.forEach((c, i) => {
    tl.set(c[0], { autoAlpha: 1 }, c[1]);
    if (i) { tl.set(cortes[i - 1][0], { autoAlpha: 0 }, c[1] + 0.02); tl.fromTo("#vflash", { opacity: 0.35 }, { opacity: 0, duration: 0.2, immediateRender: false }, c[1]); }
    tl.fromTo(c[0], { scale: 1.14 }, { scale: 1.02, duration: 0.9, ease: "expo.out" }, c[1]);
  });
  tl.fromTo("#vselo", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "expo.out" }, 11.3);
  grupo(280, [[[88, "sm"], [89, "hl"]], [[90, "sm"], [91, "sm"], [92, "sm"], [93, "sm"]]], 34.22);
  some("#vcard", 14.05, { scale: 0.85, rotationX: -20, y: 120 }, 0.3);
  tl.set("#vwE", { autoAlpha: 0 }, 14.4);

  // ======== C2 (34,2 a 39,3): assume o financeiro e o comercial, arruma a casa, toca a gestão ========
  bloco(false, null);
  grupo(290, [[[94, "big hl"]], [[95, "sm"], [96, "big"]]], 35.47);
  grupo(290, [[[97, "sm"], [98, "sm"], [99, "big"]]], 36.32);
  grupo(290, [[[100, "big"], [101, "sm"], [102, "big hl"]]], 37.62);
  grupo(290, [[[103, "sm"], [104, "sm"], [105, "sm"], [106, "hl"]], [[107, "sm"], [108, "big"]]], 39.27);
  tl.set(["#cardF", "#cardC", "#cardG"], { autoAlpha: 0 }, 0);
  mostra("#cardF", 34.5, { z: -500, x: -200, rotationY: 40, filter: "blur(16px)" }, 0.7);
  mostra("#cardC", 35.4, { z: -500, x: 200, rotationY: -40, filter: "blur(16px)" }, 0.7);
  [["#cardF", [34.5, 36.3, 38.45]], ["#cardC", [35.4, 37.3]]].forEach((c) => {
    const vs = $(c[0]).querySelectorAll(".vw");
    vs.forEach((v, j) => {
      tl.set(v, { autoAlpha: j ? 0 : 1 }, 0);
      if (j) {
        tl.set(v, { autoAlpha: 1 }, c[1][j]);
        tl.fromTo(v, { scale: 1.12 }, { scale: 1.02, duration: 0.8, ease: "expo.out", immediateRender: false }, c[1][j]);
      }
    });
    tl.fromTo($(c[0]).querySelector(".ok"), { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: "back.out(2)" }, c[1][0] + 0.6);
  });
  tl.to("#cardF", { scale: 0.8, y: -60, x: 20, rotationY: 8, duration: 0.6, ease: "power3.inOut" }, 36.32);
  tl.to("#cardC", { scale: 0.8, y: -60, x: -20, rotationY: -8, duration: 0.6, ease: "power3.inOut" }, 36.32);
  tl.set("#c2lig", { autoAlpha: 0 }, 0);
  tl.to("#c2lig", { autoAlpha: 1, duration: 0.3 }, 36.55);
  tl.fromTo(["#c2l1", "#c2l2"], { strokeDashoffset: 0 }, { strokeDashoffset: -84, duration: 1.6, ease: "none" }, 36.55);
  mostra("#cardG", 36.55, { z: -500, y: 200, rotationX: 40, filter: "blur(16px)" }, 0.7);
  $$("#cardG .mods div").forEach((m, i) => tl.fromTo(m, { autoAlpha: 0, y: 40, scale: 0.8 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2)" }, 36.98 + i * 0.12));

  // ======== S5 (39,2 a 45,7): metas com responsável + plano de ação ========
  bloco(true, par(58, 73, 109).concat([[26.23, 45.73]]));
  tl.set("#win-metas", { autoAlpha: 0 }, 0);
  tl.fromTo("#win-metas", { autoAlpha: 0, rotationY: -30, z: -300, filter: "blur(10px)" },
    { autoAlpha: 1, rotationY: 12, rotationX: 10, z: 0, filter: "blur(0px)", duration: 0.9, ease: "expo.out" }, 20.3);
  tl.to("#win-metas", { rotationY: 4, rotationX: 4, duration: 1.4, ease: "sine.inOut" }, 21.18);
  $$("#win-metas .meta").forEach((m, i) => {
    tl.fromTo(m, { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }, 20.75 + i * 0.12);
    tl.fromTo(m.querySelector(".ench"), { scaleX: 0 }, { scaleX: [1, 0.95, 1][i], duration: 0.8, ease: "power2.out" }, 20.95 + i * 0.12);
    const pc = m.querySelector(".pct");
    contar(pc, 0, +pc.dataset.v, 20.95 + i * 0.12, 0.8, (v) => Math.round(v) + "%");
    const rs = m.querySelector(".resp");
    tl.fromTo(rs, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: "back.out(2)" }, 21.68 + i * 0.1);
  });
  grupo(300, [[[109, "sm"], [110, "sm"]], [[111], [112], [113, "hl"]]], 41.65);
  some("#win-metas", 23.4, {}, 0.2);
  // plano de ação
  tl.set(["#acao", "#toast"], { autoAlpha: 0 }, 0);
  tl.fromTo("#acao", { autoAlpha: 0, rotationX: 30, z: -300, filter: "blur(10px)" },
    { autoAlpha: 1, rotationY: -10, rotationX: 8, z: 0, filter: "blur(0px)", duration: 0.9, ease: "expo.out" }, 22.45);
  tl.to("#acao", { rotationY: 6, rotationX: 4, duration: 2.4, ease: "sine.inOut" }, 23.37);
  grupo(300, [[[114, "sm"], [115, "sm"]], [[116, "big"], [117, "big hl"]]], 43.22);
  tl.fromTo("#prazo", { scale: 1 }, { scale: 1.18, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, 23.5);
  tl.to("#prazo", { backgroundColor: "#2f7bff", color: "#ffffff", borderColor: "#2f7bff", duration: 0.2 }, 23.55);
  grupo(300, [[[118, "sm"], [119, "sm"], [120, "sm"], [121, "sm"]], [[122], [123], [124, "hl"]]], 45.72);
  tl.to("#st-pill", { backgroundColor: "#fff4e5", color: "#b45309", duration: 0.15 }, 24.5);
  tl.fromTo("#st-pill", { x: 0 }, { x: 10, duration: 0.05, repeat: 5, yoyo: true, ease: "none", immediateRender: false }, 24.5);
  (function () { const p = $("#st-pill"); const o = { v: 0 };
    tl.fromTo(o, { v: 0 }, { v: 1, duration: 0.01, onUpdate: () => { p.textContent = o.v >= 1 ? "● Travado" : "● Em andamento"; } }, 24.52); })();
  tl.to("#acao", { boxShadow: "0 46px 100px rgba(245,158,11,.25), 0 0 0 3px rgba(245,158,11,.7)", duration: 0.2 }, 24.52);
  mostra("#toast", 24.9, { y: 160, scale: 0.85, filter: "blur(12px)" }, 0.55);
  some("#acao", 26.3, {}, 0.2);
  some("#toast", 26.3, {}, 0.2);

  // ======== S7 (45,7 a 50,1): no Legacy Plan, todos os números num lugar só ========
  bloco(false, null);
  tl.set(["#m1", "#m2", "#m3", "#m4", "#m5", "#lockup"], { autoAlpha: 0 }, 0);
  grupo(600, [[[125, "sm dim"], [126, "sm dim"]]], 47.1);
  mostra("#lockup", 46.12, { scale: 1.6, filter: "blur(20px)" }, 0.6);
  tl.to("#lockup", { scale: 1.05, duration: 0.8, ease: "none" }, 46.5);
  some("#lockup", 47.3, { scale: 0.6, y: -200 }, 0.25);
  const minis = ["#m1", "#m2", "#m3", "#m4", "#m5"];
  const zs = [-200, 150, 120, -180, -350];
  minis.forEach((m, i) => {
    tl.fromTo(m, { autoAlpha: 0, z: -1200, scale: 0.5, filter: "blur(18px)" }, { autoAlpha: 1, z: zs[i], scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 47.55 + i * 0.13);
  });
  tl.fromTo("#orbita", { rotationY: -18, rotationX: 10 }, { rotationY: 14, rotationX: 4, duration: 2.0, ease: "sine.inOut" }, 47.55);
  grupo(290, [[[129, "sm"], [130, "sm"], [131, "sm"], [132, "sm"]]], 48.18);
  grupo(290, [[[133, "big"], [134, "sm"], [135, "big hl"]]], 49.2);
  minis.forEach((m, i) => {
    tl.to(m, { x: 540 - (parseFloat($(m).style.left) + parseFloat($(m).style.width) / 2), y: 870 - (parseFloat($(m).style.top) + parseFloat($(m).style.height) / 2),
      z: -200, scale: 0.15, autoAlpha: 0, filter: "blur(8px)", duration: 0.45, ease: "power3.in" }, 49.3 + i * 0.03);
  });
  tl.fromTo("#lockup", { autoAlpha: 0, scale: 0.4, y: 0, filter: "blur(12px)" }, { autoAlpha: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "back.out(1.6)", immediateRender: false }, 49.72);
  grupo(290, [[[136, "sm"], [137, "sm"], [138, "sm"]], [[139, "big hl"]]], 50.22);

  // ======== S4 (50,1 a 55,1): DRE: o que planejou, o que faturou, quanto sobrou ========
  bloco(true, [[15.0, 50.15], [15.12, 50.3], [16.29, 50.6], [16.56, 50.85], [17.31, 51.55], [17.81, 51.87], [18.47, 52.55], [18.93, 53.15], [19.0, 53.3], [19.24, 53.75], [21.17, 55.1]]);
  tl.set("#planilha", { autoAlpha: 0 }, 0);
  const graf = $("#graf");
  const meses = [["JUL", 110, 122], ["AGO", 132, 140], ["SET", 150, 146], ["OUT", 165, 182]];
  const barras = [];
  meses.forEach((m, i) => {
    const x = 70 + i * 185;
    const p = document.createElement("div"); p.className = "barra p"; p.style.left = x + "px"; p.style.height = m[1] + "px";
    const r = document.createElement("div"); r.className = "barra r"; r.style.left = (x + 52) + "px"; r.style.height = m[2] + "px";
    const l = document.createElement("div"); l.className = "mes"; l.style.left = (x - 22) + "px"; l.textContent = m[0];
    graf.appendChild(p); graf.appendChild(r); graf.appendChild(l);
    barras.push([p, r]);
  });
  tl.set("#win-dre", { autoAlpha: 0 }, 0);
  tl.fromTo("#win-dre", { autoAlpha: 0, z: -1400, y: 500, rotationX: 55, rotationY: -35, rotation: 8, filter: "blur(24px)" },
    { autoAlpha: 1, z: 0, y: 0, rotationX: 16, rotationY: -14, rotation: 2, filter: "blur(0px)", duration: 1.0, ease: "expo.out" }, 15.2);
  tl.to("#win-dre", { rotationX: 6, rotationY: -4, rotation: 0, duration: 2.6, ease: "sine.inOut" }, 16.2);
  contar($("#k1"), 0, 82150, 15.55, 0.9, (v) => "R$ " + br(v));
  contar($("#k2"), 0, 63256, 15.65, 0.9, (v) => "R$ " + br(v));
  contar($("#k3"), 0, 18894, 15.75, 0.9, (v) => "R$ " + br(v));
  barras.forEach((b, i) => {
    tl.fromTo(b[0], { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: "back.out(1.6)" }, 16.33 + i * 0.09);
    tl.fromTo(b[1], { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: "back.out(1.6)" }, 17.85 + i * 0.09);
  });
  grupo(300, [[[140, "sm"], [141, "sm"], [142, "big hl"]]], 51.5);
  grupo(300, [[[143, "sm"], [144, "sm"], [145, "big hl"]], [[146, "sm"], [147, "big"]]], 52.78);
  // cursor
  tl.set("#cur1", { autoAlpha: 0, x: 900, y: 700 }, 0);
  tl.to("#cur1", { autoAlpha: 1, duration: 0.2 }, 16.5);
  tl.to("#cur1", { x: 800, y: 70, duration: 0.7, ease: "power3.inOut" }, 16.6);
  tl.to("#chip-comp", { backgroundColor: "#195576", color: "#ffffff", duration: 0.15 }, 17.35);
  tl.to("#cur1", { scale: 0.85, duration: 0.08, yoyo: true, repeat: 1 }, 17.3);
  tl.to("#cur1", { x: 720, y: 520, duration: 0.8, ease: "power3.inOut" }, 17.6);
  tl.set("#tip", { autoAlpha: 0 }, 0);
  mostra("#tip", 18.45, { y: 20, scale: 0.9 }, 0.35);
  // sobrou: o lucro salta para fora da tela
  grupo(300, [[[148, "sm"], [149, "sm"]], [[150, "big hl"]], [[151, "sm"], [152, "sm"], [153, "sm"], [154, "sm"]]], 55.1);
  tl.to("#win-dre", { z: -320, y: -60, rotationX: 10, filter: "blur(3px)", duration: 0.8, ease: "power3.out" }, 18.85);
  tl.set("#lucro-pop", { autoAlpha: 0 }, 0);
  mostra("#lucro-pop", 19.05, { z: -600, y: -260, scale: 0.6, rotationX: 30, filter: "blur(14px)" }, 0.7);
  contar($("#luc-v"), 0, 18894, 19.3, 0.75, (v) => "R$ " + br(v));
  tl.to("#lucro-pop", { rotationY: 8, rotationX: -5, duration: 1.0, ease: "sine.inOut" }, 19.6);
  some("#win-dre", 21.2, {}, 0.2);
  some("#lucro-pop", 21.2, {}, 0.2);
  tl.to("#cur1", { autoAlpha: 0, duration: 0.15 }, 18.6);

  // ======== câmera: parada, só anda com intenção (como no reel de referência) ========
  bloco(false, null);
  let CAM = null;
  (function () {
    const P = { s1: [0, 0], n1: [0, 2300], n2: [1700, 2300], n3: [1700, 4600], s2: [3400, 4600], s3: [3400, 6900], c2: [5100, 6900],
      s5: [5100, 9200], s5b: [6800, 9200], s7: [6800, 11500], s4: [8500, 11500], c3: [8500, 13800], c4: [10200, 13800], c5: [10200, 16100] };
    const lugar = { "#s1": "s1", "#n1": "n1", "#n2": "n2", "#n3": "n3", "#s2": "s2", "#s-vid": "s3", "#c2": "c2", "#s5": "s5", "#s5b": "s5b",
      "#s7": "s7", "#s4": "s4", "#c3": "c3", "#c4": "c4", "#c5": "c5" };
    Object.keys(lugar).forEach((sel) => { const q = P[lugar[sel]]; $(sel).style.translate = q[0] + "px " + q[1] + "px"; });
    ["#s6", "#c1"].forEach((s) => { $(s).style.display = "none"; });

    const cam = $("#camera");
    const curT = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    curT.setAttribute("id", "curT"); curT.setAttribute("viewBox", "0 0 58 70");
    curT.innerHTML = '<path d="M4 4 L4 56 L18 44 L28 66 L38 61 L28 40 L50 40 Z" fill="#2f7bff" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>';
    cam.insertBefore(curT, cam.firstChild);
    tl.set(curT, { autoAlpha: 0 }, 0);

    const C = (k) => [P[k][0] + 540, P[k][1] + 960];
    let atual = "s1";
    gsap.set(cam, { x: 0, y: 0, transformOrigin: "540px 960px" });

    // viagem: a linha nasce na cena atual, a setinha corre por ela e a câmera vai junto
    function viagem(t, para, dur) {
      dur = dur || 0.7;
      const a = C(atual), b = C(para);
      const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
      const ang = Math.atan2(dy, dx) * 180 / Math.PI - 90;
      const lig = document.createElement("div");
      lig.className = "lig";
      lig.style.left = (a[0] - 4) + "px"; lig.style.top = a[1] + "px"; lig.style.height = L + "px";
      lig.style.transform = "rotate(" + ang + "deg)";
      const i = document.createElement("i");
      lig.appendChild(i);
      cam.insertBefore(lig, cam.firstChild);
      tl.fromTo(i, { scaleY: 0 }, { scaleY: 1, duration: dur + 0.15, ease: "power3.inOut" }, t - 0.15);
      tl.fromTo(lig, { opacity: 1 }, { opacity: 0, duration: 0.25, immediateRender: false }, t + dur - 0.15);
      // setinha corre na frente da câmera
      tl.set(curT, { x: a[0] + 30, y: a[1] + 40, rotation: ang + 160, autoAlpha: 0 }, t - 0.2);
      tl.to(curT, { autoAlpha: 1, duration: 0.12 }, t - 0.2);
      tl.to(curT, { x: b[0] + 30, y: b[1] + 40, duration: dur, ease: "power3.inOut" }, t - 0.08);
      tl.to(curT, { autoAlpha: 0, duration: 0.2 }, t + dur + 0.05);
      // câmera: anda, recua um pouco no meio do caminho e borra com a velocidade
      tl.to(cam, { x: -P[para][0], y: -P[para][1], duration: dur, ease: "power3.inOut" }, t);
      tl.set(cam, { transformOrigin: b[0] + "px " + b[1] + "px" }, t);
      tl.to(cam, { scale: 0.86, filter: "blur(6px)", duration: dur / 2, ease: "power2.in" }, t);
      tl.to(cam, { scale: 1, filter: "blur(0px)", duration: dur / 2, ease: "power2.out" }, t + dur / 2);
      atual = para;
    }
    // salto escondido (atrás do azul ou de uma passagem)
    function salto(t, para) {
      tl.set(cam, { x: -P[para][0], y: -P[para][1], transformOrigin: C(para)[0] + "px " + C(para)[1] + "px" }, t);
      atual = para;
    }
    // aproximação no ponto importante (câmera chega perto e volta devagar)
    function chega(t, quanto, dur, ox, oy, hold) {
      const c = C(atual);
      tl.set(cam, { transformOrigin: (c[0] + (ox || 0)) + "px " + (c[1] + (oy || 0)) + "px" }, t - 0.01);
      tl.to(cam, { scale: quanto, duration: dur || 0.6, ease: "power3.out" }, t);
      tl.to(cam, { scale: 1, duration: 0.5, ease: "power2.inOut" }, t + (dur || 0.6) + (hold == null ? 0.5 : hold));
    }

    chega(2.75, 1.06, 0.6, 0, -300);        // quanto sobra
    viagem(4.45, "n1", 0.65);               // desce até as planilhas
    chega(9.0, 1.06, 0.5, 0, 0, 0.2);       // controle
    viagem(10.22, "n2", 0.6);               // caixa, vendas, metas
    viagem(15.32, "n3", 0.6);               // ninguém sabe quem faz
    chega(20.5, 1.06, 0.4, 0, 200, 0.05);   // incêndio
    viagem(21.1, "s2", 0.65);               // consultoria e o plano de 80 páginas
    chega(23.45, 1.05, 0.6, 0, -100);       // 80 páginas
    chega(27.95, 1.04, 0.5, 0, -200, 0.4);  // continua sem solução
    salto(29.8, "s3");                      // atrás da cortina azul
    chega(32.95, 1.05, 0.5, 0, 0, 0.2);     // entra na sua empresa
    viagem(34.08, "c2", 0.55);              // financeiro e comercial
    chega(38.15, 1.05, 0.5, 0, 260, 0.2);   // toca a gestão
    viagem(39.12, "s5", 0.6);               // metas
    chega(40.78, 1.05, 0.4, 300, 0, 0);     // responsável
    viagem(41.58, "s5b", 0.6);              // plano de ação
    chega(44.22, 1.05, 0.4, 0, 300, 0);     // travado
    viagem(45.55, "s7", 0.6);               // Legacy Plan
    viagem(50.02, "s4", 0.6);               // DRE
    chega(53.42, 1.06, 0.4, -40, 360, 0.2); // quanto sobrou
    viagem(55.0, "c3", 0.6);                // para de apagar incêndio
    CAM = { viagem, chega };
  })();

  // ======== CTA (texto igual ao da voz F: leva da voz F para a G pelas palavras) ========
  bloco(false, [[42.38, 54.95]].concat(par(122, 167, 155), [[57.32, 70.9], [60, 73.58]]));

  // Você para de apagar incêndio, vê o seu lucro crescer e recupera o seu tempo para focar no que você domina.
  const ALS = [["🔔", "Boleto vencido hoje", "Fornecedor ligando de novo"], ["🔔", "Cliente cobrando entrega", "Pedido parado desde segunda"], ["🔔", "Vendedor sem meta", "Ninguém sabe quanto vendeu"]];
  ALS.forEach((a, i) => {
    const e = document.createElement("div");
    e.className = "alerta vidro p3";
    e.style.top = (640 + i * 160) + "px";
    e.innerHTML = '<div class="ic">' + a[0] + '</div><div class="tx1">' + a[1] + '</div><div class="tx2">' + a[2] + '</div><div class="ck">✓</div>';
    $("#alertas").appendChild(e);
    tl.fromTo(e, { autoAlpha: 0, y: 80, scale: 0.85, filter: "blur(10px)" }, { autoAlpha: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "back.out(1.6)" }, 42.73 + i * 0.18);
    tl.fromTo(e, { x: 0 }, { x: 10, duration: 0.05, repeat: 3, yoyo: true, ease: "none", immediateRender: false }, 43.61 + i * 0.05);
    tl.fromTo(e.querySelector(".ck"), { scale: 0, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.3, ease: "back.out(2.5)" }, 43.91 + 0.25 + i * 0.15);
    tl.to(e, { x: 900, autoAlpha: 0, filter: "blur(8px)", duration: 0.4, ease: "power3.in" }, 43.91 + 0.65 + i * 0.12);
  });
  gF(290, [[[155, "sm"], [156, "sm"], [157, "sm"]], [[158], [159, "hl"]]], 44.57);
  tl.set(["#lucroC", "#relogio", "#vfoco"], { autoAlpha: 0 }, 0);
  mostra("#lucroC", 44.65, { z: -500, y: 200, rotationX: 35, filter: "blur(16px)" }, 0.6);
  tl.fromTo("#luc-linha", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut" }, 45.07 - 0.1);
  tl.fromTo("#luc-area", { opacity: 0 }, { opacity: 1, duration: 0.8 }, 45.07);
  tl.fromTo("#luc-pt", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.4, ease: "back.out(3)" }, 45.35 + 0.4);
  gF(290, [[[160, "sm"], [161, "sm"], [162, "sm"]], [[163], [164, "hl"]]], 45.79);
  tl.to("#lucroC", { y: -500, z: -400, scale: 0.7, autoAlpha: 0, filter: "blur(12px)", duration: 0.45, ease: "power3.in" }, 45.87);
  mostra("#relogio", 45.87 + 0.1, { z: -500, scale: 0.6, filter: "blur(14px)" }, 0.6);
  tl.fromTo("#rel-m", { rotation: 0, svgOrigin: "200 200" }, { rotation: -1080, svgOrigin: "200 200", duration: 1.4, ease: "power2.inOut" }, 46.13);
  tl.fromTo("#rel-h", { rotation: 0, svgOrigin: "200 200" }, { rotation: -90, svgOrigin: "200 200", duration: 1.4, ease: "power2.inOut" }, 46.13);
  tl.fromTo("#rel-arco", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.4, ease: "power2.inOut" }, 46.13);
  gF(290, [[[165, "sm"], [166, "sm"], [167, "sm"], [168, "sm"]], [[169, "big hl"]]], 47.09);
  CAM.chega(46.87, 1.06, 0.4, 0, 0, 0);
  tl.to("#relogio", { scale: 2.2, autoAlpha: 0, filter: "blur(16px)", duration: 0.35, ease: "power2.in" }, 47.17 - 0.25);
  tl.set(["#fA", "#fB", "#fC"], { autoAlpha: 0 }, 0);
  if (VAR === "atual") {
    mostra("#vfoco", 47.17 - 0.15, { scale: 0.7, z: -300, filter: "blur(16px)" }, 0.6);
    tl.fromTo("#vfoco .vw", { scale: 1.15 }, { scale: 1.02, duration: 1.6, ease: "power2.out" }, 47.17 - 0.15);
  }
  // variações do "recupera o seu tempo para focar no que você domina" (tempos da voz nova, sem mapa)
  const t0 = M(47.17 - 0.15);
  const entra = (el, t) => tlr.fromTo(el, { autoAlpha: 0, z: -500, scale: 0.7, filter: "blur(16px)" }, { autoAlpha: 1, z: 0, scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, t);
  const brilha = (el, t) => tlr.to(el, { boxShadow: "0 30px 70px rgba(47,123,255,.45), 0 0 0 5px #2f7bff", scale: 1.04, duration: 0.3, ease: "back.out(2)" }, t);
  if (VAR === "A") {   // agenda: sai o incêndio, entra o que você domina
    entra("#fA", t0);
    $$("#fA .ruim").forEach((e, i) => tlr.to(e, { x: 620, autoAlpha: 0, filter: "blur(8px)", duration: 0.35, ease: "power3.in" }, t0 + 0.25 + i * 0.1));
    $$("#fA .bom").forEach((e, i) => tlr.fromTo(e, { autoAlpha: 0, x: -200, scale: 0.85 }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.8)" }, t0 + 0.55 + i * 0.12));
    brilha("#fA .bom.um", TT[175] - 0.05);
  }
  if (VAR === "B") {   // quadro: a operação vai para a Legacy, fica com você o que você domina
    entra("#fB", t0);
    $$("#fB .tar").forEach((e, i) => {
      tlr.to(e, { x: 380, duration: 0.5, ease: "power3.inOut" }, t0 + 0.3 + i * 0.12);
      tlr.fromTo(e.querySelector("b"), { autoAlpha: 0, scale: 0 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }, t0 + 0.75 + i * 0.12);
    });
    tlr.fromTo("#fB .seu", { autoAlpha: 0, y: 60, scale: 0.8 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.8)" }, t0 + 0.95);
    brilha("#fB .seu", TT[175] - 0.05);
  }
  if (VAR === "C") {   // barra do seu tempo: o laranja do incêndio vira azul do que você domina
    entra("#fC", t0);
    tlr.fromTo("#fC .lar", { width: 520 }, { width: 90, duration: 0.9, ease: "power3.inOut" }, t0 + 0.35);
    tlr.fromTo("#fC .az", { width: 90 }, { width: 520, duration: 0.9, ease: "power3.inOut" }, t0 + 0.35);
    tlr.fromTo("#fC .lg2", { scale: 1 }, { scale: 1.12, transformOrigin: "0% 50%", duration: 0.3, ease: "back.out(2)" }, TT[175] - 0.05);
    brilha("#fC .barra2", TT[175] - 0.05);
  }
  gF(290, [[[170, "sm"], [171, "sm"], [172, "sm"], [173, "sm"]], [[174], [175, "hl"]]], 48.59);

  // E se em seis meses você não tiver resultado, devolvemos todo o seu investimento.
  CAM.viagem(48.64, "c4", 0.6);
  (function () {
    const g = $("#arcos");
    for (let i = 0; i < 6; i++) {
      const a0 = (-90 + i * 60 + 4) * Math.PI / 180, a1 = (-90 + (i + 1) * 60 - 4) * Math.PI / 180, r = 205;
      const pth = document.createElementNS("http://www.w3.org/2000/svg", "path");
      pth.setAttribute("d", "M" + (230 + r * Math.cos(a0)).toFixed(1) + " " + (230 + r * Math.sin(a0)).toFixed(1) + " A" + r + " " + r + " 0 0 1 " + (230 + r * Math.cos(a1)).toFixed(1) + " " + (230 + r * Math.sin(a1)).toFixed(1));
      pth.setAttribute("fill", "none"); pth.setAttribute("stroke-width", "16"); pth.setAttribute("stroke-linecap", "round");
      pth.setAttribute("stroke", "#dce8fb");
      g.appendChild(pth);
      tl.to(pth, { attr: { stroke: "#2f7bff" }, duration: 0.12 }, 49.59 + i * 0.12);
    }
  })();
  tl.set("#selo", { autoAlpha: 0 }, 0);
  tl.fromTo("#selo", { autoAlpha: 0, z: -700, scale: 0.6, rotationY: -60 }, { autoAlpha: 1, z: 0, scale: 1, rotationY: 0, duration: 0.8, ease: "expo.out" }, 48.99);
  gF(290, [[[176, "sm"], [177, "sm"], [178, "sm"]], [[179, "big hl", "6"], [180, "big"]]], 50.15);
  gF(290, [[[181, "sm"], [182, "sm"], [183, "sm"]], [[184, "big"]]], 51.69);
  tl.to("#selo", { rotationY: 180, duration: 0.8, ease: "power3.inOut" }, 51.77);
  gF(290, [[[185]], [[186, "sm"], [187, "sm"], [188, "sm"]], [[189, "big hl"]]], 53.45);
  CAM.chega(52.99, 1.06, 0.5, 0, 0, 0.2);

  // Clique no link da bio e agende sua sessão agora mesmo.
  CAM.viagem(53.50, "c5", 0.6);
  tl.set(["#bio", "#botao", "#cur3", "#logo-fim", "#tag"], { autoAlpha: 0 }, 0);
  mostra("#bio", 54.37, { y: 40, scale: 0.8 }, 0.5);
  mostra("#botao", 53.85, { z: -600, y: 200, rotationX: 40, filter: "blur(16px)" }, 0.7);
  tl.set("#cur3", { x: 880, y: 1150 }, 0);
  tl.to("#cur3", { autoAlpha: 1, duration: 0.2 }, 55.01 - 0.4);
  tl.to("#cur3", { x: 640, y: 860, duration: 0.45, ease: "power3.out" }, 55.01 - 0.4);
  tl.to("#cur3", { scale: 0.82, duration: 0.08, yoyo: true, repeat: 1 }, 55.23);
  tl.to("#botao", { scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }, 55.23);
  (function () { const b = $("#bt-tx"); const o = { v: 0 };
    tl.fromTo(o, { v: 0 }, { v: 1, duration: 0.01, onUpdate: () => { b.textContent = o.v >= 1 ? "✓ Sessão agendada" : "📅 Agendar minha sessão"; } }, 55.73); })();
  tl.to("#botao", { background: "linear-gradient(110deg,#10b981,#34d399)", boxShadow: "0 30px 70px rgba(16,185,129,.4)", duration: 0.25 }, 55.73);
  gF(290, [[[190, "sm"], [191, "sm"]], [[192], [193], [194, "hl"]]], 54.93);
  gF(290, [[[195, "sm"], [196], [197, "sm"]], [[198, "big hl"]], [[199, "sm"], [200, "sm"]]], 57.32);
  tl.to(["#bio", "#botao", "#cur3"], { autoAlpha: 0, y: -60, filter: "blur(10px)", duration: 0.35, ease: "power2.in" }, 57.32);
  mostra("#logo-fim", 57.32 + 0.25, { y: 60, scale: 0.9, filter: "blur(14px)" }, 0.8);
  mostra("#tag", 57.32 + 0.7, { y: 40, filter: "blur(10px)" }, 0.7);
  tl.fromTo("#tag .marca", { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power3.out" }, 57.32 + 1.1);
  tl.fromTo("#tag .tx", { color: "#0a1a33" }, { color: "#ffffff", duration: 0.2 }, 57.32 + 1.15);
  CAM.chega(57.32 + 0.2, 1.04, 1.2, 0, 0, 0);

  bloco(false, null);
  // fundo respira o tempo todo
  tl.fromTo("#grade", { y: 0 }, { y: -300, duration: DUR, ease: "none" }, 0);
  tl.fromTo("#blob1", { x: 0, y: 0 }, { x: 260, y: 300, duration: DUR, ease: "sine.inOut" }, 0);
  tl.fromTo("#blob2", { x: 0, y: 0 }, { x: -300, y: -260, duration: DUR, ease: "sine.inOut" }, 0);
  tlr.set({}, {}, DUR);
})();

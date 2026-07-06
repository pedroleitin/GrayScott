# Backlog — gray_scott_smooth_svg.html

Itens para revisitar mais tarde (anotado em 2026-06-23).

## 1. Resolução
- Hoje a simulação roda em `N` (slider Resolution, 64–320). O detalhe do halftone de
  imagem fica limitado por `N`, e valores altos pesam no desempenho.
- A investigar: permitir resolução maior; desacoplar a resolução de
  render/export da resolução da simulação; supersampling só no export.

## 2. Export
- Estado atual: SVG (marching squares → Catmull-Rom), PNG (1024px com filtro
  blur+contraste), Sequência PNG (120 frames em ZIP store-only).
- A revisar: opções de resolução/tamanho no export; conferir qualidade do export
  no modo Gray-Scott halftone com imagem; simplificação/peso dos paths SVG;
  contagem de frames da sequência configurável.

## 3. Refino das linhas do halftone
- O efeito atual modula o threshold do Gray-Scott por pixel pela luminância da
  imagem (linhas do labirinto engrossam no escuro, afinam no claro).
- A refinar: curva de mapeamento luminância→espessura (gama/contraste do efeito);
  suavização das linhas; possivelmente reintroduzir um halftone de linhas dedicado,
  porém melhor feito (o modo "Lines" anterior foi removido a pedido).

## 4. Port GPU — WebGL2 + WebGPU (anotado 2026-07-03)
- Motivação: o gargalo é o `step()` na CPU (~64ms/step a N=1024, ~3-10fps).
  RD é o caso clássico de GPU (stencil por vizinhos = paralelo perfeito).
- Fazer **as duas versões** (WebGL2 e WebGPU) como arquivos separados, sem mexer
  no app atual. Contexto do usuário: ferramenta pra hardware novo, **rodar servidor
  é OK** → WebGPU (compute shaders WGSL) vale a pena, apesar de exigir secure context.
  - WebGL2: sim via fragment shader + ping-pong de framebuffers; texturas float
    R32F/RG32F; roda até em `file://`.
  - WebGPU: compute shader real sobre o grid; API mais limpa; teto de performance
    maior; precisa de servidor/https e browser recente.
- Arquitetura híbrida: sim 100% na GPU (2 texturas A/B ping-pong); render direto da
  textura; **readback (`readPixels`/copy) só no export SVG/PNG e pra alimentar o
  trace**; paint/wall/texto/halftone viram textura de obstáculo amostrada no shader.
- Meta do protótipo: medir o ganho real e validar o híbrido antes de portar tudo.

### Progresso — WebGL2 (2026-07-03)
- **Protótipo `gray_scott_webgl.html` pronto e validado.** Sim 100% na GPU:
  ping-pong de 2 texturas RG32F (A,B), update via fragment shader com `texelFetch`
  + wrap toroidal, display por threshold + filtro CSS blur/contraste. Coefs
  idênticos ao app (0.2/0.1, THRESH 0.18).
- **Resultado medido (headless Chromium):** 60fps em 512² / 1024² / 2048²;
  a 2048² com 60 steps/frame = **3.600 steps/s ainda travado no vsync** (folga
  enorme). Na CPU o 1024² fazia ~3-10fps. Ganho comprovado.
### WebGL2 — COMPLETO (2026-07-03)
- **`gray_scott_webgl.html` = app WebGL2 com paridade de recursos.** Partiu do app
  atual (UI + pipeline de export reaproveitados verbatim); só o motor virou GPU.
  - Estado A/B em 2 texturas RGBA32F (ping-pong); wall e img em texturas R32F.
  - Sim/display/splat em 3 shaders. Display faz Y-flip; wallColor/border/halftone no
    shader. Paint: seed = splat GPU; wall/erase = CPU `wall` + `uploadWall`.
  - Export: `readbackB()` (gl.readPixels do fbo float) → `buildDarkField` CPU → mesmo
    trace/PNG de antes. `preserveDrawingBuffer:true` p/ o PNG capturar o canvas.
- **Validado:** sim bate com a CPU (Coral 10k passos: GPU 0.493 vs CPU 0.495);
  10k passos a 192² em 55ms; texto/paint/halftone/export SVG+PNG ok; 60fps até 2048².
- Nota: rAF é throttled em tab não-focada (comportamento normal do browser) — no
  preview headless o padrão parece imaturo; com a aba focada roda a 60fps normal.
- **Falta:** 2ª versão em **WebGPU** (ver §6).

## 5. Controle de espessura do brush + preview no mouse (anotado 2026-07-03)
- Hoje o raio do brush é fixo (`R=Math.max(3,N/45|0)` em `paint()`). Adicionar um
  **slider de espessura** na seção Brush controlando esse raio.
- **Preview no cursor:** um anel/círculo que segue o mouse sobre o canvas mostrando
  o tamanho atual do brush (em px de tela = raio em cells × escala do canvas).
  Provavelmente um `<div>` ou SVG posicionado por `mousemove` sobre `#canvas-wrap`,
  visível só quando o mouse está sobre o canvas.
- Aplicar nos dois apps (CPU `gray_scott_smooth_svg.html` e WebGL
  `gray_scott_webgl.html`); no WebGL o raio já vai pro shader de splat (`u_r`) e pro
  loop de wall/erase.

## 6. Port WebGPU — COMPLETO (2026-07-03)
- 2ª versão do motor em **WebGPU** (compute shaders WGSL), arquivo separado
  `gray_scott_webgpu.html`, sem tocar nos outros dois apps.
- **Arquitetura:** 2 storage buffers (A,B intercalados) em ping-pong; wall e img em
  storage buffers próprios; 3 pipelines — `pUpdate`/`pSplat` (compute,
  `@workgroup_size(8,8)`) e `pDisplay` (render, fullscreen triangle direto no canvas
  via `GPUCanvasContext`). Init assíncrono (`requestAdapter`/`requestDevice`).
  Export: `readbackB()` agora é **assíncrono** (`copyBufferToBuffer` + `mapAsync`),
  então o handler do `export-btn` virou `async` com `await readbackB()`. UI/trace/
  PNG reaproveitados verbatim do app WebGL.
- **Validado:** sim bate com CPU/WebGL (Coral 10k passos síncronos: WebGPU 0.492 vs
  CPU 0.495 vs WebGL 0.493); 10k passos a 192² em 329ms; texto colisor com orientação
  correta e borda; paint seed/wall/erase ok; halftone gs (centro escuro 0.66 vs canto
  claro 0.27); export SVG (readback async, path válido, sem NaN) e PNG válidos; zero
  erros JS/console em todos os testes.
- Requer `navigator.gpu` (Chrome/Edge recentes) + secure context (servidor/https —
  não abre em `file://`, diferente do WebGL2).

## 7. Trocar cores do padrão
### CPU — COMPLETO (2026-07-03)
- Nova seção **"Colors"** em `gray_scott_smooth_svg.html`: dois `<input type="color">`
  no estilo visual do app — **Foreground** (default `#000000`) e **Background**
  (default `#ffffff`).
- `render()` recolore por display apenas (`fgRGB`/`bgRGB`, sem tocar em `A`/`B`/`step`)
  — trocar a cor é instantâneo e **não recalcula a simulação** (verificado: soma de
  `B` idêntica antes/depois de mudar a cor). Export SVG usa `fgColor`/`bgColor` como
  `fill` (PNG herda automaticamente, pois copia o canvas já colorido).
- **Border** (texto colisor) virou **checkbox** (`#bd-chk`), substituindo o segmentado
  Off/On; handler único `change`.
- **Preview de imagem**: a `#drop-zone` agora mostra uma miniatura 40×40 (thumbnail
  gerado via canvas) da imagem carregada, ao lado do nome do arquivo.
- Convive normalmente com `wallColor` (texto ainda escolhe fg ou bg) e com o halftone.
- **Falta portar:** WebGL (`gray_scott_webgl.html`) e WebGPU (`gray_scott_webgpu.html`)
  — os shaders de display (`_FS_DISPLAY`/`WGSL_DISPLAY`) hoje geram `vec4(v,v,v,1)`;
  trocar por `mix(corFundo, corTinta, v)` alimentado por um novo uniform/param buffer
  de cor (sem precisar recompilar shader a cada troca — só atualizar o uniform).
  Mesma UI (Colors section, checkbox Border, preview de imagem) deve ser copiada.

> Sem prazo definido — retomar quando voltarmos ao projeto. Python/AppleScript
> (companion offline) foram movidos para `archive/` a pedido.

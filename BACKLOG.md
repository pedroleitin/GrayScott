# Backlog — gray_scott_webgl.html

Itens em aberto para o app WebGL2 (`gray_scott_webgl.html`). Concluídos ficam
resumidos no rodapé; o histórico detalhado está no `CHANGELOG.md`.

## 1. Export — opções e qualidade
- Estado atual: **SVG** (marching squares → Catmull-Rom, blur fixo `BLUR_REF=512`,
  trace detail 2×/3×/4×), **PNG** (espelha o tamanho de tela, reaplica blur+contraste
  + gradient map), **Seq PNG** (frames em ZIP store-only).
- A revisar:
  - opções de **resolução/tamanho** no export (hoje SVG é 512 e PNG segue a tela);
  - **peso/simplificação** dos paths SVG (contagem de pontos, tolerância de fit);
  - **contagem de frames** da sequência configurável;
  - conferir qualidade do export no modo **Gray-Scott halftone** com imagem.

## 2. Refino das linhas do halftone
- O efeito modula o threshold do Gray-Scott por pixel pela luminância da imagem
  (`gsBase`/`gsSlope`, controlados por Thinnest/Thickest) — linhas engrossam no escuro,
  afinam no claro.
- A refinar: **curva de mapeamento** luminância→espessura (gama/contraste do efeito);
  suavização das linhas; possivelmente um halftone de linhas dedicado, melhor feito
  (o modo "Lines" anterior foi removido a pedido).

## 3. Resolução — supersampling só no export
- Já resolvido: teto de **2048²** e mudança de resolução **sem limpar** (reamostra o
  campo por bilinear).
- Em aberto: desacoplar a resolução de **render/export** da resolução da **simulação**
  — rodar o trace/PNG numa grade mais fina que a do sim (supersampling só no export),
  sem pesar o loop em tempo real.

## Concluídos (resumo — detalhes no `CHANGELOG.md`)
- **Port GPU:** motor WebGL2 (`gray_scott_webgl.html`, app principal) e WebGPU
  (`archive/gray_scott_webgpu.html`, comparação). Sim 100% na GPU, 60fps até 2048².
- **Cores:** Foreground/Background com recolor instantâneo via gradient map (sem
  recalcular o sim); Border e Invert como checkbox.
- **Brush:** slider de espessura + anel de preview no cursor.
- **Detail ramp:** gradiente espacial de tamanho de feature (Horiz/Vert/Radial).
- **Controle:** Clear (limpa texto+paredes, mantém o padrão); resolução até 2048² com
  reamostragem (não limpa a tela).
- **Halftone:** preview em miniatura na drop-zone; **morph A→B** (Cross/Dissolve,
  Play com easing + Speed + Loop, Swap/Remove, Export morph em sequência PNG).

> `archive/` guarda os motores antigos (CPU `gray_scott_smooth_svg.html`, WebGPU
> `gray_scott_webgpu.html`) e o companion offline Python/AppleScript. Fora do fluxo atual.

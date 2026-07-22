---
theme: default
title: "PyVista on WebAssembly: Server-less 3D Visualization"
info: |
  PyCon JP 2026 talk by Tetsuo Koyama.
  Running PyVista entirely in the browser via WebAssembly — no server required.
class: text-center
highlighter: shiki
transition: slide-left
mdc: true
fonts:
  sans: Noto Sans JP
  mono: JetBrains Mono
layout: cover
---

# PyVista on WebAssembly

<div class="text-2xl font-light opacity-80">Server-less 3D Visualization</div>

<div class="text-xl opacity-60 mt-2">サーバーレス3D可視化の実現</div>

<div class="text-sm opacity-70 mt-10 mx-auto max-w-xl">
Running PyVista entirely in the browser via WebAssembly — no server required
</div>

<div class="abs-bl mx-14 my-12 flex items-center gap-3 text-base opacity-80">
  <div>PyCon JP 2026</div>
  <div class="opacity-40">·</div>
  <div>Tetsuo Koyama</div>
</div>

---
layout: two-cols
class: text-left
---

# Agenda

<div class="text-sm opacity-70 mb-6">A 30-minute tour, from the why to the how</div>

<div class="flex flex-col gap-4">

<div class="flex items-baseline gap-3">
  <div class="text-2xl opacity-40 w-8">1</div>
  <div>
    <div class="font-medium">PyVista and WASM overview</div>
    <div class="text-sm opacity-60">Why run 3D visualization in the browser</div>
  </div>
</div>

<div class="flex items-baseline gap-3">
  <div class="text-2xl opacity-40 w-8">2</div>
  <div>
    <div class="font-medium">Technical stack & implementation</div>
    <div class="text-sm opacity-60">vtk-wasm, TypeScript glue, PyVista API</div>
  </div>
</div>

<div class="flex items-baseline gap-3">
  <div class="text-2xl opacity-40 w-8">3</div>
  <div>
    <div class="font-medium">Live demo in browser</div>
    <div class="text-sm opacity-60">PyVista running with no server</div>
  </div>
</div>

<div class="flex items-baseline gap-3">
  <div class="text-2xl opacity-40 w-8">4</div>
  <div>
    <div class="font-medium">Performance & limitations</div>
    <div class="text-sm opacity-60">What works today, what does not yet</div>
  </div>
</div>

</div>

::right::

<div class="ml-8">

# Speaker

<div class="text-lg font-medium mt-2">Tetsuo Koyama</div>
<div class="text-sm opacity-60 mb-6">小山 哲央</div>

<div class="flex flex-col gap-3 text-sm">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧩</div>
  <div>PyVista contributor — bug fixes and feature PRs</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔧</div>
  <div>pyvista-wasm co-maintainer</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div>SciPy Conference 2022–2025 — MyST, PyVista, GeoVista sprints</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🗾</div>
  <div>SciPyData Japan 2025 co-organizer</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎤</div>
  <div>PyCon JP speaker and organizer</div>
</div>

</div>

</div>

---
layout: two-cols
class: text-left
---

# What is PyVista?

<div class="text-sm opacity-70 mb-6">A Pythonic interface to the Visualization Toolkit</div>

<div class="flex flex-col gap-4">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🏛️</div>
  <div>
    <div class="font-medium">Built on VTK</div>
    <div class="text-sm opacity-60">The Visualization Toolkit — a C++ scientific visualization library by Kitware, 30+ years of development since 1993</div>
  </div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div>
    <div class="font-medium">PyVista wraps VTK for Python</div>
    <div class="text-sm opacity-60">An intuitive, high-level API over VTK's powerful but verbose C++ core</div>
  </div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔬</div>
  <div>
    <div class="font-medium">Hundreds of filters</div>
    <div class="text-sm opacity-60">Point clouds, meshes, and volume data, rendered via OpenGL / Vulkan</div>
  </div>
</div>

</div>

::right::

<div class="ml-8">

# Where it is used

<div class="text-sm opacity-60 mb-6">A de facto standard across scientific and engineering fields</div>

<div class="flex flex-col gap-3 text-sm">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🩻</div>
  <div>Medical imaging — diagnostics and analysis</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚙️</div>
  <div>CAE — manufacturing and simulation</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌏</div>
  <div>Geoscience and meteorology</div>
</div>

</div>

<div class="text-sm opacity-60 mt-8 mb-3">A rich ecosystem</div>

<div class="flex flex-col gap-3 text-sm">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧠</div>
  <div>ITK — medical image processing</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔢</div>
  <div>NumPy / SciPy — arrays and scientific computing</div>
</div>

</div>

</div>

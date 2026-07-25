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
layout: two-cols-header
class: text-left
---

<script setup>
// Public assets are served at the deck's base path, which differs between
// the PR preview and the deployed deck — resolve it at runtime so the live
// demo iframe loads under either base.
const demoUrl = import.meta.env.BASE_URL + 'pyvista-demo.html'
</script>

# What is PyVista?

<div class="text-lg opacity-80 mt-1">30 years of VTK's 3D power — made Pythonic</div>

::left::

<div class="pr-8 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🏛️</div>
  <div><span class="font-medium">Built on VTK</span> — Kitware's C++ visualization toolkit, 30+ years of development since 1993</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div><span class="font-medium">Pythonic API</span> — wraps VTK's powerful but verbose C++ core in a few intuitive lines</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🩺</div>
  <div><span class="font-medium">De facto standard</span> — medical imaging, CAE, geoscience, and meteorology</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔢</div>
  <div><span class="font-medium">Rich ecosystem</span> — ITK, NumPy, and SciPy</div>
</div>

</div>

::right::

<div class="pt-6 pl-2">

<iframe
  :src="demoUrl"
  class="w-full rounded-lg shadow-xl"
  style="height: 340px; border: 1px solid rgba(125,125,125,0.3)"
></iframe>

<div class="text-xs opacity-60 mt-3 text-center">A triangulated 3D mesh, rendered by PyVista — <span class="font-medium">drag to rotate it</span>.</div>

</div>

---
layout: two-cols-header
class: text-left
---

# The Problem

<div class="text-lg opacity-80 mt-1">Sharing 3D results on the web still means running a server</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎨</div>
  <div><span class="font-medium">Three.js is not enough</span> — the go-to browser 3D library has no direct path to render physics and simulation results</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🖥️</div>
  <div><span class="font-medium">SSR needs a server</span> — server-side rendering fills the gap, but someone has to build and maintain a dedicated visualization server</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">💸</div>
  <div><span class="font-medium">Cost</span> — standing up and operating that infrastructure is an ongoing expense</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔒</div>
  <div><span class="font-medium">Security risk</span> — confidential simulation data has to leave the analyst's machine and travel to the server</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">These barriers make it hard to share analysis results <span class="font-medium">quickly and securely</span> — what if the browser could do it all?</div>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Why WASM?

<div class="text-lg opacity-80 mt-1">The browser can do it all — every barrier falls away at once</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧠</div>
  <div><span class="font-medium">Nothing is sent anywhere</span> — WebAssembly runs the whole visualization pipeline in the browser, so the round trip to a rendering server disappears</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔒</div>
  <div><span class="font-medium">Data never leaves the machine</span> — confidential simulation results stay client-side, so there is no transfer to secure in the first place</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">💸</div>
  <div><span class="font-medium">No infrastructure to stand up</span> — no visualization server to provision, scale, or pay for month after month</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔬</div>
  <div><span class="font-medium">Where this came from</span> — a physics simulation project asked for one thing: <span class="italic">drop the analyzed mesh into the browser and see it</span></div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">💼</div>
  <div><span class="font-medium">Demos anywhere</span> — show results in the field or at a client site with a browser and nothing else</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">A URL becomes the whole delivery mechanism — <span class="font-medium">so how do we get PyVista in there?</span></div>
</div>

</div>

---
class: text-left
---

# Architecture: SSR vs Wasm

<div class="text-lg opacity-80 mt-1">SSR puts a server in the loop — Wasm closes the loop inside the browser</div>

<div class="grid grid-cols-2 gap-12 mt-10">

<div class="flex flex-col items-center">

<div class="text-sm font-medium opacity-60 mb-6">Traditional · Server-Side Rendering</div>

<div class="rounded-lg px-6 py-4 text-center" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-xl">💻</div>
  <div class="font-medium text-sm">Client</div>
</div>
<div class="text-xs opacity-70 my-2">↓ data send</div>
<div class="rounded-lg px-6 py-4 text-center" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-xl">🖥️</div>
  <div class="font-medium text-sm">Server</div>
</div>
<div class="text-xs opacity-70 my-2">↓ render and return</div>
<div class="rounded-lg px-6 py-4 text-center" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-xl">💻</div>
  <div class="font-medium text-sm">Client</div>
</div>

<div class="text-xs opacity-60 mt-5 text-center">Every frame round-trips over the network</div>

</div>

<div class="flex flex-col items-center">

<div class="text-sm font-medium opacity-60 mb-6">Wasm · Browser-Complete</div>

<div class="rounded-lg px-8 py-6 text-center" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-2xl">🌐</div>
  <div class="font-medium">Client</div>
  <div class="text-xs opacity-60 mt-1">render in browser</div>
</div>

<div class="text-xs opacity-60 mt-5 text-center">No server — the pipeline runs entirely client-side</div>

</div>

</div>

<div class="flex items-baseline gap-3 mt-8">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">The round-trip is gone entirely — <span class="font-medium">rendering happens where the data already is</span></div>
</div>

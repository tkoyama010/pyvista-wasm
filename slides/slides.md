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

---
layout: two-cols-header
class: text-left
---

# What is vtk.wasm?

<div class="text-lg opacity-80 mt-1">30 years of VTK's capability — now running in the browser</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🏛️</div>
  <div><span class="font-medium">Built by Kitware</span> — the C++ Visualization Toolkit, maintained since 1993, 30+ years of accumulated capability</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🩺</div>
  <div><span class="font-medium">Field-proven</span> — medical imaging, CAE, and geoscience run on VTK every day</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📊</div>
  <div><span class="font-medium">Hundreds of filters</span> — point clouds, meshes, and volume data out of the box</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎨</div>
  <div><span class="font-medium">OpenGL/Vulkan renderers</span> — production-grade GPU pipelines</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔢</div>
  <div><span class="font-medium">Rich ecosystem</span> — PyVista (Python wrapper), ITK (medical imaging), and the NumPy/SciPy scientific stack</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">Wasm port</span> — all of these capabilities now run without a server, entirely in the browser</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">💼</div>
  <div><span class="font-medium">Demos anywhere</span> — particularly significant for field demos and client-site presentations</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">VTK's full power in a URL — <span class="font-medium">so how do we glue it to PyVista?</span></div>
</div>

</div>

---
class: text-left
---

# Wasm Build History & Current Status

<div class="text-lg opacity-80 mt-1">From experimental builds to runtime GPU switching — a steady maturity trajectory</div>

<div class="grid grid-cols-3 gap-8 mt-10">

<div class="rounded-lg px-5 py-4" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-2xl font-medium">2018</div>
  <div class="text-sm opacity-60 mb-3">Experimental</div>
  <div class="text-sm">Emscripten builds began — early proof-of-concept bringing VTK to the browser</div>
</div>

<div class="rounded-lg px-5 py-4" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-2xl font-medium">2021</div>
  <div class="text-sm opacity-60 mb-3">Official</div>
  <div class="text-sm">Integrated into the official build pipeline; <span class="font-medium">vtk.wasm</span> published on npm — distinct from <span class="font-medium">vtk.js</span> (the JavaScript reimplementation)</div>
</div>

<div class="rounded-lg px-5 py-4" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-2xl font-medium">2023–2024</div>
  <div class="text-sm opacity-60 mb-3">WebGPU</div>
  <div class="text-sm">WebGPU backend support progressed — higher rendering performance and GPU compute compared to WebGL</div>
</div>

</div>

<div class="flex flex-col gap-4 mt-8">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔄</div>
  <div><span class="font-medium">Runtime switching</span> — current packages can switch between WebGL and WebGPU at runtime</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🛡️</div>
  <div><span class="font-medium">Automatic fallback</span> — gracefully degrades based on browser support, a design still progressing</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">From experiment to production-ready — <span class="font-medium">the technology is maturing steadily</span></div>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Capabilities & Current Limitations

<div class="text-lg opacity-80 mt-1">What vtk.wasm can do today — and where the edges still are</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Capabilities</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚙️</div>
  <div><span class="font-medium">VTK filter pipeline</span> — full filter execution runs entirely in the browser</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📦</div>
  <div><span class="font-medium">Mesh loading</span> — VTP, VTU, and STL formats load directly client-side</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎮</div>
  <div><span class="font-medium">Interactive camera</span> — rotate, pan, and zoom with direct manipulation</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div><span class="font-medium">Python integration</span> — the PyVista API drives it all from Python</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Limitations</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📏</div>
  <div><span class="font-medium">Module size</span> — 30–50 MB, 10–15 MB after gzip</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧵</div>
  <div><span class="font-medium">COOP/COEP headers</span> — multi-threading requires cross-origin isolation</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚩</div>
  <div><span class="font-medium">WebGPU flags</span> — may need experimental flags in some browsers</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⏳</div>
  <div><span class="font-medium">Initial load</span> — several seconds to 10+ seconds before first render</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">Large-scale meshes still have constraints — but <span class="font-medium">~100K elements run at practical interactive speed</span></div>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Build & Distribution Mechanism

<div class="text-lg opacity-80 mt-1">A hours-long Emscripten build collapses to <code>npm install</code> — the binary streams from CDN at runtime</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Build</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🏗️</div>
  <div><span class="font-medium">Emscripten</span> — VTK's C++ compiled to WebAssembly; the build takes hours, but consumers just <code>npm install</code></div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📦</div>
  <div><span class="font-medium">@kitware/vtk-wasm</span> — the JavaScript binding npm package that exposes the VTK API to the browser</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Distribution</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">CDN at runtime</span> — the WASM binary is loaded separately from CDN, not bundled into the JS package</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚙️</div>
  <div><span class="font-medium">createNamespace(url)</span> — loads VTK classes asynchronously from a tarball URL</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚀</div>
  <div><span class="font-medium">jsDelivr over GitLab</span> — multi-CDN (Cloudflare, Fastly, Bunny CDN) edge caching beats Kitware's GitLab direct delivery in the Asia region</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">⏳</div>
  <div class="opacity-90">First load is ~12–15 MB (gzip) — pair with a spinner and lazy loading (Intersection Observer)</div>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# VTK Emscripten Build Pipeline

<div class="text-lg opacity-80 mt-1">C++ compiled to WebAssembly once — consumers just <code>npm install</code> and add two Vite lines</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🏗️</div>
  <div><span class="font-medium">Emscripten</span> — VTK's entire C++ codebase compiled to WebAssembly, bringing 30 years of capability into the browser</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⏳</div>
  <div><span class="font-medium">Heavy build, light consumption</span> — the build itself takes hours, but consumers simply <code>npm install @kitware/vtk-wasm</code></div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📦</div>
  <div><span class="font-medium">Tarball at runtime</span> — the WASM binary streams from CDN as a tarball, not bundled into the JS package</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">One Vite config unlocks it all — <span class="font-medium">two lines stand between you and browser-native VTK</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="text-sm font-medium opacity-60 mb-3">vite.config.js</div>

```js
export default {
  build: {
    target: 'esnext',
  },
  optimizeDeps: {
    exclude: ['@kitware/vtk-wasm'],
  },
};
```

<div class="flex flex-col gap-4 mt-6">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎯</div>
  <div><span class="font-medium">build.target: 'esnext'</span> — vtk-wasm relies on modern JS features that require next-generation build targets</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚫</div>
  <div><span class="font-medium">optimizeDeps.exclude</span> — Vite must not pre-bundle the WASM package; it loads asynchronously at runtime</div>
</div>

</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Pyodide + PyVista in the Browser

<div class="text-lg opacity-80 mt-1">CPython in Wasm meets a Pythonic VTK wrapper — write Python, render 3D meshes, no server required</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div><span class="font-medium">Pyodide</span> — CPython compiled to WebAssembly, running the real CPython interpreter inside the browser</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧊</div>
  <div><span class="font-medium">PyVista</span> — a Pythonic wrapper over VTK, the same API scientists already use on the desktop</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔗</div>
  <div><span class="font-medium">The combination</span> — write Python in the browser, visualize 3D meshes on the same page, zero backend</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌉</div>
  <div><span class="font-medium">pyvista-wasm</span> — bridges the gap with a PyVista-like API built on top of vtk-wasm</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">TypeScript is the glue — <span class="font-medium">loading vtk-wasm and bridging C++ VTK bindings to the Python-facing API</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="text-sm font-medium opacity-60 mb-3">Layered architecture</div>

```text
Python (Pyodide)
       │  pyvista_wasm
       ▼
TypeScript glue layer
       │  @kitware/vtk-wasm
       ▼
VTK (C++) → WebAssembly
```

<div class="flex flex-col gap-4 mt-6">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚙️</div>
  <div><span class="font-medium">Glue layer</span> — TypeScript loads the vtk-wasm module and exposes its VTK classes to Python</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🛰️</div>
  <div><span class="font-medium">Runtime fallback</span> — when <code>"pyodide" in sys.modules</code>, mesh fetches use XMLHttpRequest instead of urllib</div>
</div>

</div>

</div>

---
layout: two-cols-header
class: text-left
---

# WebGL / WebGPU Rendering Integration

<div class="text-lg opacity-80 mt-1">Two render backends, one runtime — WebGL keeps it everywhere, WebGPU pushes it further</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">WebGL · the baseline</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">Universally supported</span> — available in every modern browser, the reliable render path that always works</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎨</div>
  <div><span class="font-medium">OpenGL ES heritage</span> — a mature, well-understood graphics API with years of tooling and driver support</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🛡️</div>
  <div><span class="font-medium">Safe default</span> — guarantees a working visualization even on older or conservative browsers</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">WebGPU · the next step</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚡</div>
  <div><span class="font-medium">Higher performance</span> — lower driver overhead and closer-to-the-metal access than WebGL</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧮</div>
  <div><span class="font-medium">GPU compute</span> — exposes general-purpose compute shaders, not just the fixed rendering pipeline</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚩</div>
  <div><span class="font-medium">Experimental in places</span> — some browsers still require flags; 2023–2024 brought significant backend progress</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">🔄</div>
  <div><span class="font-medium">Runtime switching</span> — current packages select between WebGL and WebGPU at runtime, with automatic fallback when WebGPU is unavailable</div>
</div>

</div>

---
layout: two-cols-header
class: text-left
---


# Development & CI Challenges

<div class="text-lg opacity-80 mt-1">Three pitfalls every vtk.wasm integration hits — and the fix for each</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⏳</div>
  <div><span class="font-medium">async/await everywhere</span> — <code>createNamespace()</code> returns a Promise, so every VTK object operation must be <code>async/await</code>; forgetting <code>await</code> touches objects before WASM loads and errors out</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧵</div>
  <div><span class="font-medium">SharedArrayBuffer</span> — parallel processing filters need it, so the server must return <code>Cross-Origin-Opener-Policy: same-origin</code> and <code>Cross-Origin-Embedder-Policy: require-corp</code></div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">Cross-origin isolation is the gate for multi-threading — <span class="font-medium">without those headers, threaded filters silently break</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="text-sm font-medium opacity-60 mb-3">vite.config.js</div>

```js
import crossOriginIsolation
  from 'vite-plugin-cross-origin-isolation';

export default {
  plugins: [crossOriginIsolation()],
  build: { target: 'esnext' },
  optimizeDeps: { exclude: ['@kitware/vtk-wasm'] },
};
```

<div class="flex flex-col gap-4 mt-6">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔌</div>
  <div><span class="font-medium">vite-plugin-cross-origin-isolation</span> — injects the COOP/COEP headers for you in dev and preview</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">CORS on the tarball URL</span> — <code>createNamespace(url)</code> fetches cross-origin, so the CDN must send CORS headers</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚀</div>
  <div><span class="font-medium">jsDelivr over GitLab</span> — Kitware's GitLab direct URL is slow in Asia; jsDelivr's multi-CDN edge cache is both CORS-enabled and faster</div>
</div>

</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Minimal Sample: Sphere Rendering

<div class="text-lg opacity-80 mt-1">Four VTK objects from geometry to pixels — the smallest complete pipeline</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Pipeline</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">1</div>
  <div><span class="font-medium">vtkSphereSource</span> — generates sphere geometry as <code>vtkPolyData</code></div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">2</div>
  <div><span class="font-medium">vtkPolyDataMapper</span> — maps polygonal data to graphics primitives</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">3</div>
  <div><span class="font-medium">vtkActor</span> — holds the sphere's position, properties, and mapper</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">4</div>
  <div><span class="font-medium">vtkRenderer</span> — renders the actor into the viewport</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">✏️</div>
  <div><span class="font-medium">StackBlitz</span> — edit parameters in the browser and watch the preview update in real time</div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="text-sm font-medium opacity-60 mb-3">sphere.js</div>

```js
createNamespace(WASM_URL).then(async (vtk) => {
  const sphere = vtk.vtkSphereSource.newInstance();
  sphere.setRadius(0.5);
  sphere.setThetaResolution(16);

  const mapper = vtk.vtkPolyDataMapper.newInstance();
  mapper.setInputConnection(sphere.getOutputPort());

  const actor = vtk.vtkActor.newInstance();
  actor.setMapper(mapper);

  const renderer = vtk.vtkRenderer.newInstance();
  renderer.addActor(actor);
  renderer.resetCamera();
});
```

<div class="flex flex-col gap-4 mt-6">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⏳</div>
  <div><span class="font-medium">async/await</span> — <code>createNamespace()</code> returns a Promise; all VTK operations must be awaited</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧵</div>
  <div><span class="font-medium">COOP/COEP</span> — <code>SharedArrayBuffer</code> requires cross-origin isolation headers</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">CORS-enabled CDN</span> — the tarball URL must allow CORS; prefer jsDelivr</div>
</div>

</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Demo: JupyterLite

<div class="text-lg opacity-80 mt-1">A browser-only Jupyter environment — write Python, render 3D meshes, share by URL</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">JupyterLite</span> — a browser-only Jupyter environment; no installation needed, 3D meshes display interactively in notebooks</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐍</div>
  <div><span class="font-medium">pv.Sphere() and pv.read()</span> — pre-prepared notebooks let you start rendering with a single cell</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">▶️</div>
  <div><span class="font-medium">Run a cell, see it render</span> — running a cell launches the 3D viewer right in the notebook</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚀</div>
  <div><span class="font-medium">No local setup</span> — the ideal entry point to experience vtk.wasm rendering quality without installing anything</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📦</div>
  <div><span class="font-medium">Static hosting</span> — deployable to GitHub Pages or any static host, no server required</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">🔗</div>
  <div class="opacity-90">Share by URL — <span class="font-medium">a reproducible analysis environment in one click</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="text-sm font-medium opacity-60 mb-3">intro.ipynb</div>

```python
import pyvista as pv

sphere = pv.Sphere()
sphere.plot()

mesh = pv.read("disk_out.vtp")
mesh.plot()
```

<div class="rounded-lg px-5 py-4 mt-6" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-sm font-medium opacity-60 mb-1">Live demo</div>
  <a href="https://pyvista-wasm.readthedocs.io/en/latest/lite/lab/index.html?path=intro.ipynb" class="text-sm break-all opacity-80 hover:opacity-100">pyvista-wasm.readthedocs.io/en/latest/lite/lab/</a>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Demo: marimo

<div class="text-lg opacity-80 mt-1">A reactive Python notebook — change a slider, the mesh redraws instantly, no rerun button needed</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔄</div>
  <div><span class="font-medium">Reactive notebook</span> — marimo runs entirely in the browser; when a cell value changes, dependent cells auto-rerun</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎨</div>
  <div><span class="font-medium">Real-time mesh updates</span> — slider values trigger instant redraw; change mesh color and viewpoint interactively</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🚫</div>
  <div><span class="font-medium">No rerun button</span> — unlike Jupyter, there is no manual rerun step; the dependency graph drives execution automatically</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔍</div>
  <div><span class="font-medium">Exploratory efficiency</span> — parameter sweeps become effortless, improving the pace of exploratory visualization work</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">🔗</div>
  <div class="opacity-90">Share by URL — <span class="font-medium">a reactive 3D exploration environment in one click</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="rounded-lg px-5 py-4" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-sm font-medium opacity-60 mb-1">Live demo</div>
  <a href="https://marimo.app/?code=JYWwDg9gTgLgBCAhlUEBQaD6mDmBTAOzykRjwBNMB3YGACzgF44AiABgDoBGAZg4DYWaRGDBMEyVBwCCogBQ1y9RixAVgAVxAsAlBjQABEWA4BjPABsLwgM4BPAqbjk8AMziY5OgFxo4-uFBIWARgUygIMGAwDAC4RCpEWlDwyOiOYAIbGEQrORYwOwA3YGzEAFpEm209OKg8GA0oAjg5EDCIqLAAGj0MI1EzS2sXd0921K6fPwCg6HhCkrLqRGr4mzgwIpn-VwiQTeLSnJW1uZC8AA9EcAs8G1iA+sbmuCubsDubbs3t-uMhlY0KMPHJ3rd7j8ttM4p8IDAyFBxFsOAAFCzwxFeHYIe4MZjgz73DjkCBUAgYxCUABGGgIBDs2NhGIRxA4VMoahsdDaeNqAThrKgHG5ZOxGGAY0wBBueGwTGYLGwSEy2BYvjiAKgdOxQA" class="text-sm break-all opacity-80 hover:opacity-100">marimo.app — pyvista-wasm reactive demo</a>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Demo: stlite

<div class="text-lg opacity-80 mt-1">Streamlit in the browser — sliders, select boxes, and widgets driving 3D mesh rendering, no server needed</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🌐</div>
  <div><span class="font-medium">Streamlit in the browser</span> — stlite runs Streamlit entirely client-side; no server, no install, share the app by URL</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🎛️</div>
  <div><span class="font-medium">Declarative widgets</span> — a few lines of slider and selectbox code build a full interactive UI around 3D mesh visualization</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🐰</div>
  <div><span class="font-medium">Stanford Bunny demo</span> — pick from 8 colors via a select box and tune opacity 0–1 with a slider, watching the mesh update live</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🧑‍💼</div>
  <div><span class="font-medium">Built for non-engineers</span> — Streamlit's declarative UI plus pyvista-wasm rendering yields a server-less tool anyone can use</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🆚</div>
  <div><span class="font-medium">Complementary, not competing</span> — JupyterLite and marimo suit exploratory notebook visualization; stlite suits widget-based interactive apps</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">Best for publishing — <span class="font-medium">when you need an interactive app with widgets, stlite is the natural choice</span></div>
</div>

</div>

::right::

<div class="pl-6 pt-6">

<div class="rounded-lg px-5 py-4 mt-6" style="border:1px solid rgba(125,125,125,0.3)">
  <div class="text-sm font-medium opacity-60 mb-1">Live demo</div>
  <a href="https://edit.share.stlite.net/#!CgZhcHAucHkSxQQKBmFwcC5weRK6BAq3BCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfd2FzbSBhcyBwdgpmcm9tIHB5dmlzdGFfd2FzbSBpbXBvcnQgZXhhbXBsZXMKCmNvbG9yID0gc3Quc2VsZWN0Ym94KAogICAgIkNvbG9yIiwKICAgIFsiZ3JheSIsICJ3aGl0ZSIsICJyZWQiLCAiZ3JlZW4iLCAiYmx1ZSIsICJ5ZWxsb3ciLCAiY3lhbiIsICJtYWdlbnRhIl0sCikKCm9wYWNpdHkgPSBzdC5zbGlkZXIoIk9wYWNpdHkiLCBtaW5fdmFsdWU9MC4wLCBtYXhfdmFsdWU9MS4wLCB2YWx1ZT0wLjgsIHN0ZXA9MC4xKQoKcGxvdHRlciA9IHB2LlBsb3R0ZXIoKQoKbWVzaCA9IGV4YW1wbGVzLmRvd25sb2FkX2J1bm55KCkKCnBsb3R0ZXIuYWRkX21lc2gobWVzaCwgY29sb3I9Y29sb3IsIG9wYWNpdHk9b3BhY2l0eSkKCmh0bWwgPSBwbG90dGVyLmdlbmVyYXRlX3N0YW5kYWxvbmVfaHRtbCgpCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoMcHl2aXN0YS13YXNt" class="text-sm break-all opacity-80 hover:opacity-100">share.stlite.net — pyvista-wasm stlite demo</a>
</div>

</div>

---
layout: two-cols-header
class: text-left
---

# Performance: Native vs Wasm

<div class="text-lg opacity-80 mt-1">Initial load costs seconds — but once loaded, ~100K-element meshes run at practical interactive speed</div>

::left::

<div class="pr-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Wasm overhead</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⏳</div>
  <div><span class="font-medium">Initial load</span> — several seconds to 10+ seconds before first render, as the WASM binary streams in from CDN</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📦</div>
  <div><span class="font-medium">Network transfer</span> — ~12–15 MB (gzip) downloaded on first load; cached thereafter by the browser</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">📏</div>
  <div><span class="font-medium">Large-scale constraints</span> — mesh processing at native-desktop scale still has practical limits in the browser</div>
</div>

</div>

::right::

<div class="pl-6 pt-6 flex flex-col gap-5">

<div class="text-sm font-medium opacity-60 mb-1">Where it holds up</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">⚡</div>
  <div><span class="font-medium">Practical interactive speed</span> — once loaded, rotate, pan, and zoom feel responsive, matching the native experience</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">🔢</div>
  <div><span class="font-medium">~100K elements</span> — meshes of this scale run at practical interactive speed, the sweet spot for analysis review</div>
</div>

<div class="flex items-baseline gap-3">
  <div class="opacity-50 w-5">👥</div>
  <div><span class="font-medium">Small-team review</span> — sufficient quality for sharing analysis results within a small team at the current stage</div>
</div>

<div class="flex items-baseline gap-3 mt-2">
  <div class="opacity-50 w-5">➡️</div>
  <div class="opacity-90">PoC confirmed — <span class="font-medium">a dedicated server is not needed to share analysis results</span></div>
</div>

</div>

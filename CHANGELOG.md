# Changelog

## [0.11.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.10.0...pyvista-wasm-v0.11.0) (2026-08-08)


### Features

* add pyvista-wasm CLI slide to PyCon JP 2026 deck ([#488](https://github.com/tkoyama010/pyvista-wasm/issues/488)) ([fbd85b2](https://github.com/tkoyama010/pyvista-wasm/commit/fbd85b29128b2d2f7421facc91652edc755d1c3e))


### Documentation

* add CLI reference documentation mirroring pyvista-js ([#489](https://github.com/tkoyama010/pyvista-wasm/issues/489)) ([bac6394](https://github.com/tkoyama010/pyvista-wasm/commit/bac63942527b34ce9e7119ba1ff4efda6e321f19))

## [0.10.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.9.0...pyvista-wasm-v0.10.0) (2026-08-08)

### Features

- add pre-commit hook for JA/EN slide locale key-parity check ([#478](https://github.com/tkoyama010/pyvista-wasm/issues/478)) ([03cc7c8](https://github.com/tkoyama010/pyvista-wasm/commit/03cc7c8120b5694dc256909a4baf7d4052cd7f46))
- embed inline iframe previews on demo slides ([#419](https://github.com/tkoyama010/pyvista-wasm/issues/419)) ([8285b15](https://github.com/tkoyama010/pyvista-wasm/commit/8285b15f81812fe13bc44c357904540d8127db1a))
- implement README i18n drift-detection per ADR-0007 ([#457](https://github.com/tkoyama010/pyvista-wasm/issues/457)) ([b1cde31](https://github.com/tkoyama010/pyvista-wasm/commit/b1cde31ed41fc794741da6c6f33ff1263ee27d94))

### Bug Fixes

- **deps:** bump fast-uri from 3.1.4 to 3.1.5 in /slides ([#434](https://github.com/tkoyama010/pyvista-wasm/issues/434)) ([bc61543](https://github.com/tkoyama010/pyvista-wasm/commit/bc615438335a8f170e4207d72e1209758f0bd533))
- **deps:** bump GitPython to 3.1.58 ([#451](https://github.com/tkoyama010/pyvista-wasm/issues/451)) ([2f406ef](https://github.com/tkoyama010/pyvista-wasm/commit/2f406ef741e39501a84dada0e5966cd2a0b477b4))
- **deps:** bump hono in /slides to fix Dependabot alert [#86](https://github.com/tkoyama010/pyvista-wasm/issues/86) ([#438](https://github.com/tkoyama010/pyvista-wasm/issues/438)) ([cb31df7](https://github.com/tkoyama010/pyvista-wasm/commit/cb31df7c8d2ad903e7246307d06c5bcb57cda89f))
- **deps:** bump image-size, dompurify, js-yaml, mermaid in slides ([#453](https://github.com/tkoyama010/pyvista-wasm/issues/453)) ([1b84ccb](https://github.com/tkoyama010/pyvista-wasm/commit/1b84ccbffa0858f7f28ba0146c62e9de641bc411))
- **deps:** bump js-yaml to 4.3.1 in root ([#452](https://github.com/tkoyama010/pyvista-wasm/issues/452)) ([7439ba5](https://github.com/tkoyama010/pyvista-wasm/commit/7439ba55fcf2f9cd280d6fe8082c94d3dc16624a))
- **deps:** bump postcss in /slides to fix Dependabot alert [#90](https://github.com/tkoyama010/pyvista-wasm/issues/90) ([#436](https://github.com/tkoyama010/pyvista-wasm/issues/436)) ([0af5bea](https://github.com/tkoyama010/pyvista-wasm/commit/0af5bea17811ca16a0d2fdb46ec1c9a209e3b8dc))
- enable key-parity hook in pre-commit.ci ([#481](https://github.com/tkoyama010/pyvista-wasm/issues/481)) ([070d5c4](https://github.com/tkoyama010/pyvista-wasm/commit/070d5c42a8a1caae27703b273374d3f68d0be276))
- point JupyterLite links to pyvista-wasm readthedocs ([#454](https://github.com/tkoyama010/pyvista-wasm/issues/454)) ([0797636](https://github.com/tkoyama010/pyvista-wasm/commit/0797636c24c33179da6add00df411e32c22703e6))
- remove metavar from typer.Option for 0.27+ compat ([#485](https://github.com/tkoyama010/pyvista-wasm/issues/485)) ([923cce1](https://github.com/tkoyama010/pyvista-wasm/commit/923cce14a29160ae6fecc5fa938e3c154a0fac7d))

### Documentation

- add ADR-0008 deciding how to internationalize the ReadTheDocs documentation ([#440](https://github.com/tkoyama010/pyvista-wasm/issues/440)) ([758bdbb](https://github.com/tkoyama010/pyvista-wasm/commit/758bdbbd829bf65831afbdc3c93f606f23f5803f))
- add CITATION.cff and Citation section to README ([#433](https://github.com/tkoyama010/pyvista-wasm/issues/433)) ([fd868b9](https://github.com/tkoyama010/pyvista-wasm/commit/fd868b9eb4ffa46c95123dc7fe9b2c491354a4fd))
- add mermaid architecture and use case diagrams to the slide deck ([#421](https://github.com/tkoyama010/pyvista-wasm/issues/421)) ([e447acd](https://github.com/tkoyama010/pyvista-wasm/commit/e447acdb4b8eb06cfce25ff648c67256ad4c2a88))
- add PyCon JP 2026 pretalx talk page as reference ([#406](https://github.com/tkoyama010/pyvista-wasm/issues/406)) ([df4704e](https://github.com/tkoyama010/pyvista-wasm/commit/df4704eb873cf4ba3f5c004fb55dfe25b6dbec80))
- add translation contributor guide and configure RTD Japanese project ([#479](https://github.com/tkoyama010/pyvista-wasm/issues/479)) ([a3590f6](https://github.com/tkoyama010/pyvista-wasm/commit/a3590f648458538827791d1b877771a08fd3fc5b))
- apply 1-slide-1-message principle to slide deck ([#396](https://github.com/tkoyama010/pyvista-wasm/issues/396)) ([397643a](https://github.com/tkoyama010/pyvista-wasm/commit/397643ac8ea01f5944531c010bcc274905a0aed7))
- bootstrap Japanese translation catalogs with sphinx-intl ([#471](https://github.com/tkoyama010/pyvista-wasm/issues/471)) ([01a4496](https://github.com/tkoyama010/pyvista-wasm/commit/01a44963278e0a57f408ca61eb257e5cf9eb5e70))
- credit the vtk.wasm article the Slidev deck is inspired by ([#417](https://github.com/tkoyama010/pyvista-wasm/issues/417)) ([e0d9457](https://github.com/tkoyama010/pyvista-wasm/commit/e0d945795cd768f35bc1ee64d49a454dd80aac86))
- define title/subtitle guideline and align slide deck subtitles ([#402](https://github.com/tkoyama010/pyvista-wasm/issues/402)) ([6814d3d](https://github.com/tkoyama010/pyvista-wasm/commit/6814d3dc74e6d369010eca1832132ccb28ed550b))
- document ja.yml as authoritative locale for slide structure ([#482](https://github.com/tkoyama010/pyvista-wasm/issues/482)) ([e15f5e4](https://github.com/tkoyama010/pyvista-wasm/commit/e15f5e4cdbdaf7abe501222a43954867a8d4b6be))
- generate .pot templates from documentation source ([#470](https://github.com/tkoyama010/pyvista-wasm/issues/470)) ([45c3453](https://github.com/tkoyama010/pyvista-wasm/commit/45c34539b3452c306e45607e9e9510bd24d8c87d))
- translate Japanese .po files for ja locale ([#472](https://github.com/tkoyama010/pyvista-wasm/issues/472)) ([80954d8](https://github.com/tkoyama010/pyvista-wasm/commit/80954d8f51918fc26ae09c6b1cd19846e0a372d9))
- write ADR-0004 deciding to adopt the "1 slide, 1 message" principle for the slide deck ([#392](https://github.com/tkoyama010/pyvista-wasm/issues/392)) ([db87294](https://github.com/tkoyama010/pyvista-wasm/commit/db87294000f381019a625c388431168dc0b89b62))
- write ADR-0005 deciding how to verify AGENTS.md quality in CI ([#399](https://github.com/tkoyama010/pyvista-wasm/issues/399)) ([b33479f](https://github.com/tkoyama010/pyvista-wasm/commit/b33479f282b2edfec92d9270963aa258bf661674))
- write ADR-0006 deciding how to keep slide locale files in sync ([#447](https://github.com/tkoyama010/pyvista-wasm/issues/447)) ([d399b38](https://github.com/tkoyama010/pyvista-wasm/commit/d399b384963750a78d2bd687a69ed384e73e0992))
- write ADR-0007 for README i18n and sync strategy ([#446](https://github.com/tkoyama010/pyvista-wasm/issues/446)) ([c5cdcf1](https://github.com/tkoyama010/pyvista-wasm/commit/c5cdcf1f520cef5a9b16313d887bc501dbb31e2f))

## [0.9.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.8.0...pyvista-wasm-v0.9.0) (2026-07-31)

### Features

- add user-story-format issue template ([#272](https://github.com/tkoyama010/pyvista-wasm/issues/272)) ([8f7ec2d](https://github.com/tkoyama010/pyvista-wasm/commit/8f7ec2d3911aa642ade5785258a692cf990474ca))
- internationalize Slidev deck with slidev-addon-i18nb (JA/EN) ([#390](https://github.com/tkoyama010/pyvista-wasm/issues/390)) ([661c9bc](https://github.com/tkoyama010/pyvista-wasm/commit/661c9bce52578a178676e7133ba9fb64bc2235de))

### Bug Fixes

- bump GitPython to 3.1.55 in the lockfile ([#349](https://github.com/tkoyama010/pyvista-wasm/issues/349)) ([47ca090](https://github.com/tkoyama010/pyvista-wasm/commit/47ca09073d0f016a9132372369e99dcff9edd9ef))
- cap ruff below 0.16.0 in the tox lint env ([#346](https://github.com/tkoyama010/pyvista-wasm/issues/346)) ([72420f8](https://github.com/tkoyama010/pyvista-wasm/commit/72420f8463422df167d1266fc3b582211523ad9b))
- **deps:** override pymdown-extensions to >=11.0.0 to resolve GHSA-9xwg-3r6f-jcx2 ([#358](https://github.com/tkoyama010/pyvista-wasm/issues/358)) ([71b8262](https://github.com/tkoyama010/pyvista-wasm/commit/71b826276b4002a8f9d9cbafcbfce9ef416b1140))
- **deps:** pin fast-uri to 3.1.4 to resolve GHSA-v2hh-gcrm-f6hx ([#344](https://github.com/tkoyama010/pyvista-wasm/issues/344)) ([105a841](https://github.com/tkoyama010/pyvista-wasm/commit/105a841ba71e6509976815c8f81da552762a63a1))
- force dompurify to a patched version in slides deck ([#325](https://github.com/tkoyama010/pyvista-wasm/issues/325)) ([73c4b96](https://github.com/tkoyama010/pyvista-wasm/commit/73c4b961357470bca035b774bb4801b15af870bd))
- resolve remaining Dependabot security alerts ([#328](https://github.com/tkoyama010/pyvista-wasm/issues/328)) ([1e33c11](https://github.com/tkoyama010/pyvista-wasm/commit/1e33c115d4c2a70153449fc752e1edb2e7d775e7))
- show landing page at GitHub Pages root instead of redirecting to ReadTheDocs ([#375](https://github.com/tkoyama010/pyvista-wasm/issues/375)) ([155a51b](https://github.com/tkoyama010/pyvista-wasm/commit/155a51b403020eb6839d196c756670909129e847))

### Reverts

- "fix: show landing page at GitHub Pages root instead of redirecting to ReadTheDocs" ([#377](https://github.com/tkoyama010/pyvista-wasm/issues/377)) ([a1ecb7b](https://github.com/tkoyama010/pyvista-wasm/commit/a1ecb7b4d0ab2e6a3391228ca7f49b5f5bb24b16))

### Documentation

- add presentation link to README ([#376](https://github.com/tkoyama010/pyvista-wasm/issues/376)) ([c380c44](https://github.com/tkoyama010/pyvista-wasm/commit/c380c441a4e61f097d2865388fd6746f354967b7))
- add PyCon JP 2026 "Architecture: SSR vs Wasm" slide ([#299](https://github.com/tkoyama010/pyvista-wasm/issues/299)) ([#350](https://github.com/tkoyama010/pyvista-wasm/issues/350)) ([11f9fb8](https://github.com/tkoyama010/pyvista-wasm/commit/11f9fb8834bd91b563cce572b0888c13352210bd))
- add PyCon JP 2026 "Build & distribution mechanism" slide ([#355](https://github.com/tkoyama010/pyvista-wasm/issues/355)) ([731a8c9](https://github.com/tkoyama010/pyvista-wasm/commit/731a8c986f03f700312423880d75f7a3aae5153d))
- add PyCon JP 2026 "Capabilities & current limitations" slide ([#354](https://github.com/tkoyama010/pyvista-wasm/issues/354)) ([e67566e](https://github.com/tkoyama010/pyvista-wasm/commit/e67566eb63d27fb2f4f2bb5327714de904b62235))
- add PyCon JP 2026 "Demo: JupyterLite" slide ([#364](https://github.com/tkoyama010/pyvista-wasm/issues/364)) ([618eaa4](https://github.com/tkoyama010/pyvista-wasm/commit/618eaa401d93d29ba795080e3d37771bd17071df))
- add PyCon JP 2026 "Demo: marimo" slide ([#365](https://github.com/tkoyama010/pyvista-wasm/issues/365)) ([a4d00e2](https://github.com/tkoyama010/pyvista-wasm/commit/a4d00e22aee5203d932af9d95a92d74e059cefbe))
- add PyCon JP 2026 "Demo: stlite" slide ([#366](https://github.com/tkoyama010/pyvista-wasm/issues/366)) ([c2259e5](https://github.com/tkoyama010/pyvista-wasm/commit/c2259e5a319417e1e2d6bfaf4e8ad7bb32dd0667))
- add PyCon JP 2026 "Development & CI challenges" slide ([#362](https://github.com/tkoyama010/pyvista-wasm/issues/362)) ([6f442f8](https://github.com/tkoyama010/pyvista-wasm/commit/6f442f85a59105d94ebeaf226e9da6784a144cb3))
- add PyCon JP 2026 "Minimal sample: sphere rendering" slide ([#363](https://github.com/tkoyama010/pyvista-wasm/issues/363)) ([1ef43f2](https://github.com/tkoyama010/pyvista-wasm/commit/1ef43f27656bd98ff6490d22ec232ad7016e904c))
- add PyCon JP 2026 "Performance: Native vs Wasm" slide ([#367](https://github.com/tkoyama010/pyvista-wasm/issues/367)) ([781183d](https://github.com/tkoyama010/pyvista-wasm/commit/781183dab6e5eb9ae1d54d7d60b034ecc6ec3381))
- add PyCon JP 2026 "Pyodide + PyVista integration" slide ([#357](https://github.com/tkoyama010/pyvista-wasm/issues/357)) ([6a66020](https://github.com/tkoyama010/pyvista-wasm/commit/6a660208ccf052242a33809756f43aea6a3ffbeb))
- add PyCon JP 2026 "The problem" slide ([#297](https://github.com/tkoyama010/pyvista-wasm/issues/297)) ([#341](https://github.com/tkoyama010/pyvista-wasm/issues/341)) ([7010d64](https://github.com/tkoyama010/pyvista-wasm/commit/7010d647b60f5b31dee57191be7e165091bbcc6b))
- add PyCon JP 2026 "VTK Emscripten build pipeline" slide ([#356](https://github.com/tkoyama010/pyvista-wasm/issues/356)) ([43e9d79](https://github.com/tkoyama010/pyvista-wasm/commit/43e9d795cd104f570c78b6dd5feb17472b1d33f3))
- add PyCon JP 2026 "Wasm build history & current status" slide ([#353](https://github.com/tkoyama010/pyvista-wasm/issues/353)) ([c9650d7](https://github.com/tkoyama010/pyvista-wasm/commit/c9650d760c2116d112765be884365b5bdfdbb06d))
- add PyCon JP 2026 "WASM constraints & workarounds" slide ([#368](https://github.com/tkoyama010/pyvista-wasm/issues/368)) ([f089522](https://github.com/tkoyama010/pyvista-wasm/commit/f089522f5ea429f342fe904a5aa13aafcb84b158))
- add PyCon JP 2026 "WebGL/WebGPU rendering integration" slide ([#359](https://github.com/tkoyama010/pyvista-wasm/issues/359)) ([72de4e5](https://github.com/tkoyama010/pyvista-wasm/commit/72de4e5ace6f5272ea3d960fab48af2f5729b7fd))
- add PyCon JP 2026 "What is PyVista?" slide ([#330](https://github.com/tkoyama010/pyvista-wasm/issues/330)) ([0343d81](https://github.com/tkoyama010/pyvista-wasm/commit/0343d81fa3b576a38e23e72e2692d4f210f7b271))
- add PyCon JP 2026 "What is vtk.wasm?" slide ([#300](https://github.com/tkoyama010/pyvista-wasm/issues/300)) ([#351](https://github.com/tkoyama010/pyvista-wasm/issues/351)) ([854b542](https://github.com/tkoyama010/pyvista-wasm/commit/854b542f4c6cc3c0ae757a2a43e693151e6a09e0))
- add PyCon JP 2026 "Why WASM?" slide ([#298](https://github.com/tkoyama010/pyvista-wasm/issues/298)) ([#348](https://github.com/tkoyama010/pyvista-wasm/issues/348)) ([9870cc7](https://github.com/tkoyama010/pyvista-wasm/commit/9870cc7009a00d56d4bdd3623bc95d0289be1ddc))
- add PyCon JP 2026 agenda and speaker slide ([#322](https://github.com/tkoyama010/pyvista-wasm/issues/322)) ([f785a47](https://github.com/tkoyama010/pyvista-wasm/commit/f785a4760509b4873a362aff5c134a41a44380a7))
- add PyCon JP 2026 title slide ([#317](https://github.com/tkoyama010/pyvista-wasm/issues/317)) ([ff3a056](https://github.com/tkoyama010/pyvista-wasm/commit/ff3a056ddb8a69e59088f374d744319b4a1cdeb6))
- add slide 21 — Suitable & unsuitable use cases ([#371](https://github.com/tkoyama010/pyvista-wasm/issues/371)) ([61049f4](https://github.com/tkoyama010/pyvista-wasm/commit/61049f40b97cb6a477dec43ec0dce1ef1bedcfc1))
- add slide 22 — Future roadmap ([#372](https://github.com/tkoyama010/pyvista-wasm/issues/372)) ([0cc1cbe](https://github.com/tkoyama010/pyvista-wasm/commit/0cc1cbe216d31817b6f4eef4a67897e5c21dca21))
- add slide 23 — Call to action & Q&A ([#373](https://github.com/tkoyama010/pyvista-wasm/issues/373)) ([3e764c7](https://github.com/tkoyama010/pyvista-wasm/commit/3e764c7f68c060502059ec8399985850d60e3f6f))
- adopt MADR 4.0.0 for architectural decision records ([#289](https://github.com/tkoyama010/pyvista-wasm/issues/289)) ([43619c8](https://github.com/tkoyama010/pyvista-wasm/commit/43619c8f6c2ab39f56aaa963c6fcfcbf6eec69cd))
- decide slide preview and deployment strategy for GitHub Pages ([#319](https://github.com/tkoyama010/pyvista-wasm/issues/319)) ([2278d1d](https://github.com/tkoyama010/pyvista-wasm/commit/2278d1d68766dd178dcc26536dd678fdd759f83a))
- select Slidev for PyCon JP 2026 talk slides ([#291](https://github.com/tkoyama010/pyvista-wasm/issues/291)) ([40d19d7](https://github.com/tkoyama010/pyvista-wasm/commit/40d19d759037d28f92c71b35238d1ef59dee8eea))
- write ADR-0003 deciding how to internationalize the Slidev deck (JA/EN) ([#387](https://github.com/tkoyama010/pyvista-wasm/issues/387)) ([e0ff150](https://github.com/tkoyama010/pyvista-wasm/commit/e0ff150bbb940176f90b9e6fd44bab126d407499))

### Continuous Integration

- implement slide preview and deployment strategy for GitHub Pages ([#321](https://github.com/tkoyama010/pyvista-wasm/issues/321)) ([969ae36](https://github.com/tkoyama010/pyvista-wasm/commit/969ae36d1ae56535983b5b3270a63688c970d83e))

## [0.8.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.7.0...pyvista-wasm-v0.8.0) (2026-06-27)

### Features

- add shfmt to pre-commit for shell script formatting ([#175](https://github.com/tkoyama010/pyvista-wasm/issues/175)) ([0e29708](https://github.com/tkoyama010/pyvista-wasm/commit/0e297087c1947b826aab57181cf5ce4333f1fe15))
- replace generate_standalone_html() iframe with plotter.show() in marimo demo ([#171](https://github.com/tkoyama010/pyvista-wasm/issues/171)) ([399642f](https://github.com/tkoyama010/pyvista-wasm/commit/399642fc012b720179ae14b166aed20346755e3c))

### Bug Fixes

- **deps:** upgrade vulnerable dependencies for Dependabot alerts ([#245](https://github.com/tkoyama010/pyvista-wasm/issues/245)) ([b08a9df](https://github.com/tkoyama010/pyvista-wasm/commit/b08a9df80e2756dcad23c7cc431f627e255073e5))

## [0.7.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.6.0...pyvista-wasm-v0.7.0) (2026-05-02)

### Features

- add marimo preview GIF capture workflow and CLI command ([#144](https://github.com/tkoyama010/pyvista-wasm/issues/144)) ([8eeb2d4](https://github.com/tkoyama010/pyvista-wasm/commit/8eeb2d4c44833fd88e63beb247184c4f1e6f4201))
- support plotter.show() for automatic rendering in marimo ([#169](https://github.com/tkoyama010/pyvista-wasm/issues/169)) ([30d5a22](https://github.com/tkoyama010/pyvista-wasm/commit/30d5a2212cc0d6de6be17e2e89109d8dfe1594e5))

### Bug Fixes

- always normalize screenshot channels when creating GIF ([#148](https://github.com/tkoyama010/pyvista-wasm/issues/148)) ([1d6e8d8](https://github.com/tkoyama010/pyvista-wasm/commit/1d6e8d838bae3bc0be7ca0e94be2bf90ef8a8288))
- bump gitpython to 3.1.49 to resolve security vulnerability GHSA-rpm5-65cw-6hj4 ([#166](https://github.com/tkoyama010/pyvista-wasm/issues/166)) ([7a7d94b](https://github.com/tkoyama010/pyvista-wasm/commit/7a7d94b5351ffd6c7d02c3abee81afaa27b4ef61))
- **deps:** upgrade pygments to v2.20.0 to fix CVE-2026-4539 ([#167](https://github.com/tkoyama010/pyvista-wasm/issues/167)) ([2c4a2ea](https://github.com/tkoyama010/pyvista-wasm/commit/2c4a2eaf4ff153be5805ecfb0e1e5cbc242e4e8c))
- normalize screenshot sizes before creating GIF ([#146](https://github.com/tkoyama010/pyvista-wasm/issues/146)) ([c64db0a](https://github.com/tkoyama010/pyvista-wasm/commit/c64db0a8652a717a0903e03905d556aef77d36f1))
- resolve npm audit vulnerabilities ([#165](https://github.com/tkoyama010/pyvista-wasm/issues/165)) ([0f8f8fb](https://github.com/tkoyama010/pyvista-wasm/commit/0f8f8fb35588434c59aef45f4ab93ce13fde86b5))

### Documentation

- add AGENTS.md and CLAUDE.md for AI coding agents ([#142](https://github.com/tkoyama010/pyvista-wasm/issues/142)) ([46e1645](https://github.com/tkoyama010/pyvista-wasm/commit/46e164574c9f07efe497bf8df639e5c2d210bcea))
- add issue template instructions to AGENTS.md ([#153](https://github.com/tkoyama010/pyvista-wasm/issues/153)) ([f061ab5](https://github.com/tkoyama010/pyvista-wasm/commit/f061ab5e1d5f26fa26b10d98af692fbf017fdff4))
- add project goal to AGENTS.md ([#150](https://github.com/tkoyama010/pyvista-wasm/issues/150)) ([0d78779](https://github.com/tkoyama010/pyvista-wasm/commit/0d7877966928ad5a95c4713b3e29db9b6cdcc708))
- add test conventions to AGENTS.md ([#149](https://github.com/tkoyama010/pyvista-wasm/issues/149)) ([feb0e1e](https://github.com/tkoyama010/pyvista-wasm/commit/feb0e1eb0c7213d0ff04c712ea9d6a313a9d34d8))
- align PR template with why-focused writing guidelines ([#152](https://github.com/tkoyama010/pyvista-wasm/issues/152)) ([f9cb7c6](https://github.com/tkoyama010/pyvista-wasm/commit/f9cb7c68bd19bd53b71c62f48de34f879d6caa8b))
- clarify PR instructions for commit message content ([#145](https://github.com/tkoyama010/pyvista-wasm/issues/145)) ([6dac1dd](https://github.com/tkoyama010/pyvista-wasm/commit/6dac1dd9f9c4eda3e05c0c52d007098535bb4f3e))
- instruct agents to monitor CI after creating a PR ([#147](https://github.com/tkoyama010/pyvista-wasm/issues/147)) ([6fad018](https://github.com/tkoyama010/pyvista-wasm/commit/6fad018e357ed35e4c799c7edab70179f4d4d6ac))

## [0.6.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.5.1...pyvista-wasm-v0.6.0) (2026-04-16)

### Features

- add marimo badge and notebook for browser-based demo ([#115](https://github.com/tkoyama010/pyvista-wasm/issues/115)) ([d215fe2](https://github.com/tkoyama010/pyvista-wasm/commit/d215fe2730b38bf4cc804904b83d4f418a8d65a7))
- add marimo support like jupyterlite ([#120](https://github.com/tkoyama010/pyvista-wasm/issues/120)) ([93a12e9](https://github.com/tkoyama010/pyvista-wasm/commit/93a12e908f62faee4d6ea0ddd27e39ce881deab5))

### Bug Fixes

- add pytest-cov to dev and test dependencies ([#121](https://github.com/tkoyama010/pyvista-wasm/issues/121)) ([e89ffd1](https://github.com/tkoyama010/pyvista-wasm/commit/e89ffd1b9eb4c2b318a5b097e8ba0ccca79f0479))

## [0.5.1](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.5.0...pyvista-wasm-v0.5.1) (2026-04-13)

### Bug Fixes

- escape WASM_CONFIG JSON in standalone.html data-config attribute ([#113](https://github.com/tkoyama010/pyvista-wasm/issues/113)) ([1a3e5b4](https://github.com/tkoyama010/pyvista-wasm/commit/1a3e5b4a612bfce45963073fa326be0819c31bea))

## [0.5.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.4.0...pyvista-wasm-v0.5.0) (2026-04-12)

### Features

- add VTK.wasm configuration options (rendering backend and execution mode) ([#108](https://github.com/tkoyama010/pyvista-wasm/issues/108)) ([d5a3347](https://github.com/tkoyama010/pyvista-wasm/commit/d5a334773c462e95b3aaf3eaecd06087f090f2a8))
- mirror VTK.wasm binary to npm and serve via jsDelivr CDN ([#110](https://github.com/tkoyama010/pyvista-wasm/issues/110)) ([2c85e37](https://github.com/tkoyama010/pyvista-wasm/commit/2c85e379095f4017bb8333712fa49d7c2f6a74b4))

## [0.4.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.3.0...pyvista-wasm-v0.4.0) (2026-04-12)

### Features

- add loading overlay components for 3D rendering UX ([#107](https://github.com/tkoyama010/pyvista-wasm/issues/107)) ([a312ffd](https://github.com/tkoyama010/pyvista-wasm/commit/a312ffd40828ebba1af6163effdbbfe817d4cae8))

### Bug Fixes

- update preview workflow to use ReadTheDocs JupyterLite URL ([#90](https://github.com/tkoyama010/pyvista-wasm/issues/90)) ([fc695bb](https://github.com/tkoyama010/pyvista-wasm/commit/fc695bb823fa9fdc0c5a489c46c7d1f419a96d4b))
- **workflow:** remove --system flag from uv run to fix nightly tests ([#88](https://github.com/tkoyama010/pyvista-wasm/issues/88)) ([42526e5](https://github.com/tkoyama010/pyvista-wasm/commit/42526e5da211afa68fc497935a0ef090fe717fb2))

## [0.3.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.2.0...pyvista-wasm-v0.3.0) (2026-04-05)

### Features

- add __main__.py to enable python -m pyvista_wasm ([#80](https://github.com/tkoyama010/pyvista-wasm/issues/80)) ([d3f4346](https://github.com/tkoyama010/pyvista-wasm/commit/d3f4346cba0cdc32f20ec70fc255d5e09552ae82))
- add intro.ipynb notebook and update ReadTheDocs config for JupyterLite ([#83](https://github.com/tkoyama010/pyvista-wasm/issues/83)) ([291f90e](https://github.com/tkoyama010/pyvista-wasm/commit/291f90eba1dc81560615f12735d6d26b779168dd))
- Update Try Lite Now link to ReadTheDocs and remove JupyterLite deploy action ([#82](https://github.com/tkoyama010/pyvista-wasm/issues/82)) ([0baad4c](https://github.com/tkoyama010/pyvista-wasm/commit/0baad4cb91b420141149b1be159edab677903bf1))

### Bug Fixes

- **workflow:** add site verification step and increase timeout for preview capture ([#81](https://github.com/tkoyama010/pyvista-wasm/issues/81)) ([3d56501](https://github.com/tkoyama010/pyvista-wasm/commit/3d5650186de66ebc63d47529e5919d35895aa93d))

### Documentation

- add SECURITY.md ([#73](https://github.com/tkoyama010/pyvista-wasm/issues/73)) ([cce04b1](https://github.com/tkoyama010/pyvista-wasm/commit/cce04b18ccdc5677a932d3df5e7ea8f4abef4720))
- update stlite badge URL to new share.stlite.net domain ([#55](https://github.com/tkoyama010/pyvista-wasm/issues/55)) ([d55d33d](https://github.com/tkoyama010/pyvista-wasm/commit/d55d33d89f41fe69c8676682babb17136176c07a))

## [0.2.0](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.1.1...pyvista-wasm-v0.2.0) (2026-03-31)

### Features

- add "Try it with JupyterLite!" button to Sphinx docs ([#40](https://github.com/tkoyama010/pyvista-wasm/issues/40)) ([39de62b](https://github.com/tkoyama010/pyvista-wasm/commit/39de62ba611133660f5c78fd3430deb63f30fef9))
- add preview table and JupyterLite deployment ([#41](https://github.com/tkoyama010/pyvista-wasm/issues/41)) ([ed5d76c](https://github.com/tkoyama010/pyvista-wasm/commit/ed5d76c206ee5283db54c76a1e289297a2b91877))

### Bug Fixes

- resolve mypy type errors in mesh.py ([#48](https://github.com/tkoyama010/pyvista-wasm/issues/48)) ([f01c4a8](https://github.com/tkoyama010/pyvista-wasm/commit/f01c4a84dca1ef1c935aa545b3f8b2370514fc4f))

### Documentation

- add stlite badge to README ([#34](https://github.com/tkoyama010/pyvista-wasm/issues/34)) ([f68169a](https://github.com/tkoyama010/pyvista-wasm/commit/f68169a3ceda6cebb00dfedab2bfeb6306acd90d))

## [0.1.1](https://github.com/tkoyama010/pyvista-wasm/compare/pyvista-wasm-v0.1.0...pyvista-wasm-v0.1.1) (2026-03-25)

### Bug Fixes

- render mesh PolyData correctly in VTK.wasm ([#25](https://github.com/tkoyama010/pyvista-wasm/issues/25)) ([14a0ca3](https://github.com/tkoyama010/pyvista-wasm/commit/14a0ca391001a7c34d4a8a8c61165e7319da1c5a))

### Documentation

- add docs folder to satisfy PY004 requirement ([#27](https://github.com/tkoyama010/pyvista-wasm/issues/27)) ([9906767](https://github.com/tkoyama010/pyvista-wasm/commit/99067674fb17fb60b812fb8607ef1bfad26050ef))
- add PyPI badge to Install section ([#24](https://github.com/tkoyama010/pyvista-wasm/issues/24)) ([8e28c82](https://github.com/tkoyama010/pyvista-wasm/commit/8e28c82226ac902a26782744d7b52d8519792fd6))

### Continuous Integration

- add concurrency group to auto-cancel redundant runs (GH102) ([#28](https://github.com/tkoyama010/pyvista-wasm/issues/28)) ([3e82392](https://github.com/tkoyama010/pyvista-wasm/commit/3e82392622e19eca6075a9f515258f1f8000bb59))
- add Renovate for automated VTK.wasm CDN version updates ([#21](https://github.com/tkoyama010/pyvista-wasm/issues/21)) ([a0cec82](https://github.com/tkoyama010/pyvista-wasm/commit/a0cec8244ad6d62cb48db760fd031d920b44f75f))
- add workflow to update uv.lock on release-please PRs ([#30](https://github.com/tkoyama010/pyvista-wasm/issues/30)) ([39af99b](https://github.com/tkoyama010/pyvista-wasm/commit/39af99bcf4fefd8f0b5ba76db303b2604f4da61f))

## 0.1.0 (2026-03-25)

### Documentation

- add contributing guide ([#14](https://github.com/tkoyama010/pyvista-wasm/issues/14)) ([37737f7](https://github.com/tkoyama010/pyvista-wasm/commit/37737f7764eb7e920d201db45b138ba358404dce)), closes [#8](https://github.com/tkoyama010/pyvista-wasm/issues/8)
- add GitHub Sponsors funding configuration ([#22](https://github.com/tkoyama010/pyvista-wasm/issues/22)) ([a4f2fbb](https://github.com/tkoyama010/pyvista-wasm/commit/a4f2fbbb5aaae7c29cc75f62e84508879de8136c))
- add issue templates for bug reports, features, and documentation ([#12](https://github.com/tkoyama010/pyvista-wasm/issues/12)) ([1eab65d](https://github.com/tkoyama010/pyvista-wasm/commit/1eab65d2c07babbf7de3e41bec42efce4a8a43cc)), closes [#6](https://github.com/tkoyama010/pyvista-wasm/issues/6)
- add pull request template and code of conduct ([#13](https://github.com/tkoyama010/pyvista-wasm/issues/13)) ([853757b](https://github.com/tkoyama010/pyvista-wasm/commit/853757b97f94caaefeb4731a1560c46152253ad4)), closes [#7](https://github.com/tkoyama010/pyvista-wasm/issues/7)

### Continuous Integration

- add Dependabot for GitHub Actions and npm dependency updates ([#20](https://github.com/tkoyama010/pyvista-wasm/issues/20)) ([63d43ea](https://github.com/tkoyama010/pyvista-wasm/commit/63d43ea6970290f427435fa9429db69186cdddba))
- add nightly tests workflow (SPEC-0004) ([#11](https://github.com/tkoyama010/pyvista-wasm/issues/11)) ([186ab1e](https://github.com/tkoyama010/pyvista-wasm/commit/186ab1e163e11eabdb3190996b7dccbf2479fe29)), closes [#5](https://github.com/tkoyama010/pyvista-wasm/issues/5)
- add release-please workflow for automated releases ([#10](https://github.com/tkoyama010/pyvista-wasm/issues/10)) ([9fb1600](https://github.com/tkoyama010/pyvista-wasm/commit/9fb160083b0ac21f2d4e53c08fcb25bda30b8718))

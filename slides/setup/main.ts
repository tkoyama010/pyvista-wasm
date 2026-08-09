import { defineAppSetup } from '@slidev/types'

// ponytail: Slidev notes go through markdown-it, not Vue, so {{ $t() }} in
// notes never resolves. This setup runs after the i18n addon's setup (the
// addon root is loaded after the user root), so app.config.globalProperties.$t
// is available. We scan .slidev-note text nodes for $t("key") patterns and
// replace them with the translated string. A 500ms poll catches locale
// switches (localStorage in the same tab doesn't fire storage events).

function processNotes(t: (key: string) => string): void {
  for (const note of document.querySelectorAll('.slidev-note')) {
    const walker = document.createTreeWalker(note, NodeFilter.SHOW_TEXT)
    const targets: Text[] = []
    let node: Node | null
    while ((node = walker.nextNode())) targets.push(node as Text)
    for (const tn of targets) {
      const text = tn.textContent
      if (!text || !text.includes('$t(')) continue
      const replaced = text.replace(/\$t\("([^"]+)"\)/g, (_, k: string) => t(k))
      if (replaced !== text) tn.textContent = replaced
    }
  }
}

export default defineAppSetup(({ app }) => {
  if (typeof window === 'undefined') return

  const t = app.config.globalProperties.$t as (key: string) => string
  if (typeof t !== 'function') return

  let lastLocale = localStorage.getItem('slidev-lang')
  const checkLocale = (): void => {
    const current = localStorage.getItem('slidev-lang')
    if (current !== lastLocale) {
      lastLocale = current
      processNotes(t)
    }
  }

  setTimeout(() => {
    processNotes(t)
    new MutationObserver(() => processNotes(t)).observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    })
    setInterval(checkLocale, 500)
  }, 1000)
})

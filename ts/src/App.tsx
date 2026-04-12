import React from "react";
import { createRoot } from "react-dom/client";
import { PyvistaCanvas } from "./components/PyvistaCanvas";

/**
 * Root application component for the pyvista-wasm interactive viewer.
 *
 * Renders a full-viewport {@link PyvistaCanvas} that initialises VTK.wasm,
 * shows a loading overlay while the 3D scene is built, and gracefully
 * handles errors.
 */
export function App(): React.JSX.Element {
  return <PyvistaCanvas width="100%" height="100%" />;
}

/* ── Mount into the DOM ───────────────────────────────────────────── */
const rootElement: HTMLElement | null = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(<App />);
}

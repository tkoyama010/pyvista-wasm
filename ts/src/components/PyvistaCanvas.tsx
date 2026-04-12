import React, { useEffect, useRef, useState } from "react";
import { LoadingOverlay } from "./LoadingOverlay";

/**
 * Scene data passed from the Python side (JSON).
 * Only the fields needed for initialization are typed here;
 * the full `SceneData` schema lives in `vtk.d.ts`.
 */
interface SceneData {
  containerId: string;
  background: [number, number, number];
  [key: string]: unknown;
}

interface PyvistaCanvasProps {
  /** Inline JSON scene data — when omitted, read from `#scene-data`. */
  sceneData?: SceneData;
  /** Width CSS value. @default "100%" */
  width?: string;
  /** Height CSS value. @default "100%" */
  height?: string;
}

/**
 * React wrapper around the pyvista-wasm VTK.wasm renderer.
 *
 * It manages three lifecycle phases:
 *  1. **Loading** – VTK.wasm namespace is created.
 *  2. **Rendering** – the scene (actors, lights, camera) is built.
 *  3. **Ready** – the canvas is interactive.
 *
 * Errors in any phase are caught and surfaced via {@link LoadingOverlay}.
 */
export function PyvistaCanvas({
  sceneData: sceneDataProp,
  width = "100%",
  height = "100%",
}: PyvistaCanvasProps): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isRendering, setIsRendering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    let cancelled = false;
    const containerEl = container;

    async function init(): Promise<void> {
      try {
        /* ── Phase 1: create the VTK.wasm namespace ───────────── */
        setIsLoading(true);
        setError(null);

        // eslint-disable-next-line @typescript-eslint/no-explicit-any -- global APIs injected by the host page
        const g = globalThis as any;

        let vtk: any;
        if (typeof g.vtkReady !== "undefined") {
          vtk = await g.vtkReady;
        } else if (typeof g.vtkWASM === "undefined") {
          throw new Error(
            "VTK.wasm runtime not found. Ensure the vtk-wasm UMD script is loaded.",
          );
        } else {
          vtk = await g.vtkWASM.createNamespace();
        }

        if (cancelled) {
          return;
        }

        /* ── Phase 2: build the scene ─────────────────────────── */
        setIsLoading(false);
        setIsRendering(true);

        const sceneData = resolveSceneData(sceneDataProp);

        const canvasId = `${sceneData.containerId}-canvas`;
        const canvas = document.createElement("canvas");
        canvas.id = canvasId;
        const DefaultCanvasWidth = 600;
        const DefaultCanvasHeight = 400;
        canvas.width = containerEl.clientWidth || DefaultCanvasWidth;
        canvas.height = containerEl.clientHeight || DefaultCanvasHeight;
        canvas.style.width = "100%";
        canvas.style.height = "100%";
        canvas.tabIndex = -1;
        canvas.addEventListener("click", () => canvas.focus());
        containerEl.appendChild(canvas);

        const canvasSelector = `#${CSS.escape(canvasId)}`;

        // Delegate heavy scene construction to the existing `buildScene`
        // pipeline exposed by the bundled renderer IIFE.
        // When the IIFE is present it sets `__pvwasmSceneData` /
        // `__pvwasmContainer` and calls `buildScene` itself, so here we
        // replicate a minimal render loop.
        const renderer = vtk.vtkRenderer();
        const bg = sceneData.background;
        renderer.setBackground(bg[0], bg[1], bg[2]);

        const renderWindow = vtk.vtkRenderWindow({ canvasSelector });
        renderWindow.addRenderer(renderer);

        renderer.resetCamera();

        const interactor = vtk.vtkRenderWindowInteractor({
          canvasSelector,
          renderWindow,
        });
        await interactor.interactorStyle.setCurrentStyleToTrackballCamera();

        renderWindow.render();
        await interactor.start();

        if (cancelled) {
          return;
        }

        /* ── Phase 3: done ────────────────────────────────────── */
        setIsRendering(false);
      } catch (err: unknown) {
        if (!cancelled) {
          let msg = "An unknown error occurred.";
          if (err instanceof Error) {
            msg = err.message;
          }
          setError(msg);
          setIsLoading(false);
          setIsRendering(false);
        }
      }
    }

    init().catch(() => {
      /* errors are handled inside init */
    });

    return () => {
      cancelled = true;
    };
  }, [sceneDataProp]);

  return (
    <div
      ref={containerRef}
      style={{
        width,
        height,
        position: "relative",
        minHeight: "400px",
        border: "2px solid #333",
      }}
    >
      <LoadingOverlay
        isLoading={isLoading}
        isRendering={isRendering}
        error={error}
      />
    </div>
  );
}

/**
 * Resolve scene data from props, global variable, or the DOM.
 */
function resolveSceneData(prop?: SceneData): SceneData {
  if (prop) {
    return prop;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- global injected by renderer template
  const g = globalThis as any;
  if (typeof g.__pvwasmSceneData !== "undefined") {
    return g.__pvwasmSceneData as SceneData;
  }

  const el = document.querySelector("#scene-data");
  if (el?.textContent) {
    return JSON.parse(el.textContent) as SceneData;
  }

  const DefaultBackgroundR = 0.2;
  const DefaultBackgroundG = 0.3;
  const DefaultBackgroundB = 0.4;
  return {
    containerId: "pyvista-container",
    background: [
      DefaultBackgroundR,
      DefaultBackgroundG,
      DefaultBackgroundB,
    ] as [number, number, number],
  };
}

import React from "react";

interface LoadingOverlayProps {
  /** Whether the WASM/Pyodide environment is initializing. */
  isLoading: boolean;
  /** Whether the 3D scene is being rendered. */
  isRendering: boolean;
  /** An error message to display, if any. */
  error: string | null;
}

/**
 * Full-screen overlay that communicates initialization, rendering,
 * and error states to the user while the 3D scene is being prepared.
 *
 * Fades out smoothly once both `isLoading` and `isRendering` are false.
 */
export function LoadingOverlay({
  isLoading,
  isRendering,
  error,
}: LoadingOverlayProps): React.JSX.Element | null {
  const visible = isLoading || isRendering || error !== null;

  const message = error
    ? error
    : isLoading
      ? "Initializing WASM Environment…"
      : "Generating 3D Model…";

  return (
    <div
      className={`pv-loading-overlay ${visible ? "pv-loading-visible" : "pv-loading-hidden"}`}
    >
      {error ? (
        <div className="pv-error-container">
          <span className="pv-error-icon" aria-hidden="true">
            ⚠
          </span>
          <p className="pv-error-message">{message}</p>
        </div>
      ) : (
        <div className="pv-spinner-container">
          <div className="pv-spinner" />
          <p className="pv-loading-message">{message}</p>
        </div>
      )}

      <style>{`
        .pv-loading-overlay {
          position: absolute;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(24, 26, 31, 0.88);
          z-index: 100;
          transition: opacity 0.5s ease;
        }
        .pv-loading-visible {
          opacity: 1;
          pointer-events: auto;
        }
        .pv-loading-hidden {
          opacity: 0;
          pointer-events: none;
        }
        .pv-spinner-container,
        .pv-error-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 18px;
        }
        .pv-spinner {
          width: 48px;
          height: 48px;
          border: 4px solid rgba(255, 255, 255, 0.15);
          border-top-color: #58a6ff;
          border-radius: 50%;
          animation: pv-spin 0.8s linear infinite;
        }
        @keyframes pv-spin {
          to { transform: rotate(360deg); }
        }
        .pv-loading-message {
          margin: 0;
          color: #c9d1d9;
          font: 14px / 1.4 -apple-system, BlinkMacSystemFont, "Segoe UI",
            Helvetica, Arial, sans-serif;
        }
        .pv-error-icon {
          font-size: 36px;
          color: #f85149;
        }
        .pv-error-message {
          margin: 0;
          color: #f85149;
          font: 14px / 1.4 -apple-system, BlinkMacSystemFont, "Segoe UI",
            Helvetica, Arial, sans-serif;
          text-align: center;
          max-width: 360px;
        }
      `}</style>
    </div>
  );
}

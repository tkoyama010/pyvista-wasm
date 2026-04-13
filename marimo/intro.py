import marimo

__generated_with = "0.13.6"
app = marimo.App(width="medium")


@app.cell
async def _():
    import micropip

    await micropip.install("pyvista-wasm")
    return (micropip,)


@app.cell
def _(micropip):
    import marimo as mo
    import pyvista_wasm as pv

    return mo, pv


@app.cell
def _(mo, pv):
    import js
    from pyodide.ffi import create_proxy

    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere(), color="red")
    html_content = plotter.generate_standalone_html()

    container_id = "vtk-wasm-container"

    def inject_vtk():
        container = js.document.getElementById(container_id)
        if container is None:
            return
        iframe = js.document.createElement("iframe")
        iframe.srcdoc = html_content
        iframe.style.cssText = "width:600px;height:400px;min-height:400px;border:2px solid #333;"
        iframe.sandbox = "allow-scripts"
        container.innerHTML = ""
        container.appendChild(iframe)

    proxy = create_proxy(inject_vtk)
    js.window.setTimeout(proxy, 500)

    return mo.Html(
        f'<div id="{container_id}" '
        'style="width:600px;height:400px;background:#f0f0f0;'
        'display:flex;align-items:center;justify-content:center;">'
        "<p>Loading VTK.wasm...</p>"
        "</div>",
    )


if __name__ == "__main__":
    app.run()

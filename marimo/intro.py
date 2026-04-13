import marimo

__generated_with = "0.13.6"
app = marimo.App(width="medium")


@app.cell
async def _():
    import micropip

    await micropip.install("pyvista-wasm")
    return (micropip,)


@app.cell
def _():
    import marimo as mo
    import pyvista_wasm as pv
    from pyvista_wasm import examples

    return examples, mo, pv


@app.cell
def _(examples, pv):
    plotter = pv.Plotter()
    mesh = examples.download_bunny()
    plotter.add_mesh(mesh)
    html = plotter.generate_standalone_html()
    return html, mesh, plotter


@app.cell
def _(html, mo):
    mo.Html(html)


if __name__ == "__main__":
    app.run()

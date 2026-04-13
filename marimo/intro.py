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
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere(), color="red")
    html = plotter.generate_standalone_html()
    return mo.Html(html)


if __name__ == "__main__":
    app.run()

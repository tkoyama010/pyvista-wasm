import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
async def _():
    import micropip

    await micropip.install("pyvista-wasm")
    return (micropip,)


@app.cell
def _(micropip):
    import pyvista_wasm as pv
    from pyvista_wasm import examples

    plotter = pv.Plotter()
    mesh = examples.download_bunny()
    plotter.add_mesh(mesh)
    plotter.show()
    return (plotter,)


if __name__ == "__main__":
    app.run()

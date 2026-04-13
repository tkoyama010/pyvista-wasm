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
    import pyvista_wasm as pv

    return (pv,)


@app.cell
def _(pv):
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere(), color="red")
    plotter.show()


if __name__ == "__main__":
    app.run()

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
    from js import URL, Blob, Object

    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere(), color="red")
    html = plotter.generate_standalone_html()
    blob = Blob.new([html], Object.fromEntries([["type", "text/html"]]))
    blob_url = URL.createObjectURL(blob)
    iframe = (
        f'<iframe src="{blob_url}" '
        'style="width:600px;height:400px;min-height:400px;border:2px solid #333;" '
        'sandbox="allow-scripts allow-same-origin"></iframe>'
    )
    return mo.Html(iframe)


if __name__ == "__main__":
    app.run()

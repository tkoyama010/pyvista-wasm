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
    html_content = plotter.generate_standalone_html()

    mo.output.append(mo.Html(
        "<div style='border:4px solid green;padding:15px;"
        "background:#efffef;font-size:18px;'>"
        f"<strong>OK: HTML = {len(html_content)} bytes</strong>"
        "</div>"
    ))


if __name__ == "__main__":
    app.run()

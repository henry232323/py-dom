window.pyodide = await loadPyodide()
await pyodide.loadPackage("micropip")
const micropip = pyodide.pyimport("micropip")
await micropip.install("cssutils")

const files = ["tinyhtml.py", "pydom.py", "app.py"]
for (const file of files) {
    await pyodide.runPythonAsync(`
        from pyodide.http import pyfetch
        response = await pyfetch("${file}")
        with open("${file}", "wb") as f:
            f.write(await response.bytes())
    `)
}

const tinyhtml = pyodide.pyimport("tinyhtml")
window.gen_callback = tinyhtml.gen_callback
window.callbacks = tinyhtml.callbacks

window.app = await pyodide.runPythonAsync(`
    from app import App
    app = App()
    app.render_root()
    app
`)

addEventListener("resize", (event) => {
    app.render_tree()
});
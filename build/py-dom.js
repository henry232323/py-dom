window.pyodide = await loadPyodide()
await pyodide.loadPackage("micropip")
const micropip = pyodide.pyimport("micropip")

const dependencies = [
    "astpretty",
    "cssutils",
    "lark",
    "autopep8",
    "astunparse"
]

for (const dependency of dependencies) {
    await micropip.install(dependency)
}


const local_deps = [
    "tinyhtml.py",
    "pydom.py",
]

const pyx_deps = [
    "pydom_parser/__init__.py",
    "pydom_parser/ast_transformer.py",
    "pydom_parser/import_handler.py",
    "pydom_parser/python_parser.py",
    "pydom_parser/unparse.py",
    "pydom_parser/pyx.lark",
]

await pyodide.runPythonAsync(`
    import os; os.mkdir("pydom_parser")
`)

async function load_file(file) {
    return await pyodide.runPythonAsync(`
        from pyodide.http import pyfetch
        response = await pyfetch("${file}")
        if (not response.ok):
            result = None
        else:
            with open("${file}", "w") as f:
                bytes = await response.bytes()
                text = bytes.decode() + "\\n"
                f.write(text)
                
            result = text
             
        result
`)
}

for (const file of local_deps) {
    await load_file(file)
}

const app_resolvers = [
    "app.py",
    "app.pyx",
]

let resolved = false
let use_pyx = false

for (const file of app_resolvers) {
    const result = await load_file(file)
    if (result) {
        resolved = true
        if (file.endsWith("pyx")) {
            use_pyx = true
        }
        break
    }
}

if (!resolved) {
    throw Error("Missing app!")
}

const tinyhtml = pyodide.pyimport("tinyhtml")
window.gen_callback = tinyhtml.gen_callback
window.callbacks = tinyhtml.callbacks

let main_source = `
from app import App
app = App()
app.render_root()
app
`

if (use_pyx) {
    for (const file of pyx_deps) {
        await load_file(file)
    }
    main_source = `import pydom_parser\n` + main_source
}

window.app = await pyodide.runPythonAsync(main_source)

addEventListener("resize", (event) => {
    app.render_tree()
});
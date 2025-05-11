// docs/js/run_demo.js
export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");

  // 1) Load Pyodide
  status.textContent = "🔄 Loading Python…";
  const py = await window.loadPy();

  // 2) Preload SciPy (needed for gaussian_filter)
  status.textContent = "🔄 Loading SciPy…";
  await py.loadPackage("scipy");

  // 3) Read and prepare the Python source
  status.textContent = "🔄 Fetching script…";
  const src = await (await fetch(`../py/${pyFile}`)).text();
  if (!src) {
    status.textContent = "❌ Python file not found.";
    return;
  }

  // 4) Gather form inputs into args
  const fd = new FormData(document.getElementById("demoForm"));
  const args = { ...defaults };
  for (const [k, v] of fd.entries()) if (v) args[k] = v;

  // 5) Construct wrapper code
  const code = `
import matplotlib.pyplot as plt, base64, io, json
args = json.loads(${JSON.stringify(JSON.stringify(args))})
${src}
buf = io.BytesIO()
plt.savefig(buf, format="png", bbox_inches="tight")
print("__IMG__" + base64.b64encode(buf.getvalue()).decode())
`;

  // 6) Run in Pyodide
  status.textContent = "▶ Running…";
  try {
    const res = await py.runPythonAsync(code);
    const png64 = res.split("__IMG__")[1];
    outDiv.innerHTML = `<img src=\"data:image/png;base64,${png64}\"/>`;
    status.textContent = "✅ Done";
  } catch (err) {
    console.error(err);
    status.textContent = "❌ Error: " + err.message;
  }
}
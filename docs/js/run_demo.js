
/* docs/js/run_demo.js
 * Generic helper: fetch .py, pass JSON args, show the PNG result.
 */
export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");
  outDiv.innerHTML = "";
  status.textContent = "🔄 Loading Python…";

  /* ensure loadPy exists (dynamic‑import if user omitted pyinit tag) */
  if (typeof window.loadPy !== "function") {
    const base = location.pathname.includes("/demos/") ? "../js/" : "js/";
    await import(base + "pyinit.js");
  }

  const py = await window.loadPy().catch(e => {
    status.textContent = "❌ Pyodide failed – see console"; console.error(e);
  });
  if (!py) return;

  /* correct relative path to the .py file */
  const base = location.pathname.includes("/demos/") ? "../py/" : "py/";
  const resp = await fetch(base + pyFile);
  if (!resp.ok) { status.textContent = "❌ Python file not found"; return; }
  const src = await resp.text();

  /* gather form values */
  const fd = new FormData(document.getElementById("demoForm"));
  const args = { ...defaults };
  for (const [k, v] of fd.entries()) if (v !== "") args[k] = v;

  /* wrap script so it *returns* the PNG (not print) */
  const code = `
import matplotlib, base64, io, json
matplotlib.use("Agg")
args = json.loads(${JSON.stringify(JSON.stringify(args))})
${src}
buf = io.BytesIO()
import matplotlib.pyplot as _plt
_plt.savefig(buf, format="png", bbox_inches="tight")
base64.b64encode(buf.getvalue()).decode()
`;

  try {
    status.textContent = "▶️ Running…";
    const png64 = await py.runPythonAsync(code);
    outDiv.innerHTML = '<img src="data:image/png;base64,' + png64 + '"/>';
    status.textContent = "✅ Done";
  } catch (err) {
    status.textContent = "❌ Python error – see console"; console.error(err);
  }
}
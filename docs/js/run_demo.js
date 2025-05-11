/* docs/js/run_demo.js
 * Robust helper that   (1) loads script,   (2) feeds args,   (3) returns a PNG
 */
export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");
  outDiv.innerHTML = "";
  status.textContent = "🔄 Loading Python…";

  /* get (or create) global pyodide */
  const py = await window.loadPy().catch(e => {
    status.textContent = "❌ Pyodide failed – see console";
    console.error(e); return null;
  });
  if (!py) return;

  /* compute correct relative path: on /demos/ pages we need ../py/ */
  const base = location.pathname.includes("/demos/") ? "../py/" : "py/";
  const resp = await fetch(base + pyFile);
  if (!resp.ok) { status.textContent = "❌ Python file not found"; return; }
  const src = await resp.text();

  /* collect inputs */
  const fd = new FormData(document.getElementById("demoForm"));
  const args = {...defaults};
  for (const [k,v] of fd.entries()) if (v !== "") args[k] = v;

  /* wrapper: returns (not prints) the Base‑64 PNG */
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
    status.textContent = "▶ Running…";
    const png64 = await py.runPythonAsync(code);   // <-- return value
    outDiv.innerHTML = '<img src="data:image/png;base64,' + png64 + '"/>';
    status.textContent = "✅ Done";
  } catch (err) {
    status.textContent = "❌ Python error – see console";
    console.error(err);
  }
}
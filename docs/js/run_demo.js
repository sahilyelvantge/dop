/*  Re‑usable helper to run any Python demo with Pyodide
 *  ----------------------------------------------------
 *  <form id="demoForm">   …inputs…   </form>
 *  <button id="runBtn">   runDemo(...)  </button>
 *  <p id="status"></p>
 *  <div id="output"></div>
 */

export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");
  outDiv.innerHTML = "";                     // clear previous figure
  status.textContent = "🔄 Loading Python…";

  /* load or reuse a global Pyodide instance */
  const py = await window.loadPy().catch(e => {
    status.textContent = "❌ Pyodide failed to load – see console";
    console.error(e);
  });
  if (!py) return;

  /* figure out correct relative path:                      *
   * - if the page URL contains /demos/  →  ../py/filename  *
   * - if we are at root (index.html)   →    py/filename    */
  const basePath = location.pathname.includes("/demos/") ? "../py/" : "py/";
  const fullPath = basePath + pyFile;

  let src = "";
  try {
    const resp = await fetch(fullPath);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    src = await resp.text();
  } catch (fetchErr) {
    status.textContent = `❌ Couldn't fetch ${pyFile}`;
    console.error(fetchErr);
    return;
  }

  /* gather user inputs */
  const fd   = new FormData(document.getElementById("demoForm"));
  const args = { ...defaults };
  for (const [k, v] of fd.entries()) if (v !== "") args[k] = v;

  /* Python wrapper code:
     - receives args as JSON
     - executes user's script
     - saves current Matplotlib figure to PNG in‑memory
     - prints a marker + base64 string so JS can extract it            */
  const wrapped = `
import matplotlib, base64, io, json
matplotlib.use("Agg")
args = json.loads(${JSON.stringify(JSON.stringify(args))})
${src}
buf = io.BytesIO()
import matplotlib.pyplot as _plt
_plt.savefig(buf, format="png", bbox_inches="tight")
print("__IMG__" + base64.b64encode(buf.getvalue()).decode())
`;

  try {
    status.textContent = "▶ Running…";
    const result = await py.runPythonAsync(wrapped);
    const b64 = (result || "").split("__IMG__")[1];
    if (!b64) throw new Error("No image produced");
    outDiv.innerHTML = `<img src="data:image/png;base64,${b64}">`;
    status.textContent = "✅ Done";
  } catch (runErr) {
    status.textContent = "❌ Python error – see console";
    console.error(runErr);
  }
}
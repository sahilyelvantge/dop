// docs/js/run_demo.js
export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");

  status.textContent = "🔄 Loading Python…";
  const py = await window.loadPy();

  status.textContent = "🔄 Loading SciPy…";
  try {
    await py.loadPackage(["scipy"]);
  } catch (e) {
    console.warn("Could not load SciPy:", e);
  }

  status.textContent = "🔄 Fetching script…";
  const resp = await fetch(`../py/${pyFile}`);
  if (!resp.ok) {
    status.textContent = "❌ Script not found.";
    return;
  }
  const src = await resp.text();

  // gather form inputs
  const fd = new FormData(document.getElementById("demoForm"));
  const args = { ...defaults };
  for (const [k,v] of fd.entries()) if (v) args[k]=v;

  const code = `
import matplotlib.pyplot as plt, base64, io, json
args = json.loads(${JSON.stringify(JSON.stringify(args))})
${src}
buf = io.BytesIO()
plt.savefig(buf, format="png", bbox_inches="tight")
print("__IMG__"+base64.b64encode(buf.getvalue()).decode())
`;

  status.textContent = "▶ Running…";
  try {
    const res = await py.runPythonAsync(code);
    const parts = res.split("__IMG__");
    if (parts.length < 2) throw new Error("No image");
    outDiv.innerHTML = `<img src="data:image/png;base64,${parts[1]}"/>`;
    status.textContent = "✅ Done";
  } catch(err) {
    console.error(err);
    status.textContent = "❌ "+err;
  }
}
export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");
  outDiv.innerHTML = "";
  
  try {
    status.textContent = "🔄 Loading Python…";
    const py = await window.loadPy();

    status.textContent = "🔄 Loading packages…";
    await py.loadPackage(["numpy", "matplotlib", "scipy"]);

    status.textContent = "🔄 Fetching script…";
    const resp = await fetch(`../py/${pyFile}`);
    if (!resp.ok) throw new Error("Script not found");
    const src = await resp.text();

    // Gather form inputs
    const fd = new FormData(document.getElementById("demoForm"));
    const args = { ...defaults };
    for (const [k,v] of fd.entries()) if (v) args[k] = v;

    // Wrap the script execution
    const code = `
import matplotlib, base64, io, json
matplotlib.use('Agg')  # Important for Pyodide
args = json.loads('${JSON.stringify(args)}')
${src}
`;
    status.textContent = "▶ Running…";
    const result = await py.runPythonAsync(code);
    
    // Handle the output
    const imgStart = result.indexOf("__IMG__");
    if (imgStart >= 0) {
      const imgData = result.slice(imgStart + 7);
      outDiv.innerHTML = `<img src="data:image/png;base64,${imgData}"/>`;
      status.textContent = "✅ Done";
    } else {
      throw new Error("No image data found");
    }
  } catch (err) {
    console.error(err);
    status.textContent = "❌ " + (err.message || "Error");
    outDiv.innerHTML = `<pre class="error">${err}</pre>`;
  }
}
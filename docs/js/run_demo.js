export async function runDemo(pyFile, defaults = {}) {
  const status = document.getElementById("status");
  const outDiv = document.getElementById("output");
  outDiv.innerHTML = "";
  
  try {
    status.textContent = "🔄 Initializing Pyodide...";
    
    // Initialize Pyodide if not already loaded
    if (!window.pyodide) {
      window.pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
      });
    }

    status.textContent = "🔄 Loading packages...";
    await window.pyodide.loadPackage(["numpy", "matplotlib", "scipy", "micropip"]);

    status.textContent = "🔄 Fetching script...";
    const resp = await fetch(`../py/${pyFile}`);
    if (!resp.ok) throw new Error("Script not found");
    const src = await resp.text();

    // Gather form inputs
    const fd = new FormData(document.getElementById("demoForm"));
    const args = { ...defaults };
    for (const [k,v] of fd.entries()) if (v) args[k] = v;

    // Prepare the Python code
    const code = `
import matplotlib
matplotlib.use('Agg')
import io, base64, json
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D

args = json.loads('${JSON.stringify(args)}')

${src}

# Convert figure to base64 and print
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
plt.close()
print("__IMG__" + base64.b64encode(buf.getvalue()).decode('utf-8'))
`;

    status.textContent = "▶ Running Python...";
    const result = await window.pyodide.runPythonAsync(code);
    
    // Extract and display the image
    const imgStart = result.indexOf("__IMG__");
    if (imgStart >= 0) {
      const imgData = result.slice(imgStart + 7);
      outDiv.innerHTML = `<img src="data:image/png;base64,${imgData}"/>`;
      status.textContent = "✅ Visualization complete";
    } else {
      throw new Error("No image data received");
    }
  } catch (err) {
    console.error(err);
    status.textContent = "❌ Error - see console";
    outDiv.innerHTML = `<pre class="error">${err.message}</pre>`;
  }
}
export async function runDemo(pyFile, defaults = {}) {
    const status = document.getElementById("status");
    const outDiv = document.getElementById("output");
  
    status.textContent = "🔄 Loading Python…";
    const py = await window.loadPy();
  
    const src = await (await fetch(`/dop/py/${pyFile}`)).text();   // note /dop
    /* collect form data */
    const fd = new FormData(document.getElementById("demoForm"));
    const args = {...defaults};
    for (const [k, v] of fd.entries()) if (v) args[k] = v;
  
    const code = `
  import matplotlib.pyplot as plt, base64, io, json
  args = json.loads(${JSON.stringify(JSON.stringify(args))})
  ${src}
  buf = io.BytesIO()
  plt.savefig(buf, format="png", bbox_inches="tight")
  print("__IMG__" + base64.b64encode(buf.getvalue()).decode())
  `;
    status.textContent = "▶ Running…";
    const res = await py.runPythonAsync(code);
    const png64 = res.split("__IMG__")[1];
    outDiv.innerHTML = '<img src="data:image/png;base64,' + png64 + '"/>';
    status.textContent = "✅ Done";
  }
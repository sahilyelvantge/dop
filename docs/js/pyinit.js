/* Load Pyodide once and cache globally */
window.loadPy = async () => {
  if (window.pyodide) return window.pyodide;

  /* 1 · Load core */
  window.pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
  });

  /* 2 · Load the std packages we need – Matplotlib is already pre‑built */
  await pyodide.loadPackage(["matplotlib"]);   // numpy, pillow auto‑deps
  await pyodide.runPythonAsync("import matplotlib; matplotlib.use('Agg')");

  return window.pyodide;
};
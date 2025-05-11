/* docs/js/pyinit.js
 * Load Pyodide once, no micropip, just the std‑packages included in Pyodide.
 */
window.loadPy = async () => {
  if (window.pyodide) return window.pyodide;   // reuse if already loaded

  /* core download (~8 MB) */
  window.pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
  });

  /* Matplotlib and its deps are pre‑built inside the bundle. */
  await pyodide.loadPackage(["matplotlib"]);    // numpy, pillow auto‑deps
  await pyodide.runPythonAsync("import matplotlib; matplotlib.use('Agg')");

  return window.pyodide;
};
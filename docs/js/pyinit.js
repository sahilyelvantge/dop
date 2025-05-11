/* docs/js/pyinit.js
 * Define window.loadPy() → returns a ready Pyodide instance.
 */
window.loadPy = async () => {
  if (window.pyodide) return window.pyodide;      // reuse

  /* core download (~8 MB) */
  window.pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
  });

  /* Matplotlib & deps are pre‑compiled inside the bundle */
  await pyodide.loadPackage(["matplotlib"]);
  await pyodide.runPythonAsync("import matplotlib; matplotlib.use('Agg')");

  return window.pyodide;
};
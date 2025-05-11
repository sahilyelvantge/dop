/* Load Pyodide once and keep in global */
window.loadPy = async () => {
  if (window.pyodide) return window.pyodide;
  window.pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
  });
  await pyodide.loadPackage(["micropip"]);
  await pyodide.runPythonAsync(`
    import micropip
    await micropip.install("matplotlib>=3.8")
    import matplotlib
    matplotlib.use("Agg")
  `);
  return window.pyodide;
};
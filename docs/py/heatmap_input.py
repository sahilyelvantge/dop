"""
heatmap_input.py – smooth one‑hue gradient per catalyst
Input  (from JS):
    args = { "csv": "100,0,0\n50,30,20\n..." }
Output:
    Figure with 1..N subplots laid out in a square grid.
"""

import numpy as np, matplotlib.pyplot as plt, math, matplotlib.colors as mcolors

# ---------- read CSV -------------------------------------------------
csv = (args.get("csv", "") or "").strip()
if not csv:
    csv = "100,0,0"

rows = []
for ln in csv.splitlines():
    parts = [p.strip() for p in ln.split(",")[:3]]
    if len(parts) != 3: continue
    try:
        w, m, h = map(float, parts)
        tot = max(w + m + h, 1e-6)
        rows.append({"Weak": w/tot, "Medium": m/tot, "High": h/tot})
    except ValueError:
        pass

if not rows:
    rows = [{"Weak":1.0, "Medium":0, "High":0}]

# ---------- palettes (cycled) ---------------------------------------
palettes = [
    [(0.95,0.88,1.0), (0.73,0.50,0.92), (0.45,0.25,0.75)],   # purple
    [(0.92,0.95,1.0), (0.40,0.70,0.96), (0.12,0.35,0.85)],   # blue
    [(0.92,1.0 ,0.92), (0.45,0.85,0.45), (0.10,0.60,0.30)],  # green
    [(1.0 ,0.92,0.92), (0.95,0.45,0.45), (0.75,0.15,0.15)]   # red
]

# ---------- smooth noise generator (no SciPy) ------------------------
def smooth_field(size=200, passes=5):
    x = np.random.rand(size, size)
    for _ in range(passes):
        x = (x + np.roll(x, 1, 0) + np.roll(x, -1, 0) +
                 np.roll(x, 1, 1) + np.roll(x, -1, 1)) / 5.0
    return x

# ---------- plotting -------------------------------------------------
n = len(rows)
cols = math.ceil(math.sqrt(n))
rows_grid = math.ceil(n / cols)

fig, axes = plt.subplots(rows_grid, cols,
                         figsize=(5*cols, 4*rows_grid), squeeze=False)
fig.suptitle("Elemental Mapping – Gradient Distribution", fontsize=16, y=.965)

for idx, pct in enumerate(rows):
    r, c = divmod(idx, cols)
    ax = axes[r][c]

    base = smooth_field()

    # map smooth field into three ranges according to percentages
    thr1 = pct["Weak"]
    thr2 = pct["Weak"] + pct["Medium"]

    pal = palettes[idx % len(palettes)]
    cmap = mcolors.LinearSegmentedColormap.from_list(f"pal{idx}", pal, N=256)

    # create scaled array 0‑1 matching cmap
    scaled = np.zeros_like(base)
    scaled[base < thr1] = base[base < thr1] / max(thr1,1e-9) * 0.33
    mid = (base >= thr1) & (base < thr2)
    scaled[mid] = 0.34 + (base[mid]-thr1)/max(thr2-thr1,1e-9)*0.32
    scaled[base >= thr2] = 0.67 + (base[base >= thr2]-thr2)/max(1-thr2,1e-9)*0.33

    im = ax.imshow(scaled, cmap=cmap, interpolation="bilinear")
    ax.set_axis_off()

    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02,
                      ticks=[0.17,0.50,0.83])
    cb.ax.set_yticklabels(["Weak","Medium","High"], fontsize=9)

    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']*100:.1f}%, Medium: {pct['Medium']*100:.1f}%, High: {pct['High']*100:.1f}%",
        fontsize=11
    )

# hide unused axes
for k in range(n, rows_grid*cols):
    axes[k//cols][k%cols].set_visible(False)

plt.tight_layout(rect=[0,0,1,0.94])
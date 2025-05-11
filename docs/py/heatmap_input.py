"""
heatmap_input.py  •  smooth one‑hue gradient per catalyst
---------------------------------------------------------
✓ Keeps the “Elemental Mapping – Gradient Distribution” look
✓ One colour scale per catalyst (Weak → Medium → High)
✓ Adds a side legend for each subplot
✓ Works with any number of catalyst rows passed via args["csv"]
"""

import numpy as np, matplotlib.pyplot as plt, math, matplotlib.colors as mcolors, json

# ---------- parse CSV from JS ---------------------------------------
csv = (args.get("csv", "") or "").strip()
if not csv:
    csv = "100,0,0"            # default single row

rows = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:3]]
    if len(parts) != 3: continue
    try:
        w, m, h = map(float, parts)
        tot = max(w + m + h, 1e-6)
        rows.append({"Weak": w/tot, "Medium": m/tot, "High": h/tot})
    except ValueError:
        pass

if not rows:
    rows = [{"Weak":1.0, "Medium":0, "High":0}]

# ---------- colour palettes (cycled) --------------------------------
palettes = [
    [(0.96,0.90,1.0), (0.75,0.55,0.95), (0.45,0.25,0.75)],   # purple
    [(0.92,0.95,1.0), (0.45,0.70,0.97), (0.12,0.35,0.85)],   # blue
    [(0.92,1.0 ,0.92), (0.45,0.85,0.45), (0.10,0.60,0.30)],  # green
    [(1.0 ,0.92,0.92), (0.95,0.50,0.50), (0.75,0.15,0.15)]   # red
]

# ---------- helper to build a smooth field --------------------------
def smooth_field(size=200, octaves=4):
    """
    Build a smooth-ish noise: add several low‑res random layers and upscale.
    No SciPy needed; we rely on imshow interpolation later anyway.
    """
    base = np.zeros((size, size))
    for i in range(octaves):
        step = 2 ** (i + 4)              # 16,32,64…
        small = np.random.rand(size//step, size//step)
        base += np.kron(small, np.ones((step, step)))
    base /= octaves
    return base

# ---------- plot grid -----------------------------------------------
n = len(rows)
cols = math.ceil(math.sqrt(n))
rows_grid = math.ceil(n / cols)

fig_w = 5 * cols
fig_h = 4 * rows_grid
fig, axes = plt.subplots(rows_grid, cols, figsize=(fig_w, fig_h), squeeze=False)
fig.suptitle("Elemental Mapping – Gradient Distribution", fontsize=16, y=.96)

for idx, pct in enumerate(rows):
    r, c = divmod(idx, cols)
    ax = axes[r][c]

    # base smooth field → values 0‑1
    field = smooth_field()

    # thresholds based on percentages
    weak_thr   = pct["Weak"]
    med_thr    = pct["Weak"] + pct["Medium"]

    # choose palette
    pal = palettes[idx % len(palettes)]
    cmap = mcolors.LinearSegmentedColormap.from_list(
        f"pal{idx}", pal, N=256)

    # create mask weights 0‑1 across three ranges
    # values < weak_thr  → 0‑0.33  ;  weak_thr‑med_thr → 0.34‑0.66 ; rest → 0.67‑1
    out = np.zeros_like(field)
    out[field < weak_thr] = field[field < weak_thr] / weak_thr * 0.33
    mid_mask = (field >= weak_thr) & (field < med_thr)
    out[mid_mask] = 0.34 + (field[mid_mask]-weak_thr)/(med_thr-weak_thr+1e-9)*0.32
    out[field >= med_thr] = 0.67 + (field[field >= med_thr]-med_thr)/(1-med_thr)*0.33

    im = ax.imshow(out, cmap=cmap, interpolation="bilinear")
    ax.set_axis_off()

    # colour‑bar legend
    cb = fig.colorbar(
        im, ax=ax, fraction=0.046, pad=0.02,
        ticks=[0.17, 0.50, 0.83]               # roughly ⅙,½,5⁄6
    )
    cb.ax.set_yticklabels(["Weak", "Medium", "High"], fontsize=9)

    # title
    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']*100:.1f}%, Medium: {pct['Medium']*100:.1f}%, High: {pct['High']*100:.1f}%",
        fontsize=11
    )

# hide unused subplots
for k in range(n, rows_grid*cols):
    axes[k//cols][k%cols].set_visible(False)

plt.tight_layout(rect=[0,0,1,0.94])
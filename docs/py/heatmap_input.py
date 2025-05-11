"""
heatmap_input.py
================
Expects args["csv"] with one line per catalyst:

    Weak,Medium,High
    Weak,Medium,High
    ...

For every row it produces a 200×200 "elemental map" that uses a single
colour scale — light for weak, mid‑tone for medium, dark for high.  All
maps are arranged in a neat grid.

Visual style (colours & layout) matches the screenshot the user supplied.
"""

import numpy as np, matplotlib.pyplot as plt, math, random

# ---------- read CSV -------------------------------------------------
csv = (args.get("csv", "") or "").strip()
if not csv:
    csv = "100,0,0"

rows = [r.strip() for r in csv.splitlines() if r.strip()]
percents = []
for r in rows:
    try:
        w,m,h = (float(x) for x in r.split(",")[:3])
        total = max(w+m+h, 1e-6)
        percents.append({"Weak":w/total, "Medium":m/total, "High":h/total})
    except ValueError:
        pass

if not percents:
    percents = [{"Weak":1.0, "Medium":0, "High":0}]

# ---------- colour palettes (cycled) --------------------------------
palettes = [
    [(0.96,0.90,1.0), (0.75,0.55,0.95), (0.45,0.25,0.75)],   # purple
    [(0.92,0.95,1.0), (0.45,0.70,0.97), (0.12,0.35,0.85)],   # blue
    [(0.92,1.0 ,0.92), (0.45,0.85,0.45), (0.10,0.60,0.30)],  # green
    [(1.0 ,0.92,0.92), (0.95,0.50,0.50), (0.75,0.15,0.15)]   # red
]

# ---------- helper: smooth noise without SciPy ----------------------
def make_field(res=50, upscale=4):
    """Low‑res random field → nearest‑neighbour upscale → 2D array"""
    low = np.random.rand(res, res)
    return np.kron(low, np.ones((upscale, upscale)))

# ---------- build figure -------------------------------------------
n = len(percents)
cols = math.ceil(math.sqrt(n))
rows_grid = math.ceil(n / cols)
fig, axes = plt.subplots(rows_grid, cols, figsize=(5*cols, 4*rows_grid),
                         squeeze=False)
fig.suptitle("Elemental Mapping – Gradient Distribution", fontsize=16, y=.96)

for idx, pc in enumerate(percents):
    r, c = divmod(idx, cols)
    ax = axes[r][c]

    # synthetic spatial field
    field = make_field()
    flat = field.flatten()
    order = np.argsort(flat)

    w_end   = int(len(flat) * pc["Weak"])
    m_end   = int(len(flat) * (pc["Weak"] + pc["Medium"]))

    pal = palettes[idx % len(palettes)]
    rgb = np.zeros((len(flat), 3))
    rgb[order[:w_end]]      = pal[0]      # weak
    rgb[order[w_end:m_end]] = pal[1]      # medium
    rgb[order[m_end:]]      = pal[2]      # high

    img = rgb.reshape(field.shape + (3,))
    ax.imshow(img)
    ax.set_axis_off()

    # caption
    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pc['Weak']*100:.1f}%, Medium: {pc['Medium']*100:.1f}%, High: {pc['High']*100:.1f}%",
        fontsize=12
    )

# hide any empty subplots (if total isn’t a perfect square)
for k in range(n, rows_grid*cols):
    axes[k//cols][k%cols].set_visible(False)

plt.tight_layout(rect=[0,0,1,0.94])
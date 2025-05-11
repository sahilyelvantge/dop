"""
heatmap_input.py
----------------
Draws a 200×200 heat‑map whose pixel colours reflect the three user
percentages:

    Weak   → cool blue
    Medium → neutral yellow
    High   → hot red

Inputs arrive via the JS runner as:

    args = {"Weak": 60, "Medium": 30, "High": 10}
"""

import numpy as np, matplotlib.pyplot as plt, json, random

# -------- read args / defaults --------------------------------------
w = float(args.get("Weak",   60))
m = float(args.get("Medium", 30))
h = float(args.get("High",   10))

total = w + m + h
if total == 0: total = 1  # avoid zero division
w, m, h = [x / total for x in (w, m, h)]  # convert to fractions

# -------- create heat‑map matrix ------------------------------------
size = 200
data = np.zeros((size, size, 3))  # RGB array

# assign pixels according to ratios
flat = data.reshape(-1, 3)
n_pix = flat.shape[0]

n_w = int(n_pix * w)
n_m = int(n_pix * m)
# remaining pixels → high
indices = np.arange(n_pix)
np.random.shuffle(indices)

# Weak → blueish
flat[indices[:n_w]]   = [0.1, 0.3, 0.9]
# Medium → yellow
flat[indices[n_w:n_w+n_m]] = [0.95, 0.85, 0.2]
# High → red
flat[indices[n_w+n_m:]] = [0.9, 0.2, 0.2]

data = flat.reshape(size, size, 3)

# -------- plot -------------------------------------------------------
fig, ax = plt.subplots(figsize=(6,6))
ax.imshow(data)
ax.set_axis_off()
ax.set_title(f"Weak {w*100:.1f} %  •  Medium {m*100:.1f} %  •  High {h*100:.1f} %", fontsize=12)
plt.tight_layout()
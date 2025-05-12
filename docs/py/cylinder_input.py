import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
import math

# Read CSV of 3 values per catalyst (Weak, Medium, High)
csv = (args.get("csv", "") or "").strip()
if not csv:
    csv = "100,0,0"
specs = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:3]]
    if len(parts) != 3:
        continue
    try:
        w, m, h = map(float, parts)
        specs.append({"Weak": w, "Medium": m, "High": h})
    except ValueError:
        continue
if not specs:
    specs = [{"Weak": 100, "Medium": 0, "High": 0}]

# Color palettes for gradients (cycled)
palette_list = [
    [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple
    [(0.8,1.0,1.0),  (0.0,0.6,0.9), (0.0,0.2,0.5)],  # cyan
    [(0.8,1.0,0.8),  (0.0,0.8,0.0), (0.0,0.4,0.0)],  # green
    [(1.0,0.8,0.8),  (0.9,0.0,0.0), (0.6,0.0,0.0)]   # red
]

# Cylinder mesh constants
radius = 1.0
height = 4.0
n_u = 300   # angular resolution
n_v = 100   # vertical resolution
u = np.linspace(0, 2 * np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)
bump_scale = 0.0  # no radial bump

# Function to create gradient distribution
# (identical to original logic)
def create_gradient_distribution(percentages, colors, size=(100, 300), smoothness=5):
    H, W = size
    total = H * W
    n_weak = int(percentages['Weak']/100 * total)
    n_med = int(percentages['Medium']/100 * total)
    n_high = total - (n_weak + n_med)

    flat = np.zeros(total, dtype=float)
    flat[n_weak:n_weak + n_med] = 0.5
    flat[n_weak + n_med:] = 1.0
    np.random.shuffle(flat)

    intensity_map = flat.reshape(H, W)
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    mn, mx = intensity_map.min(), intensity_map.max()
    if mx > mn:
        intensity_map = (intensity_map - mn) / (mx - mn)

    cmap = LinearSegmentedColormap.from_list('grad', colors, N=256)
    colored_map = cmap(intensity_map)
    return intensity_map, colored_map

# Plot dynamic grid: 2 columns, rows = ceil(n/2)
n = len(specs)
cols = 2
rows = math.ceil(n / 2)
fig = plt.figure(figsize=(7 * cols, 5 * rows))

for idx, pct in enumerate(specs):
    palette = palette_list[idx % len(palette_list)]
    intensity_map, colored_map = create_gradient_distribution(
        pct, palette, size=(n_v, n_u), smoothness=8
    )

    R = radius + bump_scale * intensity_map
    X = R * np.cos(U)
    Y = R * np.sin(U)
    Z = V

    ax = fig.add_subplot(rows, cols, idx+1, projection='3d')
    ax.plot_surface(
        X, Y, Z,
        facecolors=colored_map,
        rcount=n_v, ccount=n_u,
        linewidth=0, antialiased=False
    )
    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']:.1f}%, Medium: {pct['Medium']:.1f}%, High: {pct['High']:.1f}%",
        fontsize=12
    )
    ax.set_axis_off()
    ax.view_init(elev=30, azim=45)

plt.tight_layout()
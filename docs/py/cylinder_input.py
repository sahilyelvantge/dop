import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import matplotlib.gridspec as gridspec
import math

# ─── Read user CSV input from JS -------------------------------------
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
        tot = max(w + m + h, 1e-6)
        specs.append({
            "Weak":   w / tot * 100,
            "Medium": m / tot * 100,
            "High":   h / tot * 100
        })
    except ValueError:
        continue
if not specs:
    specs = [{"Weak":100, "Medium":0, "High":0}]

# ─── Palettes (cycled) -----------------------------------------------
palette_list = [
    [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],   # purple
    [(0.8,1.0,1.0),  (0.0,0.6,0.9), (0.0,0.2,0.5)],   # cyan
    [(0.8,1.0,0.8),  (0.0,0.8,0.0), (0.0,0.4,0.0)],   # green
    [(1.0,0.8,0.8),  (0.9,0.0,0.0), (0.6,0.0,0.0)],   # red
]

# ─── Cylinder mesh constants -----------------------------------------
radius = 1.0
height = 4.0
n_u = 300   # angular resolution
n_v = 100   # vertical resolution
u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)
bump_scale = 0.0  # no radial bump

# ─── Gradient distribution (identical logic) -------------------------
def create_gradient_distribution(percentages, colors, size=(n_v, n_u), smoothness=8):
    H, W = size
    total = H * W
    n_weak   = int(percentages['Weak']   / 100 * total)
    n_medium = int(percentages['Medium'] / 100 * total)
    # remaining → high
    n_high   = total - (n_weak + n_medium)

    flat = np.zeros(total, dtype=float)
    flat[n_weak:n_weak+n_medium] = 0.5
    flat[n_weak+n_medium:]       = 1.0
    np.random.shuffle(flat)

    intensity_map = flat.reshape(H, W)
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    intensity_map = (intensity_map - intensity_map.min()) / (
        intensity_map.max() - intensity_map.min() + 1e-9
    )

    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    colored_map = cmap(intensity_map)
    return intensity_map, colored_map

# ─── Plot grid of cylinders ------------------------------------------
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)
fig = plt.figure(figsize=(7*cols, 5*rows))
gs = gridspec.GridSpec(rows, cols, wspace=0.3, hspace=0.4)

for idx, pct in enumerate(specs):
    colors = palette_list[idx % len(palette_list)]
    intensity_map, colored_map = create_gradient_distribution(
        pct, colors, size=(n_v, n_u), smoothness=8
    )

    R = radius + bump_scale * intensity_map
    X = R * np.cos(U)
    Y = R * np.sin(U)
    Z = V

    ax = fig.add_subplot(gs[idx], projection='3d')
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
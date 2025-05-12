import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import math

# ─── Helper: pure-NumPy Gaussian blur (separable) ────────────────────
def gaussian_blur(img, sigma=5):
    if sigma <= 0:
        return img
    # 1D Gaussian kernel
    radius = int(3 * sigma)
    x = np.arange(-radius, radius+1)
    kernel = np.exp(-0.5 * (x / sigma)**2)
    kernel /= kernel.sum()
    # convolve rows then columns
    tmp = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode='same'), 1, img)
    return np.apply_along_axis(lambda c: np.convolve(c, kernel, mode='same'), 0, tmp)

# ─── Read user CSV: Weak,Medium,High per line ────────────────────────
csv = (args.get("csv","") or "").strip()
if not csv:
    csv = "100,0,0"
specs = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:3]]
    if len(parts)!=3:
        continue
    try:
        w,m,h = map(float, parts)
        specs.append({"Weak":w, "Medium":m, "High":h})
    except:
        pass
if not specs:
    specs = [{"Weak":100,"Medium":0,"High":0}]

# ─── Color palettes (cycled) ─────────────────────────────────────────
palette_list = [
    [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple → deep purple
    [(0.8,1.0,1.0), (0.0,0.6,0.9), (0.0,0.2,0.5)],   # cyan → navy
    [(0.8,1.0,0.8), (0.0,0.8,0.0), (0.0,0.4,0.0)],   # lime → dark green
    [(1.0,0.8,0.8), (0.9,0.0,0.0), (0.6,0.0,0.0)]    # pink → deep red
]

# ─── Cylinder mesh constants ─────────────────────────────────────────
radius = 1.0
height = 4.0
n_u = 300   # angular resolution (matches original)
n_v = 100   # vertical resolution (matches original)
bump_scale = 0.0  # keep at 0 for no protrusion (matches original)

u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)            # shape (n_v, n_u)
X0 = radius * np.cos(U)
Y0 = radius * np.sin(U)
Z0 = V

# ─── Build gradient distribution matching original ───────────────────
def create_gradient_distribution(percentages, colors, size=(100, 300), smoothness=5):
    H, W = size
    total = H * W

    # Compute counts for each category
    n_weak   = int(percentages['Weak']   / 100 * total)
    n_medium = int(percentages['Medium'] / 100 * total)
    n_high   = total - (n_weak + n_medium)

    # Flat array: 0=weak, 0.5=medium, 1=high
    flat = np.zeros(total, dtype=float)
    flat[n_weak:n_weak + n_medium] = 0.5
    flat[n_weak + n_medium:]      = 1.0
    np.random.shuffle(flat)

    # Reshape and smooth
    intensity_map = flat.reshape(H, W)
    intensity_map = gaussian_blur(intensity_map, sigma=smoothness)
    intensity_map = (intensity_map - intensity_map.min()) / (
        intensity_map.max() - intensity_map.min()
    )

    # Custom colormap
    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    colored_map = cmap(intensity_map)

    return intensity_map, colored_map

# ─── Plot dynamic grid: 2 columns × rows ─────────────────────────────
n = len(specs)
cols = 2
rows = math.ceil(n/cols)
fig = plt.figure(figsize=(7*cols, 5*rows))

for idx, pct in enumerate(specs):
    colors = palette_list[idx % len(palette_list)]
    intensity_map, colored_map = create_gradient_distribution(
        pct, colors, size=(n_v, n_u), smoothness=8
    )
    
    # perturb radius by intensity (matches original)
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
plt.suptitle("Wrapped Gradient Visualization", y=1.02, fontsize=16)
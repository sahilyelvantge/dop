# ─── Ensure SciPy is installed in Pyodide ───────────────────────────────────
import micropip, asyncio
asyncio.run(micropip.install("scipy"))

# ─── Original cylinder code (unchanged) ────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def create_gradient_distribution(percentages, colors, size=(100, 300), smoothness=5):
    """
    Build a 2D intensity_map (H×W) from percentages dict and then color it
    with a custom colormap defined by colors (3 RGB stops).
    """
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
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    intensity_map = (intensity_map - intensity_map.min()) / (
        intensity_map.max() - intensity_map.min()
    )

    # Custom colormap
    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    colored_map = cmap(intensity_map)

    return intensity_map, colored_map

# ─── Catalyst data & contrasting gradients ─────────────────────────────────────
catalysts_data = {
    "NiO@Ce3O4": {"Weak":98, "Medium":1,   "High":1},
    "NiO@SiO2":  {"Weak":59.3, "Medium":9.43,"High":31.27},
    "NiO@ZrO2":  {"Weak":36,   "Medium":12,  "High":52},
    "NiO@CeO2":  {"Weak":39,   "Medium":42,  "High":19}
}

gradient_colors = {
    "NiO@Ce3O4": [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple → deep purple
    "NiO@SiO2":  [(0.8,1.0,1.0), (0.0,0.6,0.9), (0.0,0.2,0.5)],  # cyan → navy
    "NiO@ZrO2":  [(0.8,1.0,0.8), (0.0,0.8,0.0), (0.0,0.4,0.0)],  # lime → dark green
    "NiO@CeO2":  [(1.0,0.8,0.8), (0.9,0.0,0.0), (0.6,0.0,0.0)]   # pink → deep red
}

# ─── Cylinder mesh (shared) ───────────────────────────────────────────────────
radius = 1.0
height = 4.0
n_u = 300   # angular resolution
n_v = 100   # vertical resolution

u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)            # shape (n_v, n_u)
X0 = radius * np.cos(U)
Y0 = radius * np.sin(U)
Z0 = V

# radial bump scale
bump_scale = 0.0 # change to 0.5 for protrusions

# ─── Plot all catalysts ───────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 12))

for idx, cat in enumerate(catalysts_data.keys()):
    perc = catalysts_data[cat]
    cols = gradient_colors[cat]

    # get gradient distribution for this catalyst
    intensity_map, colored_map = create_gradient_distribution(
        perc, cols, size=(n_v, n_u), smoothness=8
    )

    # perturb radius by intensity
    R = radius + bump_scale * intensity_map
    X = R * np.cos(U)
    Y = R * np.sin(U)
    Z = V

    ax = fig.add_subplot(2, 2, idx+1, projection='3d')
    ax.plot_surface(
        X, Y, Z,
        facecolors=colored_map,
        rcount=n_v, ccount=n_u,
        linewidth=0, antialiased=False
    )
    ax.set_title(cat, fontsize=14)
    ax.set_axis_off()
    ax.view_init(elev=30, azim=45)

plt.tight_layout()
plt.suptitle("Wrapped Gradient + Protruding Particles on Cylinders",
             y=1.02, fontsize=16)
plt.show()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
import math
import io
import base64
import json

# SciPy Import Handling
try:
    from scipy.ndimage import gaussian_filter
except ImportError:
    # Simple fallback implementation if scipy not available
    def gaussian_filter(input, sigma):
        kernel = np.array([[1, 2, 1],
                         [2, 4, 2],
                         [1, 2, 1]]) / 16
        output = np.zeros_like(input)
        for i in range(1, input.shape[0]-1):
            for j in range(1, input.shape[1]-1):
                output[i,j] = np.sum(input[i-1:i+2, j-1:j+2] * kernel)
        return output

# Read user CSV input from JS
csv = args.get("csv", "100,0,0").strip()
specs = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:3]]
    if len(parts) != 3: continue
    try:
        w, m, h = map(float, parts)
        tot = max(w + m + h, 1e-6)
        specs.append({"Weak": w/tot*100, "Medium": m/tot*100, "High": h/tot*100})
    except ValueError:
        pass
if not specs:
    specs = [{"Weak":100, "Medium":0, "High":0}]

# Color palettes (cycled if >4 rows)
palette_list = [
    [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple → deep purple
    [(0.8,1.0,1.0), (0.0,0.6,0.9), (0.0,0.2,0.5)],    # cyan → navy
    [(0.8,1.0,0.8), (0.0,0.8,0.0), (0.0,0.4,0.0)],    # lime → dark green
    [(1.0,0.8,0.8), (0.9,0.0,0.0), (0.6,0.0,0.0)]     # pink → deep red
]

# Cylinder mesh parameters
radius = 1.0
height = 4.0
n_u = 300   # angular resolution
n_v = 100   # vertical resolution
u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)
X0 = radius * np.cos(U)
Y0 = radius * np.sin(U)
Z0 = V
bump_scale = 0.0  # no radial bump

def create_gradient_distribution(percentages, colors, size=(n_v, n_u), smoothness=5):
    H, W = size
    total = H * W

    # Compute counts for each category
    n_weak = int(percentages['Weak'] / 100 * total)
    n_medium = int(percentages['Medium'] / 100 * total)
    n_high = total - (n_weak + n_medium)

    # Create and shuffle intensity values
    flat = np.zeros(total, dtype=float)
    flat[n_weak:n_weak + n_medium] = 0.5
    flat[n_weak + n_medium:] = 1.0
    np.random.shuffle(flat)

    # Reshape and smooth
    intensity_map = flat.reshape(H, W)
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    intensity_map = (intensity_map - intensity_map.min()) / (intensity_map.max() - intensity_map.min() + 1e-9)

    # Apply colormap
    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    return intensity_map, cmap(intensity_map)

# Create figure with subplots
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)
fig = plt.figure(figsize=(7*cols, 5*rows))

# Plot each catalyst
for idx, pct in enumerate(specs):
    colors = palette_list[idx % len(palette_list)]
    intensity_map, colored_map = create_gradient_distribution(
        pct, colors, size=(n_v, n_u), smoothness=8
    )

    # Create 3D surface
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
plt.suptitle("Wrapped Gradient on Cylinders", y=1.02, fontsize=16)

# Output the image
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
plt.close()
print("__IMG__" + base64.b64encode(buf.getvalue()).decode('utf-8'))
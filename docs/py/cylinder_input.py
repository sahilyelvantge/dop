import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
import math
import io
import base64

# SciPy Import Handling
try:
    from scipy.ndimage import gaussian_filter
except ImportError:
    def gaussian_filter(input, sigma):
        """Simple 3x3 gaussian-like blur fallback"""
        kernel = np.array([[1, 2, 1],
                         [2, 4, 2],
                         [1, 2, 1]]) / 16
        output = np.zeros_like(input)
        for i in range(1, input.shape[0]-1):
            for j in range(1, input.shape[1]-1):
                output[i,j] = np.sum(input[i-1:i+2, j-1:j+2] * kernel)
        return output

# Process input data
try:
    csv = args["csv"].strip()
except (KeyError, AttributeError):
    csv = "100,0,0"

specs = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:3]]
    if len(parts) != 3: 
        continue
    try:
        w, m, h = map(float, parts)
        total = max(w + m + h, 1e-6)
        specs.append({
            "Weak": w/total*100,
            "Medium": m/total*100,
            "High": h/total*100
        })
    except ValueError:
        continue

if not specs:
    specs = [{"Weak": 100, "Medium": 0, "High": 0}]

# Color palettes
palette_list = [
    [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple
    [(0.8,1.0,1.0), (0.0,0.6,0.9), (0.0,0.2,0.5)],    # cyan
    [(0.8,1.0,0.8), (0.0,0.8,0.0), (0.0,0.4,0.0)],    # green
    [(1.0,0.8,0.8), (0.9,0.0,0.0), (0.6,0.0,0.0)]     # red
]

# Cylinder configuration
radius = 1.0
height = 4.0
n_u = 300  # angular resolution
n_v = 100  # vertical resolution
u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)
bump_scale = 0.0

def create_gradient(percentages, colors, size=(n_v, n_u), smoothness=5):
    H, W = size
    total = H * W
    
    n_weak = int(percentages['Weak'] / 100 * total)
    n_medium = int(percentages['Medium'] / 100 * total)
    n_high = total - (n_weak + n_medium)
    
    flat = np.zeros(total)
    flat[n_weak:n_weak+n_medium] = 0.5
    flat[n_weak+n_medium:] = 1.0
    np.random.shuffle(flat)
    
    intensity = flat.reshape(H, W)
    intensity = gaussian_filter(intensity, sigma=smoothness)
    intensity = (intensity - intensity.min()) / (intensity.max() - intensity.min() + 1e-9)
    
    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    return intensity, cmap(intensity)

# Create visualization
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)
fig = plt.figure(figsize=(7*cols, 5*rows))

for idx, pct in enumerate(specs):
    colors = palette_list[idx % len(palette_list)]
    intensity, colored = create_gradient(pct, colors, smoothness=8)
    
    R = radius + bump_scale * intensity
    X = R * np.cos(U)
    Y = R * np.sin(U)
    Z = V
    
    ax = fig.add_subplot(rows, cols, idx+1, projection='3d')
    ax.plot_surface(
        X, Y, Z,
        facecolors=colored,
        rcount=n_v, ccount=n_u,
        linewidth=0, antialiased=False
    )
    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']:.1f}% Medium: {pct['Medium']:.1f}% High: {pct['High']:.1f}%",
        fontsize=10
    )
    ax.set_axis_off()
    ax.view_init(elev=30, azim=45)

plt.tight_layout()
plt.suptitle("Wrapped Gradient on Cylinders", y=1.02, fontsize=14)

# Output image
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
plt.close()
print("__IMG__" + base64.b64encode(buf.getvalue()).decode('utf-8'))
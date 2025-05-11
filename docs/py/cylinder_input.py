import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
import math
import io
import base64
import json

# ─── SciPy Import Handling ──────────────────────────────────────────
try:
    from scipy.ndimage import gaussian_filter
    has_scipy = True
except ImportError:
    has_scipy = False
    try:
        import micropip
        # Store the promise for micropip install
        scipy_install_promise = micropip.install("scipy")
        from scipy.ndimage import gaussian_filter
        has_scipy = True
    except:
        # Fallback implementation if scipy not available
        def gaussian_filter(input, sigma):
            """Simple 3x3 gaussian-like blur as fallback"""
            kernel = np.array([[1, 2, 1],
                            [2, 4, 2],
                            [1, 2, 1]]) / 16
            output = np.zeros_like(input)
            for i in range(1, input.shape[0]-1):
                for j in range(1, input.shape[1]-1):
                    output[i,j] = np.sum(input[i-1:i+2, j-1:j+2] * kernel)
            return output

# Main function that will be called from JS
async def generate_plot():
    # If we have a pending scipy install, wait for it
    if 'scipy_install_promise' in globals():
        await scipy_install_promise

    # ─── Read user CSV input from JS ────────────────────────────────
    csv = (args.get("csv", "") or "").strip()
    if not csv:
        csv = "100,0,0"

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

    # ─── Palettes (cycled if >4 rows) ──────────────────────────────
    palette_list = [
        [(0.95,0.8,1.0), (0.6,0.2,0.9), (0.3,0.0,0.6)],  # purple → deep purple
        [(0.8,1.0,1.0), (0.0,0.6,0.9), (0.0,0.2,0.5)],    # cyan → navy
        [(0.8,1.0,0.8), (0.0,0.8,0.0), (0.0,0.4,0.0)],    # lime → dark green
        [(1.0,0.8,0.8), (0.9,0.0,0.0), (0.6,0.0,0.0)]     # pink → deep red
    ]

    # ─── Cylinder mesh (shared) ────────────────────────────────────
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

    # radial bump scale (0 for smooth cylinder)
    bump_scale = 0.0

    # ─── Gradient distribution ────────────────────────────────────
    def create_gradient_distribution(percentages, colors, size=(n_v, n_u), smoothness=5):
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
            intensity_map.max() - intensity_map.min() + 1e-9
        )

        # Custom colormap
        cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
        colored_map = cmap(intensity_map)

        return intensity_map, colored_map

    # ─── Plot all catalysts ──────────────────────────────────────
    n = len(specs)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    fig = plt.figure(figsize=(7*cols, 5*rows))

    for idx, pct in enumerate(specs):
        colors = palette_list[idx % len(palette_list)]
        intensity_map, colored_map = create_gradient_distribution(
            pct, colors, size=(n_v, n_u), smoothness=8
        )

        # perturb radius by intensity (if bump_scale > 0)
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

    # Return the figure as PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')
if __name__ == '__main__':
    # Convert the figure to base64 and print it
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    print("__IMG__" + base64.b64encode(buf.getvalue()).decode('utf-8'))
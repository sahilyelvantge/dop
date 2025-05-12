import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from scipy.ndimage import gaussian_filter
import math

# ─── Read user CSV: Weak,Medium,High per line ────────────────────────
def parse_user_input(csv_string):
    if not csv_string.strip():
        return [{"Weak": 100, "Medium": 0, "High": 0}], ["Catalyst 1"]
    
    specs = []
    names = []
    for i, line in enumerate(csv_string.splitlines()):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            w, m, h = map(float, parts[:3])
            # Ensure percentages add up to 100
            total = w + m + h
            if total != 100:
                w, m, h = w*100/total, m*100/total, h*100/total
                
            spec = {"Weak": w, "Medium": m, "High": h}
            specs.append(spec)
            
            # If name is provided as 4th value, use it
            if len(parts) > 3 and parts[3].strip():
                names.append(parts[3].strip())
            else:
                names.append(f"Catalyst {i+1}")
        except:
            pass
    
    if not specs:
        return [{"Weak": 100, "Medium": 0, "High": 0}], ["Catalyst 1"]
    
    return specs, names

# Get user input
csv = args.get("csv", "") or ""
specs, catalyst_names = parse_user_input(csv)

# ─── Color palettes from cylinder.py ─────────────────────────────────
gradient_colors = {
    "NiO@Co3O4": [(0.95, 0.8, 1.0), (0.6, 0.2, 0.9), (0.3, 0.0, 0.6)],  # purple → deep purple
    "NiO@SiO2": [(0.8, 1.0, 1.0), (0.0, 0.6, 0.9), (0.0, 0.2, 0.5)],    # cyan → navy
    "NiO@ZrO2": [(0.8, 1.0, 0.8), (0.0, 0.8, 0.0), (0.0, 0.4, 0.0)],    # lime → dark green
    "NiO@CeO2": [(1.0, 0.8, 0.8), (0.9, 0.0, 0.0), (0.6, 0.0, 0.0)]     # pink → deep red
}

# Use these as fallbacks
default_catalysts = list(gradient_colors.keys())
palette_list = list(gradient_colors.values())

# ─── Create gradient distribution function from cylinder.py ─────────────────
def create_gradient_distribution(percentages, colors, size=(100, 300), smoothness=5):
    """
    Build a 2D intensity_map (H×W) from percentages dict and color it
    with a custom colormap defined by colors (3 RGB stops).
    """
    H, W = size
    total = H * W
    # Compute counts for each category
    n_weak = int(percentages['Weak'] / 100 * total)
    n_medium = int(percentages['Medium'] / 100 * total)
    
    # Flat array: 0=weak, 0.5=medium, 1=high
    flat = np.zeros(total, dtype=float)
    flat[n_weak:n_weak + n_medium] = 0.5
    flat[n_weak + n_medium:] = 1.0
    np.random.shuffle(flat)
    
    # Reshape and smooth
    intensity_map = flat.reshape(H, W)
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    
    # Normalize
    mi, ma = intensity_map.min(), intensity_map.max()
    intensity_map = (intensity_map - mi) / (ma - mi) if ma > mi else intensity_map
    
    # Custom colormap
    cmap = LinearSegmentedColormap.from_list("grad", colors, N=256)
    colored_map = cmap(intensity_map)
    
    return intensity_map, colored_map

# ─── Overlay circular particles on cylindrical surface ─────────────────────
def overlay_circular_particles(intensity_map, colored_map, spot_color, dispersion=0.5, radius=1):
    """
    Overlays circular particles on the surface based on intensity and dispersion.
    """
    H, W = intensity_map.shape
    result = colored_map.copy()
    
    # Calculate number of particles based on dispersion
    total_spots = int(H * W * dispersion / 100.0)
    
    # Create random positions
    positions = np.random.choice(H*W, size=total_spots, replace=False)
    y_spots, x_spots = np.unravel_index(positions, (H, W))
    
    # Create circular particles
    for y, x in zip(y_spots, x_spots):
        # Determine if this is a cluster center or single particle
        is_cluster = np.random.random() < 0.3  # 30% chance for cluster
        particles = [(y, x)]
        
        # Add cluster particles
        if is_cluster:
            cluster_size = np.random.randint(2, 6)  # 2-5 particles per cluster
            for _ in range(cluster_size):
                offset_y = np.random.randint(-4, 5)
                offset_x = np.random.randint(-4, 5)
                if 0 <= y + offset_y < H and 0 <= x + offset_x < W:
                    particles.append((y + offset_y, x + offset_x))
        
        # Draw each particle as a circle
        for py, px in particles:
            for i in range(-radius, radius+1):
                for j in range(-radius, radius+1):
                    if i*i + j*j <= radius*radius:  # Circle equation
                        ny, nx = py + i, px + j
                        if 0 <= ny < H and 0 <= nx < W:
                            result[ny, nx] = spot_color
    
    return result

# ─── Cylinder mesh constants ─────────────────────────────────────────
radius = 1.0
height = 4.0
n_u = 300  # angular resolution
n_v = 100  # vertical resolution
u = np.linspace(0, 2*np.pi, n_u)
v = np.linspace(-height/2, height/2, n_v)
U, V = np.meshgrid(u, v)  # shape (n_v, n_u)

# Radial bump scale (0 for flat, >0 for bumps)
bump_scale = 0.0

# Spot colors for particles
spot_colors = {
    "NiO@Co3O4": (0.4, 0.1, 0.4, 1.0),  # dark purple
    "NiO@SiO2": (0.0, 0.0, 0.5, 1.0),   # dark blue
    "NiO@ZrO2": (0.0, 0.4, 0.0, 1.0),   # dark green
    "NiO@CeO2": (0.5, 0.0, 0.0, 1.0)    # dark red
}

# Dispersion values for example catalysts (or use your own)
dispersion_values = {
    "NiO@Co3O4": 0.8,
    "NiO@SiO2": 0.5,
    "NiO@ZrO2": 0.4,
    "NiO@CeO2": 0.4
}

# ─── Plot all catalysts ───────────────────────────────────────────────
n = len(specs)
cols = 2
rows = math.ceil(n/cols)
fig = plt.figure(figsize=(14, 12) if n > 2 else (14, 6))

for idx, spec in enumerate(specs):
    # Get catalyst name
    cat_name = catalyst_names[idx] if idx < len(catalyst_names) else f"Catalyst {idx+1}"
    
    # Default colors and spot color
    colors = palette_list[idx % len(palette_list)]
    spot_color = (0.2, 0.2, 0.2, 1.0)  # Default dark gray
    
    # Use predefined colors if catalyst name matches
    for key in gradient_colors:
        if key.lower() in cat_name.lower():
            colors = gradient_colors[key]
            spot_color = spot_colors[key]
            break
    
    # Get dispersion value (default to 0.5 if not defined)
    dispersion = 0.5
    for key in dispersion_values:
        if key.lower() in cat_name.lower():
            dispersion = dispersion_values[key]
            break
    
    # Create gradient distribution
    intensity_map, colored_map = create_gradient_distribution(
        spec, colors, size=(n_v, n_u), smoothness=8
    )
    
    # Add circular particles
    surface_map = overlay_circular_particles(
        intensity_map, colored_map, spot_color, 
        dispersion=dispersion*100, radius=2
    )
    
    # Perturb radius by intensity for 3D effect (if bump_scale > 0)
    R = radius + bump_scale * intensity_map
    X = R * np.cos(U)
    Y = R * np.sin(U)
    Z = V
    
    # Create 3D plot
    ax = fig.add_subplot(rows, cols, idx+1, projection='3d')
    ax.plot_surface(
        X, Y, Z,
        facecolors=surface_map,
        rcount=n_v, ccount=n_u,
        linewidth=0, antialiased=True
    )
    
    # Format title like cylinder.py
    ax.set_title(f"{cat_name}\nWeak: {spec['Weak']:.1f}%, Medium: {spec['Medium']:.1f}%, High: {spec['High']:.1f}%", fontsize=14)
    ax.set_axis_off()
    ax.view_init(elev=30, azim=45)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.suptitle("Wrapped Gradient + Circular Particles on Cylinders", y=1.02, fontsize=16)
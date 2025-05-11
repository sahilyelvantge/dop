import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter

# ---------- parse CSV ------------------------------------------------
csv = (args.get("csv","") or "").strip()
if not csv: csv = "100,0,0"

specs=[]
for ln in csv.splitlines():
    try:
        w,m,h=map(float,ln.split(",")[:3])
        tot=max(w+m+h,1e-6)
        specs.append({"Weak":w/tot*100,"Medium":m/tot*100,"High":h/tot*100})  # Convert to percentages
    except ValueError: pass

if not specs:
    specs=[{"Weak":100,"Medium":0,"High":0}]

# ---------- palettes (cycled) ---------------------------------------
palettes=[
    [(0.9, 0.8, 1.0), (0.7, 0.5, 0.9), (0.5, 0.2, 0.7)],  # Purple gradient
    [(0.8, 0.9, 1.0), (0.3, 0.6, 0.9), (0.1, 0.3, 0.8)],  # Blue gradient
    [(0.8, 1.0, 0.8), (0.4, 0.8, 0.4), (0.1, 0.6, 0.3)],  # Green gradient
    [(1.0, 0.8, 0.8), (0.9, 0.4, 0.4), (0.7, 0.1, 0.1)]   # Red gradient
]

# ---------- create gradient distribution (original logic) -----------
def create_gradient_distribution(percentages, colors, size=200, smoothness=10):
    # Special case for 100% single intensity
    if percentages["Weak"] == 100 or percentages["Medium"] == 100 or percentages["High"] == 100:
        # Create a uniform map with slight texture
        if percentages["Weak"] == 100:
            base_color = colors[0]
            noise_range = 0.1
        elif percentages["Medium"] == 100:
            base_color = colors[1]
            noise_range = 0.1
        else:  # High == 100
            base_color = colors[2]
            noise_range = 0.1
            
        # Create base RGBA array
        r, g, b = base_color
        base_map = np.ones((size, size, 4))
        base_map[:, :, 0] = r
        base_map[:, :, 1] = g
        base_map[:, :, 2] = b
        base_map[:, :, 3] = 1.0
        
        # Add subtle texture
        for i in range(3):  # RGB channels only
            noise = (np.random.rand(size, size) - 0.5) * noise_range
            base_map[:, :, i] = np.clip(base_map[:, :, i] + noise, 0, 1)
            
        return base_map
        
    # For mixed distributions
    intensity_map = np.zeros((size, size))
    total_cells = size * size
    n_weak = int(total_cells * percentages["Weak"] / 100)
    n_medium = int(total_cells * percentages["Medium"] / 100)
    n_high = int(total_cells * percentages["High"] / 100)
    
    # Adjust for rounding errors
    remainder = total_cells - (n_weak + n_medium + n_high)
    n_weak += remainder
    
    # Create distribution
    flat_map = np.zeros(total_cells)
    flat_map[:n_weak] = 0  # Weak
    flat_map[n_weak:n_weak+n_medium] = 0.5  # Medium
    flat_map[n_weak+n_medium:] = 1.0  # High
    
    # Shuffle and reshape
    np.random.shuffle(flat_map)
    intensity_map = flat_map.reshape((size, size))
    
    # Apply gaussian filter
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    
    # Normalize
    if np.max(intensity_map) > np.min(intensity_map):
        intensity_map = (intensity_map - np.min(intensity_map)) / (np.max(intensity_map) - np.min(intensity_map))
    
    # Apply colormap
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)
    colored_map = cmap(intensity_map)
    
    return colored_map

# ---------- build figure -------------------------------------------
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows_grid = math.ceil(n / cols)
fig, axes = plt.subplots(rows_grid, cols, figsize=(5*cols, 4*rows_grid), squeeze=False)
fig.suptitle("Elemental Mapping - Gradient Distribution", fontsize=16, y=0.96)

for idx, pct in enumerate(specs):
    r, c = divmod(idx, cols)
    ax = axes[r][c]
    
    # Get the appropriate color palette
    colors = palettes[idx % len(palettes)]
    
    # Create the gradient distribution using original logic
    colored_map = create_gradient_distribution(
        pct,
        colors,
        size=200,
        smoothness=10
    )
    
    # Display the image
    im = ax.imshow(colored_map, interpolation='gaussian')
    
    # Add border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_edgecolor('black')
    
    # Create colorbar
    cmap_for_colorbar = mcolors.LinearSegmentedColormap.from_list('custom_cbar', colors, N=256)
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap_for_colorbar), ax=ax, fraction=0.045, pad=0.04)
    
    # Set colorbar ticks based on available intensities
    tick_positions = []
    tick_labels = []
    
    if pct["Weak"] > 0:
        tick_positions.append(0.1)
        tick_labels.append('Weak')
    if pct["Medium"] > 0:
        tick_positions.append(0.5)
        tick_labels.append('Medium')
    if pct["High"] > 0:
        tick_positions.append(0.9)
        tick_labels.append('High')
    
    cb.set_ticks(tick_positions)
    cb.set_ticklabels(tick_labels)
    
    # Set title with percentages
    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']:.1f}%, Medium: {pct['Medium']:.1f}%, High: {pct['High']:.1f}%",
        fontsize=11
    )
    ax.axis('off')

# Hide unused axes
for k in range(n, rows_grid * cols):
    axes[k // cols][k % cols].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
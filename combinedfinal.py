import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
from scipy.ndimage import gaussian_filter

def create_gradient_distribution(percentages, colors, size=200, smoothness=2):
    H, W = size, size
    total = H * W
    if 100 in percentages.values():
        base_int = list(percentages.values()).index(100) / 2
        noise = np.random.rand(H, W) * 0.05
        intensity = np.clip(base_int + noise, 0, 1)
    else:
        n_weak = int(percentages['Weak'] / 100 * total)
        n_medium = int(percentages['Medium'] / 100 * total)
        flat = np.zeros(total, dtype=float)
        flat[n_weak:n_weak + n_medium] = 0.5
        flat[n_weak + n_medium:] = 1.0
        np.random.shuffle(flat)
        intensity = gaussian_filter(flat.reshape(H, W), sigma=smoothness)
        mi, ma = intensity.min(), intensity.max()
        intensity = (intensity - mi) / (ma - mi) if ma > mi else intensity
    cmap = LinearSegmentedColormap.from_list('grad', colors, N=256)
    return cmap(intensity)

def overlay_circular_particles(colored_map, val, spot_color, r=1):
    H, W, _ = colored_map.shape
    num_spots = int(H * W * (val / 100.0))
    overlay = colored_map.copy()
    all_coords = [(x, y) for x in range(W) for y in range(H)]
    centers = random.sample(all_coords, num_spots)
    for x, y in centers:
        for i in range(max(0, x - r), min(W, x + r + 1)):
            for j in range(max(0, y - r), min(H, y + r + 1)):
                if (i - x)**2 + (j - y)**2 <= r*r:
                    overlay[j, i, :3] = spot_color
                    overlay[j, i, 3] = 1.0
    return overlay

# Catalyst data
gradient_specs = {
    "NiO@Co3O4": {"Weak": 100, "Medium": 0, "High": 0},
    "NiO@SiO2": {"Weak": 59.3, "Medium": 9.43, "High": 31.27},
    "NiO@ZrO2": {"Weak": 36, "Medium": 12, "High": 52},
    "NiO@CeO2": {"Weak": 39, "Medium": 42, "High": 19}
}

gradient_colors = {
    "NiO@Co3O4": [(0.9, 0.8, 1.0), (0.7, 0.5, 0.9), (0.5, 0.2, 0.7)],
    "NiO@SiO2": [(0.8, 0.9, 1.0), (0.3, 0.6, 0.9), (0.1, 0.3, 0.8)],
    "NiO@ZrO2": [(0.8, 1.0, 0.8), (0.4, 0.8, 0.4), (0.1, 0.6, 0.3)],
    "NiO@CeO2": [(1.0, 0.8, 0.8), (0.9, 0.4, 0.4), (0.7, 0.1, 0.1)]
}

dispersion_values = {
    "NiO@Co3O4": {"Fresh": 0.80, "Reduced": 0.19},
    "NiO@SiO2": {"Fresh": 0.41, "Reduced": 0.69},
    "NiO@ZrO2": {"Fresh": 0.36, "Reduced": 0.52},
    "NiO@CeO2": {"Fresh": 0.39, "Reduced": 0.42}
}

spot_colors = {
    "NiO@Co3O4": (0.4, 0.1, 0.4),  # dark purple
    "NiO@SiO2": (0.0, 0.0, 0.5),   # dark blue
    "NiO@ZrO2": (0.0, 0.4, 0.0),   # dark green
    "NiO@CeO2": (0.5, 0.0, 0.0)    # dark red
}

# Generate plots
for cat in gradient_specs:
    base = create_gradient_distribution(gradient_specs[cat], gradient_colors[cat], size=200, smoothness=2)
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    for ax, kind in zip(axs, ["Fresh", "Reduced"]):
        val = dispersion_values[cat][kind]
        image = overlay_circular_particles(base, val, spot_colors[cat], r=1)
        ax.imshow(image)
        ax.set_title(f"{cat} – {kind}")
        ax.axis('off')
    fig.suptitle(f"{cat}: Crisp Gradient + Fine Ni Dispersion", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

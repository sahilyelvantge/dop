import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

# Grid size for the dispersion map
grid_size = 200

def create_dispersion_distribution(fresh_value, reduced_value,
                                   fresh_color, reduced_color,
                                   size=200):
    """
    Create an RGBA array with random circular spots for fresh vs reduced catalysts.
    No blurring; spots have crisp edges.
    """
    rgba = np.ones((size, size, 4))  # white background, alpha=1

    # compute ratios
    total = fresh_value + reduced_value
    fresh_ratio = fresh_value / total if total > 0 else 0
    reduced_ratio = reduced_value / total if total > 0 else 0

    # number of spots (5% coverage scaled by ratio)
    num_fresh_spots = int(size * size * 0.05 * fresh_ratio)
    num_reduced_spots = int(size * size * 0.05 * reduced_ratio)

    def draw_spots(num_spots, color, value):
        for _ in range(num_spots):
            x = np.random.randint(0, size)
            y = np.random.randint(0, size)
            radius = np.random.randint(2, 7)
            intensity = (0.5 + np.random.random() * 0.5) * value * 2
            for i in range(max(0, x-radius), min(size, x+radius+1)):
                for j in range(max(0, y-radius), min(size, y+radius+1)):
                    d = np.hypot(i - x, j - y)
                    if d <= radius:
                        fade = 1 - (d / radius) ** 2
                        rgba[j, i, :3] = np.clip(color * intensity * fade, 0, 1)

    # draw fresh (green) and reduced (red) spots
    draw_spots(num_fresh_spots, np.array(fresh_color), fresh_value)
    draw_spots(num_reduced_spots, np.array(reduced_color), reduced_value)

    # light gray background for untouched pixels
    bg = (rgba[:, :, :3] == 1).all(axis=2)
    rgba[bg, :3] = 0.95

    return rgba, fresh_ratio * 100, reduced_ratio * 100

def visualize_dispersion(ax, fresh_value, reduced_value, title,
                         fresh_color, reduced_color):
    """Plot one catalyst’s dispersion map on the given Axes."""
    cmap, fp, rp = create_dispersion_distribution(
        fresh_value, reduced_value,
        fresh_color, reduced_color,
        size=grid_size
    )
    ax.imshow(cmap, interpolation='nearest')
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_xticks([]); ax.set_yticks([])

    # thin black border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)
        spine.set_color('black')

    # annotate percentages and values
    ax.text(0.05, 0.92, f"Fresh (F): {fresh_value} ({fp:.1f}%)",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor='white', alpha=0.7))
    ax.text(0.05, 0.84, f"Reduced (R): {reduced_value} ({rp:.1f}%)",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor='white', alpha=0.7))
    ax.text(0.05, 0.76, f"Total: {(fresh_value + reduced_value):.2f}",
            transform=ax.transAxes, fontsize=10, fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7))

# dataset
catalysts_data = {
    "NiO@Co₃O₄": {"Fresh": 0.80, "Reduced": 0.19},
    "NiO@CeO₂":  {"Fresh": 0.39, "Reduced": 0.42},
    "NiO@ZrO₂":  {"Fresh": 0.36, "Reduced": 0.52},
    "NiO@SiO₂":  {"Fresh": 0.41, "Reduced": 0.69}
}

# define colors
fresh_color   = (0.0, 0.7, 0.2)  # bright green
reduced_color = (0.9, 0.1, 0.1)  # bright red

# set up the figure
plt.figure(figsize=(16, 14))
gs = gridspec.GridSpec(2, 2)

# plot each catalyst
for i, (name, vals) in enumerate(catalysts_data.items()):
    ax = plt.subplot(gs[i])
    visualize_dispersion(ax,
                         vals["Fresh"],
                         vals["Reduced"],
                         name,
                         fresh_color,
                         reduced_color)

# create shared legend
legend_elements = [
    Patch(facecolor=fresh_color,   edgecolor='black', label='Fresh (F)'),
    Patch(facecolor=reduced_color, edgecolor='black', label='Reduced (R)')
]
plt.figlegend(
    handles=legend_elements,
    labels=['Fresh (F)', 'Reduced (R)'],
    loc='lower center',
    ncol=2,
    fontsize=12,
    bbox_to_anchor=(0.5, 0.02)
)

plt.suptitle('% Ni Dispersion for Fresh and Reduced Catalysts',
             fontsize=16)
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('catalyst_ni_dispersion_sharp.png', dpi=300,
            bbox_inches='tight')
plt.show()
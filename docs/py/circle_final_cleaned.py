import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from matplotlib.patches import Circle
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
import random

# Your catalyst data
catalysts = {
    "NiO@Ce3O4": {
        "Weak": 100,
        "Medium": 0,
        "High": 0
    },
    "NiO@SiO2": {
        "Weak": 59.3,
        "Medium": 9.43,
        "High": 31.3
    },
    "NiO@ZrO2": {
        "Weak": 5.70,
        "Medium": 0,
        "High": 94.3
    },
    "NiO@CeO2": {
        "Weak": 84.7,
        "Medium": 4.85,
        "High": 10.4
    }
}

# Custom color gradients for each catalyst
catalyst_gradients = {
    "NiO@Ce3O4": [(0.9, 0.8, 1.0), (0.7, 0.5, 0.9), (0.5, 0.2, 0.7)],  # Purple gradient
    "NiO@SiO2": [(0.8, 0.9, 1.0), (0.3, 0.6, 0.9), (0.1, 0.3, 0.8)],    # Blue gradient
    "NiO@ZrO2": [(0.8, 1.0, 0.8), (0.4, 0.8, 0.4), (0.1, 0.6, 0.3)],    # Green gradient
    "NiO@CeO2": [(1.0, 0.8, 0.8), (0.9, 0.4, 0.4), (0.7, 0.1, 0.1)]     # Red gradient
}

# Define texture patterns for different intensities
def create_texture_points(intensity, n_points=100):
    if intensity == "Weak":
        # Sparse, small dots pattern
        size = 5
        spacing = 0.15
    elif intensity == "Medium":
        # Medium density striped pattern
        size = 10
        spacing = 0.10
    else:  # High
        # Dense, larger bumps pattern
        size = 15
        spacing = 0.05
    
    return size, spacing

# Create a figure with subplots for each catalyst
fig = plt.figure(figsize=(16, 16))
spec = fig.add_gridspec(2, 2)

catalyst_list = list(catalysts.keys())

for i, catalyst in enumerate(catalyst_list):
    # Get subplot position
    row, col = i // 2, i % 2
    ax = fig.add_subplot(spec[row, col], projection='3d')
    
    # Get data for this catalyst
    catalyst_data = catalysts[catalyst]
    colors = catalyst_gradients[catalyst]
    
    # Calculate surface area for each intensity based on percentage
    intensity_areas = {"Weak": 0, "Medium": 0, "High": 0}
    for intensity, percentage in catalyst_data.items():
        intensity_areas[intensity] = percentage / 100.0
    
    # Base sphere
    radius = 1.0
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 50)
    
    # Generate base sphere points
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Calculate which points belong to which intensity
    # This maps spherical coordinates to intensity regions based on percentages
    intensity_points = {}
    
    # Create a mapping from surface points to intensity
    point_count = len(u) * len(v)
    point_assignments = []
    remaining_points = point_count
    
    # Assign points to intensities based on percentages
    for intensity, area in sorted(intensity_areas.items(), key=lambda x: x[1], reverse=True):
        if area > 0:
            n_points = int(area * point_count)
            if len(point_assignments) == 2:  # If this is the last intensity with non-zero area
                n_points = remaining_points
            point_assignments.extend([intensity] * n_points)
            remaining_points -= n_points
    
    # Shuffle to distribute points more naturally
    random.shuffle(point_assignments)
    
    # Create intensity mapping for each vertex
    intensity_map = np.zeros((len(u), len(v)), dtype=object)
    idx = 0
    for i in range(len(u)):
        for j in range(len(v)):
            if idx < len(point_assignments):
                intensity_map[i, j] = point_assignments[idx]
                idx += 1
            else:
                intensity_map[i, j] = "Weak"  # Default
    
    # Create color mapping based on intensity
    color_map = np.zeros((len(u), len(v), 3))
    for i in range(len(u)):
        for j in range(len(v)):
            intensity = intensity_map[i, j]
            if intensity == "Weak":
                color_map[i, j] = colors[0]
            elif intensity == "Medium":
                color_map[i, j] = colors[1]
            else:  # High
                color_map[i, j] = colors[2]
    
    # Apply texture/perturbation to the surface based on intensity type
    for i in range(len(u)):
        for j in range(len(v)):
            intensity = intensity_map[i, j]
            size, spacing = create_texture_points(intensity)
            
            # Add perturbation based on intensity texture
            if intensity == "Weak":
                # Smooth texture - small random perturbation
                perturbation = 0.02 * np.random.rand()
            elif intensity == "Medium":
                # Medium bumps - sinusoidal pattern
                perturbation = 0.05 * np.sin(u[i] / spacing) * np.cos(v[j] / spacing)
            else:  # High
                # Pronounced bumps - combined sinusoidal pattern
                perturbation = 0.08 * (np.sin(u[i] / spacing) * np.cos(v[j] / spacing) + 
                                      np.sin(2*u[i] / spacing) * np.cos(2*v[j] / spacing))
            
            # Apply perturbation to surface
            factor = 1.0 + perturbation
            x[i, j] *= factor
            y[i, j] *= factor
            z[i, j] *= factor
    
    # Plot the surface with color mapping
    ax.plot_surface(x, y, z, facecolors=color_map, alpha=0.9, linewidth=0, 
                    antialiased=True, shade=True)
    
    # Create legend elements - custom spheres for each intensity level
    legend_elements = []
    legend_labels = []
    
    # Position for the legend
    legend_x, legend_y, legend_z = 2.2, 0, 0
    legend_spacing = 0.7
    
    # Add legend spheres
    for i, (intensity, percentage) in enumerate(catalyst_data.items()):
        if percentage > 0:
            color_idx = 0 if intensity == "Weak" else 1 if intensity == "Medium" else 2
            size, spacing = create_texture_points(intensity)
            
            # Create small legend sphere
            legend_u = np.linspace(0, 2 * np.pi, 20)
            legend_v = np.linspace(0, np.pi, 10)
            
            legend_radius = 0.2
            legend_sphere_x = legend_radius * np.outer(np.cos(legend_u), np.sin(legend_v)) + legend_x
            legend_sphere_y = legend_radius * np.outer(np.sin(legend_u), np.sin(legend_v)) + legend_y - i * legend_spacing
            legend_sphere_z = legend_radius * np.outer(np.ones(np.size(legend_u)), np.cos(legend_v)) + legend_z
            
            # Apply texture to legend sphere
            for li in range(len(legend_u)):
                for lj in range(len(legend_v)):
                    if intensity == "Weak":
                        perturbation = 0.02 * np.random.rand()
                    elif intensity == "Medium":
                        perturbation = 0.05 * np.sin(legend_u[li] / spacing) * np.cos(legend_v[lj] / spacing)
                    else:  # High
                        perturbation = 0.08 * (np.sin(legend_u[li] / spacing) * np.cos(legend_v[lj] / spacing) + 
                                            np.sin(2*legend_u[li] / spacing) * np.cos(2*legend_v[lj] / spacing))
                    
                    # Apply perturbation to legend sphere
                    factor = 1.0 + perturbation
                    legend_sphere_x[li, lj] *= factor
                    legend_sphere_y[li, lj] *= factor
                    legend_sphere_z[li, lj] *= factor
            
            # Create color array for legend sphere
            legend_colors = np.zeros((len(legend_u), len(legend_v), 3))
            legend_colors[:,:] = colors[color_idx]
            
            # Plot legend sphere
            ax.plot_surface(legend_sphere_x, legend_sphere_y, legend_sphere_z, 
                            facecolors=legend_colors, alpha=0.9, linewidth=0, antialiased=True)
            
            # Add legend text
            ax.text(legend_x + 0.3, legend_y - i * legend_spacing, legend_z, 
                   f"{intensity}: {percentage:.1f}%", fontsize=10, ha='left', va='center')
    
    # Add percentage text near each significant area
    for intensity, percentage in catalyst_data.items():
        if percentage >= 10:  # Only add text for significant percentages
            # Find a representative point for this intensity
            for i in range(len(u)):
                for j in range(len(v)):
                    if intensity_map[i, j] == intensity:
                        # Text position slightly off the surface
                        text_x = x[i, j] * 1.1
                        text_y = y[i, j] * 1.1
                        text_z = z[i, j] * 1.1
                        ax.text(text_x, text_y, text_z, f"{percentage:.1f}%", 
                               fontsize=9, ha='center', va='center')
                        break
                else:
                    continue
                break
    
    # Set plot settings
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-1.5, 1.5)
    ax.set_title(f"{catalyst}", fontsize=16)
    ax.set_axis_off()
    
    # Set a consistent viewpoint
    ax.view_init(elev=30, azim=45)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.suptitle("Catalyst Molecular Simulation with Textured Surfaces", fontsize=20, y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.95)
plt.savefig('catalyst_molecular_simulation.png', dpi=300, bbox_inches='tight')
plt.show()
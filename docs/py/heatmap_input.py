import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec
import sys
import json

# Read input data from command line arguments
input_data = json.loads(sys.argv[1])
csv_data = input_data['csv'].strip().split('\n')

# Process the CSV data into catalyst data
catalysts = {}
for i, row in enumerate(csv_data):
    if not row:
        continue
    w, m, h = map(float, row.split(','))
    catalysts[f"Catalyst {i+1}"] = {
        "Weak": w,
        "Medium": m,
        "High": h
    }

# Generate color gradients for each catalyst (using the same color scheme as original)
color_palettes = [
    [(0.9, 0.8, 1.0), (0.7, 0.5, 0.9), (0.5, 0.2, 0.7)],  # Purple
    [(0.8, 0.9, 1.0), (0.3, 0.6, 0.9), (0.1, 0.3, 0.8)],  # Blue
    [(0.8, 1.0, 0.8), (0.4, 0.8, 0.4), (0.1, 0.6, 0.3)],  # Green
    [(1.0, 0.8, 0.8), (0.9, 0.4, 0.4), (0.7, 0.1, 0.1)]   # Red
]
# For more than 4 catalysts, cycle through the colors
catalyst_gradients = {}
for i, (name, _) in enumerate(catalysts.items()):
    catalyst_gradients[name] = color_palettes[i % len(color_palettes)]

# Parameters for visualization
grid_size = 200
sigma = 10  # Controls the smoothness of the gradient

# Function to create a more accurate gradient distribution
def create_gradient_distribution(percentages, colors, size=200, smoothness=10):
    # Special case for 100% single intensity
    if percentages["Weak"] == 100 or percentages["Medium"] == 100 or percentages["High"] == 100:
        # Create a uniform map with slight texture for visual interest
        # Determine which intensity is 100%
        if percentages["Weak"] == 100:
            base_color = colors[0]
            noise_range = 0.1  # Small noise range for texture
        elif percentages["Medium"] == 100:
            base_color = colors[1]
            noise_range = 0.1
        else:  # High == 100
            base_color = colors[2]
            noise_range = 0.1
            
        # Create base RGBA array filled with the single color
        r, g, b = base_color
        base_map = np.ones((size, size, 4))
        base_map[:, :, 0] = r
        base_map[:, :, 1] = g
        base_map[:, :, 2] = b
        base_map[:, :, 3] = 1.0  # Alpha channel
        
        # Add subtle texture with controlled random variation
        for i in range(3):  # RGB channels only
            noise = (np.random.rand(size, size) - 0.5) * noise_range
            base_map[:, :, i] = np.clip(base_map[:, :, i] + noise, 0, 1)
            
        return base_map, percentages
        
    # For mixed distributions, continue with gradient approach
    # Create an empty grid
    intensity_map = np.zeros((size, size))
    
    # Calculate number of points for each intensity
    total_cells = size * size
    n_weak = int(total_cells * percentages["Weak"] / 100)
    n_medium = int(total_cells * percentages["Medium"] / 100)
    n_high = int(total_cells * percentages["High"] / 100)
    
    # Adjust for rounding errors
    remainder = total_cells - (n_weak + n_medium + n_high)
    n_weak += remainder
    
    # Create more accurate distribution by using intensity thresholds
    flat_map = np.zeros(total_cells)
    
    # Fill with appropriate proportions
    flat_map[:n_weak] = 0  # Weak
    flat_map[n_weak:n_weak+n_medium] = 0.5  # Medium
    flat_map[n_weak+n_medium:] = 1.0  # High
    
    # Shuffle to randomize
    np.random.shuffle(flat_map)
    intensity_map = flat_map.reshape((size, size))
    
    # Apply gaussian filter for smoother transitions
    from scipy.ndimage import gaussian_filter
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    
    # Normalize the intensity map to 0-1 range
    if np.max(intensity_map) > np.min(intensity_map):  # Avoid division by zero
        intensity_map = (intensity_map - np.min(intensity_map)) / (np.max(intensity_map) - np.min(intensity_map))
    
    # Create custom colormap from the gradient colors
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)
    
    # Apply colormap to intensity map
    colored_map = cmap(intensity_map)
    
    # Verify the distribution by sampling points
    sampled_map = (intensity_map * 2).round() / 2  # Round to 0, 0.5, or 1
    unique, counts = np.unique(sampled_map, return_counts=True)
    count_dict = dict(zip(unique, counts))
    
    # Calculate actual percentages
    actual_percentages = {
        "Weak": count_dict.get(0, 0) / total_cells * 100,
        "Medium": count_dict.get(0.5, 0) / total_cells * 100,
        "High": count_dict.get(1, 0) / total_cells * 100
    }
    
    return colored_map, actual_percentages

# Create a figure with all catalysts
plt.figure(figsize=(16, 12))
num_catalysts = len(catalysts)
rows = int(np.ceil(num_catalysts / 2))
cols = 2 if num_catalysts > 1 else 1
gs = gridspec.GridSpec(rows, cols, wspace=0.3, hspace=0.4)

for i, (catalyst, percentages) in enumerate(catalysts.items()):
    gradient_colors = catalyst_gradients[catalyst]
    colored_map, actual_percentages = create_gradient_distribution(
        percentages, 
        gradient_colors, 
        size=grid_size, 
        smoothness=sigma
    )
    
    # Plot in the corresponding grid position
    ax = plt.subplot(gs[i])
    im = ax.imshow(colored_map, interpolation='gaussian')
    
    # Add border box around the figure
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_edgecolor('black')
    
    # Add title with actual percentages
    ax.set_title(f"{catalyst}\nWeak: {percentages['Weak']:.1f}%, Medium: {percentages['Medium']:.1f}%, High: {percentages['High']:.1f}%")
    ax.axis('off')
    
    # Create correct colorbar that matches the gradient colors
    cmap_for_colorbar = LinearSegmentedColormap.from_list('custom_cbar', gradient_colors, N=256)
    
    # Create a new axes for the colorbar
    cax = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap_for_colorbar), ax=ax, fraction=0.046, pad=0.04)
    cax.set_ticks([0.1, 0.5, 0.9])
    cax.set_ticklabels(['Weak', 'Medium', 'High'])

# Add an overall title
plt.suptitle("Elemental Mapping - Gradient Distribution", fontsize=16, y=0.98)

# Add a note about the visualization
note_text = "Note: Colors represent element intensity distribution. Gradients show spatial transitions between intensity levels."
plt.figtext(0.5, 0.01, note_text, ha='center', fontsize=10)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('elemental_mapping_gradient.png', dpi=300, bbox_inches='tight')
plt.show()

# Individual plots for each catalyst
for catalyst, percentages in catalysts.items():
    # Create a more sophisticated figure
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    
    # Main plot
    ax_main = plt.subplot(gs[0])
    
    # Generate the gradient map
    gradient_colors = catalyst_gradients[catalyst]
    colored_map, actual_percentages = create_gradient_distribution(
        percentages, 
        gradient_colors, 
        size=grid_size, 
        smoothness=sigma
    )
    
    # Display the gradient map
    im = ax_main.imshow(colored_map, interpolation='gaussian')
    
    # Add border box around the figure
    for spine in ax_main.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)
        spine.set_edgecolor('black')
    
    ax_main.set_title(f"Elemental Mapping for {catalyst}", fontsize=14)
    ax_main.axis('off')
    
    # Create correct colorbar that matches the gradient colors
    cmap_for_colorbar = LinearSegmentedColormap.from_list('custom_cbar', gradient_colors, N=256)
    
    # Only include intensity levels that are present in the data
    tick_positions = []
    tick_labels = []
    
    if percentages["Weak"] > 0:
        tick_positions.append(0.1)
        tick_labels.append('Weak')
    
    if percentages["Medium"] > 0:
        tick_positions.append(0.5)
        tick_labels.append('Medium')
    
    if percentages["High"] > 0:
        tick_positions.append(0.9)
        tick_labels.append('High')
    
    # Create a new colorbar with the correct colormap
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap_for_colorbar), ax=ax_main, fraction=0.046, pad=0.04)
    cbar.set_ticks(tick_positions)
    cbar.set_ticklabels(tick_labels)
    
    # Add a histogram in the bottom panel
    ax_hist = plt.subplot(gs[1])
    
    # Data for histogram
    hist_data = [percentages["Weak"], percentages["Medium"], percentages["High"]]
    categories = ["Weak", "Medium", "High"]
    
    # Only show bars for non-zero percentages
    active_categories = []
    active_data = []
    active_colors = []
    
    for i, (cat, val) in enumerate(zip(categories, hist_data)):
        if val > 0:
            active_categories.append(cat)
            active_data.append(val)
            active_colors.append(gradient_colors[i])
    
    # Plot histogram
    bars = ax_hist.bar(active_categories, active_data, color=active_colors)
    
    # Add percentage labels on top of each bar
    for bar, percentage in zip(bars, active_data):
        height = bar.get_height()
        ax_hist.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{percentage:.1f}%', ha='center', va='bottom', fontsize=10)
    
    ax_hist.set_ylabel("Percentage (%)")
    ax_hist.set_title("Intensity Distribution")
    ax_hist.set_ylim(0, 105)  # Leave room for text labels
    
    plt.tight_layout()
    plt.savefig(f'{catalyst}_elemental_mapping.png', dpi=300, bbox_inches='tight')
    #plt.show()
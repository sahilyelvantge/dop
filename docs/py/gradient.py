import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# Data for each catalyst
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

# Colors for each catalyst
catalyst_colors = {
    "NiO@Ce3O4": "yellow",
    "NiO@SiO2": "blue",
    "NiO@ZrO2": "green",
    "NiO@CeO2": "red"
}

# Colors for weak, medium, high basicity (shades of the catalyst color)
def get_shade_color(base_color, intensity):
    if intensity == "Weak":
        return plt.cm.colors.to_rgb(base_color) + (0.3,)  # Light shade
    elif intensity == "Medium":
        return plt.cm.colors.to_rgb(base_color) + (0.6,)  # Medium shade
    elif intensity == "High":
        return plt.cm.colors.to_rgb(base_color) + (1.0,)  # Dark shade

# Function to create a grid with random distribution of colors
def create_distribution_grid(percentages, base_color, grid_size=100):
    grid = np.zeros((grid_size, grid_size), dtype=int)
    total_cells = grid_size * grid_size
    
    # Calculate the number of cells for each category
    weak_cells = int(total_cells * percentages["Weak"] / 100)
    medium_cells = int(total_cells * percentages["Medium"] / 100)
    high_cells = int(total_cells * percentages["High"] / 100)
    
    # Flatten the grid and assign colors
    flat_grid = grid.flatten()
    flat_grid[:weak_cells] = 0  # Weak
    flat_grid[weak_cells:weak_cells + medium_cells] = 1  # Medium
    flat_grid[weak_cells + medium_cells:weak_cells + medium_cells + high_cells] = 2  # High
    
    # Shuffle to randomize the distribution
    np.random.shuffle(flat_grid)
    
    # Reshape back to 2D grid
    grid = flat_grid.reshape((grid_size, grid_size))
    
    # Create a color grid
    color_grid = np.zeros((grid_size, grid_size, 4))  # RGBA format
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i, j] == 0:
                color_grid[i, j] = get_shade_color(base_color, "Weak")
            elif grid[i, j] == 1:
                color_grid[i, j] = get_shade_color(base_color, "Medium")
            else:
                color_grid[i, j] = get_shade_color(base_color, "High")
    
    return color_grid

# Create a grid for each catalyst
grid_size = 400
for catalyst, percentages in catalysts.items():
    base_color = catalyst_colors[catalyst]
    color_grid = create_distribution_grid(percentages, base_color, grid_size)
    
    plt.figure(figsize=(6, 6))
    plt.imshow(color_grid, interpolation='nearest')
    plt.title(f"Basicity Distribution for {catalyst}")
    plt.axis('off')
    
    # Create a legend
    legend_elements = [
        Patch(facecolor=get_shade_color(base_color, "Weak"), label='Weak'),
        Patch(facecolor=get_shade_color(base_color, "Medium"), label='Medium'),
        Patch(facecolor=get_shade_color(base_color, "High"), label='High')
    ]
    
    # Add the legend below the graph
    plt.legend(handles=legend_elements, bbox_to_anchor=(0.5, -0.05), loc='upper center', ncol=3)
    
    plt.tight_layout()
    plt.show()
import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors

# ---------- scipy import handling -----------------------------------
try:
    # First try normal scipy import
    from scipy.ndimage import gaussian_filter
    has_scipy = True
except ImportError:
    has_scipy = False
    try:
        # Fallback for Pyodide environments
        import micropip
        async def install_scipy():
            await micropip.install("scipy")
            from scipy.ndimage import gaussian_filter
            return gaussian_filter
        # Note: In Pyodide, you'd need to await this separately
        # gaussian_filter = await install_scipy()
        # For now we'll fall through to the numpy implementation
    except ImportError:
        pass

# Pure numpy fallback for gaussian filter
if not has_scipy:
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

# ---------- parse CSV ------------------------------------------------
csv = (args.get("csv","") or "").strip()
if not csv: csv = "100,0,0"

specs=[]
for ln in csv.splitlines():
    try:
        w,m,h=map(float,ln.split(",")[:3])
        tot=max(w+m+h,1e-6)
        specs.append({"Weak":w/tot*100,"Medium":m/tot*100,"High":h/tot*100})
    except ValueError: pass

if not specs:
    specs=[{"Weak":100,"Medium":0,"High":0}]

# ---------- palettes ------------------------------------------------
palettes=[
    [(0.9, 0.8, 1.0), (0.7, 0.5, 0.9), (0.5, 0.2, 0.7)],  # Purple
    [(0.8, 0.9, 1.0), (0.3, 0.6, 0.9), (0.1, 0.3, 0.8)],  # Blue
    [(0.8, 1.0, 0.8), (0.4, 0.8, 0.4), (0.1, 0.6, 0.3)],  # Green
    [(1.0, 0.8, 0.8), (0.9, 0.4, 0.4), (0.7, 0.1, 0.1)]   # Red
]

# ---------- gradient distribution -----------------------------------
def create_gradient_distribution(percentages, colors, size=200, smoothness=10):
    if percentages["Weak"] == 100 or percentages["Medium"] == 100 or percentages["High"] == 100:
        if percentages["Weak"] == 100:
            base_color = colors[0]
        elif percentages["Medium"] == 100:
            base_color = colors[1]
        else:
            base_color = colors[2]
            
        base_map = np.zeros((size, size, 3))
        base_map[:,:,:] = base_color
        return base_map
        
    intensity_map = np.zeros((size, size))
    total = size * size
    n_weak = int(total * percentages["Weak"] / 100)
    n_medium = int(total * percentages["Medium"] / 100)
    
    flat = np.zeros(total)
    flat[:n_weak] = 0
    flat[n_weak:n_weak+n_medium] = 0.5
    flat[n_weak+n_medium:] = 1.0
    
    np.random.shuffle(flat)
    intensity_map = flat.reshape((size, size))
    intensity_map = gaussian_filter(intensity_map, sigma=smoothness)
    
    if np.max(intensity_map) > np.min(intensity_map):
        intensity_map = (intensity_map - np.min(intensity_map)) / (np.max(intensity_map) - np.min(intensity_map))
    
    cmap = mcolors.LinearSegmentedColormap.from_list('cmap', colors, N=256)
    return cmap(intensity_map)

# ---------- build figure -------------------------------------------
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)
fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows), squeeze=False)
fig.suptitle("Elemental Mapping - Gradient Distribution", fontsize=16, y=0.96)

for idx, pct in enumerate(specs):
    r, c = divmod(idx, cols)
    ax = axes[r][c]
    colors = palettes[idx % len(palettes)]
    img = create_gradient_distribution(pct, colors)
    
    ax.imshow(img, interpolation='gaussian')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_edgecolor('black')
    
    cmap = mcolors.LinearSegmentedColormap.from_list('cbar', colors, N=256)
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), ax=ax, fraction=0.045, pad=0.04)
    
    ticks, labels = [], []
    if pct["Weak"] > 0:
        ticks.append(0.1)
        labels.append('Weak')
    if pct["Medium"] > 0:
        ticks.append(0.5)
        labels.append('Medium')
    if pct["High"] > 0:
        ticks.append(0.9)
        labels.append('High')
    
    cb.set_ticks(ticks)
    cb.set_ticklabels(labels)
    
    ax.set_title(f"Catalyst {idx+1}\nWeak: {pct['Weak']:.1f}%, Medium: {pct['Medium']:.1f}%, High: {pct['High']:.1f}%")
    ax.axis('off')

for k in range(n, rows*cols):
    axes[k//cols][k%cols].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.94])
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec
import math

# ─── Read user CSV input --------------------------------------------
csv = (args.get("csv", "") or "").strip()
if not csv:
    csv = "0.80,0.19"

specs = []
for line in csv.splitlines():
    parts = [p.strip() for p in line.split(",")[:2]]
    if len(parts) != 2:
        continue
    try:
        fresh, reduced = map(float, parts)
        specs.append({"Fresh": fresh, "Reduced": reduced})
    except ValueError:
        continue
if not specs:
    specs = [{"Fresh": 0, "Reduced": 0}]

# ─── Colors & grid --------------------------------------------------
fresh_color   = (0.0, 0.7, 0.2)  # bright green
reduced_color = (0.9, 0.1, 0.1)  # bright red
grid_size = 200

# ─── Core spot‐drawing logic (unchanged) ----------------------------
def create_dispersion_distribution(fresh_value, reduced_value,
                                   fresh_color, reduced_color,
                                   size=200):
    rgba = np.ones((size, size, 4))
    total = fresh_value + reduced_value
    fr = fresh_value / total if total>0 else 0
    rr = reduced_value / total if total>0 else 0
    nf = int(size*size*0.05*fr)
    nr = int(size*size*0.05*rr)
    def draw_spots(n,color,val):
        for _ in range(n):
            x = np.random.randint(0,size)
            y = np.random.randint(0,size)
            r = np.random.randint(2,7)
            inten = (0.5+np.random.random()*0.5)*val*2
            for i in range(max(0,x-r),min(size,x+r+1)):
                for j in range(max(0,y-r),min(size,y+r+1)):
                    d = np.hypot(i-x,j-y)
                    if d<=r:
                        fade = 1-(d/r)**2
                        rgba[j,i,:3] = np.clip(color*inten*fade,0,1)
    draw_spots(nf, np.array(fresh_color), fresh_value)
    draw_spots(nr, np.array(reduced_color), reduced_value)
    bg = (rgba[:,:,:3]==1).all(axis=2)
    rgba[bg,:3]=0.95
    return rgba, fr*100, rr*100

# ─── Plot dynamic grid ----------------------------------------------
n = len(specs)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n/cols)
fig = plt.figure(figsize=(6*cols, 6*rows))
gs = gridspec.GridSpec(rows, cols, wspace=0.3, hspace=0.4)

for idx, spec in enumerate(specs):
    rgba_map, fp, rp = create_dispersion_distribution(
        spec["Fresh"], spec["Reduced"],
        fresh_color, reduced_color,
        size=grid_size
    )
    r = idx//cols; c = idx%cols
    ax = fig.add_subplot(gs[r,c])
    ax.imshow(rgba_map, interpolation="nearest")
    ax.set_title(f"Catalyst {idx+1}", fontsize=12, pad=8)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True); spine.set_linewidth(1); spine.set_color("black")
    ax.text(0.05,0.92,f"Fresh: {spec['Fresh']} ({fp:.1f}%)",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor='white',alpha=0.7))
    ax.text(0.05,0.84,f"Reduced: {spec['Reduced']} ({rp:.1f}%)",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor='white',alpha=0.7))
    ax.text(0.05,0.76,f"Total: {(spec['Fresh']+spec['Reduced']):.2f}",
            transform=ax.transAxes, fontsize=10, fontweight="bold",
            bbox=dict(facecolor='white',alpha=0.7))

# shared legend
legend_elements = [
    Patch(facecolor=fresh_color, edgecolor='black', label='Fresh'),
    Patch(facecolor=reduced_color, edgecolor='black', label='Reduced')
]
plt.figlegend(handles=legend_elements,
              labels=['Fresh','Reduced'],
              loc='lower center', ncol=2,
              fontsize=12, bbox_to_anchor=(0.5,0.02))

plt.suptitle("Dispersion Maps for Fresh & Reduced Catalysts", fontsize=16, y=1.02)
plt.tight_layout(rect=[0,0.05,1,0.95])
"""
heatmap_input.py  – true‑quantile smooth gradients
--------------------------------------------------
args["csv"]  -> lines of  Weak,Medium,High
Outputs the classic 'Elemental Mapping – Gradient Distribution' figure.
"""

import numpy as np, matplotlib.pyplot as plt, math, matplotlib.colors as mcolors

# ---------- parse CSV ------------------------------------------------
csv = (args.get("csv","") or "").strip()
if not csv: csv = "100,0,0"

specs=[]
for ln in csv.splitlines():
    try:
        w,m,h=map(float,ln.split(",")[:3])
        tot=max(w+m+h,1e-6)
        specs.append({"Weak":w/tot,"Medium":m/tot,"High":h/tot})
    except ValueError: pass

if not specs:
    specs=[{"Weak":1,"Medium":0,"High":0}]

# ---------- palettes (cycled) ---------------------------------------
palettes=[
    [(0.96,0.88,1.0),(0.75,0.55,0.95),(0.45,0.25,0.75)],
    [(0.92,0.95,1.0),(0.40,0.70,0.96),(0.12,0.35,0.85)],
    [(0.92,1.0 ,0.92),(0.45,0.85,0.45),(0.10,0.60,0.30)],
    [(1.0 ,0.92,0.92),(0.95,0.45,0.45),(0.75,0.15,0.15)],
]

# ---------- smooth noise helper -------------------------------------
def smooth_noise(sz=200, passes=6):
    x=np.random.rand(sz,sz)
    for _ in range(passes):
        x=(x+np.roll(x,1,0)+np.roll(x,-1,0)+np.roll(x,1,1)+np.roll(x,-1,1))/5
    return x

# ---------- build figure -------------------------------------------
n=len(specs); cols=math.ceil(math.sqrt(n)); rows_grid=math.ceil(n/cols)
fig,axes=plt.subplots(rows_grid,cols,figsize=(5*cols,4*rows_grid),squeeze=False)
fig.suptitle("Elemental Mapping – Gradient Distribution",fontsize=16,y=.96)

for idx,pct in enumerate(specs):
    r,c=divmod(idx,cols); ax=axes[r][c]
    field=smooth_noise()

    # quantile thresholds so exact area matches percentages
    q1=np.quantile(field,pct["Weak"])
    q2=np.quantile(field,pct["Weak"]+pct["Medium"])

    pal=palettes[idx%len(palettes)]
    cmap=mcolors.LinearSegmentedColormap.from_list(f"pal{idx}",pal,N=256)

    # map field into 0‑1 scale piece‑wise to keep 3 bands distinct
    scaled=np.empty_like(field)
    mask1=field<=q1
    mask2=(field>q1)&(field<=q2)
    mask3=field>q2

    # Weak band maps to 0‑0.33 (light)
    scaled[mask1]=(field[mask1]-field.min())/(q1-field.min()+1e-9)*0.33
    # Medium band maps to 0.34‑0.66
    scaled[mask2]=0.34+(field[mask2]-q1)/(q2-q1+1e-9)*0.32
    # High band maps to 0.67‑1
    scaled[mask3]=0.67+(field[mask3]-q2)/(field.max()-q2+1e-9)*0.33

    im=ax.imshow(scaled,cmap=cmap,interpolation="bilinear")
    ax.set_axis_off()

    cb=fig.colorbar(im,ax=ax,fraction=0.045,pad=0.02,ticks=[0.17,0.50,0.83])
    cb.ax.set_yticklabels(["Weak","Medium","High"],fontsize=9)

    ax.set_title(
        f"Catalyst {idx+1}\n"
        f"Weak: {pct['Weak']*100:.1f}%, Medium: {pct['Medium']*100:.1f}%, High: {pct['High']*100:.1f}%",
        fontsize=11
    )

# hide unused axes
for k in range(n,rows_grid*cols):
    axes[k//cols][k%cols].set_visible(False)

plt.tight_layout(rect=[0,0,1,0.94])
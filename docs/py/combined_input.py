import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
from scipy.ndimage import gaussian_filter
import math

# ─── Read CSV of 5 values per catalyst -----------------------------
csv = (args.get("csv","") or "").strip()
if not csv:
    csv = "100,0,0,0.80,0.19"

rows=[]
for ln in csv.splitlines():
    parts = [p.strip() for p in ln.split(",")[:5]]
    if len(parts)!=5: continue
    try:
        w,m,h,f,r = map(float, parts)
        rows.append({
            "Weak":w, "Medium":m, "High":h,
            "Fresh":f, "Reduced":r
        })
    except:
        continue
if not rows:
    rows=[{"Weak":100,"Medium":0,"High":0,"Fresh":0,"Reduced":0}]

# ─── Color palettes & spot-colors -----------------------------------
gradient_palettes=[
    [(0.9,0.8,1.0),(0.7,0.5,0.9),(0.5,0.2,0.7)],   # purple
    [(0.8,0.9,1.0),(0.3,0.6,0.9),(0.1,0.3,0.8)],   # blue
    [(0.8,1.0,0.8),(0.4,0.8,0.4),(0.1,0.6,0.3)],   # green
    [(1.0,0.8,0.8),(0.9,0.4,0.4),(0.7,0.1,0.1)]    # red
]
spot_palettes=[
    (0.4,0.1,0.4),  # dark purple
    (0.0,0.0,0.5),  # dark blue
    (0.0,0.4,0.0),  # dark green
    (0.5,0.0,0.0)   # dark red
]

# ─── Gradient generator (your exact logic) -------------------------
def create_gradient_distribution(percentages, colors, size=200, smoothness=2):
    H=W=size; total=H*W
    # all-100 special case
    if 100 in percentages.values():
        base_idx = list(percentages.values()).index(100)/2
        noise = np.random.rand(H,W)*0.05
        intensity = np.clip(base_idx+noise,0,1)
    else:
        n_w = int(percentages['Weak']/100*total)
        n_m = int(percentages['Medium']/100*total)
        flat = np.zeros(total,float)
        flat[n_w:n_w+n_m]=0.5
        flat[n_w+n_m:]=1.0
        np.random.shuffle(flat)
        intensity = gaussian_filter(flat.reshape(H,W),sigma=smoothness)
        mn,mx = intensity.min(), intensity.max()
        intensity = (intensity-mn)/(mx-mn) if mx>mn else intensity
    cmap = LinearSegmentedColormap.from_list('grad',colors,N=256)
    return cmap(intensity)

# ─── Overlay smooth circles (your exact logic) ----------------------
def overlay_smooth_circles(colmap,val,spot_color,
                           r=2.5,cluster_size=7,cluster_count=8,single_fraction=0.5):
    H,W,_ = colmap.shape
    overlay = colmap.copy()
    num_spots = int(H*W*(val/100.0))
    num_single = int(num_spots*single_fraction)
    num_cluster = num_spots - num_single
    per_cluster = max(1,num_cluster//cluster_count)
    # high-res circle drawer
    def draw_circle(cx,cy,rad):
        for dy in range(-int(rad)-1,int(rad)+2):
            for dx in range(-int(rad)-1,int(rad)+2):
                x,y = cx+dx, cy+dy
                if 0<=x<W and 0<=y<H:
                    d = math.hypot(dx,dy)
                    if d<=rad:
                        alpha = 1.0 if d<=rad-0.5 else (rad-d+0.5)
                        bg = overlay[y,x,:3]
                        overlay[y,x,:3] = (1-alpha)*bg + alpha*np.array(spot_color)
    # clusters
    centers = [(random.randint(int(r)+5,W-int(r)-5),
                random.randint(int(r)+5,H-int(r)-5))
               for _ in range(cluster_count)]
    for cx,cy in centers:
        for _ in range(per_cluster):
            ox = random.randint(-cluster_size,cluster_size)
            oy = random.randint(-cluster_size,cluster_size)
            draw_circle(cx+ox, cy+oy, r)
    # singles
    coords = [(x,y) for x in range(int(r)+1,W-int(r)-1)
                    for y in range(int(r)+1,H-int(r)-1)]
    for x,y in random.sample(coords,min(num_single,len(coords))):
        draw_circle(x,y,r)
    return overlay

# ─── Plot all rows: 2 cols × N rows ----------------------------------
N = len(rows)
fig, axes = plt.subplots(N, 2,
    figsize=(6*2, 5*N), squeeze=False)
plt.suptitle("Combined Gradient + Dispersion", fontsize=16, y=0.92)

for idx,spec in enumerate(rows):
    grad = create_gradient_distribution(
        spec, gradient_palettes[idx%len(gradient_palettes)],
        size=200, smoothness=2
    )
    spot_c = spot_palettes[idx%len(spot_palettes)]
    # left: Fresh overlay
    axL = axes[idx][0]
    imgF = overlay_smooth_circles(grad,spec["Fresh"],spot_c)
    axL.imshow(imgF); axL.set_title(f"Catalyst {idx+1} – Fresh"); axL.axis('off')
    # right: Reduced overlay
    axR = axes[idx][1]
    imgR = overlay_smooth_circles(grad,spec["Reduced"],spot_c)
    axR.imshow(imgR); axR.set_title(f"Catalyst {idx+1} – Reduced"); axR.axis('off')

plt.tight_layout(rect=[0,0,1,0.90])
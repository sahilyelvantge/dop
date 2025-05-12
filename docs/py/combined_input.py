import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
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
        rows.append({"Weak":w, "Medium":m, "High":h, "Fresh":f, "Reduced":r})
    except:
        continue
if not rows:
    rows=[{"Weak":100,"Medium":0,"High":0,"Fresh":0,"Reduced":0}]

# ─── Palettes for background & spots -------------------------------
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

# ─── NumPy Gaussian blur (separable) -------------------------------
def gaussian_blur(img, sigma=2):
    if sigma<=0: return img
    # build 1D kernel
    radius = int(3*sigma)
    x = np.arange(-radius, radius+1)
    kernel = np.exp(-0.5*(x/sigma)**2)
    kernel /= kernel.sum()
    # blur rows
    temp = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode='same'),
                               1, img)
    # blur cols
    blurred = np.apply_along_axis(lambda col: np.convolve(col, kernel, mode='same'),
                                  0, temp)
    return blurred

# ─── Gradient generator (identical logic) -------------------------
def create_gradient_distribution(pct, colors, size=200, smoothness=2):
    H=W=size; total=H*W
    if 100 in pct.values():
        idx = list(pct.values()).index(100)/2
        noise = np.random.rand(H,W)*0.05
        intensity = np.clip(idx+noise,0,1)
    else:
        n_w = int(pct['Weak']/100*total)
        n_m = int(pct['Medium']/100*total)
        flat = np.zeros(total, float)
        flat[n_w:n_w+n_m] = 0.5
        flat[n_w+n_m:] = 1.0
        np.random.shuffle(flat)
        intensity = gaussian_blur(flat.reshape(H,W), sigma=smoothness)
        mn,mx = intensity.min(), intensity.max()
        if mx>mn:
            intensity = (intensity-mn)/(mx-mn)
    cmap = LinearSegmentedColormap.from_list('grad', colors, N=256)
    return cmap(intensity)

# ─── Overlay smooth circles (identical logic) ----------------------
def overlay_smooth_circles(base_map, val, spot_color,
                           r=2.5, cluster_size=7, cluster_count=8, single_fraction=0.5):
    H,W,_ = base_map.shape
    overlay = base_map.copy()
    num_spots = int(H*W*(val/100.0))
    num_single = int(num_spots*single_fraction)
    num_cluster = num_spots - num_single
    per_cluster = max(1, num_cluster//cluster_count)

    def draw_circle(cx,cy,rad):
        for dy in range(-int(rad)-1, int(rad)+2):
            for dx in range(-int(rad)-1, int(rad)+2):
                x, y = cx+dx, cy+dy
                if 0<=x<W and 0<=y<H:
                    d = math.hypot(dx,dy)
                    if d<=rad:
                        alpha = 1.0 if d<=rad-0.5 else (rad-d+0.5)
                        bg = overlay[y,x,:3]
                        overlay[y,x,:3] = (1-alpha)*bg + alpha*np.array(spot_color)

    # cluster spots
    centers = [(random.randint(int(r)+5, W-int(r)-5),
                random.randint(int(r)+5, H-int(r)-5))
               for _ in range(cluster_count)]
    for cx,cy in centers:
        for _ in range(per_cluster):
            ox, oy = random.randint(-cluster_size,cluster_size), random.randint(-cluster_size,cluster_size)
            draw_circle(cx+ox, cy+oy, r)

    # single spots
    coords = [(x,y) for x in range(int(r)+1, W-int(r)-1) for y in range(int(r)+1, H-int(r)-1)]
    for x,y in random.sample(coords, min(num_single, len(coords))):
        draw_circle(x, y, r)

    return overlay

# ─── Render N rows × 2 cols -----------------------------------------
N=len(rows)
fig, axes = plt.subplots(N, 2, figsize=(6*2, 5*N), squeeze=False)
plt.suptitle("Combined Gradient + Dispersion", fontsize=16, y=0.92)

for i, pct in enumerate(rows):
    grad = create_gradient_distribution(
        pct, gradient_palettes[i%len(gradient_palettes)],
        size=200, smoothness=2
    )
    spot_c = spot_palettes[i%len(spot_palettes)]
    # Fresh
    imgF = overlay_smooth_circles(grad, pct["Fresh"], spot_c)
    axF = axes[i][0]
    axF.imshow(imgF); axF.set_title(f"Catalyst {i+1} – Fresh"); axF.axis('off')
    # Reduced
    imgR = overlay_smooth_circles(grad, pct["Reduced"], spot_c)
    axR = axes[i][1]
    axR.imshow(imgR); axR.set_title(f"Catalyst {i+1} – Reduced"); axR.axis('off')

plt.tight_layout(rect=[0,0,1,0.90])
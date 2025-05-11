"""
circle_input.py  –  dynamic version
-----------------------------------
Reads a CSV list of catalysts from args["csv"]:

    NiO@Ce3O4,100,0,0
    NiO@SiO2,59.3,9.43,31.3
    ...

For each row it draws a textured sphere whose surface areas follow
Weak / Medium / High percentages.  All spheres are placed in an NxM grid.
"""
import matplotlib.pyplot as plt, numpy as np, random, math, io, base64, json

# -------- helper for bump parameters -----------------------------
def tex_params(inten):
    return (5,0.15) if inten=="Weak" else (10,0.10) if inten=="Medium" else (15,0.05)

def make_gradient(i):
    """Return 3 RGB tuples, cycling through 4 base palettes."""
    palettes = [
        [(0.9,0.8,1.0),(0.7,0.5,0.9),(0.5,0.2,0.7)],   # purple
        [(0.8,0.9,1.0),(0.3,0.6,0.9),(0.1,0.3,0.8)],   # blue
        [(0.8,1.0,0.8),(0.4,0.8,0.4),(0.1,0.6,0.3)],   # green
        [(1.0,0.8,0.8),(0.9,0.4,0.4),(0.7,0.1,0.1)]    # red
    ]
    return palettes[i % len(palettes)]

def sphere(ax, perc, colors, title):
    u = np.linspace(0, 2*np.pi, 100)
    v = np.linspace(0, np.pi, 50)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(u.size), np.cos(v))

    verts = len(u)*len(v)
    order = (["Weak"]*int(perc["Weak"]/100*verts) +
             ["Medium"]*int(perc["Medium"]/100*verts))
    order += ["High"]*(verts-len(order))
    random.shuffle(order)
    idx = 0

    cmap = np.zeros((len(u),len(v),3))
    for i in range(len(u)):
        for j in range(len(v)):
            inten = order[idx]; idx += 1
            cmap[i,j] = colors[0] if inten=="Weak" else colors[1] if inten=="Medium" else colors[2]
            size,space = tex_params(inten)
            if inten=="Weak":
                bump = 0.02*np.random.rand()
            elif inten=="Medium":
                bump = 0.05*np.sin(u[i]/space)*np.cos(v[j]/space)
            else:
                bump = 0.08*(np.sin(u[i]/space)*np.cos(v[j]/space)+
                             np.sin(2*u[i]/space)*np.cos(2*v[j]/space))
            factor = 1+bump
            x[i,j]*=factor; y[i,j]*=factor; z[i,j]*=factor

    ax.plot_surface(x,y,z,facecolors=cmap,linewidth=0,alpha=0.9,shade=True)
    ax.set_axis_off(); ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4); ax.set_zlim(-1.4,1.4)
    ax.view_init(elev=30, azim=45)
    ax.set_title(title, fontsize=10)

# -------- parse incoming args ------------------------------------
try:
    csv_text = args["csv"]
except Exception:
    csv_text = "NiO@Ce3O4,100,0,0"

rows = [l.strip() for l in csv_text.splitlines() if l.strip()]
catalysts = []
for line in rows:
    name,*vals = [s.strip() for s in line.split(",")]
    if len(vals)!=3: continue
    w,m,h = map(float, vals)
    catalysts.append((name, {"Weak":w,"Medium":m,"High":h}))

if not catalysts:
    catalysts = [("Example", {"Weak":100,"Medium":0,"High":0})]

# -------- build figure ------------------------------------------
n = len(catalysts)
cols = math.ceil(math.sqrt(n))
rows = math.ceil(n / cols)
fig = plt.figure(figsize=(5*cols, 4*rows))
grid = fig.add_gridspec(rows, cols)

for idx,(name,perc) in enumerate(catalysts):
    r,c = divmod(idx, cols)
    ax = fig.add_subplot(grid[r,c], projection='3d')
    sphere(ax, perc, make_gradient(idx), name)

fig.suptitle("Catalyst Textured Spheres", fontsize=14)
import matplotlib.pyplot as plt
import numpy as np
import random

# ---- collect user args --------------------------------------------------
try:
    args          # provided by run_demo.js
except NameError:
    args = {}

weak_pct  = float(args.get("Weak",   100))
med_pct   = float(args.get("Medium",   0))
high_pct  = float(args.get("High",    0))

# purple gradient (user can override with a list of 3 RGB tuples)
default_col = [(0.9,0.8,1.0), (0.7,0.5,0.9), (0.5,0.2,0.7)]
colors = args.get("colors", default_col)

data = {"Weak": weak_pct, "Medium": med_pct, "High": high_pct}

# ---- helper for bump parameters -----------------------------------------
def tex_params(inten):
    if inten == "Weak":   return 5, 0.15
    if inten == "Medium": return 10, 0.10
    return 15, 0.05

# ---- build textured sphere ----------------------------------------------
fig = plt.figure(figsize=(6,6))
ax  = fig.add_subplot(111, projection='3d')

u = np.linspace(0, 2*np.pi, 100)
v = np.linspace(0,     np.pi, 50)
x = np.outer(np.cos(u), np.sin(v))
y = np.outer(np.sin(u), np.sin(v))
z = np.outer(np.ones(u.size), np.cos(v))

# assign each vertex an intensity according to %, shuffled for randomness
verts = len(u) * len(v)
order = (["Weak"]*int(data["Weak"]/100*verts) +
         ["Medium"]*int(data["Medium"]/100*verts))
order += ["High"]*(verts-len(order))
random.shuffle(order)

imap, idx = np.empty((len(u),len(v)), object), 0
for i in range(len(u)):
    for j in range(len(v)):
        imap[i,j] = order[idx]; idx += 1

cmap = np.zeros((len(u),len(v),3))

for i in range(len(u)):
    for j in range(len(v)):
        inten = imap[i,j]
        cmap[i,j] = colors[0] if inten=="Weak" else \
                    colors[1] if inten=="Medium" else colors[2]

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

ax.plot_surface(x, y, z, facecolors=cmap, alpha=.9, linewidth=0, shade=True)

# ---- legend to the side --------------------------------------------------
lx, ly, lz = 2.2, 0, 0
gap = 0.7
for k,(inten,pct) in enumerate(data.items()):
    if pct<=0: continue
    col = colors[0] if inten=="Weak" else colors[1] if inten=="Medium" else colors[2]
    lu = np.linspace(0,2*np.pi,20); lv=np.linspace(0,np.pi,10); r=0.2
    sx = r*np.outer(np.cos(lu),np.sin(lv))+lx
    sy = r*np.outer(np.sin(lu),np.sin(lv))+ly-k*gap
    sz = r*np.outer(np.ones(lu.size),np.cos(lv))+lz
    ax.plot_surface(sx, sy, sz, color=col, alpha=.85, linewidth=0, zorder=1)
    ax.text(lx+.3, ly-k*gap, lz, f"{inten}: {pct:.1f}%", zorder=10,
            color='black', backgroundcolor='white')

ax.set_axis_off(); ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5); ax.set_zlim(-1.5,1.5)
ax.view_init(elev=30, azim=45)
plt.title("Textured Sphere")
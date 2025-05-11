"""
Reads args["csv"]  – a plain‑text block:
    100,0,0
    59.3,9.43,31.3
    ...
Each line is Weak,Medium,High for one catalyst.
Draws a grid of textured spheres (same visual style as before).
"""
import matplotlib.pyplot as plt, numpy as np, random, math

csv = args.get("csv", "").strip()
if not csv:
    csv = "100,0,0"

rows = [r.strip() for r in csv.splitlines() if r.strip()]
percents = []
for r in rows:
    try:
        w, m, h = (float(x) for x in r.split(",")[:3])
        percents.append({"Weak": w, "Medium": m, "High": h})
    except ValueError:
        pass

# palettes (re‑use originals, cycle if >4)
palettes = [
    [(0.9,0.8,1.0), (0.7,0.5,0.9), (0.5,0.2,0.7)],
    [(0.8,0.9,1.0), (0.3,0.6,0.9), (0.1,0.3,0.8)],
    [(0.8,1.0,0.8), (0.4,0.8,0.4), (0.1,0.6,0.3)],
    [(1.0,0.8,0.8), (0.9,0.4,0.4), (0.7,0.1,0.1)]
]

def tex(inten):
    return (5,0.15) if inten=="Weak" else (10,0.10) if inten=="Medium" else (15,0.05)

def draw(ax, perc, cols):
    u=np.linspace(0,2*np.pi,100); v=np.linspace(0,np.pi,50)
    x=np.outer(np.cos(u),np.sin(v)); y=np.outer(np.sin(u),np.sin(v)); z=np.outer(np.ones(u.size),np.cos(v))
    verts=len(u)*len(v)
    order=(["Weak"]*int(perc["Weak"]/100*verts)+
           ["Medium"]*int(perc["Medium"]/100*verts))
    order+=["High"]*(verts-len(order))
    random.shuffle(order); idx=0
    cmap=np.zeros((len(u),len(v),3))
    for i in range(len(u)):
        for j in range(len(v)):
            inten=order[idx]; idx+=1
            cmap[i,j]=cols[0] if inten=="Weak" else cols[1] if inten=="Medium" else cols[2]
            size,sp=tex(inten)
            bump = (0.02*np.random.rand() if inten=="Weak" else
                    0.05*np.sin(u[i]/sp)*np.cos(v[j]/sp) if inten=="Medium" else
                    0.08*(np.sin(u[i]/sp)*np.cos(v[j]/sp)+np.sin(2*u[i]/sp)*np.cos(2*v[j]/sp)))
            f=1+bump; x[i,j]*=f; y[i,j]*=f; z[i,j]*=f
    ax.plot_surface(x,y,z,facecolors=cmap,alpha=.9,linewidth=0,shade=True)
    ax.set_axis_off(); ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4); ax.set_zlim(-1.4,1.4)
    ax.view_init(elev=30,azim=45)

n=len(percents)
cols = math.ceil(math.sqrt(n))
rows_grid = math.ceil(n/cols)
fig = plt.figure(figsize=(5*cols,4*rows_grid))
grid = fig.add_gridspec(rows_grid, cols)

for i,pc in enumerate(percents):
    r,c = divmod(i, cols)
    ax = fig.add_subplot(grid[r,c], projection='3d')
    draw(ax, pc, palettes[i % 4])

fig.suptitle("Catalyst Spheres", fontsize=14)
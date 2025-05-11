"""
circle_input.py  –  renders one sphere or a 2×2 grid, depending on args.

Expected args (sent as JSON dict from JS):

  { "mode":"Single", "Catalyst":"NiO@SiO2",
    "Weak": 60, "Medium": 10, "High": 30 }

  or

  { "mode":"All",
    "NiO@Ce3O4_weak": 100, "NiO@Ce3O4_medium": 0,   "NiO@Ce3O4_high": 0,
    "NiO@SiO2_weak":  59.3, "NiO@SiO2_medium": 9.43,"NiO@SiO2_high": 31.3,
    ...
  }

If a value is missing we fall back to the hard‑coded defaults.
"""
import matplotlib.pyplot as plt, numpy as np, random, math, json

# ---------- default data & colour palettes -------------------------------
defaults = {
    "NiO@Ce3O4": {"Weak":100, "Medium":0,    "High":0},
    "NiO@SiO2":  {"Weak":59.3,"Medium":9.43, "High":31.3},
    "NiO@ZrO2":  {"Weak":5.70,"Medium":0,    "High":94.3},
    "NiO@CeO2":  {"Weak":84.7,"Medium":4.85, "High":10.4},
}
palettes = {
    "NiO@Ce3O4":[(0.9,0.8,1.0),(0.7,0.5,0.9),(0.5,0.2,0.7)],
    "NiO@SiO2": [(0.8,0.9,1.0),(0.3,0.6,0.9),(0.1,0.3,0.8)],
    "NiO@ZrO2": [(0.8,1.0,0.8),(0.4,0.8,0.4),(0.1,0.6,0.3)],
    "NiO@CeO2": [(1.0,0.8,0.8),(0.9,0.4,0.4),(0.7,0.1,0.1)],
}

def tex_params(inten):  # perturbation amplitude & spacing
    return (5,0.15) if inten=="Weak" else (10,0.10) if inten=="Medium" else (15,0.05)

def plot_sphere(ax, perc, colors, title):
    u=np.linspace(0,2*np.pi,100); v=np.linspace(0,np.pi,50)
    x=np.outer(np.cos(u),np.sin(v))
    y=np.outer(np.sin(u),np.sin(v))
    z=np.outer(np.ones(u.size),np.cos(v))

    verts=len(u)*len(v)
    order=(["Weak"]*int(perc["Weak"]/100*verts)+
           ["Medium"]*int(perc["Medium"]/100*verts))
    order+=["High"]*(verts-len(order)); random.shuffle(order)
    cmap=np.zeros((len(u),len(v),3)); idx=0
    for i in range(len(u)):
        for j in range(len(v)):
            inten=order[idx]; idx+=1
            cmap[i,j]=colors[0] if inten=="Weak" else colors[1] if inten=="Medium" else colors[2]
            size,sp=tex_params(inten)
            if inten=="Weak":   bump=0.02*np.random.rand()
            elif inten=="Medium": bump=0.05*np.sin(u[i]/sp)*np.cos(v[j]/sp)
            else: bump=0.08*(np.sin(u[i]/sp)*np.cos(v[j]/sp)+np.sin(2*u[i]/sp)*np.cos(2*v[j]/sp))
            f=1+bump; x[i,j]*=f; y[i,j]*=f; z[i,j]*=f
    ax.plot_surface(x,y,z,facecolors=cmap,alpha=.9,linewidth=0,shade=True)
    ax.set_axis_off(); ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4); ax.set_zlim(-1.4,1.4)
    ax.view_init(elev=30,azim=45); ax.set_title(title,fontsize=10)

# ---------- read args dict from JS ---------------------------------------
try:
    mode=args["mode"]
except Exception:
    mode="Single"

if mode=="All":
    cats=list(defaults.keys())
    data={}
    for cat in cats:
        w=float(args.get(f"{cat}_weak",   defaults[cat]["Weak"]))
        m=float(args.get(f"{cat}_medium", defaults[cat]["Medium"]))
        h=float(args.get(f"{cat}_high",   defaults[cat]["High"]))
        data[cat]={"Weak":w,"Medium":m,"High":h}
    # grid 2×2
    fig=plt.figure(figsize=(10,10)); grid=fig.add_gridspec(2,2)
    for i,cat in enumerate(cats):
        ax=fig.add_subplot(grid[i//2,i%2],projection='3d')
        plot_sphere(ax,data[cat],palettes[cat],cat)
    fig.suptitle("All Catalysts",fontsize=14)
else:
    cat=args.get("Catalyst","NiO@Ce3O4")
    w=float(args.get("Weak",defaults[cat]["Weak"]))
    m=float(args.get("Medium",defaults[cat]["Medium"]))
    h=float(args.get("High",defaults[cat]["High"]))
    fig=plt.figure(figsize=(6,6)); ax=fig.add_subplot(111,projection='3d')
    plot_sphere(ax,{"Weak":w,"Medium":m,"High":h},palettes[cat],cat)
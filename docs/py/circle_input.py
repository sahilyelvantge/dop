"""
circle_input.py
Runs inside Pyodide.  Expects an `args` dict:
  args = {
      "Catalyst": "NiO@SiO2" | "NiO@Ce3O4" | "NiO@ZrO2" | "NiO@CeO2" | "All",
      "Weak": 100, "Medium": 0, "High": 0        # used only for custom
  }
If Catalyst == 'Custom', we use the Weak/Medium/High fields.
"""

import matplotlib.pyplot as plt, numpy as np, random, json, math

# ------------- data -------------------------------------------------------
catalysts = {
    "NiO@Ce3O4": {"Weak": 100,  "Medium": 0,    "High": 0   },
    "NiO@SiO2":  {"Weak": 59.3, "Medium": 9.43, "High": 31.3},
    "NiO@ZrO2":  {"Weak": 5.70, "Medium": 0,    "High": 94.3},
    "NiO@CeO2":  {"Weak": 84.7, "Medium": 4.85, "High": 10.4}
}
gradients = {
    "NiO@Ce3O4": [(0.9,0.8,1.0),(0.7,0.5,0.9),(0.5,0.2,0.7)],
    "NiO@SiO2":  [(0.8,0.9,1.0),(0.3,0.6,0.9),(0.1,0.3,0.8)],
    "NiO@ZrO2":  [(0.8,1.0,0.8),(0.4,0.8,0.4),(0.1,0.6,0.3)],
    "NiO@CeO2":  [(1.0,0.8,0.8),(0.9,0.4,0.4),(0.7,0.1,0.1)]
}

# ------------- helpers ----------------------------------------------------
def tex_params(inten):
    return (5,0.15) if inten=="Weak" else (10,0.10) if inten=="Medium" else (15,0.05)

def sphere(ax, perc, colors, title):
    # base mesh
    u = np.linspace(0, 2*np.pi, 100)
    v = np.linspace(0, np.pi, 50)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(u.size), np.cos(v))

    # shuffle intensity assignment
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
    ax.set_title(title, fontsize=12)

# ------------- read args --------------------------------------------------
try:
    args
except NameError:
    args = {}

choice = args.get("Catalyst","NiO@Ce3O4")

if choice == "All":
    fig = plt.figure(figsize=(10,10))
    grid = fig.add_gridspec(2,2)
    for k,(cat,perc) in enumerate(catalysts.items()):
        row,col = divmod(k,2)
        ax = fig.add_subplot(grid[row,col], projection='3d')
        sphere(ax, perc, gradients[cat], cat)
    fig.suptitle("All Catalysts", fontsize=16)
else:
    if choice not in catalysts:
        # custom percentages
        perc = {"Weak":float(args.get("Weak",100)),
                "Medium":float(args.get("Medium",0)),
                "High":float(args.get("High",0))}
        colors = gradients["NiO@Ce3O4"]   # reuse purple gradient
        title = "Custom Catalyst"
    else:
        perc = catalysts[choice]
        colors = gradients[choice]
        title = choice
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    sphere(ax, perc, colors, title)
"""Scientific surfaces and space-time geometry from observed PE MAC events."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation, colors
import numpy as np


def first_tile(trace):
    result=[]
    for f in trace['frames']:
        result.append(f)
        if f[0]==3:break
    return result


def counts_at(trace,clock):
    p=trace['P'];counts=np.zeros((p,p),dtype=int)
    frames=first_tile(trace)
    for f in frames[:clock]:
        mask=int(f[4],16)
        for i in range(p*p):counts[i//p,i%p]+=(mask>>(p*p-1-i))&1
    return counts,frames[min(clock,len(frames))-1][0]


def render(traces,output):
    output=Path(output)
    selected=[next(t for t in traces if (t['P'],t['N'],t['B'])==(8,16,b)) for b in (16,4)]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':'black',
                         'axes.labelcolor':'black','svg.hashsalt':'systolic-trace'})
    xx,yy=np.meshgrid(np.arange(8),np.arange(8))
    cmap=plt.get_cmap('viridis');norm=colors.Normalize(0,16)

    def axes_style(ax,zlabel,zmax):
        ax.set(xlabel='PE column',ylabel='PE row',zlabel=zlabel,xlim=(-.1,7.1),ylim=(-.1,7.1),zlim=(0,zmax))
        ax.set_xticks([0,2,4,6,7]);ax.set_yticks([0,2,4,6,7]);ax.view_init(elev=28,azim=-57)
        if ax.get_subplotspec().colspan.start > 0: ax.set_zlabel('')
        for axis in (ax.xaxis,ax.yaxis,ax.zaxis):axis.set_pane_color((1,1,1,1))

    def surfaces(clock):
        fig=plt.figure(figsize=(12,5.5))
        fig.subplots_adjust(left=.01,right=.90,bottom=.07,top=.80,wspace=.12)
        for i,t in enumerate(selected,1):
            ax=fig.add_subplot(1,2,i,projection='3d');values,phase=counts_at(t,clock)
            ax.plot_surface(xx,yy,values,cmap=cmap,norm=norm,edgecolor='#46515a',linewidth=.35,antialiased=True)
            axes_style(ax,'Useful MACs completed',16)
            length=len(first_tile(t));local=min(clock,length)
            state='tile complete' if clock>=length else {1:'grid advance',2:'waiting for input',3:'tile complete'}[phase]
            ax.set_title(f'P=8, N=16, B={t["B"]} · clock {local}/{length}\n{state}',pad=14)
        fig.suptitle('The same 8×8 topology: useful work after the same number of clocks',fontsize=13)
        return fig

    fig=surfaces(16)
    fig.savefig(output/'work_surface.png',dpi=170,bbox_inches='tight')
    fig.savefig(output/'work_surface.svg',bbox_inches='tight',metadata={'Date':None})
    plt.close(fig)

    fig=plt.figure(figsize=(12,5.8))
    fig.subplots_adjust(left=.01,right=.90,bottom=.07,top=.82,wspace=.12)
    for k,t in enumerate(selected,1):
        ax=fig.add_subplot(1,2,k,projection='3d');cs=[];rs=[];clocks=[]
        for cycle,f in enumerate(first_tile(t),1):
            mask=int(f[4],16)
            for i in range(64):
                if mask>>(63-i)&1:cs.append(i%8);rs.append(i//8);clocks.append(cycle)
        ax.scatter(cs,rs,clocks,c=clocks,cmap='viridis',vmin=1,vmax=76,s=7,marker='s',alpha=.7,depthshade=False)
        axes_style(ax,'Tile clock',76)
        ax.set_title(f'B={t["B"]}: {len(first_tile(t))} clocks for one tile',pad=14)
    fig.suptitle('Space–time geometry · each point is one observed PE multiply-accumulate',fontsize=13)
    fig.savefig(output/'space_time.png',dpi=170,bbox_inches='tight')
    fig.savefig(output/'space_time.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

    fig=plt.figure(figsize=(11,4.8))
    fig.subplots_adjust(left=.01,right=.90,bottom=.10,top=.85,wspace=.18)
    for i,n in enumerate((8,16),1):
        ax=fig.add_subplot(1,2,i,projection='3d');grid=np.zeros((3,3))
        for r,b in enumerate((4,8,16)):
            for c,p in enumerate((2,4,8)):
                t=next(t for t in traces if (t['P'],t['N'],t['B'])==(p,n,b));grid[r,c]=t['macs']/t['compute']
        px,bx=np.meshgrid([2,4,8],[4,8,16])
        ax.plot_surface(px,bx,grid,cmap='viridis',edgecolor='#46515a',linewidth=.6,alpha=.85)
        ax.scatter(px.ravel(),bx.ravel(),grid.ravel(),c='black',s=14,depthshade=False)
        ax.set(xlabel='Grid dimension P',ylabel='Input words / clock B',zlabel='Useful MACs / clock',title=f'N={n}',xticks=[2,4,8],yticks=[4,8,16])
        ax.view_init(elev=26,azim=-132)
        if i==2:ax.set_zlabel('')
    fig.suptitle('Scaling landscape · mesh joins the nine measured configurations per workload',fontsize=12)
    fig.savefig(output/'scaling_surface.png',dpi=170,bbox_inches='tight')
    fig.savefig(output/'scaling_surface.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

    fig=plt.figure(figsize=(12,5.8))
    fig.subplots_adjust(left=.01,right=.90,bottom=.07,top=.82,wspace=.12)
    for k,t in enumerate(selected,1):
        ax=fig.add_subplot(1,2,k,projection='3d')
        first=np.full((8,8),np.nan);last=np.full((8,8),np.nan)
        for cycle,f in enumerate(first_tile(t),1):
            mask=int(f[4],16)
            for i in range(64):
                if mask>>(63-i)&1:
                    r,c=divmod(i,8)
                    if np.isnan(first[r,c]):first[r,c]=cycle
                    last[r,c]=cycle
        for values,color in ((first,'#377f9b'),(last,'#cf8b3c')):
            ax.plot_surface(xx,yy,values,color=color,alpha=.75,edgecolor='#46515a',linewidth=.4)
        axes_style(ax,'Tile clock',76)
        ax.set_title(f'B={t["B"]}: first and last MAC at every PE',pad=14)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor='#377f9b',label='First useful MAC'),Patch(facecolor='#cf8b3c',label='Last useful MAC')],
               loc='lower center',ncol=2,frameon=False)
    fig.suptitle('The execution window bends as operand supply slows',fontsize=13)
    fig.savefig(output/'wavefront_surfaces.png',dpi=170,bbox_inches='tight')
    fig.savefig(output/'wavefront_surfaces.svg',bbox_inches='tight',metadata={'Date':None});plt.close(fig)

    # Shared elapsed tile clocks: a completed tile stays on screen while its peer finishes.
    fig=plt.figure(figsize=(10,4.8))
    fig.subplots_adjust(left=.01,right=.90,bottom=.08,top=.82,wspace=.12)
    axes=[fig.add_subplot(1,2,i,projection='3d') for i in (1,2)]
    def update(clock):
        for ax,t in zip(axes,selected):
            ax.clear();values,phase=counts_at(t,clock)
            ax.plot_surface(xx,yy,values,cmap=cmap,norm=norm,edgecolor='#46515a',linewidth=.3)
            axes_style(ax,'Useful MACs',16)
            length=len(first_tile(t));state='COMPLETE' if clock>=length else ('STALL' if phase==2 else 'ADVANCE')
            ax.set_title(f'B={t["B"]} · {min(clock,length)}/{length} clocks · {state}')
        fig.suptitle('First output tile · completed tiles stay on screen',fontsize=12)
        return []
    ani=animation.FuncAnimation(fig,update,frames=range(1,77),interval=100,repeat=False)
    ani.save(output/'tile_story.gif',writer=animation.PillowWriter(fps=10),dpi=85)
    plt.close(fig)

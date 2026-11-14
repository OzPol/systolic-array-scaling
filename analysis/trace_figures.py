"""Spatial views covering every grid, matrix workload, and input budget."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation, colors
import numpy as np

GRIDS=(2,4,8)
MATRICES=(8,16)
BUDGETS=(4,8,16)


def configurations(traces):
    by_key={(t['N'],t['P'],t['B']):t for t in traces}
    expected={(n,p,b) for n in MATRICES for p in GRIDS for b in BUDGETS}
    if len(traces)!=18 or set(by_key)!=expected:
        raise ValueError('spatial comparison requires all 18 configurations')
    return by_key


def activity(trace):
    """One binary MAC-event value for each physical PE and compute clock."""
    p=trace['P'];volume=np.zeros((trace['compute'],p,p),dtype=np.uint8)
    for clock,frame in enumerate(trace['frames'][:trace['compute']]):
        mask=int(frame[4],16)
        for i in range(p*p):volume[clock,i//p,i%p]=(mask>>(p*p-1-i))&1
    if int(volume.sum())!=trace['N']**3:raise ValueError('incomplete useful work in spatial trace')
    return volume


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


def render(traces,output,make_animation=True):
    by_key=configurations(traces);output=Path(output)
    volumes={key:activity(t) for key,t in by_key.items()}
    cumulative={key:np.cumsum(v,axis=0) for key,v in volumes.items()}
    cmap=plt.get_cmap('turbo');norm=colors.Normalize(0,1)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'text.color':'black',
                         'axes.labelcolor':'black','svg.hashsalt':'systolic-all-configurations'})

    def save(fig,name,dpi=155):
        fig.savefig(output/f'{name}.png',dpi=dpi,bbox_inches='tight',pad_inches=.2)
        fig.savefig(output/f'{name}.svg',bbox_inches='tight',metadata={'Date':None})
        plt.close(fig)

    def style(ax,p,zmax,zlabel='',zpercent=False,cells=False):
        extent=(-.5,p-.5) if cells else (0,p-1)
        ax.set(xlabel='PE column',ylabel='PE row',zlabel=zlabel,xlim=extent,ylim=extent,zlim=(0,zmax))
        ticks=[0,p-1] if p==2 else [0,(p-1)//2,p-1]
        ax.set_xticks(ticks);ax.set_yticks(ticks)
        ax.set_zticks([0,.5,1] if zpercent else [0,int(zmax)//2,int(zmax)])
        if zpercent:ax.set_zticklabels(['0%','50%','100%'])
        ax.tick_params(labelsize=8,pad=0)
        ax.xaxis.labelpad=0;ax.yaxis.labelpad=0;ax.zaxis.labelpad=2
        ax.view_init(elev=24,azim=-55)
        ax.set_box_aspect((1,1,1.05))
        for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
            axis.set_pane_color((1,1,1,1))
            axis._axinfo['grid']['color']=(.75,.78,.8,.3)

    def title(t):
        p,n,b=t['P'],t['N'],t['B']
        return f'Grid {p}×{p} · matrix {n}×{n}\nB={b} · {t["compute"]} clocks · {t["macs"]/(p*p*t["compute"]):.1%} PE use'

    def atlas(matrices,kind,name):
        rows=len(matrices)*3
        height=rows*3.35+.7
        fig=plt.figure(figsize=(12,height))
        fig.subplots_adjust(left=.03,right=.88,bottom=.055,top=1-1.5/height,hspace=.45,wspace=.28)
        for ni,n in enumerate(matrices):
            for pi,p in enumerate(GRIDS):
                for bi,b in enumerate(BUDGETS):
                    key=(n,p,b);t=by_key[key];v=volumes[key]
                    ax=fig.add_subplot(rows,3,(ni*3+pi)*3+bi+1,projection='3d')
                    xx,yy=np.meshgrid(np.arange(p),np.arange(p))
                    if kind=='volume':
                        # Four-clock bins retain actual physical time on the vertical axis.
                        starts=np.arange(0,t['compute'],4)
                        z=np.array([0,*[min(s+4,t['compute']) for s in starts]],dtype=float)
                        density=np.array([v[s:min(s+4,len(v))].mean(axis=0) for s in starts])
                        mid=p//2
                        edges=np.arange(p+1)-.5
                        xz,zz=np.meshgrid(edges,z)
                        ax.plot_surface(xz,np.full_like(xz,mid),zz,facecolors=cmap(density[:,mid,:]),
                                        rstride=1,cstride=1,shade=False,alpha=.9,linewidth=0,rasterized=True)
                        yz,zz=np.meshgrid(edges,z)
                        ax.plot_surface(np.full_like(yz,mid),yz,zz,facecolors=cmap(density[:,:,mid]),
                                        rstride=1,cstride=1,shade=False,alpha=.9,linewidth=0,rasterized=True)
                        for fraction in (.25,.5,.75):
                            zslice=max(1,int(t['compute']*fraction))
                            index=min(len(density)-1,(zslice-1)//4)
                            sx,sy=np.meshgrid(edges,edges)
                            ax.plot_surface(sx,sy,np.full_like(sx,zslice),facecolors=cmap(density[index]),
                                            rstride=1,cstride=1,shade=False,alpha=.8,linewidth=0,rasterized=True)
                        style(ax,p,t['compute'],'Compute clock' if bi==0 else '',cells=True)
                    elif kind=='work':
                        clock=min(32,t['compute']);values=cumulative[key][clock-1]/(n**3/(p*p))
                        ax.plot_surface(xx,yy,values,cmap=cmap,norm=norm,edgecolor='#424b54',linewidth=.35,alpha=.95)
                        style(ax,p,1,'Assigned MAC work' if bi==0 else '',True)
                    elif kind=='wavefront':
                        first=np.full((p,p),np.nan);last=np.full((p,p),np.nan)
                        for clock,frame in enumerate(first_tile(t),1):
                            mask=int(frame[4],16)
                            for i in range(p*p):
                                if mask>>(p*p-1-i)&1:
                                    r,c=divmod(i,p)
                                    if np.isnan(first[r,c]):first[r,c]=clock
                                    last[r,c]=clock
                        for values,color in ((first,'#377f9b'),(last,'#cf8b3c')):
                            ax.plot_surface(xx,yy,values,color=color,alpha=.8,edgecolor='#424b54',linewidth=.35)
                        style(ax,p,len(first_tile(t)),'Tile clock' if bi==0 else '')
                    ax.set_title(title(t),fontsize=9,pad=10)
        heading={'volume':'PE activity through space and time','work':'Full-product work completed after 32 compute clocks',
                 'wavefront':'First and last MAC at every PE in the first output tile'}[kind]
        workload=' · '.join(f'{n}×{n} matrices' for n in matrices)
        fig.suptitle(f'{heading}\n{workload} · every PE grid and input budget',fontsize=14,y=.985)
        if kind in ('volume','work'):
            colorax=fig.add_axes([.91,.16,.012,.65])
            bar=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=colorax)
            bar.set_label('MACs / PE / clock in 4-clock bins' if kind=='volume' else 'Fraction of total assigned MAC work',labelpad=9)
        else:
            from matplotlib.patches import Patch
            fig.legend(handles=[Patch(facecolor='#377f9b',label='First MAC'),Patch(facecolor='#cf8b3c',label='Last MAC')],
                       loc='lower center',ncol=2,frameon=False)
        save(fig,name)

    for n in MATRICES:
        atlas((n,),'volume',f'activity_matrix{n:02d}')
        atlas((n,),'work',f'work_matrix{n:02d}')
        atlas((n,),'wavefront',f'wavefront_matrix{n:02d}')
    atlas(MATRICES,'volume','space_time')
    atlas(MATRICES,'work','work_surface')
    atlas(MATRICES,'wavefront','wavefront_surfaces')

    fig=plt.figure(figsize=(12,5))
    fig.subplots_adjust(left=.03,right=.91,bottom=.12,top=.83,wspace=.24)
    for index,n in enumerate(MATRICES,1):
        ax=fig.add_subplot(1,2,index,projection='3d')
        grid=np.array([[by_key[(n,p,b)]['macs']/by_key[(n,p,b)]['compute'] for p in GRIDS] for b in BUDGETS])
        px,bx=np.meshgrid(GRIDS,BUDGETS)
        ax.plot_surface(px,bx,grid,cmap='viridis',edgecolor='#46515a',linewidth=.6,alpha=.85)
        ax.scatter(px.ravel(),bx.ravel(),grid.ravel(),c='black',s=18,depthshade=False)
        ax.set(xlabel='PE grid dimension',ylabel='Input words / clock',zlabel='Useful MACs / clock' if index==1 else '',
               title=f'{n}×{n} matrix workload',xticks=GRIDS,yticks=BUDGETS)
        ax.set_xticklabels(['2×2','4×4','8×8']);ax.view_init(elev=26,azim=-132)
    fig.suptitle('All 18 configurations · nine measured points per matrix workload',fontsize=14)
    save(fig,'scaling_surface')

    if not make_animation:return

    # Each chapter shows all three PE grids and both complete matrix workloads.
    fig=plt.figure(figsize=(11,7.7))
    fig.subplots_adjust(left=.025,right=.93,bottom=.04,top=.84,hspace=.33,wspace=.22)
    axes={(n,p):fig.add_subplot(2,3,ni*3+pi+1,projection='3d')
          for ni,n in enumerate(MATRICES) for pi,p in enumerate(GRIDS)}
    chapters=[]
    for b in BUDGETS:
        completions=[by_key[(n,p,b)]['compute'] for n in MATRICES for p in GRIDS]
        limit=max(completions)
        samples=sorted(set([*np.linspace(1,32,12).astype(int),*np.linspace(32,limit,12).astype(int),
                            *completions,*[c-1 for c in completions]]))
        chapters.extend((b,int(clock)) for clock in samples)
    def update(frame):
        b,clock=chapters[frame]
        for (n,p),ax in axes.items():
            ax.clear();t=by_key[(n,p,b)];local=min(clock,t['compute'])
            xx,yy=np.meshgrid(np.arange(p),np.arange(p))
            values=cumulative[(n,p,b)][local-1]/(n**3/(p*p))
            ax.plot_surface(xx,yy,values,cmap=cmap,norm=norm,edgecolor='#424b54',linewidth=.35)
            style(ax,p,1,'Assigned MAC work' if p==2 else '',True)
            phase='COMPLETE' if clock>=t['compute'] else 'RUNNING'
            ax.set_title(f'Grid {p}×{p} · matrix {n}×{n}\n{local}/{t["compute"]} clocks · {phase}',fontsize=10,pad=8)
        fig.suptitle(f'All three arrays · both matrix workloads · input budget {b} words/clock\nShared elapsed compute clock: {clock}',fontsize=13,y=.97)
        return []
    movie=animation.FuncAnimation(fig,update,frames=len(chapters),interval=150,repeat=False)
    movie.save(output/'tile_story.gif',writer=animation.PillowWriter(fps=7),dpi=80)
    plt.close(fig)
    manifest={'configurations':[{'matrix_order':n,'grid_dimension':p,'input_budget':b,
                                'compute_cycles':by_key[(n,p,b)]['compute']}
                               for n in MATRICES for p in GRIDS for b in BUDGETS],
              'activity_color':'MACs per PE per physical clock, averaged over four-clock bins',
              'work_height':'fraction of a physical PE\'s full-product MAC assignment',
              'work_snapshot_clock':32,'animation_budget_chapters':list(BUDGETS)}
    (output/'coverage.json').write_text(json.dumps(manifest,indent=2)+'\n')

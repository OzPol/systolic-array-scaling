#!/usr/bin/env python3
"""Compile the paper and slide PDFs against the same generated analysis."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def build(analysis,visualization,destination):
    analysis,visualization,destination=map(lambda p:Path(p).resolve(),(analysis,visualization,destination))
    engine=shutil.which('tectonic')
    if not engine and not shutil.which('pdflatex'):
        raise RuntimeError('Install Tectonic or a complete LaTeX distribution to compile the PDFs')
    destination.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for name,source in [('report',ROOT/'deliverables/report/main.tex'),('presentation',ROOT/'deliverables/presentation/slides.tex')]:
        with tempfile.TemporaryDirectory(prefix=f'.{name}-',dir=destination) as temp:
            temp=Path(temp)
            wrapper=temp/f'{name}.tex'
            wrapper.write_text('\\def\\AnalysisPath{'+analysis.as_posix()+'}\n\\def\\TracePath{'+visualization.as_posix()+'}\n\\input{'+source.as_posix()+'}\n')
            if engine:
                command=[engine,'--keep-logs','--keep-intermediates',str(wrapper)]
            else:
                command=['pdflatex','-output-format=pdf','-interaction=nonstopmode','-halt-on-error',str(wrapper)]
            console=temp/'build-console.txt'
            with console.open('w') as stream:
                # Tectonic reruns automatically; pdfLaTeX needs a reference pass.
                for _ in range(1 if engine else 2):
                    result=subprocess.run(command,cwd=temp,stdout=stream,stderr=subprocess.STDOUT)
                    if result.returncode:
                        stream.flush()
                        tail='\n'.join(console.read_text(errors='replace').splitlines()[-35:])
                        raise RuntimeError(f'{name} PDF build failed:\n{tail}')
            target=destination/f'{name}.pdf'
            shutil.copy2(temp/f'{name}.pdf',target)
            shutil.copy2(temp/f'{name}.log',destination/f'{name}.log')
            outputs.append(target)
            print(f'Built {target}')
    return outputs

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis',type=Path,default=ROOT/'results/analysis')
    parser.add_argument('--visualization',type=Path,default=ROOT/'results/visualization')
    parser.add_argument('--output',type=Path,default=ROOT/'build/documents')
    args=parser.parse_args();build(args.analysis,args.visualization,args.output)

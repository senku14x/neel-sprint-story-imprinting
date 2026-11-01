import os
d=os.path.dirname(os.path.abspath(__file__))+'/..'
t=open(f'{d}/template.html').read(); b=open(f'{d}/data.b64').read()
open(f'{d}/E4_report.html','w').write(t.replace('__DATA__',b))
print('built', round(os.path.getsize(f'{d}/E4_report.html')/1e6,2),'MB')

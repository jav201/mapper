import ast
src=open('mapper/app.py',encoding='utf-8').read(); tree=ast.parse(src)
top={}
for n in tree.body:
    if isinstance(n,(ast.ClassDef,ast.FunctionDef)): top[n.name]=n
    elif isinstance(n,ast.Assign):
        for t in n.targets:
            if isinstance(t,ast.Name): top[t.id]=n
    elif isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name): top[n.target.id]=n
imports=set()
for n in tree.body:
    if isinstance(n,(ast.Import,ast.ImportFrom)):
        for a in n.names: imports.add((a.asname or a.name).split('.')[0])
# step at which each app.py-defined name leaves app.py
step={}
order=['A1','A2','A3','A5a','B0','A5b','A6','A7','A4']
common=['MapHintLine','map_hint','home_hint','_home_door_key','screen_bindings','keybar_groups','_refusal_toast','_save_or_toast','_path_refusal']
for k in common: step[k]='A1'
for k in [x for x in top if x.isupper() or x.startswith('_HINT') or x.startswith('_QUERY')]: step.setdefault(k,'A1')
for k in ['_PromptScreen','_ConfirmScreen','_TemplateScreen','_FichaScreen']: step[k]='A2'
step['ConstructScreen']='A3'; step['NavigationModel']='A5a'; step['MapScreen']='B0'
step['RepoScreen']='A5b'; step['PlugRepoScreen']='A6'; step['_ImportPreviewScreen']='A7'; step['HomeScreen']='A4'
movers=['MapHintLine','_PromptScreen','_ConfirmScreen','_TemplateScreen','_FichaScreen','ConstructScreen','NavigationModel','MapScreen','RepoScreen','PlugRepoScreen','_ImportPreviewScreen','HomeScreen']
bad=0
for m in movers:
    used={x.id for x in ast.walk(top[m]) if isinstance(x,ast.Name)} & set(top)
    used.discard(m)
    for u in sorted(used):
        su=step.get(u,'STAYS')
        if su=='STAYS' or order.index(su) > order.index(step[m]):
            print(f'ILLEGAL: {m} ({step[m]}) uses {u} (home step {su})'); bad+=1
print('stays in app.py:', sorted(k for k in top if k not in step))
print('illegal edges:', bad)

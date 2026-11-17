import json,os,subprocess,sys
def gws(cfg,*a):
    env=dict(os.environ,GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(cfg),GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    r=subprocess.run(["gws",*a,"--format","json"],env=env,capture_output=True,text=True)
    o=r.stdout[r.stdout.find("{"):]
    d=json.loads(o) if o.strip() else {}
    if isinstance(d,dict) and "error" in d: raise RuntimeError(f"gws error: {d['error']}")
    return d
def col(n):
    s=""
    while n: n,r=divmod(n-1,26); s=chr(65+r)+s
    return s
def find(cfg,key,render="FORMULA"):
    T="'Gas pipelines'"
    hdr=gws(cfg,"sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":key,"range":T+"!A1:ZZ8","valueRenderOption":"FORMATTED_VALUE"}))["values"]
    for hi,row in enumerate(hdr):
        if "ProjectID" in row and "CountriesOrAreas" in row: break
    else: raise SystemExit("no header")
    ci=row.index("CountriesOrAreas")+1; pi=row.index("ProjectID")+1
    ids=gws(cfg,"sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":key,"range":f"{T}!{col(pi)}:{col(pi)}"}))["values"]
    r=[i+1 for i,v in enumerate(ids) if v and v[0]=="P7597"]
    cell=f"{T}!{col(ci)}{r[0]}"
    cur=gws(cfg,"sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":key,"range":cell,"valueRenderOption":render}))
    return r,cell,cur.get("values")
if __name__=="__main__":
    for name,key in [("live","1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"),("snapshot","1f-7LGFWa6v9O63e2P7X3aHRWIJGgp87eSer_i3jm91Q")]:
        print(name,find("~/.config/gws-gem",key))

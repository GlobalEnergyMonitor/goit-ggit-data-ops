import json,sys,math,pandas as pd
sys.path.insert(0,'/Users/baird/Dropbox/_git_ALL/_github-repos-gem/gem-db-ops')
import gem_sheets
from find_cell import gws
K="15vRJg2uwsNbEKYB1LrvqKRkEi-0Ta4OP7x6awUNEGgI"; import os; SNAP=os.environ.get("SNAP","1f-7LGFWa6v9O63e2P7X3aHRWIJGgp87eSer_i3jm91Q")
import os; G=os.environ.get("GXLSX",os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","GGIT-Summary-Sheets-Gas-2026-11-17.xlsx")); R="~/.config/gws-gem"; W="~/.config/gws-gem-write"
DRY=len(sys.argv)>1 and sys.argv[1]=="dry"
def clean(v,dp=2):
    if v is None or (isinstance(v,float) and math.isnan(v)): return ""
    if isinstance(v,(int,float)) and not isinstance(v,bool): return round(float(v),dp)
    return v
def rows(df,dp=2): return [[clean(x,dp) for x in r] for r in df.itertuples(index=False,name=None)]
def rd(t,r): return gws(R,"sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":K,"range":f"'{t}'!{r}"})).get("values",[])
def col(n):
    s=""
    while n: n,r=divmod(n-1,26); s=chr(65+r)+s
    return s
x=lambda s:pd.read_excel(G,sheet_name=s)
# --- build
km_c=rows(x('Kilometers by country'))
km_r=x('Kilometers by region'); km_r=rows(km_r)
km_o=rows(x('Kilometers by owner'))
sy=x('Kilometers by start year'); sy=sy[pd.to_numeric(sy['Start year'],errors='coerce').between(1980,2025)]
sy_rows=[[int(a),clean(b)] for a,b in zip(sy['Start year'],sy.iloc[:,1])]+[["Total",clean(sum(r[1] for r in sy_rows_) if False else sy.iloc[:,1].sum())]]
cx_r=rows(x('Capex USD billions by region'))
cc=x('Capex USD billions by country')
v=gem_sheets.read_tab_values('Country dictionary',SNAP); h=next(i for i,r in enumerate(v[:8]) if 'Country' in r and 'Region' in r)
dic=pd.DataFrame(v[h+1:],columns=v[h]).drop_duplicates('Country').set_index('Country')[['Region','SubRegion']]
tot=cc[cc.Country=='Total']; body=cc[cc.Country!='Total'].copy()
body['Region']=body.Country.map(dic.Region); body['Sub']=body.Country.map(dic.SubRegion)
assert body.Region.notna().all()
body=body.sort_values(['Region','Sub','Country'])
out=[];pr=ps=None
for r in body.itertuples(index=False):
    d=r._asdict() if hasattr(r,'_asdict') else None
for _,r in body.iterrows():
    rg=r.Region if r.Region!=pr else ""; sb=r.Sub if (r.Sub!=ps or r.Region!=pr) else ""
    pr,ps=r.Region,r.Sub
    out.append([rg,sb,r.Country]+[clean(r[c]) for c in cc.columns[1:10]])
out.append(["","","Total"]+[clean(tot.iloc[0][c]) for c in cc.columns[1:10]])
cx_c=out
# (tab, first data row, expected header cell(row,text), data, banner-A3)
PLAN=[("Pipeline km by country/area",6,"A5","Country/Area",km_c),
("Pipeline km by region",6,"A5","Region",km_r),
("Pipeline km by owner",6,"A5","Owner",km_o),
("Pipeline km by start year",6,"A5","Start year",sy_rows),
("Pipeline capex estimates by region",7,"A6","Region",cx_r),
("Pipeline capex estimates by country/area",7,"A6","Region",cx_c)]
for t,r0,hc,ht,data in PLAN:
    got=rd(t,hc)
    assert got and got[0][0]==ht,(t,got)
    old=rd(t,f"A{r0}:A800"); old_end=r0+len(old)-1; new_end=r0+len(data)-1; w=max(len(r) for r in data)
    print(f"{t}: write {col(1)}{r0}:{col(w)}{new_end} ({len(data)} rows); old data ended row {old_end}"+(f"; clear rows {new_end+1}-{old_end}" if old_end>new_end else ""))
    if DRY: continue
    gws(W,"sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":K,"range":f"'{t}'!A{r0}","valueInputOption":"RAW"}),"--json",json.dumps({"values":data}))
    if old_end>new_end:
        gws(W,"sheets","spreadsheets","values","clear","--params",json.dumps({"spreadsheetId":K,"range":f"'{t}'!A{new_end+1}:Z{old_end}"}),"--json","{}")
    note="Gas Pipelines data, November 2026 (DRAFT; parent research not finished, owner figures are provisional)" if "owner" in t else "Gas Pipelines data, November 2026 (DRAFT)"
    gws(W,"sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":K,"range":f"'{t}'!A3","valueInputOption":"RAW"}),"--json",json.dumps({"values":[[note]]}))
import pandas as pd
ct="Pipeline cost per km estimates"
def cost(sheet,first):
    x=pd.read_excel(G,sheet_name=sheet)
    rows=[[str(a),int(b),round(float(c),2)] for a,b,c in x.iloc[:,:3].itertuples(index=False)]
    print(ct,"rows from",first,len(rows))
    if not DRY: gws(W,"sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":K,"range":f"'{ct}'!A{first}","valueInputOption":"RAW"}),"--json",json.dumps({"values":rows}))
cost("Cost per km by region",9); cost("Cost per km by subregion",17)
if not DRY: gws(W,"sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":K,"range":f"'{ct}'!A3","valueInputOption":"RAW"}),"--json",json.dumps({"values":[["Gas Pipelines data, November 2026 (DRAFT)"]]}))
print("done" if not DRY else "dry run only")

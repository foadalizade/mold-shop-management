import openpyxl, json, os
from collections import Counter
from datetime import datetime, date, time

SOURCE = "data/source/1405.xlsx"
OUT_JSON = "data/processed/1405_profile.json"
OUT_MD = "data/processed/1405_profile.md"

def typ(v):
    if v in (None, ""): return "blank"
    if isinstance(v, bool): return "boolean"
    if isinstance(v, datetime): return "datetime"
    if isinstance(v, date): return "date"
    if isinstance(v, time): return "time"
    if isinstance(v, (int,float)): return "number"
    return "text"

def clean(v):
    return v.isoformat() if isinstance(v,(datetime,date,time)) else v

wb = openpyxl.load_workbook(SOURCE, data_only=False)
out = {"generated_at_utc": datetime.utcnow().isoformat()+"Z", "source_file": SOURCE, "sheet_count": len(wb.sheetnames), "sheets":[]}

for ws in wb.worksheets:
    mr, mc = ws.max_row, ws.max_column
    headers, hrow = [], None
    for i,row in enumerate(ws.iter_rows(min_row=1,max_row=min(mr,30)),1):
        vals=[c.value for c in row]
        if any(v not in (None,"") for v in vals):
            hrow=i; headers=[clean(v) for v in vals]; break
    cols=[]
    for c in range(1,mc+1):
        vals=[ws.cell(r,c).value for r in range(1,mr+1)]
        non=[v for v in vals if v not in (None,"")]
        types=Counter(typ(v) for v in non)
        samples=[]; seen=set()
        for v in non:
            if len(samples)>=20: break
            k=str(clean(v))
            if k not in seen:
                seen.add(k); samples.append(k)
        cols.append({"column_index":c,"column_letter":openpyxl.utils.get_column_letter(c),
                     "provisional_header":headers[c-1] if c<=len(headers) else None,
                     "nonblank_count":len(non),"blank_count":mr-len(non),
                     "data_types":dict(types),"sample_unique_values":samples})
    formulas=sum(1 for row in ws.iter_rows() for cell in row if isinstance(cell.value,str) and cell.value.startswith("="))
    out["sheets"].append({"sheet_name":ws.title,"max_row":mr,"max_column":mc,
        "nonempty_rows":sum(1 for row in ws.iter_rows() if any(c.value not in (None,"") for c in row)),
        "formula_count":formulas,"merged_range_count":len(ws.merged_cells.ranges),
        "merged_ranges":[str(x) for x in list(ws.merged_cells.ranges)[:100]],
        "provisional_header_row":hrow,"provisional_headers":headers,
        "sample_rows_first_6":[{"row":r,"values":[clean(ws.cell(r,c).value) for c in range(1,mc+1)]} for r in range(1,min(mr,6)+1)],
        "columns":cols})

os.makedirs("data/processed",exist_ok=True)
with open(OUT_JSON,"w",encoding="utf-8") as f: json.dump(out,f,ensure_ascii=False,indent=2,default=str)
with open(OUT_MD,"w",encoding="utf-8") as f:
    f.write("# 1405.xlsx — Workbook Profile\n\n")
    f.write(f"- Generated: {out['generated_at_utc']}\n- Sheets: **{out['sheet_count']}**\n\n")
    for s in out["sheets"]:
        f.write(f"## {s['sheet_name']}\n\n")
        f.write(f"- Dimensions: {s['max_row']} × {s['max_column']}\n- Non-empty rows: {s['nonempty_rows']}\n- Formulas: {s['formula_count']}\n- Merged ranges: {s['merged_range_count']}\n- Header row: {s['provisional_header_row']}\n\n")
        f.write("| Col | Header | Nonblank | Blank | Types | Samples |\n|---:|---|---:|---:|---|---|\n")
        for c in s["columns"]:
            samples = ", ".join(c["sample_unique_values"][:8]).replace("|", "\\|")
            f.write(f"| {c['column_index']} | {c['provisional_header']!r} | {c['nonblank_count']} | {c['blank_count']} | {c['data_types']} | {samples} |\n")

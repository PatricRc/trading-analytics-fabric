%pip install -q semantic-link-labs
# Build an Import-mode copy of sm_trading_gold (same tables, relationships, measures) for Publish to web
import json, copy
import sempy.fabric as fabric
import sempy_labs as labs

WS_ID = "fe75eb04-2e1e-4499-ab7f-94ea15fa7c71"
LH_ID = "87124dd0-a1e2-438a-8117-c1bc9c7a3e7c"
SRC, DST = "sm_trading_gold", "sm_trading_gold_import"

lh = fabric.FabricRestClient().get(f"v1/workspaces/{WS_ID}/lakehouses/{LH_ID}").json()
server = lh["properties"]["sqlEndpointProperties"]["connectionString"]
db = lh["displayName"]
print("SQL endpoint:", server, "| database:", db)

bim = labs.get_semantic_model_bim(dataset=SRC, workspace=WS_ID)
new = copy.deepcopy(bim)
model = new["model"]
changed = []
for t in model["tables"]:
    for p in t.get("partitions", []):
        src = p.get("source", {})
        if p.get("mode") == "directLake" or src.get("type") == "entity":
            schema = src.get("schemaName") or "dbo"
            entity = src.get("entityName") or t["name"]
            p["mode"] = "import"
            p["source"] = {"type": "m", "expression": [
                "let",
                f'    Source = Sql.Database("{server}", "{db}"),',
                f'    Data = Source{{[Schema="{schema}", Item="{entity}"]}}[Data]',
                "in",
                "    Data"]}
            changed.append(f"{t['name']} <- {schema}.{entity}")
model.pop("defaultMode", None)
# drop the Direct Lake shared expression if nothing references it any more
model["expressions"] = [e for e in model.get("expressions", []) if e.get("name") != "DatabaseQuery"]
print(len(changed), "tables switched to Import:", *changed, sep="\n  ")
print("measures:", sum(len(t.get("measures", [])) for t in model["tables"]),
      "| relationships:", len(model.get("relationships", [])))

labs.create_semantic_model_from_bim(dataset=DST, bim_file=new, workspace=WS_ID)
print("created", DST)

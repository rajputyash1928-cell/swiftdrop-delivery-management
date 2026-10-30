"""Network model and conversion helpers shared by web and CLI."""
import json, random, math
from pathlib import Path
DATA=Path(__file__).parent/"data"
class DeliveryNetwork:
    def __init__(self, data=None):
        self.data=data or {"locations":[],"roads":[]}
        self.validate()
    def validate(self):
        locs=self.data.get("locations",[]); ids=[x.get("id") for x in locs]
        if len(ids)!=len(set(ids)):raise ValueError("Location IDs must be unique.")
        if any(not x.get("id") for x in locs):raise ValueError("Every location needs an ID.")
        known=set(ids)
        for r in self.data.get("roads",[]):
            if r.get("from") not in known or r.get("to") not in known:raise ValueError("Road endpoints must reference existing locations.")
            if float(r.get("distance",0))<0 or float(r.get("travel_time",0))<0:raise ValueError("Road distance and travel time cannot be negative.")
            if float(r.get("traffic",1))<=0:raise ValueError("Traffic factor must be greater than zero.")
    def load(self,name):
        if name not in ("small","medium","large"):raise ValueError("Dataset must be small, medium, or large.")
        self.data=json.loads((DATA/f"sample_{name}.json").read_text());self.validate();return self.data
    def graph(self,weight="effective"):
        ids=[x["id"] for x in self.data["locations"]]; idx={v:i for i,v in enumerate(ids)}; edges=[]
        for r in self.data["roads"]:
            w=float(r["distance"])*float(r.get("traffic",1)) if weight=="effective" else float(r.get(weight, r["distance"]))
            u,v=idx[r["from"]],idx[r["to"]];edges.extend([(u,v,w),(v,u,w)])
        return ids,edges,idx
    def matrix(self):
        ids,edges,_=self.graph(); n=len(ids);m=[[None]*n for _ in range(n)]
        for i in range(n):m[i][i]=0
        for u,v,w in edges:
            if m[u][v] is None or w<m[u][v]:m[u][v]=w
        return ids,m
    def random_graph(self,n=10,seed=7):
        if not 2<=n<=100:raise ValueError("Random graph size must be between 2 and 100.")
        random.seed(seed);loc=[{"id":"W","name":"Warehouse","x":0,"y":0,"priority":0,"time_window":"08:00-18:00","weight":0}]
        for i in range(1,n):loc.append({"id":f"C{i}","name":f"Customer {i}","x":random.randint(0,100),"y":random.randint(0,100),"priority":random.randint(1,5),"time_window":"09:00-17:00","weight":random.randint(1,10)})
        roads=[]
        for i in range(n):
            for j in range(i+1,n):
                if random.random()<0.25 or j==i+1:
                    d=round(math.hypot(loc[i]["x"]-loc[j]["x"],loc[i]["y"]-loc[j]["y"]),2)
                    roads.append({"from":loc[i]["id"],"to":loc[j]["id"],"distance":d,"travel_time":round(d*1.5,2),"traffic":round(random.uniform(1,1.5),2)})
        self.data={"locations":loc,"roads":roads};self.validate();return self.data

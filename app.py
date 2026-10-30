from flask import Flask, render_template, request, jsonify, make_response
from algorithms.graph import bfs,dijkstra,astar,bellman_ford,floyd_warshall
from algorithms.tsp import brute_force,nearest_neighbour,held_karp,two_opt
from algorithms.sorting import sort_items,linear_search,binary_search
from algorithms.loading import knapsack_01,fractional_greedy,greedy_vehicle_assignment
from algorithms.mst import prim,kruskal
from algorithms.benchmark import measure
from service import DeliveryNetwork
import csv,io,json,math
app=Flask(__name__); network=DeliveryNetwork(); network.load("small"); history=[]
# Operational demo records are in-memory and reset when the server restarts.
orders=[]
drivers=[
 {"id":"DRV-101","name":"Aarav Sharma","vehicle":"Bike","capacity":15,"status":"Available","phone":"+91 90000 10001"},
 {"id":"DRV-102","name":"Priya Patel","vehicle":"Scooter","capacity":12,"status":"Available","phone":"+91 90000 10002"},
 {"id":"DRV-103","name":"Kabir Khan","vehicle":"Mini Van","capacity":40,"status":"Available","phone":"+91 90000 10003"},
]
def seed_orders():
    global orders
    if orders: return
    for i, loc in enumerate(network.data["locations"]):
        if loc["id"] == "W": continue
        orders.append({"id":f"ORD-{1001+i}","customer":f"{['Riya Mehta','Dev Shah','Ananya Rao','Ishaan Joshi','Meera Nair'][i%5]}","address":loc["name"],"location_id":loc["id"],"weight":loc.get("weight",1),"priority":loc.get("priority",1),"status":["In Transit","Pending","Delivered","Pending","In Transit"][i%5],"driver_id":["DRV-101","DRV-102","DRV-103"][i%3],"eta":f"{25+i*7} min"})
seed_orders()
def err(fn):
    try:return jsonify(fn())
    except (ValueError,KeyError,TypeError,IndexError) as e:return jsonify({"error":str(e)}),400
@app.get("/")
def home():return render_template("index.html")
@app.get("/api/network")
def get_network():return jsonify(network.data)
@app.post("/api/network/load")
def load_network():return err(lambda:{"network":network.load(request.json.get("size","small"))})
@app.post("/api/network/random")
def random_network():return err(lambda:{"network":network.random_graph(int(request.json.get("n",10)),int(request.json.get("seed",7)))})
@app.post("/api/network")
def set_network():
    def run():
        global network
        network=DeliveryNetwork(request.json);return {"network":network.data}
    return err(run)
@app.get("/api/network/export")
def export_network():
    r=make_response(json.dumps(network.data,indent=2));r.headers["Content-Type"]="application/json";r.headers["Content-Disposition"]="attachment; filename=delivery_network.json";return r
@app.post("/api/shortest")
def shortest():
    def run():
        ids,edges,idx=network.graph(request.json.get("weight","effective"));s=idx[request.json["source"]];t=idx[request.json["target"]];n=len(ids);algo=request.json.get("algorithm","dijkstra")
        coords=[(x.get("x",0),x.get("y",0)) for x in network.data["locations"]]
        fn={"bfs":lambda:bfs(n,edges,s,t),"dijkstra":lambda:dijkstra(n,edges,s,t),"astar":lambda:astar(n,edges,s,t,coords),"bellman_ford":lambda:bellman_ford(n,edges,s,t),"floyd_warshall":lambda:floyd_warshall(n,edges)}.get(algo)
        if not fn:raise ValueError("Unknown shortest-path algorithm.")
        m=measure(fn);res=m.pop("result")
        if algo=="floyd_warshall":res={"distance":res["distances"][s][t],"path":[],"operations":res["operations"],"nodes_visited":None}
        res["path"]=[ids[i] for i in res.get("path",[])];out={**m,**res,"algorithm":algo};history.append(out);return out
    return err(run)
@app.post("/api/tsp")
def tsp():
    def run():
        ids,m=network.matrix();algo=request.json.get("algorithm","nearest")
        fn={"brute":lambda:brute_force(m),"nearest":lambda:nearest_neighbour(m),"held_karp":lambda:held_karp(m),"two_opt":lambda:two_opt(m)}.get(algo)
        if not fn:raise ValueError("Unknown route algorithm.")
        measured=measure(fn);res=measured.pop("result");res["route"]=[ids[i] for i in res["route"]]
        out={**measured,**res,"algorithm":algo};history.append(out);return out
    return err(run)
@app.post("/api/sort")
def sorting():
    def run():
        orders=request.json.get("orders",network.data["locations"]);field=request.json.get("field","priority");method=request.json.get("algorithm","merge")
        if field=="deadline":key=lambda x:x.get("time_window","")
        elif field=="distance":key=lambda x:float(x.get("distance",0))
        else:key=lambda x:-float(x.get("priority",0))
        return sort_items(orders,key,method)
    return err(run)
@app.post("/api/search")
def searching():
    def run():
        orders=request.json.get("orders",network.data["locations"]);fn=linear_search if request.json.get("algorithm")=="linear" else binary_search
        return fn(orders,request.json.get("id",""))
    return err(run)
@app.post("/api/loading")
def loading():
    def run():
        items=request.json.get("items") or [{"id":x["id"],"weight":x.get("weight",1),"value":x.get("priority",1)*10} for x in network.data["locations"] if x["id"]!="W"]
        cap=int(request.json.get("capacity",20));algo=request.json.get("algorithm","01")
        if algo=="fractional":return fractional_greedy(items,cap)
        if algo=="assign":return {"assignment":greedy_vehicle_assignment(items,int(request.json.get("vehicles",3)))}
        return knapsack_01(items,cap)
    return err(run)
@app.post("/api/mst")
def mst():
    def run():
        ids,edges,_=network.graph();und=[]
        seen=set()
        for u,v,w in edges:
            k=tuple(sorted((u,v)))
            if k not in seen:seen.add(k);und.append((u,v,w))
        algo=request.json.get("algorithm","prim")
        res=prim(len(ids),und) if algo=="prim" else kruskal(len(ids),und)
        res["edges"]=[[ids[u],ids[v],w] for u,v,w in res["edges"]];history.append(res);return res
    return err(run)
@app.post("/api/benchmark")
def benchmark():
    def run():
        ids,m=network.matrix(); tests=[]
        for name,fn in [("Nearest Neighbour",nearest_neighbour),("Held-Karp",held_karp)]:
            try:
                x=measure(fn,m);r=x.pop("result");tests.append({"algorithm":name,**x,"cost":r["cost"],"operations":r["operations"]})
            except ValueError as e:tests.append({"algorithm":name,"error":str(e)})
        valid=[x for x in tests if x.get("cost") is not None]
        best=min((x["cost"] for x in valid),default=None)
        for x in valid:x["optimality_gap_percent"]=round((x["cost"]-best)/best*100,2) if best else 0
        # Scalability sweep: deterministic complete Euclidean graphs at requested sizes.
        import random
        scaling=[]
        for size in (5,10,20,50,100):
            rng=random.Random(100+size); points=[(rng.random()*100,rng.random()*100) for _ in range(size)]
            matrix=[[round(math.hypot(points[i][0]-points[j][0],points[i][1]-points[j][1]),3) for j in range(size)] for i in range(size)]
            for label,fn in (("Nearest Neighbour",nearest_neighbour),("2-Opt",two_opt)):
                measured=measure(fn,matrix); result=measured.pop("result")
                scaling.append({"size":size,"algorithm":label,"time_ms":measured["time_ms"],"memory_kb":measured["memory_kb"],"operations":result["operations"]})
        out={"results":tests,"scaling":scaling,"recommendation":min(valid,key=lambda x:x["time_ms"])["algorithm"] if valid else "No feasible route"};history.extend(tests);return out
    return err(run)
@app.get("/api/history")
def get_history():return jsonify(history[-100:])
@app.get("/api/report.csv")
def report_csv():
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=["algorithm","time_ms","memory_kb","operations","cost","optimality_gap_percent"]);w.writeheader()
    for row in history:w.writerow({k:row.get(k,"") for k in w.fieldnames})
    r=make_response(out.getvalue());r.headers["Content-Type"]="text/csv";r.headers["Content-Disposition"]="attachment; filename=algorithm_report.csv";return r
@app.get("/api/report")
def report():return jsonify({"title":"Smart Delivery Route Optimization","network":network.data,"runs":history})
@app.get("/report/print")
def printable_report():
    rows="".join(f"<tr><td>{r.get('algorithm','')}</td><td>{r.get('time_ms','')}</td><td>{r.get('memory_kb','')}</td><td>{r.get('operations','')}</td><td>{r.get('cost','')}</td></tr>" for r in history)
    html=f"""<!doctype html><html><head><meta charset='utf-8'><title>Delivery Algorithm Report</title><style>body{{font:15px Arial;margin:35px;color:#17243a}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #aaa;padding:8px;text-align:left}}h1{{color:#175da8}}@media print{{button{{display:none}}}}</style></head><body><h1>Smart Delivery Route Optimization</h1><p>Algorithm Performance Laboratory — printable run report</p><p>Locations: {len(network.data['locations'])} | Roads: {len(network.data['roads'])} | Recorded runs: {len(history)}</p><table><tr><th>Algorithm</th><th>Time (ms)</th><th>Memory (KB)</th><th>Operations</th><th>Cost</th></tr>{rows}</table><p>Use the browser Print command to save this report as PDF.</p><button onclick='window.print()'>Print / Save as PDF</button></body></html>"""
    return html

@app.get("/api/operations")
def operations():
    seed_orders()
    delivered=sum(o["status"]=="Delivered" for o in orders)
    pending=sum(o["status"]=="Pending" for o in orders)
    transit=sum(o["status"]=="In Transit" for o in orders)
    return jsonify({"orders":orders,"drivers":drivers,"stats":{"total":len(orders),"delivered":delivered,"pending":pending,"transit":transit,"active_drivers":sum(d["status"]!="Available" for d in drivers),"distance_saved":round(max(0,len(orders)*2.4),1)},"locations":network.data["locations"],"roads":network.data["roads"]})

@app.post("/api/orders")
def create_order():
    def run():
        data=request.get_json(force=True); loc_id=data.get("location_id")
        loc=next((x for x in network.data["locations"] if x["id"]==loc_id),None)
        if not loc or loc_id=="W": raise ValueError("Choose a valid delivery location.")
        order={"id":f"ORD-{1001+len(orders)+int(len(orders)>0)}","customer":data.get("customer","New Customer").strip(),"address":loc["name"],"location_id":loc_id,"weight":float(data.get("weight",1)),"priority":int(data.get("priority",2)),"status":"Pending","driver_id":"Unassigned","eta":"To be planned"}
        if not order["customer"] or order["weight"]<=0: raise ValueError("Enter a customer name and valid parcel weight.")
        orders.insert(0,order); return {"order":order,"orders":orders}
    return err(run)

@app.patch("/api/orders/<order_id>")
def update_order(order_id):
    def run():
        data=request.get_json(force=True); order=next((o for o in orders if o["id"]==order_id),None)
        if not order: raise ValueError("Order not found.")
        if "status" in data:
            if data["status"] not in ["Pending","In Transit","Delivered","Cancelled"]: raise ValueError("Invalid delivery status.")
            order["status"]=data["status"]
        if "driver_id" in data:
            driver=next((d for d in drivers if d["id"]==data["driver_id"]),None)
            if not driver: raise ValueError("Driver not found.")
            order["driver_id"]=driver["id"]
            driver["status"]="On Delivery"
        return {"order":order}
    return err(run)

@app.post("/api/route/optimize")
def optimize_operations_route():
    def run():
        ids,m=network.matrix()
        active=[o for o in orders if o["status"] in ("Pending","In Transit") and o["location_id"] in ids]
        # Use the warehouse plus active delivery stops; algorithm remains an internal service detail.
        chosen=["W"]+[o["location_id"] for o in active if o["location_id"]!="W"]
        indexes=[ids.index(x) for x in chosen]
        matrix=[[m[i][j] for j in indexes] for i in indexes]
        result=nearest_neighbour(matrix)
        route=[chosen[i] for i in result["route"]]
        for order in active:
            order["eta"]=f"{max(10, int((result.get('cost') or 0)*2))} min"
        return {"route":route,"distance":round(result.get("cost") or 0,2),"stops":len(route)-1,"message":"Delivery sequence generated successfully."}
    return err(run)

if __name__=="__main__":app.run(host="127.0.0.1",port=5000,debug=True)

"""Terminal menu uses the same algorithm modules as the Flask application."""
import json
from service import DeliveryNetwork
from algorithms.graph import bfs,dijkstra,astar,bellman_ford
from algorithms.tsp import brute_force,nearest_neighbour,held_karp,two_opt
from algorithms.sorting import sort_items,linear_search,binary_search
from algorithms.loading import knapsack_01,fractional_greedy,greedy_vehicle_assignment
from algorithms.mst import prim,kruskal
from algorithms.benchmark import measure
net=DeliveryNetwork()
def show(obj):print(json.dumps(obj,indent=2,default=str))
def main():
    global net
    while True:
        print("""
SMART DELIVERY ROUTE OPTIMIZATION — ALGORITHM PERFORMANCE LAB
1. Create/Load Delivery Network
2. Shortest Path Algorithms
3. Multi-Stop Route Optimization
4. Delivery Prioritization (Sorting and Searching)
5. Vehicle Loading and Assignment
6. Network Infrastructure (MST)
7. Performance Laboratory
8. Visualization (web interface)
9. Reports
10. Help / About / Exit
""")
        choice=input("Choose module: ").strip()
        try:
            if choice=="1":
                sub=input("Load small/medium/large, random, export, import: ").lower()
                if sub in ("small","medium","large"):show(net.load(sub))
                elif sub=="random":show(net.random_graph(int(input("Nodes (2-100): "))))
                elif sub=="export":open("network_export.json","w").write(json.dumps(net.data,indent=2));print("Saved network_export.json")
                elif sub=="import":net=DeliveryNetwork(json.load(open(input("JSON filename: "))));print("Imported.")
            elif choice=="2":
                ids,e,idx=net.graph();s=idx[input("Source ID: ")];t=idx[input("Target ID: ")];name=input("bfs/dijkstra/astar/bellman_ford: ").lower();coords=[(x.get("x",0),x.get("y",0)) for x in net.data["locations"]]
                fn={"bfs":lambda:bfs(len(ids),e,s,t),"dijkstra":lambda:dijkstra(len(ids),e,s,t),"astar":lambda:astar(len(ids),e,s,t,coords),"bellman_ford":lambda:bellman_ford(len(ids),e,s,t)}[name];show(fn())
            elif choice=="3":
                ids,m=net.matrix();name=input("brute/nearest/held_karp/two_opt: ").lower();show({"brute":brute_force,"nearest":nearest_neighbour,"held_karp":held_karp,"two_opt":two_opt}[name](m))
            elif choice=="4":
                method=input("Sort bubble/insertion/merge/quick/heap: ");field=input("priority/deadline/distance: ")
                key=(lambda x:-x.get("priority",0)) if field=="priority" else (lambda x:x.get("time_window","") if field=="deadline" else x.get("distance",0))
                show(sort_items(net.data["locations"],key,method));print("Search:",linear_search(net.data["locations"],input("Order ID to find: ")))
            elif choice=="5":
                items=[{"id":x["id"],"weight":x.get("weight",1),"value":x.get("priority",1)*10} for x in net.data["locations"] if x["id"]!="W"];cap=int(input("Vehicle capacity: "));show(knapsack_01(items,cap));show(fractional_greedy(items,cap))
            elif choice=="6":
                ids,e,_=net.graph();und=list({(min(u,v),max(u,v),w) for u,v,w in e});show(prim(len(ids),und));show(kruskal(len(ids),und))
            elif choice=="7":
                ids,m=net.matrix();show(measure(nearest_neighbour,m))
            elif choice=="8":print("Run python app.py and open http://localhost:5000 for map/route visualization.")
            elif choice=="9":open("network_export.json","w").write(json.dumps(net.data,indent=2));print("Network exported. Use web UI for CSV run-history report.")
            elif choice=="10":print("Smart Delivery Route Optimization | Algorithms from scratch | Python + Flask");break
            else:print("Please select 1–10.")
        except Exception as ex:print("Input/algorithm error:",ex)
if __name__=="__main__":main()

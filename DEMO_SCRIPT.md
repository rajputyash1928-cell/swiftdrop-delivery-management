# 5-Minute Project Demonstration Script

## 0:00–0:30 — Introduction
**Click:** Open `http://localhost:5000`.  
**Say:** “My project is Smart Delivery Route Optimization. It is an Algorithm Performance Laboratory that models a warehouse and customer network, runs different algorithms, and compares their performance.”

## 0:30–1:00 — Create the network
**Click:** Sidebar → Create/Load Network → Small dataset.  
**Say:** “The sample network contains six locations and roads. I can also load 15 or 50 nodes, generate a random graph, or import and export JSON.”

## 1:00–1:45 — Shortest path
**Click:** Shortest Path → choose W as source and C3 as destination → Dijkstra → Run.  
**Say:** “Dijkstra finds the minimum traffic-adjusted distance when all edge weights are non-negative. The result includes the route, cost, execution time, memory and operation count. BFS is also available, but it minimizes edge count rather than weighted distance.”

## 1:45–2:30 — Multi-stop route
**Click:** Multi-Stop Routing → Nearest Neighbour → Optimize.  
**Say:** “For visiting multiple customers, I implemented a TSP-style route. Nearest Neighbour is fast but heuristic. Held–Karp and brute force are exact on small inputs, while 2-Opt improves a starting route.”

## 2:30–3:15 — Other algorithm families
**Click:** Prioritization, then Vehicle Loading, then Network Infrastructure.  
**Say:** “Orders can be sorted by priority or deadline and searched by ID. Knapsack chooses whole packages under capacity; fractional greedy is a comparison. Prim and Kruskal build a minimum spanning tree for infrastructure planning.”

## 3:15–4:15 — Performance lab and visualization
**Click:** Performance Lab → Benchmark algorithms; then Visualization.  
**Say:** “The benchmark measures both algorithms on the same matrix. Runtime and peak traced memory are empirical measurements; operation counts help explain algorithmic work. The graph view displays roads and the chosen route, which can be animated.”

## 4:15–5:00 — Reports and conclusion
**Click:** Reports → Download CSV results.  
**Say:** “The run history can be exported as CSV, and the full network and history are available as JSON. This project shows that algorithm choice depends on correctness requirements, input size, runtime and memory—not only on the shortest route.”

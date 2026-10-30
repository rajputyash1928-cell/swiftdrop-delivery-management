# 15 Viva Questions and Answers

1. **What is the aim of this project?**  
   To model delivery locations and compare algorithms that find routes, prioritize orders, load vehicles and connect road infrastructure.

2. **Why is a graph suitable for a delivery network?**  
   Locations are vertices and roads are edges. Edge weights can represent distance, travel time or traffic-adjusted cost.

3. **What is the difference between BFS and Dijkstra?**  
   BFS minimizes the number of edges in an unweighted graph. Dijkstra minimizes total non-negative edge weight.

4. **When is A* useful?**  
   A* uses a heuristic estimate of remaining cost to guide search toward a target. A suitable admissible heuristic can reduce exploration while preserving optimality.

5. **Why can Dijkstra not handle negative edges?**  
   Its greedy finalization assumes that extending a path cannot later produce a cheaper route through a negative edge.

6. **What does Bellman–Ford provide that Dijkstra does not?**  
   It supports negative edge weights and detects reachable negative-weight cycles.

7. **What is Floyd–Warshall used for?**  
   It computes shortest distances between every pair of vertices using dynamic programming.

8. **Why is brute-force TSP limited to small inputs?**  
   It checks permutations, so its time grows factorially as the number of stops increases.

9. **What is Held–Karp?**  
   It is a dynamic-programming solution to TSP with O(n²2ⁿ) time and O(n2ⁿ) space.

10. **Is Nearest Neighbour guaranteed to find the optimal tour?**  
    No. It greedily chooses the closest unvisited stop and can make locally good but globally poor choices.

11. **What does 2-Opt improve?**  
    It removes crossing or inefficient route segments by reversing subsequences when the total tour cost decreases.

12. **What is the difference between 0/1 and fractional knapsack?**  
    0/1 knapsack either selects an entire item or rejects it. Fractional knapsack can take part of an item.

13. **What is a minimum spanning tree?**  
    It connects every vertex in a connected undirected weighted graph with minimum total edge weight and no cycles.

14. **How is performance measured?**  
    `perf_counter` measures elapsed time, `tracemalloc` measures peak traced Python memory, and instrumented counters record algorithmic operations.

15. **What are the limitations and possible improvements?**  
    The current model uses abstract coordinates and static road costs. Real maps, time-dependent traffic, delivery time windows, and persistent history can be added.

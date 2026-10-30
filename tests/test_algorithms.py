import pytest
from algorithms.graph import bfs,dijkstra,astar,bellman_ford,floyd_warshall
from algorithms.tsp import brute_force,nearest_neighbour,held_karp,two_opt
from algorithms.sorting import sort_items,linear_search,binary_search
from algorithms.loading import knapsack_01,fractional_greedy
from algorithms.mst import prim,kruskal

def test_shortest_paths():
    e=[(0,1,2),(1,2,3),(0,2,9)]
    assert dijkstra(3,e,0,2)["distance"]==5
    assert astar(3,e,0,2,[(0,0),(1,0),(2,0)])["distance"]==5
    assert bellman_ford(3,e,0,2)["distance"]==5
    assert bfs(3,e,0,2)["distance"]==1
    assert floyd_warshall(3,e)["distances"][0][2]==5

def test_disconnected_and_negative():
    assert dijkstra(3,[(0,1,1)],0,2)["path"]==[]
    with pytest.raises(ValueError):dijkstra(2,[(0,1,-1)],0,1)
    with pytest.raises(ValueError):bellman_ford(2,[(0,1,1),(1,0,-3)],0,1)

def test_tsp():
    m=[[0,1,4],[1,0,2],[4,2,0]]
    assert brute_force(m)["cost"]==held_karp(m)["cost"]==7
    assert nearest_neighbour(m)["cost"]==7
    assert two_opt(m)["cost"]==7
    with pytest.raises(ValueError):brute_force([[0]*10 for _ in range(10)])

def test_sort_search():
    x=[{"id":"b","priority":1},{"id":"a","priority":3}]
    assert sort_items(x,lambda z:-z["priority"],"merge")["items"][0]["id"]=="a"
    assert linear_search(x,"b")["index"]==0
    assert binary_search(x,"a")["item"]["id"]=="a"

def test_loading_mst():
    x=[{"id":"a","weight":2,"value":3},{"id":"b","weight":3,"value":5}]
    assert knapsack_01(x,3)["total_value"]==5
    assert fractional_greedy(x,3)["total_value"]>0
    e=[(0,1,1),(1,2,2),(0,2,4)]
    assert prim(3,e)["cost"]==kruskal(3,e)["cost"]==3
    with pytest.raises(ValueError):kruskal(3,[(0,1,1)])

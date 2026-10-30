"""Shortest-path algorithms. All counters count key algorithmic operations."""
from math import hypot, inf

def _validate(n, edges, source, target=None, allow_negative=False):
    if not isinstance(n, int) or n <= 0: raise ValueError("Network must contain at least one node.")
    if not 0 <= source < n: raise ValueError("Source node is out of range.")
    if target is not None and not 0 <= target < n: raise ValueError("Target node is out of range.")
    for u,v,w in edges:
        if not (0 <= u < n and 0 <= v < n): raise ValueError("Road endpoint is out of range.")
        if not isinstance(w,(int,float)): raise ValueError("Road weight must be numeric.")
        if w < 0 and not allow_negative: raise ValueError("Negative road weights are not allowed for this algorithm.")

def _adj(n, edges, undirected=False):
    a=[[] for _ in range(n)]
    for u,v,w in edges:
        a[u].append((v,w))
        if undirected: a[v].append((u,w))
    return a

def _result(dist, prev, target, ops, visited):
    if target is None: path=[]
    elif dist[target] == inf: path=[]
    else:
        path=[]; x=target
        while x is not None: path.append(x); x=prev[x]
        path.reverse()
    return {"distance": None if target is None or dist[target] == inf else dist[target],
            "distances":[None if x == inf else x for x in dist], "path":path,
            "operations":ops, "nodes_visited":visited}

def bfs(n, edges, source, target):
    """Unweighted shortest path. Time O(V+E), space O(V+E)."""
    _validate(n,edges,source,target); a=_adj(n,edges)
    from collections import deque
    d=[inf]*n; p=[None]*n; d[source]=0; q=deque([source]); ops=0; seen=0
    while q:
        u=q.popleft(); seen+=1
        for v,_ in a[u]:
            ops+=1
            if d[v] == inf: d[v]=d[u]+1; p[v]=u; q.append(v)
    return _result(d,p,target,ops,seen)

def dijkstra(n, edges, source, target):
    """Dijkstra with a binary heap. Time O((V+E)log V), space O(V+E)."""
    import heapq
    _validate(n,edges,source,target); a=_adj(n,edges)
    d=[inf]*n; p=[None]*n; d[source]=0; h=[(0,source)]; ops=seen=0
    while h:
        du,u=heapq.heappop(h); ops+=1
        if du != d[u]: continue
        seen+=1
        for v,w in a[u]:
            ops+=1
            if du+w < d[v]: d[v]=du+w; p[v]=u; heapq.heappush(h,(d[v],v))
    return _result(d,p,target,ops,seen)

def astar(n, edges, source, target, coords=None):
    """A* using Euclidean coordinate heuristic. Time O((V+E)log V) typical; space O(V+E)."""
    import heapq
    _validate(n,edges,source,target)
    if coords is None: coords=[(0,0)]*n
    if len(coords)!=n: raise ValueError("Provide coordinates for every node.")
    a=_adj(n,edges)
    hfun=lambda x: hypot(coords[x][0]-coords[target][0],coords[x][1]-coords[target][1])
    g=[inf]*n; p=[None]*n; g[source]=0; heap=[(hfun(source),0,source)]; ops=seen=0
    while heap:
        _,gu,u=heapq.heappop(heap); ops+=1
        if gu != g[u]: continue
        seen+=1
        if u==target: break
        for v,w in a[u]:
            ops+=1
            if gu+w<g[v]:
                g[v]=gu+w; p[v]=u; heapq.heappush(heap,(g[v]+hfun(v),g[v],v))
    return _result(g,p,target,ops,seen)

def bellman_ford(n, edges, source, target):
    """Bellman-Ford. Time O(VE), space O(V). Detects reachable negative cycles."""
    _validate(n,edges,source,target,allow_negative=True)
    d=[inf]*n; p=[None]*n; d[source]=0; ops=0
    for _ in range(n-1):
        changed=False
        for u,v,w in edges:
            ops+=1
            if d[u]!=inf and d[u]+w<d[v]: d[v]=d[u]+w; p[v]=u; changed=True
        if not changed: break
    for u,v,w in edges:
        ops+=1
        if d[u]!=inf and d[u]+w<d[v]: raise ValueError("Reachable negative-weight cycle detected.")
    return _result(d,p,target,ops,n)

def floyd_warshall(n, edges):
    """All-pairs shortest paths. Time O(V^3), space O(V^2)."""
    if n<=0: raise ValueError("Network must contain at least one node.")
    d=[[inf]*n for _ in range(n)]; nxt=[[None]*n for _ in range(n)]; ops=0
    for i in range(n): d[i][i]=0; nxt[i][i]=i
    for u,v,w in edges:
        if not (0<=u<n and 0<=v<n): raise ValueError("Road endpoint is out of range.")
        d[u][v]=min(d[u][v],w); nxt[u][v]=v
    for k in range(n):
        for i in range(n):
            for j in range(n):
                ops+=1
                if d[i][k]+d[k][j]<d[i][j]:
                    d[i][j]=d[i][k]+d[k][j]; nxt[i][j]=nxt[i][k]
    if any(d[i][i]<0 for i in range(n)): raise ValueError("Negative cycle detected.")
    return {"distances":[[None if x==inf else x for x in row] for row in d],
            "operations":ops,"space_cells":n*n}

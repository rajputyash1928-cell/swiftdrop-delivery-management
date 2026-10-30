"""Minimum spanning tree implementations for undirected weighted roads."""
def prim(n,edges,start=0):
    """Prim using a simple array frontier. Time O(V^2+E), space O(V+E)."""
    if n<=0:raise ValueError("Node count must be positive.")
    a=[[] for _ in range(n)]
    for u,v,w in edges:
        if w<0:raise ValueError("MST edge weights must be non-negative.")
        a[u].append((v,w));a[v].append((u,w))
    used={start}; tree=[]; total=0; ops=0
    while len(used)<n:
        best=None
        for u in used:
            for v,w in a[u]:
                ops+=1
                if v not in used and (best is None or w<best[2]):best=(u,v,w)
        if best is None:raise ValueError("Graph is disconnected; no spanning tree exists.")
        u,v,w=best;used.add(v);tree.append([u,v,w]);total+=w
    return {"edges":tree,"cost":total,"operations":ops}

def kruskal(n,edges):
    """Kruskal with disjoint-set union. Time O(E log E), space O(V)."""
    parent=list(range(n));rank=[0]*n;ops=0
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    tree=[];total=0
    for u,v,w in sorted(edges,key=lambda x:x[2]):
        ops+=1;ru,rv=find(u),find(v)
        if ru!=rv:
            if rank[ru]<rank[rv]:ru,rv=rv,ru
            parent[rv]=ru
            if rank[ru]==rank[rv]:rank[ru]+=1
            tree.append([u,v,w]);total+=w
            if len(tree)==n-1:break
    if n>1 and len(tree)!=n-1:raise ValueError("Graph is disconnected; no spanning tree exists.")
    return {"edges":tree,"cost":total,"operations":ops}

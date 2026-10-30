"""Multi-stop routing algorithms. Costs are directed as supplied by the distance matrix."""
from itertools import permutations
from math import inf

def _check(m):
    n=len(m)
    if n==0 or any(len(r)!=n for r in m): raise ValueError("Distance matrix must be non-empty and square.")
    if any(x is not None and x<0 for row in m for x in row): raise ValueError("TSP distances cannot be negative.")
    return n

def route_cost(route,m,return_to_start=True):
    seq=route+([route[0]] if return_to_start and route else [])
    total=0
    for a,b in zip(seq,seq[1:]):
        w=m[a][b]
        if w is None: return inf
        total+=w
    return total

def brute_force(m,start=0):
    """Exact permutation search. Time O((n-1)!), space O(n). Restricted to n<=9."""
    n=_check(m)
    if n>9: raise ValueError("Brute force is limited to 9 locations.")
    if not 0<=start<n: raise ValueError("Start index out of range.")
    others=[i for i in range(n) if i!=start]; best=inf; best_route=[]; ops=0
    for p in permutations(others):
        r=[start]+list(p); c=route_cost(r,m); ops+=n
        if c<best: best,best_route=c,r
    return {"route":best_route,"cost":None if best==inf else best,"operations":ops,"optimal":True}

def nearest_neighbour(m,start=0):
    """Greedy nearest unvisited stop. Time O(n^2), space O(n)."""
    n=_check(m); route=[start]; un=set(range(n))-{start}; ops=0
    while un:
        u=route[-1]; choices=[]
        for v in un:
            ops+=1
            if m[u][v] is not None: choices.append((m[u][v],v))
        if not choices: return {"route":route,"cost":None,"operations":ops,"optimal":False}
        v=min(choices)[1]; route.append(v); un.remove(v)
    c=route_cost(route,m)
    return {"route":route,"cost":None if c==inf else c,"operations":ops+n,"optimal":False}

def held_karp(m,start=0):
    """Held-Karp exact dynamic programming. Time O(n^2 2^n), space O(n 2^n)."""
    n=_check(m)
    if n>20: raise ValueError("Held-Karp is limited to 20 locations to protect memory.")
    if n==1: return {"route":[start],"cost":0,"operations":1,"optimal":True}
    nodes=[i for i in range(n) if i!=start]; dp={(1<<i, i): (m[start][v] if m[start][v] is not None else inf, None) for i,v in enumerate(nodes)}
    ops=len(nodes)
    for mask in range(1,1<<len(nodes)):
        for j,v in enumerate(nodes):
            if not mask&(1<<j): continue
            if mask==(1<<j): continue
            prevmask=mask^(1<<j); best=inf; parent=None
            for k,u in enumerate(nodes):
                if prevmask&(1<<k):
                    base=dp.get((prevmask,k),(inf,None))[0]; edge=m[u][v]; ops+=1
                    if edge is not None and base+edge<best: best,parent=base+edge,k
            dp[(mask,j)]=(best,parent)
    full=(1<<len(nodes))-1; best=inf; last=None
    for j,v in enumerate(nodes):
        edge=m[v][start]; val=dp[(full,j)][0]; ops+=1
        if edge is not None and val+edge<best: best,last=val+edge,j
    if last is None: return {"route":[],"cost":None,"operations":ops,"optimal":True}
    order=[]; mask=full; j=last
    while j is not None:
        order.append(nodes[j]); _,parent=dp[(mask,j)]; mask^=1<<j; j=parent
    route=[start]+order[::-1]
    return {"route":route,"cost":best,"operations":ops,"optimal":True}

def two_opt(m, initial=None):
    """2-opt local improvement. Worst-case O(n^3) time, O(n) extra space."""
    n=_check(m)
    if initial is None: initial=nearest_neighbour(m)["route"]
    if len(initial)!=n: raise ValueError("Initial route must include each location exactly once.")
    route=initial[:]; best=route_cost(route,m); ops=0; improved=True
    while improved:
        improved=False
        for i in range(1,n-1):
            for k in range(i+1,n):
                candidate=route[:i]+route[i:k+1][::-1]+route[k+1:]
                c=route_cost(candidate,m); ops+=1
                if c<best: route,best,improved=candidate,c,True
    return {"route":route,"cost":None if best==inf else best,"operations":ops,"optimal":False}

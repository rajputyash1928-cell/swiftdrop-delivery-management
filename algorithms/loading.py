"""Vehicle loading algorithms."""
def knapsack_01(items,capacity):
    """0/1 knapsack DP. Time O(nW), space O(nW) for reconstruction."""
    if capacity<0: raise ValueError("Capacity cannot be negative.")
    if any(x["weight"]<0 or x["value"]<0 for x in items): raise ValueError("Weight and value must be non-negative.")
    n=len(items); dp=[[0]*(capacity+1) for _ in range(n+1)]; ops=0
    for i,x in enumerate(items,1):
        w=int(x["weight"]); val=float(x["value"])
        for cap in range(capacity+1):
            dp[i][cap]=dp[i-1][cap]; ops+=1
            if w<=cap: dp[i][cap]=max(dp[i][cap],dp[i-1][cap-w]+val)
    chosen=[]; cap=capacity
    for i in range(n,0,-1):
        if dp[i][cap]!=dp[i-1][cap]:chosen.append(items[i-1]);cap-=int(items[i-1]["weight"])
    chosen.reverse()
    return {"items":chosen,"total_weight":sum(x["weight"] for x in chosen),"total_value":dp[n][capacity],"operations":ops}

def fractional_greedy(items,capacity):
    """Fractional knapsack greedy. Time O(n log n), space O(n)."""
    if capacity<0:raise ValueError("Capacity cannot be negative.")
    if any(x["weight"]<=0 or x["value"]<0 for x in items):raise ValueError("Weights must be positive and values non-negative.")
    a=sorted(items,key=lambda x:x["value"]/x["weight"],reverse=True); remain=capacity; picked=[]; value=0
    for x in a:
        if remain<=0:break
        take=min(1,remain/x["weight"]); picked.append({"item":x,"fraction":take}); remain-=take*x["weight"];value+=take*x["value"]
    return {"items":picked,"total_weight":capacity-remain,"total_value":value,"operations":len(a)}

def greedy_vehicle_assignment(customers,vehicles):
    """Assign each customer to the currently least-loaded vehicle that can fit it. O(CV)."""
    loads=[0]*vehicles; groups=[[] for _ in range(vehicles)]
    for c in sorted(customers,key=lambda x:x.get("weight",0),reverse=True):
        candidates=[i for i in range(vehicles) if loads[i]+c.get("weight",0)<=float("inf")]
        i=min(candidates,key=lambda j:loads[j]);groups[i].append(c);loads[i]+=c.get("weight",0)
    return [{"vehicle":i+1,"customers":g,"total_weight":loads[i]} for i,g in enumerate(groups)]

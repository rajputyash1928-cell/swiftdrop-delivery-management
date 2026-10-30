"""Sorting/searching implementations with comparison counters."""
def sort_items(items,key,method="merge"):
    a=[dict(x) for x in items]; c={"comparisons":0,"operations":0}
    def less(x,y): c["comparisons"]+=1; return key(x)<key(y)
    if method=="bubble":
        for i in range(len(a)):
            for j in range(0,len(a)-i-1):
                if less(a[j+1],a[j]): a[j],a[j+1]=a[j+1],a[j]
    elif method=="insertion":
        for i in range(1,len(a)):
            x=a[i]; j=i-1
            while j>=0 and less(x,a[j]): a[j+1]=a[j]; j-=1
            a[j+1]=x
    elif method=="merge":
        def ms(x):
            if len(x)<=1:return x
            mid=len(x)//2; l=ms(x[:mid]); r=ms(x[mid:]); out=[]; i=j=0
            while i<len(l) and j<len(r):
                if less(r[j],l[i]): out.append(r[j]); j+=1
                else: out.append(l[i]); i+=1
            return out+l[i:]+r[j:]
        a=ms(a)
    elif method=="quick":
        def qs(lo,hi):
            if lo>=hi:return
            pivot=key(a[hi]); i=lo
            for j in range(lo,hi):
                c["comparisons"]+=1
                if key(a[j])<=pivot: a[i],a[j]=a[j],a[i]; i+=1
            a[i],a[hi]=a[hi],a[i]; qs(lo,i-1); qs(i+1,hi)
        qs(0,len(a)-1)
    elif method=="heap":
        def sift(n,i):
            largest=i; l=2*i+1; r=l+1
            if l<n and less(a[largest],a[l]):largest=l
            if r<n and less(a[largest],a[r]):largest=r
            if largest!=i:a[i],a[largest]=a[largest],a[i]; sift(n,largest)
        for i in range(len(a)//2-1,-1,-1):sift(len(a),i)
        for end in range(len(a)-1,0,-1):a[0],a[end]=a[end],a[0];sift(end,0)
    else: raise ValueError("Sort method must be bubble, insertion, merge, quick, or heap.")
    c["operations"]=c["comparisons"]
    return {"items":a,**c}

def linear_search(items,order_id):
    ops=0
    for i,x in enumerate(items):
        ops+=1
        if str(x.get("id"))==str(order_id):return {"index":i,"item":x,"operations":ops}
    return {"index":-1,"item":None,"operations":ops}

def binary_search(items,order_id):
    """Requires items sorted by stringified ID. Time O(log n), space O(1)."""
    a=sorted(items,key=lambda x:str(x.get("id"))); lo=0; hi=len(a)-1; ops=0
    while lo<=hi:
        mid=(lo+hi)//2; ops+=1; val=str(a[mid].get("id"))
        if val==str(order_id):return {"index":mid,"item":a[mid],"operations":ops}
        if val<str(order_id):lo=mid+1
        else:hi=mid-1
    return {"index":-1,"item":None,"operations":ops}

from mip import Model, xsum, minimize, BINARY   
import random as rd
import math
from sys import stdout as out

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


n_customer = 10
n_nodes = n_customer + 1 # 1 for warehouse

nodes = [ (rd.randint(0, 10), rd.randint(0, 10)) for _ in range(n_nodes)]
graph = [[0 for _ in range(n_nodes)] for _ in range(n_nodes)]

for i in range(n_nodes):
    for j in range(n_nodes):
        graph[i][j] = dist(nodes[i], nodes[j])


capacity = 100

P = [ 0 for _ in range(n_customer)]
D = [ rd.randint(0,10) for _ in range(n_customer)]


V = no_vehicle = 1
c = graph 


# Decision Parameters

model = Model()

x = [[[model.add_var(var_type=BINARY) for _ in range(n_nodes)] for _ in range(n_nodes)] for _ in range(V)]

S = [model.add_var() for _ in range(n_customer)]

Iv = [model.add_var() for _ in range(V)]

Ij = [model.add_var() for _ in range(n_customer)]



pd_max = max(P+D)
c_max = sum([c[i][j] for i in range(n_nodes) for j in range(n_nodes)])
M = max(pd_max, c_max)
# print (M)

# Ojective Function


model.objective = minimize(xsum(c[i][j]*x[k][i][j] for k in range(no_vehicle) for i in range(n_nodes) for j in range(n_nodes)))

# Constraints

# 3.
# range(1,n_nodes) refers to excluding warehouse
for j in range(1, n_nodes):
        model += xsum(x[v][i][j] for i in range(n_nodes) for v in range(no_vehicle) if i!=j) == 1

# 4.
for v in range(no_vehicle):
    for k in range(1,n_nodes):
        model += xsum(x[v][i][k] for i in range(n_nodes)) == xsum(x[v][k][j] for j in range(n_nodes)) 

# 5.
for v in range(no_vehicle):
    model += xsum(D[j-1] * x[v][i][j] for i in range(n_nodes) for j in range(1,n_nodes)) == Iv[v]

# 6.
for v in range(no_vehicle):
    for j in range(1, n_nodes):
        model += Ij[j-1] >= Iv[v] - D[j-1] + P[j-1] - M*(1-x[v][0][j])

# 7.
for i in range(1, n_nodes):
    for j in range(1, n_nodes):
        if i != j:
            model += Ij[j-1] >= Ij[i-1] - D[j-1] + P[j-1] - M*(1 - xsum(x[v][i][j] for v in range(no_vehicle)))

# 8.
for i in range(no_vehicle):
    model += Iv[v] <= capacity

# 9.
for i in range(n_customer):
    model += Ij[i] <= capacity


# 10. 
for i in range(1, n_nodes):
    for j in range(1, n_nodes):
        if i!=j:
            model += S[j-1] >= S[i-1] + 1 - n_nodes*(1- xsum(x[v][i][j] for v in range(no_vehicle)))

# 11.
for i in range(n_customer):
    model += S[i] >= 0


model.optimize(max_seconds=30)


# print ("graph", c)
# print (D)

print ("--"*15)
for i in c:
    print (i)
print ("--"*15)

# checking if a solution was found
if model.num_solutions:
    # print ("******"*15)
    # out.write('route with total distance %g found: %s'
            #   % (model.objective_value, places[0]))
    # nc = 0
    # while True:
    #     nc = [i for i in V if x[nc][i].x >= 0.99][0]
    #     out.write(str(nc) + "\n")
    #     # out.write(' -> %s' % places[nc])
    #     if nc == 0:
    #         break

    for v in range(no_vehicle):
        for i in range(n_nodes):
            for k in range(n_nodes):
                if x[v][i][k].x>=0.9:
                    print (i, k)
                # print (x[v][i][j].x)

    print ("--"*15)
    print ("Sequence in oder will be delivered")
    for i in range(n_customer):
        print (S[i].x)
    print ("--"*15)
    out.write('\n')
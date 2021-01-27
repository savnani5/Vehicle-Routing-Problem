# -*- coding: utf-8 -*-
## Savings based Hybrid CWS method for CVRP

import random as rd

rd.seed(105)                                                          ## Only for testing
nodes = 50                                                           ## Total nodes with depot 
node_designations = [i for i in range(1,nodes)]                       ## Node designations
depot = (0,0)                                                         ## Coordinates of depot and customers
customer_demand = [rd.randint(5,6) for i in range(1,nodes)]          ## eg: [3,2,4,5,1,2,2,3,4,5]   ## index = 1 to 10      
vehicle_capacity = [5,3,4,10,15,2,3,1]                                    ## Vehicle capacity vector 
vehicle_capacity = sorted(vehicle_capacity, reverse = True)           ## Sorted in decreasing order to utilize high capacity vehicle first
vehicles = len(vehicle_capacity)                                      ## No. of vehicles alloted

print("\nCustomer_demands=", customer_demand)

def distance(x, y):
    return ((x[0]-y[0])**2 + (x[1]-y[1])**2)**0.5

def demand_sum(route, customer_demand):
    demand = 0
    for i in route:
        demand = demand + customer_demand[i-1]
    return demand

def preprocess(nodes, vehicles):
    node_list = [] 
    
    node_list.append(depot)
    for i in range(nodes-1):
        node_list.append((rd.randint(1,10), rd.randint(1,10)))

    distance_matrix = [[0 for i in range(nodes)] for j in range(nodes)]   
    saving_matrix = [[[i, j, 0] for i in range(0, nodes)] for j in range(0, nodes)] ## Savings matrix for CWS  # index : 0 to 10; 0 is depot
   
    for i in range(nodes):
        for j in range(nodes):
            distance_matrix[i][j] = round(distance(node_list[i], node_list[j]), 2)
    # print("\nDistance_matrix=\n", distance_matrix)
    
    for i in range(nodes):
        for j in range(0,i):
            saving_matrix[i][j][2] = round(distance_matrix[0][i] + distance_matrix[0][j] - distance_matrix[i][j], 2) 
    # print("\nSaving_matrix=\n", saving_matrix)       
   
    saving_list = [elem for twod in saving_matrix for elem in twod]                 ## To flatten a 3d list to 2d list
    saving_list = sorted(saving_list, key=lambda l:l[2], reverse=True)              ## To sort the list in descending order along the 3rd column
    # print("\nSaving list= ",saving_list)
    return saving_list, node_list
     
def main(nodes, saving_list):
    
    vehicle_routes = []
    
    for i in range(vehicles):
        capacity = vehicle_capacity[i]
        route_list = []
        
        for demand in customer_demand:
            if capacity < demand:
                continue
            else:
                break
        else:
            continue
                
        for path in saving_list:
            
            if path[2]==0:
                break
            
            if len(route_list) == 0:
                demand0 = customer_demand[path[0]-1]  
                demand1 = customer_demand[path[1]-1]
                if demand0 + demand1 <= capacity: 
                    route_list.append([path[0], path[1]])
                    continue
                if demand0 <= capacity:
                    route_list.append([path[0]])
                    continue
                if demand1 <= capacity:
                    route_list.append([path[1]])
                    continue
                
            ## First Condition ##  Creating new routes
            
            for route in route_list:
                if (path[0] in route) or (path[1] in route):
                    break
            else:
                demand0 = customer_demand[path[0]-1]  
                demand1 = customer_demand[path[1]-1]
                if demand0 + demand1 <= capacity: 
                    route_list.append([path[0], path[1]])
                    continue
                if demand0 <= capacity:
                    route_list.append([path[0]])
                    continue
                if demand1 <= capacity:
                    route_list.append([path[1]])
                    continue
            
            ## Second condition ##  Combining two routes having similar edges
            
            if len(route_list) >= 2:
                buffer = []
                for route in route_list:
                    
                    if path[0] == route[0] or path[0] == route[-1]:
                        a = route_list.index(route)
                        buffer.append(route)
        
                    if path[1] == route[0] or path[1] == route[-1]:
                        b = route_list.index(route)
                        buffer.append(route)
                
                if len(buffer) == 2 and buffer[0] != buffer[1]:
    
                    for i in range(2): 
                        path[0], path[1] = path[1], path [0]
                        
                        if path[0] == buffer[0][0] and path[1] == buffer[1][0]:
                            result = buffer[0][::-1] + buffer[1]
                        
                        if path[0] == buffer[0][0] and path[1] == buffer[1][-1]:
                            result = buffer[0][::-1] + buffer[1][::-1]
                        
                        if path[0] == buffer[0][-1] and path[1] == buffer[1][0]:
                            result = buffer[0] + buffer[1]
                            
                        if path[0] == buffer[0][-1] and path[1] == buffer[1][-1]:
                            result = buffer[0] + buffer[1][::-1]
                    
                    demand = demand_sum(result, customer_demand)
                    if demand <= capacity:
                        if a<b:
                            route_list.pop(b)
                            route_list.pop(a)
                        else:
                            route_list.pop(a)
                            route_list.pop(b)
                        route_list.append(result) 
            
           
            ## Third Condition ##  Adding nodes on edges of the route
                        
            check = []
            for i in route_list:
                check = check + i         
            for route in route_list:
                demand = demand_sum(route, customer_demand)
                if path[0] == route[0] and path[1] not in check:
                    demand = demand + customer_demand[path[1]-1]
                    if demand <= capacity:
                        route.insert(0, path[1])
                        break
                
                if path[0] == route[-1] and path[1] not in check:
                    demand = demand + customer_demand[path[1]-1]
                    if demand <= capacity:
                        route.append(path[1])
                        break
                    
                if path[1] == route[0] and path[0] not in check:
                    demand = demand + customer_demand[path[0]-1]
                    if demand <= capacity:
                        route.insert(0, path[0])
                        break
                    
                if path[1] == route[-1] and path[0] not in check:  
                    demand = demand + customer_demand[path[0]-1]
                    if demand <= capacity:
                        route.append(path[0])
                        break
                    
        # print("\nroute_list = ",route_list)
                    
        ## To get the route with max weight utilized for current vehicle:
            
        customer_demand_vec = [customer_demand for i in range(len(route_list))]
        demand_vec = list(map(demand_sum, route_list, customer_demand_vec))
        index = demand_vec.index(max(demand_vec))

        ## Renewing the saving_list for next vehicle
        
        new_saving_list = []
        for path in saving_list:
           if path[0] not in route_list[index] and path[1] not in route_list[index]:
               new_saving_list.append(path)
        
        saving_list = new_saving_list
        # print("saving_list=", saving_list)
        vehicle_routes.append(route_list[index])
        
        if saving_list[0][2]==0:            ## If no new vehicles are needed for delivery
            break
        
    return vehicle_routes


if __name__=="__main__":
    
    saving_list, node_list = preprocess(nodes, vehicles)
    vehicle_routes = main(nodes, saving_list)
    print("\n---Vehicle Routes---")
    
    total_distance = 0
    printing_node_list = [ [(0,0),i] for i in node_list[1:]]
    print("\nNode list= ",printing_node_list)
    for i in range(len(vehicle_routes)):
        prev = (0, 0)
        for j in vehicle_routes[i]:
            total_distance += distance(prev, node_list[j])
            prev = node_list[j]
        vehicle_routes[i].insert(0,0)
        print(f"\nVehicle {i+1} with {vehicle_capacity[i]}kg capacity should go on: ",vehicle_routes[i])
    
    print ("\ntotal distance: ",total_distance)


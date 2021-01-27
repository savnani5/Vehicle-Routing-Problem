from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
import random as rd

def euclidean_dist(a, b):
    return math.sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2)


# TO DO: add documentation
class VRPSPD_ortools():

    def __init__(self, depot_location, total_orders, type_of_orders, locations_of_orders, delivery_sizes, no_vehicles, capcaity_of_vehicles):
        """
        """
        self.data = self._preprocess(depot_location, total_orders, type_of_orders, locations_of_orders, delivery_sizes, no_vehicles, capcaity_of_vehicles)


    def _preprocess(self, depot_location, total_orders, type_of_orders, locations_of_orders, delivery_sizes, no_vehicles, capcaity_of_vehicles):
        # TO DO: check input validation
        # TO DO: Optimization of distance matrix calculation
        data = {}
        data['locations'], data['pickups_deliveries'] = [ depot_location ], []
        data['demands'] = [0]
        cnt = 1
        for i, k in zip(locations_of_orders, delivery_sizes):
            data['locations'].append(i[0])
            data['locations'].append(i[1])
            data['pickups_deliveries'].append([cnt, cnt+1])
            data['demands'].append(k)
            data['demands'].append(-k)
            cnt += 2

        data['distance_matrix'] =  [ [ euclidean_dist(i,j) for j in data['locations']] for i in data['locations']]
        data['num_vehicles'] = no_vehicles
        data['vehicle_capacities'] = capcaity_of_vehicles
        data['depot'] = 0
        

        return data

    def generate_output(self, manager, routing, solution):
        total_distance = 0
        full_plan = []
        for vehicle_id in range(self.data['num_vehicles']):
            index = routing.Start(vehicle_id)
            vehicle_plan = []
            route_distance = 0
            while not routing.IsEnd(index):
                actual_id = manager.IndexToNode(index)
                if not vehicle_plan:
                    vehicle_plan.append(self.data['locations'][actual_id])
                if vehicle_plan and vehicle_plan[-1] != self.data['locations'][actual_id]:
                    vehicle_plan.append(self.data['locations'][actual_id])
            
                # plan_output += f"{actual_id}  {data['locations'][actual_id]} [{data['demands'][actual_id]}] -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            
            # plan_output += '{}\n'.format(manager.IndexToNode(index))
            # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            # print(plan_output)
            full_plan.append(vehicle_plan)
            total_distance += route_distance
        # print('Total Distance of all routes: {}m'.format(total_distance))
        return full_plan
        
 
    def solve(self):
        manager = pywrapcp.RoutingIndexManager(len(self.data['distance_matrix']),
                                           self.data['num_vehicles'], self.data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)


        # Define cost of each arc.
        def distance_callback(from_index, to_index):
            """Returns the manhattan distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Define Transportation Requests.
        for request in self.data['pickups_deliveries']:
            pickup_index = manager.NodeToIndex(request[0])
            delivery_index = manager.NodeToIndex(request[1])
            routing.AddPickupAndDelivery(pickup_index, delivery_index)
            routing.solver().Add(
                routing.VehicleVar(pickup_index) == routing.VehicleVar(
                    delivery_index))
            routing.solver().Add(
                distance_dimension.CumulVar(pickup_index) <=
                distance_dimension.CumulVar(delivery_index))

        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return self.data['demands'][from_node]


        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)


        output_dict = {}

        # Print solution on console.
        if solution:
            output_dict['status'] = "Success"
            full_plan = self.generate_output(manager, routing, solution)
            return True, full_plan, output_dict
        else:
            output_dict['status'] = "Failed!"
            return False, None, output_dict

if __name__ == "__main__":

    depot_location = (0,0)
    rd.seed(1)
    total_orders = 10 
    type_of_orders = [0] # 0 for delivery, 1 for pickup
    
    locations_of_orders = [[(0, 0), (58, 61)], [(0, 0), (49, 27)], [(0, 0), (13, 63)], [(0, 0), (4, 50)], [(0, 0), (56, 1)], [(0, 0), (58, 35)], [(0, 0), (30, 14)], [(0, 0), (41, 4)], [(0, 0), (3, 4)], [(0, 0), (70, 2)]]
    # for i in range(total_orders):
    #    locations_of_orders.append([(0,0), (rd.randint(1,10), rd.randint(1,10))])
    
       
    delivery_sizes = [2, 5, 7, 7, 7, 1, 3, 1, 4, 7]
    no_vehicles =  1
    capcaity_of_vehicles = [70]

    solver = VRPSPD_ortools(depot_location, total_orders, type_of_orders, locations_of_orders, delivery_sizes, no_vehicles, capcaity_of_vehicles)
    status, full_plan, output_dict = solver.solve()
    if status:
        for idx, i in enumerate(full_plan):
            print (f"vehicle: {idx} path:{i}")

    

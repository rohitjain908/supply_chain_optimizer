import requests
from cachetools import TTLCache
from model import RouteCostResponse, StatusCode, StoresResponse


class SupplyChainOptimizer:
    """Supply chain optimizer"""

    _INF = float('inf')

    def __init__(self, api_base_url, cache_ttl=300):
        self.api_base_url = api_base_url
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)
        self.routes = {}
        self.route_cost = {}
        self.route_store_mapping = {}
        self.cost = []
        self.sample_stores = {
            "warehouses": [
                {
                    "warehouseId": "WH-rDImX",
                    "demand": 192,
                    "availableRoutes": [
                        {
                            "routeNumber": 1,
                            "distance": 174.47
                        },
                        {
                            "routeNumber": 2,
                            "distance": 250
                        }
                    ]
                },
                {
                    "warehouseId": "WH-5a7KO",
                    "demand": 104,
                    "availableRoutes": [
                        {
                            "routeNumber": 3,
                            "distance": 471.08
                        },
                        {
                            "routeNumber": 2,
                            "distance": 280
                        }
                    ]
                },
                {
                    "warehouseId": "WH-Wp7LX",
                    "demand": 288,
                    "availableRoutes": [
                        {
                            "routeNumber": 3,
                            "distance": 220.87
                        }
                    ]
                }
            ]
        } 
        self.route1_cost = {
            "status": 200,
            "data": {
                "basicRouteCost": "765.35",
                "routeCostPerKm": "2.39",
                "estimatedTimeHours": "42.83",
                "isExpress": False,
                "additionalInsuranceCost": "99.07"
            }
        }

        self.route2_cost = {
            "status": 200,
            "data": {
                "cost": {
                    "baseCost": "1115.51",
                    "tax": "0",
                    "perKm": "3.93"
                },
                "routeDetails": {
                    "transitTimeDays": 9,
                    "premiumService": False
                },
                "additionalCost": {
                    "fuelSurcharge": "150.66",
                    "customsDuty": "0"
                }
            }
        }

        self.route3_cost = {
            "status": 200,
            "data": {
                "pricing": {
                    "baseRate": "768.42",
                    "perKm": "3.71"
                },
                "logistics": {
                    "mileage": "472.20",
                    "deliveryWindowHours": 48,
                    "expeditedShipping": False
                },
                "surcharges": {
                    "peakSeasonCharge": "111.09",
                    "remoteAreaFee": "0"
                }
            }
        }


    def sort_routes_store_by_distance(self) -> None:
        """Sorts the stores for each route by distance in ascending order."""

        for route, stores in self.route_store_mapping.items():
            # Sort the list of (distance, store) tuples by the first element (distance)
            self.route_store_mapping[route] = sorted(stores, key=lambda x: x[0])

        # Optionally, you can log or print the sorted route mappings if needed
        print(self.route_store_mapping)
    
    def setup_store_routes(self, store_data: StoresResponse) -> None:
        """Sets up the route-to-store mapping based on store data."""

        for index, store in enumerate(store_data.warehouses):
            available_routes = store.availableRoutes

            for route in available_routes:
                route_number = route.routeNumber
                distance = route.distance

                # Initialize the route if it's not already in the mapping
                if route_number not in self.route_store_mapping:
                    self.route_store_mapping[route_number] = []

                # Append the (distance, store index) tuple to the route mapping
                self.route_store_mapping[route_number].append((distance, index + 1))

        # Sort the stores in each route by distance
        self.sort_routes_store_by_distance()
    
    def fetch_and_setup_stores_data(self) -> None:
        """Fetches store data from the API and sets up store routes."""

        try:
            stores_response = requests.get(f"{self.api_base_url}/warehouse-supply-requirements")
            stores_response.raise_for_status()
        except requests.RequestException as e:
            print(f"failed to fetch stores data, internal server error")

        # Parse the response into the StoresResponse Pydantic model
        stores_data = StoresResponse(**stores_response.json())

        # Set up store routes using the parsed data
        self.setup_store_routes(stores_data)


        # self.setup_store_routes(StoresResponse(**self.sample_stores))
    def set_route_cost(self, route_number: int, route_cost: RouteCostResponse) -> None:
        """Sets the cost for a specific route based on the provided route cost data."""
        
        # Access the cost data directly from the RouteCostResponse model
        cost_data = route_cost.data
        base_cost = 0.0
        per_km_cost = 0.0
        additional_cost = 0.0

        # Base cost calculation
        base_cost += float(cost_data.get('basicRouteCost', 0))
        
        cost_section = cost_data.get('cost', {})
        
        base_cost += float(cost_section.get('baseCost', 0))
        base_cost += float(cost_section.get('tax', 0))
        
        pricing_section = cost_data.get('pricing', {})
        base_cost += float(pricing_section.get('baseRate', 0))
        
        # Per kilometer cost calculation
        per_km_cost += float(cost_data.get('routeCostPerKm', 0))
        per_km_cost += float(cost_section.get('perKm', 0))
        per_km_cost += float(pricing_section.get('perKm', 0))
        
        # Additional cost calculation
        additional_cost += float(cost_data.get('additionalInsuranceCost', 0))
        
        additional_cost_section = cost_data.get('additionalCost', {})
        
        for cost_value in additional_cost_section.values():
            additional_cost += float(cost_value)
        
        surcharges_section = cost_data.get('surcharges', {})
        
        for cost_value in surcharges_section.values():
            additional_cost += float(cost_value)
        
        # Calculate final fixed cost
        fix_cost = base_cost + additional_cost
        
        # Store the calculated route costs
        self.route_cost[route_number] = {
            "fix_cost": fix_cost,
            "per_km_cost": per_km_cost
        }

        # Debugging output
        print("route_number", route_number)
        print("Stored Route Cost:", self.route_cost[route_number])


    def fetch_and_set_route_cost(self) -> None:
        for route, _ in self.route_store_mapping.items():
            try:
                response = requests.get(f"{self.api_base_url}/route/{route}")
                response.raise_for_status()
                route_cost_response = RouteCostResponse(**response.json())
                if route_cost_response.status == StatusCode.OK:
                    self.set_route_cost(route, route_cost_response)
                else:
                    raise RuntimeError(f"failed to fetch route {route} data, {route_cost_response.error}")
            
            except requests.RequestException as e:
                print(f"Error fetching cost for route {route}: {e}")

        # self.set_route_cost(1, RouteCostResponse(**self.route1_cost))
        # self.set_route_cost(2, RouteCostResponse(**self.route2_cost))
        # self.set_route_cost(3, RouteCostResponse(**self.route3_cost))
        
    def get_routes_count(self):
        self.routes_count = len(self.route_store_mapping)
        return len(self.route_store_mapping)

    def recursion(self, route_index, stores_covered):

        total_stores_covered_value = ((2**self.get_routes_count())) - 1
        if stores_covered == total_stores_covered_value:
            return 0
        
        if route_index > self.routes_count:
            return SupplyChainOptimizer._INF
        
        minimum_cost = SupplyChainOptimizer._INF
        minimum_cost = min(minimum_cost, self.recursion(route_index + 1, stores_covered))

        added_cost = self.route_cost[route_index]['fix_cost']
        previous_distance = 0
        updated_stores_covered_value = stores_covered
        
        for distance, store in self.route_store_mapping[route_index]:
            added_cost+= (distance - previous_distance) * self.route_cost[route_index]['per_km_cost']
            updated_stores_covered_value = updated_stores_covered_value ^ (2**(store - 1))
            minimum_cost = min(minimum_cost, added_cost + self.recursion(route_index + 1, updated_stores_covered_value))
            previous_distance = distance

        return minimum_cost

    def calculate_optimal_cost(self):
        self.fetch_and_set_route_cost()
        optimal_cost = self.recursion(1, 0)
        return optimal_cost
    
        


# Example Usage
if __name__ == "__main__":
    optimizer = SupplyChainOptimizer(api_base_url="https://dzap-backend-task-production.up.railway.app/task")

    optimizer.fetch_and_setup_stores_data()
    optimal_cost = optimizer.calculate_optimal_cost()
    if optimal_cost == SupplyChainOptimizer._INF:
        print("From give routes we can't send items to all stores")
    else:
        print("optimal_cost", optimal_cost)


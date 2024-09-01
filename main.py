import requests
from model import RouteCostResponse, StatusCode, StoresResponse
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv
import os
from utility import CacheUtility
import logging

load_dotenv()  # Load environment variables from a .env file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupplyChainOptimizer:
    """Supply chain optimizer for managing routes and costs."""

    _INF = float('inf')
    STORES_DATA_CACHE_KEY = "stores_data"

    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL")
        cache_ttl = int(os.getenv("CACHE_TIME_TO_LIVE_IN_SECONDS", 30))
        cache_maxsize = int(os.getenv("CACHE_MAXSIZE", 5))

        self.cache_util = CacheUtility(maxsize=cache_maxsize, ttl=cache_ttl)  # Use the caching utility
        self.route_cost: Dict[int, Dict[str, float]] = {}
        self.route_store_mapping: Dict[int, List[Tuple[float, int]]] = {}
        self.routes_count = 0

    def sort_routes_store_by_distance(self) -> None:
        """Sorts the stores for each route by distance in ascending order."""

        for route in self.route_store_mapping:
            self.route_store_mapping[route].sort(key=lambda x: x[0])
        logger.info(f"Sorted route store mapping: {self.route_store_mapping}")

    def setup_store_routes(self, store_data: StoresResponse) -> None:
        """Sets up the route-to-store mapping based on store data."""

        for index, store in enumerate(store_data.warehouses):
            for route in store.availableRoutes:
                self.route_store_mapping.setdefault(route.routeNumber, []).append((route.distance, index + 1))
        self.routes_count = len(self.route_store_mapping)
        self.sort_routes_store_by_distance()

    def fetch_and_setup_stores_data(self) -> None:
        """Fetches store data from the API and sets up store routes."""

        stores_data = self.cache_util.get(self.STORES_DATA_CACHE_KEY)
        if stores_data is not None:
            logger.info("Using cached store data.")
            return 

        try:
            response = requests.get(f"{self.api_base_url}/warehouse-supply-requirements")
            response.raise_for_status()
            stores_data = StoresResponse(**response.json())
            self.cache_util.set(self.STORES_DATA_CACHE_KEY, stores_data)  # Cache the fetched store data
            self.setup_store_routes(stores_data)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch stores data: {e}")

    def calculate_costs(self, cost_data: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate fixed and per km costs from cost data."""

        base_cost = (
            float(cost_data.get('basicRouteCost', 0)) +
            float(cost_data.get('cost', {}).get('baseCost', 0)) +
            float(cost_data.get('cost', {}).get('tax', 0)) +
            float(cost_data.get('pricing', {}).get('baseRate', 0))
        )

        per_km_cost = (
            float(cost_data.get('routeCostPerKm', 0)) +
            float(cost_data.get('cost', {}).get('perKm', 0)) +
            float(cost_data.get('pricing', {}).get('perKm', 0))
        )

        additional_cost = (
            float(cost_data.get('additionalInsuranceCost', 0)) +
            sum(float(value) for value in cost_data.get('additionalCost', {}).values()) +
            sum(float(value) for value in cost_data.get('surcharges', {}).values())
        )

        return base_cost + additional_cost, per_km_cost

    def set_route_cost(self, route_number: int, route_cost: RouteCostResponse) -> None:
        """Sets the cost for a specific route based on the provided route cost data."""

        cost_data = route_cost.data or {}
        fixed_cost, per_km_cost = self.calculate_costs(cost_data)

        self.route_cost[route_number] = {
            "fix_cost": fixed_cost,
            "per_km_cost": per_km_cost
        }

        logger.info(f"Route number: {route_number}, Stored Route Cost: {self.route_cost[route_number]}")

    def fetch_and_set_route_cost(self) -> None:
        """Fetches and sets route costs for all routes."""

        for route in self.route_store_mapping.keys():
            route_cost_response = self.cache_util.get(f"route_cost_{route}")
            if route_cost_response is not None:
                logger.info(f"Using cached route cost for route {route}. data is {route_cost_response} ")
                continue 

            try:
                response = requests.get(f"{self.api_base_url}/route/{route}")
                response.raise_for_status()
                route_cost_response = RouteCostResponse(**response.json())

                if route_cost_response.status == StatusCode.OK:
                    self.cache_util.set(f"route_cost_{route}", route_cost_response)  # Cache the fetched route cost
                    self.set_route_cost(route, route_cost_response)
                else:
                    raise RuntimeError(f"Failed to fetch route {route} data, {route_cost_response.error}")
            except requests.RequestException as e:
                logger.error(f"Error fetching cost for route {route}: {e}")


    def recursion(self, route_index: int, stores_covered: int, memo: Dict[Tuple[int, int], float]) -> float:
        """Recursively calculates the minimum cost to cover all stores."""

        total_stores_covered_value = (1 << self.routes_count) - 1
        if stores_covered == total_stores_covered_value:
            return 0
        
        if route_index > self.routes_count:
            return SupplyChainOptimizer._INF
        
        # Check if the result is already computed
        if (route_index, stores_covered) in memo:
            return memo[(route_index, stores_covered)]

        minimum_cost = SupplyChainOptimizer._INF
        minimum_cost = min(minimum_cost, self.recursion(route_index + 1, stores_covered, memo))

        added_cost = self.route_cost[route_index]['fix_cost']
        previous_distance = 0
        updated_stores_covered_value = stores_covered
        
        for distance, store in self.route_store_mapping[route_index]:
            added_cost += (distance - previous_distance) * self.route_cost[route_index]['per_km_cost']
            updated_stores_covered_value ^= (1 << (store - 1))
            minimum_cost = min(minimum_cost, added_cost + self.recursion(route_index + 1, updated_stores_covered_value, memo))
            previous_distance = distance

        memo[(route_index, stores_covered)] = minimum_cost  # Cache the result
        return minimum_cost

    def calculate_optimal_cost(self) -> float:
        """Calculates the optimal cost for delivering to all stores."""
        
        optimal_cost = self.recursion(1, 0, {})
        logger.info(f"Calculated optimal cost: {optimal_cost}")
        return optimal_cost

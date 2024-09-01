from main import SupplyChainOptimizer

def test_supply_chain_optimizer():
    # Initialize the SupplyChainOptimizer
    optimizer = SupplyChainOptimizer()

    # Step 1: Fetch and set up stores data
    print("Fetching and setting up stores data...")
    optimizer.fetch_and_setup_stores_data()
    print("Stores data setup complete.")

    # Step 2: Fetch and set up route costs
    print("Fetching and setting up route costs...")
    optimizer.fetch_and_set_route_cost()
    print("Route costs setup complete.")

    # Step 3: Calculate the optimal distribution cost
    print("Calculating the optimal distribution cost...")
    optimal_cost = optimizer.calculate_optimal_cost()

    if optimal_cost == SupplyChainOptimizer._INF:
        print("Error: From the given routes, the warehouse can't send items to all stores.")
    else:
        print(f"Optimal cost calculated: {optimal_cost}")

if __name__ == '__main__':
    test_supply_chain_optimizer()
from flask import Flask, jsonify
from main import SupplyChainOptimizer  # Replace with your actual module name

app = Flask(__name__)
optimizer = SupplyChainOptimizer()

@app.route('/fetch_stores', methods=['GET'])
def fetch_stores():
    """Fetch and setup stores data."""
    optimizer.fetch_and_setup_stores_data()
    return jsonify({"message": "Stores data fetched and set up successfully"}), 200

@app.route('/fetch_route_cost', methods=['GET'])
def fetch_route_cost():
    """Fetch and set route cost data."""
    optimizer.fetch_and_set_route_cost()
    return jsonify({"message": "Route costs fetched and set up successfully"}), 200

@app.route('/optimal_cost', methods=['GET'])
def optimal_cost():
    """Calculate the optimal cost."""
    optimal_cost = optimizer.calculate_optimal_cost()
    if optimal_cost == SupplyChainOptimizer._INF:
        return jsonify({"error": "From the given routes we can't send items to all stores."}), 400
    return jsonify({"optimal_cost": optimal_cost}), 200

if __name__ == '__main__':
    app.run(debug=True)

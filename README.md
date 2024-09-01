## Setup and Installation

1. **Clone the Repository**:
   
   ```bash
   git clone https://github.com/yourusername/supply_chain_optimizer.git
   cd supply_chain_optimizer

2. **Create a Virtual Environment**:
   
   - On macOS and Linux:
     
     ```bash
     python3 -m venv venv
     ```
   - On Windows:
     
     ```bash
     python -m venv venv
     ```

4. **Activate the Virtual Environment**:
   
   - On macOS and Linux:
     
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     
     ```bash
     venv\Scripts\activate
     ```

6. **Install Dependencies**:
   
   ```bash
   pip install -r requirements.txt

8. **Run the Server**:
   
   ```bash
   python app.py


## Testing the Solution

1. **Start the Server**:
   - Ensure the server is running by using the following command:
     
     ```bash
     python app.py
     ```

2. **Call the APIs in Sequence**:

   - **Step 1**: Call the `fetch_stores` API to fetch and set up stores data.
     
      **NOTE**: Keep calling this API until it returns a success message.
       
     ```bash
     curl http://127.0.0.1:5000/fetch_stores
     ```
     Example success response:
     
     ```json
     {
       "message": "Stores data fetched and set up successfully"
     }
     ```

   - **Step 2**: Call the `fetch_route_cost` API to fetch and set up route cost data.
     
     **NOTE**: Ensure this API returns a success message before proceeding.
       
     ```bash
     curl http://127.0.0.1:5000/fetch_route_cost
     ```
     
     Example success response:
     
     ```json
     {
       "message": "Route costs fetched and set up successfully"
     }
     ```

   - **Step 3**: Call the `optimal_cost` API to calculate the optimal distribution cost.
     
     **NOTE**: Only call this API after the previous two APIs have successfully executed.
       
     ```bash
     curl http://127.0.0.1:5000/optimal_cost
     ```
     
     Example success response:
     
     ```json
     {
       "optimal_cost": 4064.51
     }
     ```

     If the system cannot deliver to all stores using the available routes, you might get an error response like this:
     ```json
     {
       "error": "From the given routes warehouse can't send items to all stores."
     }
     ```

3. **Alternative Testing Method:**

   You can either follow the above steps for testing the APIs or run the test suite directly using

    ```bash
     python test.py
     ```


# SwiftDrop — Smart Delivery Operations

A Flask-based delivery operations demo with order management, driver assignments, route planning, delivery status updates and operational analytics. The route and optimization logic runs in the backend; the interface is designed around everyday dispatch work rather than algorithm terminology.

## Run on Windows (PowerShell)

Open PowerShell in this folder, then run:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the PowerShell window open while using the app. To stop the server, press `Ctrl+C`.

If PowerShell says scripts are disabled, run the `Set-ExecutionPolicy` command above in the same PowerShell window and activate again. You do not need to type the PowerShell prompt itself—only the commands inside the code block.

## Main features

- Operations dashboard with order status and fleet summary
- Create delivery orders
- Assign drivers and update delivery statuses
- Generate a suggested multi-stop route
- Review driver capacity and assignments
- View operational insights and export a CSV report

## Demo data and limitations

The included warehouse, customers, roads, orders and drivers are sample data for demonstration. Records created in the web app are held in memory and reset when the server restarts. Route distance is based on the included sample road network; this is not connected to live maps, GPS, customer notifications, or a real dispatch service. Do not enter real customer personal or payment information.

## Developer checks

Run the algorithm unit tests with:

```powershell
python -m pytest -q
```

The original algorithm modules, CLI, test suite, project report, demo script and viva notes are retained in the project for technical evaluation. The customer-facing web interface intentionally presents operational features rather than classroom topic names.

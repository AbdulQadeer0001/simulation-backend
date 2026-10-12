# Simulation Backend

A Python-based simulation backend built with **Flask**. The project includes simulation-related application modules, data files, tests, and queueing-analysis dependencies. It is intended to provide the simulation logic and supporting results for the project's user interface.

**Repository:** [AbdulQadeer0001/Simulation](https://github.com/AbdulQadeer0001/Simulation)

## Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Run the Application](#run-the-application)
- [Run Tests](#run-tests)
- [Project Structure](#project-structure)
- [Frontend Integration](#frontend-integration)
- [Data and Results](#data-and-results)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Overview

This repository contains the Python side of a simulation project. Flask provides the web-application layer, while scientific and simulation libraries support data processing and simulation workflows.

### Main components

- **Flask** — web application and server
- **Flask-CORS** — Cross-Origin Resource Sharing support for a separately hosted frontend
- **SimPy** — discrete-event simulation
- **NumPy, pandas, and SciPy** — numerical computation and data analysis
- **openpyxl and xlrd** — spreadsheet file support
- **pytest** — automated testing

The repository also contains an `app/` package, a `tests/` directory, observed data, configuration, and a CSV results file. See the source code for the exact simulation models and currently implemented features.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Backend programming language |
| Flask | Web application |
| Flask-CORS | Cross-origin API access |
| SimPy | Discrete-event simulation |
| NumPy | Numerical operations |
| pandas | Tabular data processing |
| SciPy | Scientific and statistical calculations |
| openpyxl / xlrd | Spreadsheet input/output support |
| pytest | Testing |

## Prerequisites

Install:

- Git
- Python 3.10 or a compatible version supported by the installed dependencies
- `pip` and Python's `venv` module

Check your tools:

```bash
git --version
python3 --version
python3 -m pip --version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AbdulQadeer0001/Simulation.git
cd Simulation
```

### 2. Create a virtual environment

On Linux, including Kali Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If the virtual-environment command fails on a Debian-based system, install the venv package for your Python version. For example:

```bash
sudo apt update
sudo apt install python3-venv
```

Then create and activate the environment again.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Keep the virtual environment activated while running the app and tests.

## Run the Application

Start the Flask application from the repository root:

```bash
python app.py
```

The current entry point configures Flask to listen on `127.0.0.1` at port `5000` with debug mode enabled. When it starts successfully, open:

```text
http://127.0.0.1:5000
```

The available pages and API endpoints depend on the routes implemented in the `app/` package. If the root URL does not have a route, that does not necessarily mean the server failed to start; inspect the application's routes or logs.

**Development note:** Debug mode is intended for local development only. Do not expose a debug server to the public internet. For deployment, use a production WSGI server and configure the host, port, and environment appropriately.

## Run Tests

Run the test suite from the project root with the virtual environment activated:

```bash
pytest
```

To see more detail:

```bash
pytest -v
```

The repository includes a `tests/` directory and a `pytest.ini` configuration file. If tests require data files or specific environment settings, follow the requirements documented in those tests.

## Project Structure

The repository's main files and folders include:

```text
Simulation/
├── app/                  # Flask application package and simulation modules
├── data/
│   └── observed/         # Observed/input data used by the project
├── tests/                # Automated tests
├── app.py                # Application entry point
├── config.py             # Application configuration
├── pytest.ini            # Pytest configuration
├── requirements.txt      # Python dependencies
├── queuelab_results.csv  # Queueing/simulation results data
└── README.md             # Project documentation
```

The exact contents of `app/` and `data/` may evolve as development continues.

## Frontend Integration

If you are using the separate React frontend, run the frontend and backend in separate terminals during development.

**Terminal 1 — backend**

```bash
cd Simulation
source .venv/bin/activate
python app.py
```

**Terminal 2 — frontend**

```bash
cd simulation-frontend
npm install
npm run dev
```

The backend's current local address is:

```text
http://127.0.0.1:5000
```

The frontend must call the API endpoints actually implemented by this backend. Before wiring up a request:

1. Inspect the Flask routes in the `app/` package.
2. Confirm the HTTP method, endpoint path, request body, and response format.
3. Configure the frontend to use the correct backend base URL.
4. Handle network errors and invalid inputs in the frontend.
5. If the frontend runs on another origin, configure CORS for the frontend's development origin in Flask.
6. Keep debug mode enabled only for local development.

Do not assume that an endpoint exists just because it is mentioned in frontend code or documentation; verify it in the backend source.

## Data and Results

- `data/observed/` contains observed data used by the project.
- `queuelab_results.csv` contains saved queueing/simulation results.

Check the relevant code and tests to understand each file's columns, units, expected format, and role in the simulation. Do not overwrite original observed data unless that is intended.

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and install the dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `Address already in use`

Port `5000` may already be occupied. Stop the other process or configure the app to use a different port.

### Frontend cannot connect to the backend

- Confirm the backend is running.
- Verify the base URL and endpoint path.
- Check the browser's developer console and Network tab.
- Check Flask's terminal output.
- Check the CORS configuration if the frontend and backend use different origins.

### `pytest` is not found

Activate the virtual environment and install the requirements again:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

### Spreadsheet or data-file errors

Verify that the expected data file exists and that its format matches what the code expects. Check file paths and column names in the relevant application module.

## Development

A suggested workflow for changes:

1. Create a branch for your feature or fix.
2. Make a focused change.
3. Run `pytest`.
4. Test the application locally with `python app.py`.
5. Confirm the frontend integration still works if API behavior changed.
6. Commit with a descriptive message and push your branch.

Example:

```bash
git checkout -b feature/describe-your-change
git add .
git commit -m "Describe the change"
git push -u origin feature/describe-your-change
```

## License

Add a `LICENSE` file and update this section if you intend to distribute the project under a specific open-source license.
# simulation-backend

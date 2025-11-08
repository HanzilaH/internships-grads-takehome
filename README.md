## Incident.io take home task
## On-Call Schedule Renderer

This repository contains a simple system for generating an on-call schedule based on a rotation policy and applying optional overrides. The core logic is implemented in (`render-schedule.py`).


### Core Components

  * **`render-schedule.py`**: The main executable CLI script. It takes the base schedule, overrides, and a time range (`--from`, `--until`) as input, generates the base schedule, applies the overrides, and outputs the final schedule as a JSON list of entries.
  * **`model.py`**: Defines Pydantic models (`Schedule` and `Entry`) for structured data parsing and validation of the schedule configuration and individual schedule/override entries.
  * **`backend.py`**: A Flask application that hosts a React App on localhost:5500 and implements REST endpoint (`/schedule`) to receive configuration via a POST request, executes the `render-schedule.py` script, and returns the final rendered schedule as a JSON response.
  * **`schedule.json`**: An example file defining the base on-call rotation: the list of users, the start time of the first handover, and the rotation interval.
  * **`overrides.json`**: An example file containing a list of `Entry` objects that define exceptions or overrides to the base rotation.
  * **`output.json`**: The resulting rendered schedule from the example run.

#### Prerequisites

  * Python 3.x
  * The `flask` and `pydantic` libraries. You can install them using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

#### Setup

1.  Make the core script executable:
    ```bash
    chmod +x render-schedule.py
    ```

### CLI Usage

The `render-schedule.py` script can be run directly from the command line.

**Syntax:**

```bash
./render-schedule.py --schedule <SCHEDULE_FILE> --overrides <OVERRIDES_FILE> --from <START_TIME> --until <END_TIME>
```

**Example (using provided files):**

```bash
./render-schedule.py \
    --schedule schedule.json \
    --overrides overrides.json \
    --from 2025-11-07T17:00:00Z \
    --until 2025-11-21T17:00:00Z
```

This command will print the final schedule to the console and write it to `output.json`.


### ⚙️ Implementation Details

#### Schedule Generation (`generate_base_entries`)

This function iteratively calculates the shifts based on the `handover_start_at`, `handover_interval_days`, and the rotating list of `users`. It finds the shifts that overlap with the requested `[from_time, until)` range and truncates them to fit within that range.

#### Override Application (`apply_overrides`)

The `apply_overrides` function ensures that any time covered by an override takes precedence. It works by:

1.  Iterating through each `base_entry`.
2.  Finding all `overrides` that overlap with the current `base_entry`.
3.  If an override is found, the original `base_entry` is split into up to three parts:
      * The part **before** the override (if any).
      * The override itself (truncated to the `base_entry` bounds).
      * The part **after** the override (if any).
4.  The final list of entries is sorted by `start_at` time.

-----


## React App

In addition to implementing algorithm, we implemented a placeholder web app to visualise the outputs from output.json

### Backend Usage (Flask API)

The `backend.py` file sets up a simple web server to serve the React frontend (assuming it exists in `./frontend/calendar-app/build`) and expose the schedule rendering logic via an API.

#### Running the Server

```bash
python3 backend.py
```

The server will typically run on `http://127.0.0.1:5500`, therefore go to chrome or another browser and paste this link to see the UI

#### API Endpoint
  * **Endpoint**: `/`
  * **Method**: `GET`
  * **Purpose**: Serves the pre-built React app through python.

  * **Endpoint**: `/schedule`
  * **Method**: `POST`
  * **Purpose**: Renders the on-call schedule based on the provided configuration.


*(Note: You donot need to install Node to run the React App. It is already built in ./frontend/calendar-app/build/ folder)*
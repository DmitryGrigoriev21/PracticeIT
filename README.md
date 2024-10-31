# Apache Log Analytics System

This system consists of three components:
1. Log Aggregator (Flask server)
2. Log Parser (Apache log file monitor)
3. Log Client (Command-line interface)

# Installation

1. Clone the repository:
```bash 
git clone <repository-url>
cd apache-logs
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate```
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```


## 1. Log Aggregator

### Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE apache_logs;
```

2. Apply database schema:
```bash
psql -d apache_logs -f schema.sql
```
3. Create `.env` file:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=apache_logs
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```
### Running the Aggregator
```bash
python app.py
```
The server will start on `http://localhost:5000` by default.

### API Endpoints

#### POST /logs
Saves a log entry to the database.

Request body example:

```json
{
"ip_address": "192.168.1.1",
"timestamp": "2023-07-20T10:00:00",
"request_method": "GET",
"request_url": "/api/resource",
"status_code": 200,
"response_size": 1024,
"user_agent": "Mozilla/5.0..."
}
```

#### GET /logs
Retrieves logs with optional filters.

Query parameters:
- `ip`: Filter by IP address
- `date`: Filter by date (YYYY-MM-DD)
- `start_time`: Filter by start timestamp
- `end_time`: Filter by end timestamp

Example: `/logs?ip=192.168.1.1&date=2023-07-20`

## 2. Log Parser

```bash
pip install -r requirements.txt
```

### Configuration

Create `parser_config.yaml`:
```yaml
log_dir: "/var/log/apache2"
file_pattern: "access.log"
aggregator_host: "localhost"
aggregator_port: 5000
scan_interval: 10
state_file: "parser_state.json"
```

Configuration parameters:
- `log_dir`: Directory containing Apache log files
- `file_pattern`: Glob pattern for log files
- `aggregator_host`: Host address of the Log Aggregator
- `aggregator_port`: Port of the Log Aggregator
- `scan_interval`: How often to check for changes (seconds)
- `state_file`: File to store parsing state

### Running the Parser

```bash
python log_parser.py
```

The parser will:
1. Process existing log files
2. Monitor for new log entries
3. Parse and send logs to the aggregator
4. Maintain state between restarts

## 3. Log Client

```bash
pip install -r requirements.txt
```

### Configuration

Create `config.yaml`:
```yaml
api_url: "http://localhost:5000"
output_format: "json" # or "text"
```

### Usage

Basic usage:

```bash
python log_client.py [options]
```

Options:
- `--config`: Path to configuration file
- `--api-url`: Override API URL
- `--output-format`: Set output format (json/text)
- `--ip`: Filter by IP address
- `--date`: Filter by date (YYYY-MM-DD)
- `--start-time`: Filter from timestamp (YYYY-MM-DDTHH:MM:SS)
- `--end-time`: Filter until timestamp (YYYY-MM-DDTHH:MM:SS)

Examples:


Using config file
```bash
python log_client.py --config config.yaml
```
Filter by IP
```bash
python log_client.py --ip 192.168.1.1
```
Filter by date range
```bash
python log_client.py --start-time 2023-07-20T10:00:00 --end-time 2023-07-20T11:00:00
```
Combine filters with text output
```bash
python log_client.py --ip 192.168.1.1 --date 2023-07-20 --output-format text
```
## Dependencies
Main dependencies:
- Flask
- psycopg2-binary
- requests
- PyYAML
- python-dotenv
- watchdog

## Error Handling

All components include comprehensive error handling:
- Database connection errors
- API communication errors
- File access errors
- Configuration errors
- Input validation








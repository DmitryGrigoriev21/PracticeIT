import argparse
import requests
import json
import sys
import yaml
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class ClientConfig:
    api_url: str = "http://localhost:5000"
    output_format: str = "json"


class LogClient:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.base_url = config.api_url.rstrip('/')

    def get_logs(self,
                 ip: Optional[str] = None,
                 date: Optional[str] = None,
                 start_time: Optional[str] = None,
                 end_time: Optional[str] = None) -> Dict:
        params = {}
        if ip:
            params['ip'] = ip
        if date:
            params['date'] = date
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time

        try:
            response = requests.get(f"{self.base_url}/logs", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching logs: {e}", file=sys.stderr)
            sys.exit(1)

    def display_logs(self, logs: Dict):
        if self.config.output_format == "json":
            print(json.dumps(logs, indent=2))
        else:  # plain text format
            for log in logs:
                print(f"IP: {log['ip_address']}")
                print(f"Timestamp: {log['timestamp']}")
                print(f"Method: {log['request_method']}")
                print(f"URL: {log['request_url']}")
                print(f"Status: {log['status_code']}")
                print(f"Size: {log['response_size']}")
                print(f"User Agent: {log['user_agent']}")
                print("-" * 50)


def load_config(config_path: Optional[str]) -> ClientConfig:
    config = ClientConfig()

    if config_path:
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                config.api_url = yaml_config.get('api_url', config.api_url)
                config.output_format = yaml_config.get('output_format', config.output_format)
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            sys.exit(1)

    return config


def validate_date(date_string: str) -> str:
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def validate_datetime(datetime_string: str) -> str:
    try:
        datetime.fromisoformat(datetime_string)
        return datetime_string
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime format: {datetime_string}. Use YYYY-MM-DDTHH:MM:SS"
        )


def main():
    parser = argparse.ArgumentParser(description="Apache Log Aggregator Client")

    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--api-url', help='API URL for the log aggregator')
    parser.add_argument('--output-format', choices=['json', 'text'],
                        help='Output format (json or text)')

    # Filter arguments
    parser.add_argument('--ip', help='Filter logs by IP address')
    parser.add_argument('--date', type=validate_date,
                        help='Filter logs by date (YYYY-MM-DD)')
    parser.add_argument('--start-time', type=validate_datetime,
                        help='Filter logs from this time (YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end-time', type=validate_datetime,
                        help='Filter logs until this time (YYYY-MM-DDTHH:MM:SS)')

    args = parser.parse_args()
    config = load_config(args.config)

    if args.api_url:
        config.api_url = args.api_url
    if args.output_format:
        config.output_format = args.output_format

    client = LogClient(config)

    logs = client.get_logs(
        ip=args.ip,
        date=args.date,
        start_time=args.start_time,
        end_time=args.end_time
    )

    client.display_logs(logs)


if __name__ == "__main__":
    main()

import os
import glob
import yaml
import requests
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import re


@dataclass
class ParserConfig:
    log_dir: str
    file_pattern: str
    aggregator_host: str
    aggregator_port: int
    scan_interval: int = 10  # seconds
    state_file: str = "parser_state.json"


class ApacheLogParser:
    LOG_PATTERN = re.compile(
        r'(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'
        r'(?P<remote_user>[-\w]+|\-)\s+'
        r'(?P<auth_user>[-\w]+|\-)\s+'
        r'\[(?P<timestamp>[\w:/]+\s[+\-]\d{4})\]\s+'
        r'"(?P<request_method>\w+)\s+'
        r'(?P<request_url>[^\s"]*)\s+'
        r'HTTP/[\d.]+"\s+'
        r'(?P<status_code>\d+)\s+'
        r'(?P<response_size>\d+|-)\s+'
        r'"(?P<referrer>[^"]*?)"\s+'
        r'"(?P<user_agent>[^"]*?)"'
    )

    def __init__(self, config: ParserConfig):
        self.config = config
        self.aggregator_url = f"http://{config.aggregator_host}:{config.aggregator_port}/logs"

    def parse_log_line(self, line: str) -> Optional[Dict]:
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        data = match.groupdict()

        try:
            timestamp = datetime.strptime(
                data['timestamp'],
                '%d/%b/%Y:%H:%M:%S %z'
            ).isoformat()
        except ValueError:
            print(f"Invalid timestamp format in line: {line}")
            return None

        response_size = data['response_size']
        response_size = int(response_size) if response_size != '-' else 0

        return {
            'ip_address': data['ip_address'],
            'timestamp': timestamp,
            'request_method': data['request_method'],
            'request_url': data['request_url'],
            'status_code': int(data['status_code']),
            'response_size': response_size,
            'user_agent': data['user_agent']
        }

    def send_to_server(self, log_data: Dict):
        try:
            response = requests.post(
                self.aggregator_url,
                json=log_data,
                timeout=5
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to send log to aggregator: {e}")

    def process_file(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    log_data = self.parse_log_line(line.strip())
                    if log_data:
                        self.send_to_server(log_data)
        except Exception as e:
            raise RuntimeError(f"Error processing file {filepath}: {e}")


def load_config(config_path: str) -> ParserConfig:
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            return ParserConfig(
                log_dir=config_data['log_dir'],
                file_pattern=config_data['file_pattern'],
                aggregator_host=config_data['aggregator_host'],
                aggregator_port=config_data['aggregator_port'],
                scan_interval=config_data.get('scan_interval', 10),
                state_file=config_data.get('state_file', 'parser_state.json')
            )
    except Exception as e:
        raise RuntimeError(f"Error loading config file: {e}")


def main():
    config = load_config('parser_config.yaml')
    parser = ApacheLogParser(config)

    log_files = glob.glob(os.path.join(config.log_dir, config.file_pattern))
    for filepath in log_files:
        parser.process_file(filepath)


if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from config import Config

app = Flask(__name__)
config = Config()


def get_db_connection():
    return psycopg2.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD
    )


@app.route('/logs', methods=['POST'])
def save_log():
    log_data = request.get_json()

    if not log_data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO access_logs 
                    (ip_address, timestamp, request_method, request_url, 
                     status_code, response_size, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                            (
                                log_data.get('ip_address'),
                                datetime.fromisoformat(log_data.get('timestamp')),
                                log_data.get('request_method'),
                                log_data.get('request_url'),
                                log_data.get('status_code'),
                                log_data.get('response_size'),
                                log_data.get('user_agent')
                            )
                            )
                conn.commit()

        return jsonify({'message': 'Log saved successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    ip = request.args.get('ip')
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if date and start_time:
        return jsonify({
            'error': 'Cannot specify both date and start_time parameters simultaneously'
        }), 400

    if end_time and not start_time:
        return jsonify({
            'error': 'end_time cannot be specified without start_time'
        }), 400

    query = "SELECT * FROM access_logs WHERE 1=1"
    params = []

    if ip:
        query += " AND ip_address = %s"
        params.append(ip)

    if date:
        query += " AND DATE(timestamp) = %s"
        params.append(date)

    if start_time:
        query += " AND timestamp >= %s"
        params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                logs = [dict(row) for row in cur.fetchall()]

                for log in logs:
                    log['timestamp'] = log['timestamp'].isoformat()
                    log['created_at'] = log['created_at'].isoformat()

                return jsonify(logs)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

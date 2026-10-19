import argparse
import json
import csv
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

# Налаштування формату логування
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Регулярний вираз для розбору рядків access.log (IP, час, метод, URI, статус, розмір)
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<uri>\S+)\s+[^"]+"\s+(?P<status>\d{3})\s+(?P<size>\d+)$'
)

# Регулярні вирази для пошуку сигнатур базових атак
ATTACK_SIGNATURES = {
    "SQLi": re.compile(r"(?i)('|%27)(?:\s+|%20)*(OR|UNION)"),
    "Directory Traversal": re.compile(r"(?i)(\.\./|\.\.\\|%2E%2E%2F)"),
    "XSS": re.compile(r"(?i)(<script>|%3Cscript%3E)"),
}


def parse_time(time_str: str) -> datetime:
    """Конвертує рядок часу з логу в об'єкт datetime з урахуванням часового поясу."""
    # Формат: 27/Sep/2026:08:00:00 +0300
    return datetime.strptime(time_str, "%d/%b/%Y:%H:%M:%S %z")


def parse_arguments():
    """Налаштування аргументів командного рядка (CLI)."""
    parser = argparse.ArgumentParser(description="Аналізатор журналів веб-сервера (Nginx/Apache Access Log)")
    parser.add_argument("--log-file", type=Path, required=True, help="Шлях до файлу access.log")
    parser.add_argument("--output", type=Path, required=True, help="Шлях до файлу звіту")
    parser.add_argument("--min-status", type=int, default=400, help="Мінімальний HTTP-статус для помилок (дефолт: 400)")
    parser.add_argument("--top", type=int, default=5, help="Кількість топових IP (дефолт: 5)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Формат звіту (json/csv)")
    
    # Додаткові аргументи для фільтрації за часовим інтервалом
    parser.add_argument("--start-time", type=str, help="Початковий час (формат: DD/MMM/YYYY:HH:MM:SS)")
    parser.add_argument("--end-time", type=str, help="Кінцевий час (формат: DD/MMM/YYYY:HH:MM:SS)")
    
    return parser.parse_args()


def main():
    args = parse_arguments()

    logging.info(f"Loading access log from {args.log_file}...")

    ip_error_counter = Counter()
    detected_attacks = []
    processed_count = 0

    # Підготовка об'єктів datetime для фільтрації, якщо вказані аргументи
    start_filter = (
        datetime.strptime(args.start_time, "%d/%b/%Y:%H:%M:%S").astimezone()
        if args.start_time
        else None
    )
    end_filter = (
        datetime.strptime(args.end_time, "%d/%b/%Y:%H:%M:%S").astimezone()
        if args.end_time
        else None
    )

    min_time = None
    max_time = None

    # Читання файлу та обробка кожного рядка
    with open(args.log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()
            log_time = parse_time(data["time"])
            status = int(data["status"])
            ip = data["ip"]
            uri = data["uri"]
            method = data["method"]

            # Фільтрація за часовим інтервалом
            if start_filter and log_time < start_filter:
                continue
            if end_filter and log_time > end_filter:
                continue

            processed_count += 1

            # Збереження меж часу для статистики
            if min_time is None or log_time < min_time:
                min_time = log_time
            if max_time is None or log_time > max_time:
                max_time = log_time

            # 1. Підрахунок IP із помилками
            if status >= args.min_status:
                ip_error_counter[ip] += 1

            # 2. Пошук сигнатур атак
            for attack_name, pattern in ATTACK_SIGNATURES.items():
                if pattern.search(uri):
                    detected_attacks.append(
                        {
                            "ip": ip,
                            "attack_type": attack_name,
                            "method": method,
                            "uri": uri,
                            "time": log_time.isoformat(),
                        }
                    )
                    # Сповіщення (ALERT) про потенційну атаку
                    logging.warning(
                        f'[ALERT] Potential {attack_name} attack from {ip}: "{method} {uri}"'
                    )

    # Друк базової статистики
    t_start_str = min_time.strftime("%Y-%m-%d %H:%M:%S") if min_time else "N/A"
    t_end_str = max_time.strftime("%Y-%m-%d %H:%M:%S") if max_time else "N/A"
    logging.info(
        f"Processed {processed_count} log entries from {t_start_str} to {t_end_str}."
    )

    # Виведення топу IP-адрес у консоль
    print(
        f"\n=== Top-{args.top} IP Addresses with Error Statuses (>={args.min_status}) ==="
    )
    top_ips = ip_error_counter.most_common(args.top)
    for ip, count in top_ips:
        print(f"{ip:15} | {count} errors")

    # Формування словника для експорту
    report_data = {
        "top_error_ips": [{"ip": ip, "errors": count} for ip, count in top_ips],
        "detected_attacks": detected_attacks,
    }

# Вивантаження звіту в JSON або CSV
    if args.format == "json":
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4)
        logging.info(f"Analysis report saved to {args.output}")
    elif args.format == "csv":
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Entity", "IP", "Count/Attack Type", "Details/URI", "Time"])
            for ip, count in top_ips:
                writer.writerow(["Top IP Error", ip, count, "N/A", "N/A"])
            for attack in detected_attacks:
                writer.writerow(["Attack Alert", attack["ip"], attack["attack_type"], attack["uri"], attack["time"]])
        logging.info(f"Analysis report saved to {args.output}")


if __name__ == "__main__":
    main()
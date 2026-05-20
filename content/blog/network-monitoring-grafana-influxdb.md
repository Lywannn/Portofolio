---
title: "Building a Real-Time Network Monitoring Dashboard with Grafana & InfluxDB"
date: 2025-05-10
tags: ["Networking", "Grafana", "Python", "Monitoring", "InfluxDB"]
excerpt: "How I built a real-time dashboard to monitor 50+ network devices — tracking bandwidth, latency, and uptime — using Python, InfluxDB, and Grafana."
cover_image: ""
---

## The Problem

Managing a growing network infrastructure without proper visibility is like driving blind. We had over 50 network devices — routers, switches, access points — and no centralized way to see what was happening in real time.

Alerts came in via phone calls. "The internet is slow." "I can't connect." By the time you diagnose, the issue might have already resolved — or gotten worse.

I decided to build a proper monitoring stack.

## The Stack

| Component | Role |
|---|---|
| **Python** | Data collector — polls devices via SNMP and MikroTik API |
| **InfluxDB** | Time-series database — stores metrics with timestamps |
| **Grafana** | Visualization — dashboards, alerts, and graphs |
| **Zabbix** | Supplementary alerting and host discovery |

## Collecting Metrics with Python

The collector runs every 30 seconds and pushes data to InfluxDB:

```python
from influxdb_client import InfluxDBClient, Point
from routeros_api import RouterOsApiPool
import time

def collect_mikrotik_metrics(host, username, password):
    pool = RouterOsApiPool(host, username=username, password=password, plaintext_login=True)
    api = pool.get_api()

    interfaces = api.get_resource('/interface')
    stats = interfaces.get()

    metrics = []
    for iface in stats:
        metrics.append({
            "name": iface.get("name"),
            "rx_bytes": int(iface.get("rx-byte", 0)),
            "tx_bytes": int(iface.get("tx-byte", 0)),
            "running": iface.get("running") == "true",
        })

    pool.disconnect()
    return metrics

def write_to_influxdb(client, metrics, host):
    write_api = client.write_api()
    for m in metrics:
        point = (
            Point("interface_traffic")
            .tag("host", host)
            .tag("interface", m["name"])
            .field("rx_bytes", m["rx_bytes"])
            .field("tx_bytes", m["tx_bytes"])
            .field("running", int(m["running"]))
        )
        write_api.write(bucket="network", record=point)
```

## Grafana Dashboard

In Grafana, I created panels for:

- **Bandwidth usage** — per interface, real-time line graph
- **Device availability** — stat panel showing up/down status
- **Latency heatmap** — response times across all devices
- **Alert history** — timeline of past incidents

The most useful panel: a "Top Talkers" table sorted by bandwidth consumption. Instantly shows which device or user is hammering the link.

## Alert Configuration

Grafana alerts are configured to notify via:

1. **Email** for non-critical thresholds (>80% bandwidth)
2. **Telegram bot** for critical alerts (device down, >95% bandwidth)

```python
# Simple Telegram alert sender
import requests

def send_telegram_alert(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
```

## Results

After deploying the monitoring stack:

- **MTTR reduced by 60%** — issues detected automatically before users report them
- **Root cause analysis** becomes faster — historical data shows exactly when the problem started
- **Capacity planning** improved — clear bandwidth trends for planning upgrades
- **Zero surprise outages** — proactive alerts handle everything

## Lessons Learned

1. **SNMP is reliable but slow** — MikroTik's own API is much faster for RouterOS devices
2. **Start with fewer metrics, add gradually** — too many panels become noise
3. **Retention policy matters** — high-frequency data gets expensive; aggregate older data

## What's Next

Adding ML-based anomaly detection using Python's `scikit-learn` to automatically flag unusual traffic patterns before they become incidents.

The whole monitoring stack turned reactive firefighting into proactive network management. Highly worth the investment.

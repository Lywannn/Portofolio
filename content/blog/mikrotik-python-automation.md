---
title: "Automating MikroTik Network Configuration with Python"
date: 2025-04-20
tags: ["Networking", "Python", "MikroTik", "Automation", "DevNet"]
excerpt: "Manual network configuration is error-prone and slow. Here's how I automated VLAN provisioning, bulk config deployment, and inventory management using Python and the MikroTik RouterOS API."
cover_image: ""
---

## Why Automate?

Every time a new VLAN needed to be provisioned across multiple switches, it meant:

1. SSH into each device manually
2. Enter the same commands with slight variations
3. Verify the config
4. Document what was done

Multiply that by 10 switches and you have 45+ minutes of repetitive work — with real risk of typos causing outages.

Python automation reduced this to under 2 minutes.

## The MikroTik RouterOS API

MikroTik devices expose a native API that's much faster and more reliable than parsing SSH output. The `routeros-api` Python library makes it easy to use:

```bash
pip install routeros-api
```

## VLAN Provisioning Automation

This script creates a new VLAN on multiple switches simultaneously:

```python
import routeros_api

DEVICES = [
    {"host": "192.168.1.1", "user": "admin", "password": "secret"},
    {"host": "192.168.1.2", "user": "admin", "password": "secret"},
    {"host": "192.168.1.3", "user": "admin", "password": "secret"},
]

def create_vlan(api, vlan_id, vlan_name, interface="bridge"):
    """Create a VLAN bridge on a MikroTik device."""
    vlans = api.get_resource('/interface/vlan')
    
    # Check if VLAN already exists
    existing = vlans.get(vlan_id=str(vlan_id))
    if existing:
        print(f"  VLAN {vlan_id} already exists, skipping.")
        return

    vlans.add(
        name=vlan_name,
        vlan_id=str(vlan_id),
        interface=interface,
        comment=f"Auto-provisioned: {vlan_name}"
    )
    print(f"  Created VLAN {vlan_id} ({vlan_name})")

def provision_vlan_all_devices(vlan_id, vlan_name):
    for device in DEVICES:
        print(f"Connecting to {device['host']}...")
        try:
            connection = routeros_api.RouterOsApiPool(
                device["host"],
                username=device["user"],
                password=device["password"],
                plaintext_login=True
            )
            api = connection.get_api()
            create_vlan(api, vlan_id, vlan_name)
            connection.disconnect()
        except Exception as e:
            print(f"  ERROR on {device['host']}: {e}")

# Provision VLAN 100 for "Guest WiFi" across all switches
provision_vlan_all_devices(100, "Guest-WiFi")
```

Output:
```
Connecting to 192.168.1.1...
  Created VLAN 100 (Guest-WiFi)
Connecting to 192.168.1.2...
  Created VLAN 100 (Guest-WiFi)
Connecting to 192.168.1.3...
  Created VLAN 100 (Guest-WiFi)
```

What used to take 45 minutes: **done in 4 seconds**.

## Automated Network Inventory

This script generates a complete inventory of all devices and their interfaces:

```python
import csv
from datetime import datetime

def get_device_inventory(host, user, password):
    connection = routeros_api.RouterOsApiPool(
        host, username=user, password=password, plaintext_login=True
    )
    api = connection.get_api()

    # Get system identity
    identity = api.get_resource('/system/identity').get()[0]
    
    # Get all interfaces
    interfaces = api.get_resource('/interface').get()
    
    # Get IP addresses
    ip_addresses = api.get_resource('/ip/address').get()

    connection.disconnect()
    
    return {
        "host": host,
        "name": identity.get("name"),
        "interfaces": interfaces,
        "ip_addresses": ip_addresses,
    }

def export_inventory_csv(devices_data, filename=None):
    if not filename:
        filename = f"network_inventory_{datetime.now().strftime('%Y%m%d')}.csv"
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Device", "Interface", "Type", "MAC", "IP", "Status"])
        
        for device in devices_data:
            ip_map = {
                ip["interface"]: ip["address"]
                for ip in device["ip_addresses"]
            }
            for iface in device["interfaces"]:
                writer.writerow([
                    device["name"],
                    iface.get("name"),
                    iface.get("type"),
                    iface.get("mac-address", ""),
                    ip_map.get(iface.get("name"), ""),
                    "Up" if iface.get("running") == "true" else "Down",
                ])
    
    print(f"Inventory exported: {filename}")
```

## Configuration Backup System

Automated daily backups with Git versioning:

```python
import subprocess
from pathlib import Path

BACKUP_DIR = Path("/backups/network-configs")
BACKUP_DIR.mkdir(exist_ok=True)

def backup_device_config(host, user, password, device_name):
    connection = routeros_api.RouterOsApiPool(
        host, username=user, password=password, plaintext_login=True
    )
    api = connection.get_api()
    
    # Export full config
    export = api.get_binary_resource('/').call('export', {'verbose': ''})
    config_text = export[b'ret'].decode('utf-8')
    
    connection.disconnect()
    
    config_file = BACKUP_DIR / f"{device_name}.rsc"
    config_file.write_text(config_text)
    return config_file

def git_commit_backups():
    subprocess.run(["git", "-C", str(BACKUP_DIR), "add", "."], check=True)
    subprocess.run([
        "git", "-C", str(BACKUP_DIR), "commit",
        "-m", f"backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ], check=True)
```

This runs via cron daily. Every config change is tracked in Git — if something breaks, you can instantly diff against yesterday's config to find what changed.

## Key Takeaways

1. **MikroTik's native API** is faster and safer than screen-scraping SSH output
2. **Idempotency matters** — always check before creating (handle "already exists" gracefully)
3. **Backup before any bulk change** — automate this as the first step
4. **Logging everything** — you'll need the audit trail when something goes wrong

Network automation isn't just for Cisco/big enterprise. Even a 10-device MikroTik network benefits enormously from Python scripting.

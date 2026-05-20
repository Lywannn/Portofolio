---
title: "Designing an Enterprise Network with OSPF: Lessons from the Field"
date: 2025-03-05
tags: ["Networking", "OSPF", "Infrastructure", "Cisco", "MikroTik"]
excerpt: "A practical guide to designing a multi-layer enterprise network using OSPF dynamic routing — based on real implementation experience, including the mistakes and how we fixed them."
cover_image: ""
---

## Context

When the company's network needed to support multiple office floors, a data center room, and eventual remote branches — the flat single-VLAN network we had wasn't going to cut it.

I was tasked with designing and implementing a proper enterprise network architecture from scratch.

## The Design: Three-Layer Hierarchy

The classic Cisco three-layer model made sense for our scale:

```
┌─────────────────────────────────────────────┐
│              CORE LAYER                      │
│    (High-speed backbone, no endpoints)       │
│         Core Switch 1 ←→ Core Switch 2       │
└──────────────┬──────────────────┬────────────┘
               │                  │
    ┌──────────▼──────┐  ┌────────▼──────────┐
    │ DISTRIBUTION    │  │  DISTRIBUTION     │
    │ (Routing, ACL)  │  │  (Routing, ACL)   │
    │  Dist Switch A  │  │   Dist Switch B   │
    └──────┬──────────┘  └──────────┬────────┘
           │                        │
   ┌───────▼───────┐        ┌───────▼──────┐
   │ ACCESS LAYER  │        │ ACCESS LAYER │
   │ (End devices) │  ...   │ (End devices)│
   │  Floor 1-3    │        │  Floor 4-6   │
   └───────────────┘        └──────────────┘
```

**Why three layers?**
- **Scalability** — add new access switches without touching the core
- **Fault isolation** — a failed access switch only affects that floor
- **Security** — enforce policies at distribution, not everywhere

## VLAN Segmentation

Each department got its own VLAN:

| VLAN ID | Name | Subnet |
|---|---|---|
| 10 | Management | 10.0.10.0/24 |
| 20 | Engineering | 10.0.20.0/24 |
| 30 | Finance | 10.0.30.0/24 |
| 40 | Operations | 10.0.40.0/24 |
| 50 | WiFi-Corporate | 10.0.50.0/24 |
| 99 | Guest-WiFi | 10.0.99.0/24 |
| 100 | Servers | 10.0.100.0/24 |

Critical isolation: Finance (VLAN 30) can't directly reach any other VLAN — all traffic goes through the firewall first.

## OSPF Configuration

Static routes don't scale. OSPF lets routers discover each other dynamically and adapt to failures automatically.

### Core Router (MikroTik) OSPF Setup

```routeros
# Enable OSPF instance
/routing ospf instance
add name=main router-id=10.0.0.1

# Define OSPF area
/routing ospf area
add instance=main name=backbone area-id=0.0.0.0

# Advertise directly connected networks
/routing ospf interface-template
add area=backbone interfaces=ether1 type=ptp
add area=backbone interfaces=ether2 type=ptp
add area=backbone interfaces=loopback0 passive
```

### Verification

```bash
# Check OSPF neighbors
/routing ospf neighbor print

# Expected output:
# router-id=10.0.0.2  state=Full  ...
# router-id=10.0.0.3  state=Full  ...

# Check learned routes
/ip route print where dynamic
```

## The Mistake That Taught Me The Most

During initial deployment, OSPF neighbors formed but routes weren't propagating correctly between distribution switches.

**Root cause:** OSPF hello/dead timer mismatch.

One device was running with hello=10s/dead=40s (default), another had been manually set to hello=30s/dead=120s from a previous config. OSPF neighbors won't form if timers don't match.

**Fix:**
```routeros
/routing ospf interface-template
set [find] hello-interval=10 dead-interval=40
```

**Lesson:** Always verify timers explicitly. Don't assume defaults.

## Redundancy

The core layer runs in an active-active setup with ECMP (Equal-Cost Multi-Path):

- Traffic load-balances across both core switches
- If one fails, all traffic moves to the other within OSPF dead interval (~40 seconds)
- Distribution switches have uplinks to BOTH core switches

OSPF handles failover automatically — no manual intervention needed.

## Results After 6 Months

- **Zero unplanned outages** caused by routing failures
- **Sub-60 second failover** when testing core switch failure
- **Network team productivity up** — automated monitoring catches issues before users notice
- **Security posture improved** — VLAN isolation prevents lateral movement

## Key Decisions I'd Repeat

1. **Loopback interfaces for router IDs** — stable, never goes down
2. **Document everything in GNS3 first** — test the design virtually before touching production
3. **Passive interfaces on access ports** — prevent rogue OSPF neighbors
4. **Gradual rollout by floor** — detect issues early before full deployment

Network design is 30% technical knowledge and 70% patience and documentation. The network that's easiest to troubleshoot is the one that's most consistently documented.

# Phase 2 – Predictive Maintenance

## Overview
This phase focuses on detecting abnormal operating behavior in a solar power plant to support predictive maintenance and early fault detection.

Instead of waiting for equipment failures, the system identifies unusual patterns in power generation that may indicate inverter or system issues.

---

## Problem Addressed
- Unexpected inverter or system issues
- Manual monitoring is slow and reactive
- No labeled failure data available in real operations

---

## Solution Approach
We implemented an anomaly-based predictive maintenance system using historical power data.

The approach combines:
- Rule-based safety checks for critical conditions
- Machine learning (Isolation Forest) to detect rare and abnormal behavior

This hybrid approach improves reliability and reduces false negatives.

---

## Key Features
- Detects abnormal power behavior automatically
- Works without labeled failure data
- Provides early warning signals for maintenance teams
- Exposed via a FastAPI endpoint for real-time usage

---

## API Endpoint
POST `/detect-anomaly`

### Output
- Normal operation → No action required
- Abnormal behavior → Maintenance check recommended

---

## Business Impact
- Reduced unexpected downtime
- Faster response to potential equipment issues
- Improved operational reliability
- Foundation for advanced asset optimization

---

## Status
Predictive Maintenance module completed and production-ready.

# Overprovisioned EC2 Instances

## Summary
EC2 instances are larger than required for their workload, resulting in unnecessary compute spend.

## Why this matters
Overprovisioning directly inflates hourly compute costs without improving performance.

## Common signals
- CPU utilization consistently below 20%
- Memory usage well below capacity
- Instance type unchanged over long periods

## Recommended action
Right-size instances based on observed utilization and workload needs.

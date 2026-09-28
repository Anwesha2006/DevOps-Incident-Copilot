# Incident 001: Checkout API Latency

## Summary

The checkout API experienced a significant increase in response latency.

## Impact

Users experienced slow checkout requests.
The checkout API p95 latency increased from approximately 400ms to 2.3 seconds.

## Timeline

14:00 - Deployment version 2.4.1 started.

14:07 - Checkout API latency began increasing.

14:10 - Error rate increased significantly.

14:15 - Engineers began investigating the incident.

14:25 - Database connection timeout errors were identified.

14:40 - Deployment 2.4.1 was rolled back.

14:45 - Latency returned to normal levels.

## Root Cause

Deployment version 2.4.1 introduced a database connection configuration that caused the checkout service to exhaust available database connections.

## Resolution

The engineering team rolled back deployment 2.4.1.

## Prevention

Future deployments should validate database connection pool configuration before production rollout.
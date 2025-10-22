# API Rate Limiting Implementation Guide

## Overview

This document describes the implementation of rate limiting middleware for the REST API using a token bucket algorithm with Redis as the backing store.

## Technical Architecture

### Token Bucket Algorithm

The rate limiter implements a token bucket algorithm where:
- Each API key has an associated bucket with a maximum capacity (burst size)
- Tokens are added to the bucket at a fixed rate (refill rate)
- Each request consumes one token
- Requests are rejected when the bucket is empty

### Redis Data Structure

```
Key: rate_limit:{api_key}
Value: {
  "tokens": float,
  "last_refill": timestamp,
  "created_at": timestamp
}
TTL: 3600 seconds
```

### Configuration Parameters

- `max_tokens`: Maximum bucket capacity (default: 100)
- `refill_rate`: Tokens added per second (default: 10)
- `window_size`: Time window in seconds (default: 60)

## Implementation Details

### Request Processing Flow

1. Extract API key from Authorization header
2. Retrieve bucket state from Redis using HGETALL
3. Calculate tokens to add based on elapsed time
4. Check if sufficient tokens available
5. If yes: decrement token count, update Redis, allow request
6. If no: return 429 Too Many Requests with Retry-After header

### Atomic Operations

To prevent race conditions in distributed environments, we use Redis Lua scripts for atomic read-modify-write operations:

```lua
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

-- Implementation details...
```

## Error Handling

- Missing API key: 401 Unauthorized
- Invalid API key format: 400 Bad Request
- Rate limit exceeded: 429 Too Many Requests
- Redis connection failure: Fail open (allow request) with logging

## Monitoring and Metrics

Key metrics to track:
- Rate limit hit rate per endpoint
- Average tokens consumed per user
- Redis operation latency
- Cache hit/miss ratio for API key validation

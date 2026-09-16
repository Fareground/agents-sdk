# Production integration

The SDK supplies execution components. Your application supplies the trust boundary and operational policy.

## Before exposing an agent

- Authenticate users and derive tenant identity from verified credentials.
- Register only the tools each role needs; authorize sensitive actions inside handlers.
- Set model, turn, timeout and concurrency limits explicitly.
- Choose durable persistence and test restart behavior.
- Record failures and usage without retaining secrets in logs.
- Test your actual providers, including malformed arguments, truncation and interruption.

## External side effects

A tool that sends an order, changes a record or makes a payment needs application-level idempotency. A timeout may leave an external request in progress. Store an operation ID and reconcile its outcome before retrying. Do not treat generic model retries as an exactly-once guarantee.

## Multiple workers

Per-session engine locks apply within one engine instance. If several workers can run the same session, route ownership or coordinate explicitly. Database persistence alone does not provide distributed execution serialization.

## Limits and observability

Track model calls, tokens, errors, tool outcomes, latency and abandoned streams. Per-turn output limits do not cap total spend. Application budgets should account for retries and delegated agents.

Use deterministic test clients for execution contracts and real-provider tests for transport compatibility. Keep live-provider tests opt-in and avoid putting credentials in recorded fixtures.

## Deployment readiness

Pin a release, validate your critical workflows on the built package, rehearse restart and recovery, and retain a rollback version. The documentation describes available interfaces; it does not certify every deployment configuration.

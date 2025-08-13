# My First Bank App — INSTRUCTION_DOC.md

## Project Title

My First Bank App — Parent‑managed virtual bank accounts for children

## Overview

**Goal:** Build a cross‑platform mobile app (React Native + TypeScript) with a FastAPI + PostgreSQL backend so parents can create child profiles and manage virtual checking and savings accounts for them (virtual money only — no real payments).

**Primary users:** Parents who want to allocate and track pocket money for children.

---

## MVP (v0.1) — scope

**Core features (must be implemented for MVP):**

* Parent authentication (email + password, JWT).
* Parent can create and list child profiles (name, birthdate).
* Each child has two virtual accounts automatically created: `checking` and `savings` (starting balance = 0).
* Parent can deposit virtual money into an account with idempotency support.
* Parent can view account balances and transaction history.
* Transaction history is cursor (keyset) paginated; mobile client implements infinite scroll.

**Non‑functional essentials (MVP must include):**

* Transaction ledger + ACID correctness (no balance races).
* Idempotency for deposits (client provides `idempotency_key`).
* Currency correctness: store amounts in integer cents (`BIGINT`) or Decimal with explicit scale — no floats.
* Authentication & access control: parents can only operate on their children/accounts.
* Input validation & reasonable limits (min > 0, max per deposit).
* Tests: unit tests for deposit logic and concurrency; API tests for auth and pagination.
* Basic logging, error handling, and meaningful error responses.

---

## Success criteria / Acceptance tests

Automate where possible; otherwise provide manual verification steps.

### Auth

* Parent can register and receive a JWT.
* Protected endpoints return `401` without a valid JWT.

### Child & accounts

* Creating a child returns the child record and two accounts: `checking` and `savings`, both with balance `0`.
* Parent can list their children.

### Deposit & ledger

* `POST /accounts/{id}/deposit` with `amount_cents` and `idempotency_key`:
  * Creates a transaction record.
  * Updates account balance atomically.
  * Returns the transaction and new balance.
* Replaying the same `idempotency_key` does NOT create a duplicate transaction.
* Concurrent deposits produce consistent final balance (test by running N concurrent deposits and assert sum equals final balance).

### Transactions & pagination

* `GET /accounts/{id}/transactions?limit=20` returns up to `limit` items + `next_cursor` when more pages exist.
* Cursor navigation is deterministic and stable across inserts.

---

## Tech stack & infra

* Backend: Python 3.11+, FastAPI, async SQLAlchemy / SQLAlchemy core (or Databases), Alembic for migrations.
* DB: PostgreSQL 13+.
* Mobile: React Native + TypeScript (Expo managed recommended for v0.1).
* Auth: JWT (short-lived access token; refresh tokens optional).
* Testing: pytest, httpx for API tests.
* CI/CD: GitHub Actions (run tests, lint).
* Local dev: Docker + docker-compose (postgres + backend).
* Lint/format: black / r

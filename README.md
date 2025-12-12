# Serverless TODO API – Python Ops Toolkit

## Overview

This project is a small **production-style cloud service** plus a **Python operations toolkit**.

- **Backend:** AWS API Gateway + Lambda (serverless)
- **Service:** Simple TODO API with health and version endpoints
- **Client:** Python CLI (`ops.py`) used to run health checks and smoke tests against the API

The goal is to simulate how a cloud / SRE / support engineer would quickly verify that a service is healthy after a deployment.

---

## Architecture

- **AWS API Gateway**
  - Public endpoint: `https://h2iz7egg4l.execute-api.us-east-1.amazonaws.com/dev`
  - Routes:
    - `GET /Health` – service health
    - `GET /Verison` – deployed version info
    - `POST /todos` – create a todo item
    - `GET /todos` – list todo items
    - (DELETE route available in the API, best-effort cleanup in the script)

- **AWS Lambda**
  - One function backing each route (Health, Verison, Todos, etc.)
  - Responds with JSON payloads that the Python client consumes

- **Client (this repo)**
  - `ops.py` – Python 3 CLI that calls the API and prints results

---

## Python Ops Toolkit (`ops.py`)

### Commands

From the project directory:

```bash
python ops.py health
python ops.py version
python ops.py smoke-test


# Weather Data CLI

A clean, beginner-friendly Python command-line interface (CLI) application that fetches, parses, and displays real-time weather information for any city worldwide using the [OpenWeatherMap API](https://openweathermap.org/api).

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites & Setup](#prerequisites--setup)
  - [1. Clone or Navigate to the Repository](#1-clone-or-navigate-to-the-repository)
  - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Obtain an OpenWeatherMap API Key](#4-obtain-an-openweathermap-api-key)
  - [5. Configure the Environment File (`.env`)](#5-configure-the-environment-file-env)
- [Usage Examples](#usage-examples)
  - [Positional Argument](#positional-argument)
  - [Named Flag (`--city`)](#named-flag---city)
  - [Multi-word City Names](#multi-word-city-names)
  - [Interactive Mode (Lookup Loop)](#interactive-mode-lookup-loop)
- [Output Format](#output-format)
- [Error Handling Guide](#error-handling-guide)
- [API Concepts & Interview Questions](#api-concepts--interview-questions)
  - [How APIs Authenticate Requests](#how-apis-authenticate-requests)
  - [What Happens When an API Returns a 404](#what-happens-when-an-api-returns-a-404)
- [License](#license)

---

## Overview

Weather Data CLI demonstrates core Python software engineering patterns:
- Interacting with RESTful Web APIs using `requests` with query parameters and timeouts.
- Safe secrets management through environment variables and `.env` files using `python-dotenv`.
- Robust JSON payload inspection, field extraction, and timezone-aware datetime calculations.
- Comprehensive defensive programming with clear, user-friendly error messages (no raw tracebacks).
- Flexible CLI interactions using Python's standard library `argparse` module, supporting both one-shot commands and an interactive lookup loop.

---

## Key Features

- **Accurate Metric Weather Metrics**: Reports temperature, feels-like temperature, daily minimum/maximum temperatures, humidity, atmospheric pressure, and wind speed.
- **Local Sunrise & Sunset Times**: Converts UTC epoch timestamps into the target city's actual local clock time using OpenWeatherMap's `timezone` offset.
- **Flexible Invocation**: Run with a positional argument, a `-c`/`--city` flag, or start in interactive prompt mode.
- **Strict Error Handling**: Gracefully handles network failures, timeouts, invalid cities, missing or unauthorized API keys, rate limits, and corrupted payloads.
- **Clean Architecture**: Follows PEP 8 styling, complete with comprehensive docstrings, explicit type hints, and modular functions.

---

## Project Structure

```text
weather-data-cli/
├── .env.example       # Template for required environment variables
├── .gitignore          # Ignores .env, virtual environments, caches, and system files
├── requirements.txt    # Project dependencies (requests, python-dotenv)
├── weather.py          # Main application script
├── sample_output.txt   # Captured output runs (valid, invalid city, wrong API key)
└── README.md           # Documentation, setup guide, and technical explanations
```

---

## Prerequisites & Setup

### 1. Clone or Navigate to the Repository

```bash
cd weather-data-cli
```

### 2. Create and Activate a Virtual Environment

It is recommended to run the project inside an isolated Python virtual environment:

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

The application relies on:
- **`requests`**: For sending HTTP GET requests to the OpenWeatherMap REST API.
- **`python-dotenv`**: For loading environment variables securely from a local `.env` file.

### 4. Obtain an OpenWeatherMap API Key

1. Sign up for a free account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Once verified, visit the **API Keys** section in your profile dashboard.
3. Copy your 32-character API key. *(Note: New keys can take 10 to 30 minutes to activate globally across OpenWeatherMap servers.)*

### 5. Configure the Environment File (`.env`)

Copy the provided `.env.example` file to create your own `.env` file:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows:**
```powershell
copy .env.example .env
```

Open `.env` in any text editor and replace the placeholder with your actual key:

```ini
OPENWEATHER_API_KEY=your_actual_api_key_here
```

> **Security Note:** The `.env` file is listed in `.gitignore` and must **never** be committed to version control.

---

## Usage Examples

### Positional Argument
Pass the city name directly as a command-line argument:

```bash
python weather.py London
```

### Named Flag (`--city`)
Specify the city using the `--city` (or `-c`) flag:

```bash
python weather.py --city Tokyo
```

### Multi-word City Names
Wrap city names that contain spaces in quotes:

```bash
python weather.py "New Delhi"
python weather.py --city "San Francisco"
```

### Interactive Mode (Lookup Loop)
If you run `weather.py` without arguments, it opens an interactive loop allowing repeated city queries:

```bash
python weather.py
```

Example session:
```text
========================================
      Welcome to Weather Data CLI      
========================================
Type a city name to view its weather.
Type 'quit' or 'exit' (or press Ctrl+C) to exit.

Enter city name: Paris
========================================
Weather in Paris, FR
========================================
Condition   : Clear sky
Temperature : 18.2 °C (feels like 17.8 °C)
Min / Max   : 16.5 °C / 19.4 °C
Humidity    : 62%
Wind Speed  : 3.1 m/s
Pressure    : 1016 hPa
Sunrise     : 07:15 AM
Sunset      : 06:40 PM
========================================

Enter city name: quit
Exiting Weather Data CLI. Goodbye!
```

---

## Output Format

The CLI displays clean, aligned output blocks:

```text
========================================
Weather in New Delhi, IN
========================================
Condition   : Light rain
Temperature : 24.0 °C (feels like 25.1 °C)
Min / Max   : 22.0 °C / 26.0 °C
Humidity    : 78%
Wind Speed  : 3.5 m/s
Pressure    : 1008 hPa
Sunrise     : 06:28 AM
Sunset      : 05:37 PM
========================================
```

---

## Error Handling Guide

All potential errors are caught gracefully and communicated with actionable messages instead of Python crash traces:

| Scenario | HTTP / Exception Code | Cause | User Feedback |
| :--- | :--- | :--- | :--- |
| **Missing API Key** | Pre-request check | `.env` missing or placeholder key | Explains step-by-step how to create `.env` and set `OPENWEATHER_API_KEY`. |
| **Empty City Input** | Pre-request validation | Empty string or whitespace supplied | `Error: City name cannot be empty. Please enter a valid city name.` |
| **Invalid City Name** | HTTP 404 Not Found | City does not exist or typo | `Error (HTTP 404 Not Found): City '<city>' was not found. Please check spelling.` |
| **Invalid API Key** | HTTP 401 Unauthorized | Key is incorrect or not activated | `Error (HTTP 401 Unauthorized): Invalid API key. Please verify your OPENWEATHER_API_KEY.` |
| **Rate Limiting** | HTTP 429 Too Many Requests | Exceeded free tier limit (60 calls/min) | `Error (HTTP 429 Too Many Requests): API rate limit exceeded. Please wait and try again.` |
| **Network Loss** | `requests.exceptions.ConnectionError` | DNS resolution failure or no internet | `Error: Network connection error. Unable to reach OpenWeatherMap servers.` |
| **Server Timeout** | `requests.exceptions.Timeout` | API server took > 10s to respond | `Error: Connection timed out after 10 seconds while contacting OpenWeatherMap.` |
| **Malformed JSON** | `ValueError` / `KeyError` | Missing or unexpected payload structure | `Error: Received malformed JSON response from OpenWeatherMap.` |

---

## API Concepts & Interview Questions

### How APIs Authenticate Requests

APIs use authentication to verify the identity of the client calling them, track usage metrics, apply rate limits, and enforce authorization policies. Common authentication schemes include:

1. **Query Parameters**:
   - The credential is sent directly in the URL query string (e.g., `?appid=YOUR_API_KEY` in OpenWeatherMap).
   - *Pros:* Simple to implement and test directly in a browser or curl.
   - *Cons:* URLs are logged in web server access logs, browser histories, and proxy logs, making this pattern less secure for highly sensitive credentials.

2. **HTTP Request Headers (`X-API-Key` / Custom Headers)**:
   - Credentials are submitted via custom request headers (e.g., `X-API-Key: YOUR_KEY`).
   - *Benefits:* Headers are encrypted over HTTPS in transit and are not typically logged in server URL access logs.

3. **Bearer Tokens & OAuth 2.0 (`Authorization` Header)**:
   - Standards-based authorization using JSON Web Tokens (JWT) or temporary access tokens:
     ```http
     Authorization: Bearer <access_token>
     ```
   - Used extensively in production web services, Google Cloud, AWS, GitHub, and enterprise APIs. Tokens are time-limited and scoped to specific permissions.

4. **HTTP Basic Authentication**:
   - Sends base64-encoded username and password in the header:
     ```http
     Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
     ```
   - Primarily used in internal services or legacy architectures.

#### Why Secret Management Matters:
- **Never commit secrets to Git:** Storing API keys in version control exposes them to everyone with repository access. Automated scrapers constantly monitor public repositories to hijack leaked credentials within seconds.
- **Environment variables and `.env`:** Separating code from configuration (following [The Twelve-Factor App](https://12factor.net/config) methodology) ensures secrets remain local to the runtime environment and differ across development, staging, and production.

---

### What Happens When an API Returns a 404

In HTTP and REST architecture, status codes communicate the outcome of a client's request:

1. **Category (4xx vs 5xx)**:
   - **4xx codes indicate Client Errors**: The client sent a request that the server cannot process due to a fault on the caller's side (e.g., incorrect URL, missing parameters, invalid city, or insufficient permissions).
   - **5xx codes indicate Server Errors**: The server understood the request, but experienced an internal fault (e.g., 500 Internal Server Error, 503 Service Unavailable).

2. **What HTTP 404 Means in a RESTful Context**:
   - In traditional web serving, a 404 means the file or route path does not exist on the web server (e.g. requesting `GET /nonexistent-page`).
   - In a REST API like OpenWeatherMap (`GET /data/2.5/weather?q=Asdfghjk`), the endpoint `/data/2.5/weather` exists and the server is healthy, but the **resource identified by the query** (`q="Asdfghjk"`) does not correspond to any known entity in the database.
   - The API server responds with:
     ```http
     HTTP/1.1 404 Not Found
     Content-Type: application/json

     {
       "cod": "404",
       "message": "city not found"
     }
     ```

3. **How Clients Should Handle 404s**:
   - **Do not crash or dump tracebacks:** An unrecognized city or input error is a common user action, not an exceptional system failure.
   - **Parse and translate:** The client should catch the 404 status code (e.g. `response.status_code == 404`), extract any helpful message from the API body if available, and present a constructive message advising the user to check their spelling.

---

## License

This project is licensed under the MIT License - feel free to use, modify, and distribute it.

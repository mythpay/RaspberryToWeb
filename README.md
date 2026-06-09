# Smart Vending Machine System with Raspberry Pi

## Overview

This project is a complete IoT-enabled vending machine control system built using **Raspberry Pi** and **Python**. The system provides real-time machine monitoring, cashless payment integration, inventory management, remote administration, and automated product dispensing.

Designed for commercial vending applications, the platform supports MDB (Multi-Drop Bus) communication, web-based management, telemetry collection, and secure remote access.

## Key Features

### Payment Integration

* MDB protocol implementation for vending machine communication
* Cashless payment device support
* Credit card, mobile wallet, and QR payment processing
* Real-time transaction monitoring
* Secure payment validation and authorization

### Product Management

* Product inventory tracking
* Product pricing configuration
* Sales reporting and analytics

### Machine Control

* Product dispensing control
* Motor and sensor monitoring
* Machine health diagnostics
* Automatic fault detection and recovery

### Remote Monitoring

* Web-based administration dashboard
* Real-time machine status updates
* Live sales and transaction logs
* Remote machine configuration
* Alert and notification system

### IoT Connectivity

* Cloud synchronization
* REST API integration
* MQTT/WebSocket support
* Remote software updates
* Data backup and reporting

## System Architecture

### Hardware Components

* Raspberry Pi 5
* MDB Interface Board
* Cashless Payment Reader
* Coin and Bill Validator
* Product Selection Keypad
* Product Dispensing Motors
* Door and Safety Sensors
* Network Connectivity Module

### Software Stack

* Python 3.11.9
* Flask Web Framework
* Flask-SocketIO for real-time communication
* SQLite/PostgreSQL Database
* APScheduler for background tasks
* Nginx Reverse Proxy
* Gunicorn Application Server

## Core Modules

### MDB Communication Layer

Handles communication between the Raspberry Pi and vending machine controller using the MDB protocol.

### Payment Processing Engine

Processes cashless transactions and manages payment device interactions.

### Inventory Management System

Tracks product stock levels, sales history, and replenishment requirements.

### Web Dashboard

Provides real-time machine monitoring, sales analytics, and administrative controls.

## Security Features

* User authentication and authorization
* Secure API endpoints
* Encrypted communications
* Transaction logging and auditing
* Remote access protection

## Applications

* Snack Vending Machines
* Beverage Vending Machines
* Coffee Machines
* Smart Retail Kiosks
* Automated Product Dispensers
* Self-Service Retail Systems

## Benefits

* Reduced operational costs
* Remote machine management
* Real-time sales visibility
* Improved machine uptime
* Cashless payment support
* Scalable multi-machine deployment

## Technology Highlights

* Raspberry Pi Embedded Computing
* Python Backend Development
* MDB Protocol Communication
* Real-Time WebSocket Updates
* IoT Device Management
* Cloud-Connected Architecture
* Commercial Vending Automation

This project demonstrates a production-ready vending machine platform combining embedded systems, IoT technologies, payment processing, and modern web applications into a unified management solution.

## How to run

**1. Set up Your Platform**
* Python (3.11 recommended)
* pip

**2. Clone the Repository**

```bash
git clone https://github.com/mythpay/RaspberryToWeb.git
cd RaspberryToWeb
```

# Install dependencies
pip install -r requirements.txt

# Run

```bash
python dbcreate.py (Create DataBase)
python app.py (you can see browser website on localhost:5000)
```

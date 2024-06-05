# Smart Elevator with ESP32, RFID, Docker, and AWS

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Contributing](#contributing)
9. [License](#license)

## Introduction
This project implements a smart elevator system using ESP32, RFID, Docker, and AWS. The system allows users to access the elevator using RFID cards. The ESP32 reads the RFID card UID and sends it to an AWS EC2 server via Mosquitto MQTT. The server checks if the user exists in the database. If the user exists, the server sends a command to the ESP32 to trigger a relay, allowing access. The web application displays user information, including name, UID, and access time, and provides a button to manually trigger the relay.

## Features
- RFID-based elevator access
- MQTT communication between ESP32 and server
- User authentication and access control
- Web interface for user management and access logs
- Dockerized deployment

## System Architecture
The system comprises the following components:
- **ESP32**: Reads RFID UID and communicates with the server via MQTT.
- **Mosquitto MQTT Broker**: Facilitates communication between ESP32 and the server.
- **AWS EC2 Server**: Hosts the web application and handles user authentication and relay control.
- **Web Application**: Provides a user interface for managing users and viewing access logs.

![System Architecture](![image](https://github.com/OtabekGofforov/smart_elevator_v3/assets/167739463/84999432-099c-4fdb-b732-47a2d0411943))

## Prerequisites
- Docker and Docker Compose
- Python 3.8+
- An AWS account with an EC2 instance

## Installation
1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/smart-elevator.git
   cd smart-elevator

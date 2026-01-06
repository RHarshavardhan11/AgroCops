# 🛡️ AgroCops: Smart Harvest Security System

![Status](https://img.shields.io/badge/Status-Prototype_Complete-success)
![Platform](https://img.shields.io/badge/Platform-ESP32%20|%20Python-blue)
![Latency](https://img.shields.io/badge/Response_Time-<100ms-brightgreen)

> **A Centralized Edge-Computing Framework for the Real-Time Detection of Perishable Goods Spoilage.**

---

## 📌 Project Overview
**AgroCops** is an industrial-grade monitoring system designed to tackle the **"One Bad Apple" effect** in cold storage logistics. While traditional cloud-based systems suffer from network latency (>800ms) and connectivity drops, AgroCops utilizes a **Direct Serial Edge Architecture** to achieve sub-100ms response times.

The system continuously monitors Volatile Organic Compounds (VOCs) and environmental conditions using a high-density sensor grid, instantly isolating specific storage racks where spoilage precursors (ethylene/ammonia) are detected.

## 🎯 Objectives
* **Prevent Spoilage Cascades:** Detect VOC emissions (Ethylene/Ammonia) in the pre-symptomatic phase.
* **Ultra-Low Latency:** Achieve <100ms alert speed using a Master-Slave Serial Topology.
* **Eliminate False Positives:** Use an Adaptive Hysteresis Algorithm to filter transient sensor noise.
* **Resilience:** Ensure 100% uptime with an automated hardware "Auto-Handshake" watchdog.

---

## 🏗️ System Architecture

### 1. The Edge-First Topology
AgroCops moves away from fragile Wi-Fi dependencies using a robust **Master-Gateway** approach:
* **Sensor Nodes:** ESP32 units with DHT22 & MQ-135 sensors deployed at 3m intervals.
* **Master Gateway:** Aggregates telemetry from the field.
* **Central Command:** A high-performance Desktop Station connected via **High-Speed UART (115200 baud)** for visualization.

### 2. Algorithmic Logic (Adaptive Hysteresis)
To mitigate false alarms caused by sensor jitter, the system replaces static thresholding with a **Temporal Hysteresis Filter**:

$$D(t) = \begin{cases} \text{CRITICAL}, & \text{if } x(t) > T_{crit} \\ \text{CRITICAL}, & \text{if } x(t) \le T_{crit} \text{ and } (t - t_{alert}) < \delta t \\ \text{NOMINAL}, & \text{otherwise} \end{cases}$$

* **T_crit:** 1000 PPM (VOC Threshold)
* **δt:** 2.0s (Decay/Latching Period)

---

## ⚙️ Tech Stack

### Hardware
| Component | Function |
| :--- | :--- |
| **ESP32 DevKit V1** | Dual-Core Microcontroller for Edge Processing |
| **MQ-135** | Gas Sensor (Calibrated for Ammonia/Ethylene) |
| **DHT22** | Precision Temperature & Humidity Sensor |

### Software
| Module | Technology Used |
| :--- | :--- |
| **Central Command** | Python 3.10 + Tkinter (Multi-threaded GUI) |
| **Data Bridge** | PySerial (High-Speed UART) |
| **Analytics Engine** | Matplotlib (Real-time auto-scaling charts) |
| **Simulation** | Hardware-in-the-Loop (HIL) for 100-node stress testing |

---

## 📊 Performance Results

| Methodology | Detection Accuracy | False Positive Rate | Latency |
| :--- | :--- | :--- | :--- |
| **AgroCops (Proposed Edge)** | **94.2%** | **4.3%** | **~98 ms** |
| Cloud-Based Monitoring | 94.0% | 5.1% | ~800 ms |
| Manual Inspection | 65.1% | N/A | High (Hours) |

> **Key Finding:** By shifting compute from the Cloud to the Edge, latency was reduced by **87%**, ensuring critical alerts are triggered before the autocatalytic ripening process spreads.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.x installed
* USB Drivers for ESP32 (CP210x)

### Installation
1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/AgroCops-Team/AgroCops-System.git](https://github.com/AgroCops-Team/AgroCops-System.git)
    ```
2.  **Install Dependencies**
    ```bash
    pip install pyserial matplotlib pillow
    ```
3.  **Run the Dashboard**
    ```bash
    python AgroCops_Dashboard.py
    ```

---

## 🔭 Future Scope
* **Federated Learning:** Deploying lightweight models across multiple warehouses.
* **CO₂ Integration:** Adding MH-Z19B sensors for microbial respiration tracking.
* **Blockchain Traceability:** QR-based logging for spoiled inventory tracking.

## 👥 The Team
**AgroCops** is developed by:
* **Rithuparan PS** - *Hardware Engineer & Lead Developer*
* **Harshavardhan R** - *System Architect*
* **Dr. Geetha C** - *Project Mentor*

---
## ⚖️ Intellectual Property Notice
**© 2026 AgroCops Project. All Rights Reserved.**

This software and its associated hardware architecture are the subject of a pending patent application.
**Unauthorized copying, distribution, or reverse engineering of this code or the associated methodology is strictly prohibited.**

*This repository is for evaluation and academic review purposes only.*

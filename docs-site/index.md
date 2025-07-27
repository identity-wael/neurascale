---
layout: default
title: Home
permalink: /
---

# NeuraScale Documentation

<div align="center">

[![Neural Engine CI/CD](https://github.com/identity-wael/neurascale/actions/workflows/neural-engine-cicd.yml/badge.svg)](https://github.com/identity-wael/neurascale/actions/workflows/neural-engine-cicd.yml)
[![Phase 7 Complete](https://img.shields.io/badge/Phase%207-Complete%20✅-success)](https://github.com/identity-wael/neurascale)
[![Documentation](https://img.shields.io/badge/docs-neurascale.io-blue)](https://docs.neurascale.io)

</div>

Welcome to the official documentation for **NeuraScale**, a comprehensive Brain-Computer Interface (BCI) platform providing real-time neural data acquisition, processing, and analysis with sub-100ms latency.

## 🎉 Latest: Phase 7 - Device Interface Enhancements Complete

We've successfully completed Phase 7, delivering enterprise-grade device management capabilities:

### ✅ Multi-Device Concurrent Streaming

- **Unified API** supporting simultaneous data from multiple devices
- **Zero-copy pipeline** with lock-free ring buffers (>10,000 ch/s)
- **Dynamic synchronization** across heterogeneous sampling rates
- **Automatic time alignment** with <1ms precision

### ✅ Real-Time Signal Quality Monitoring

- **Impedance checking** in <5s per channel (6nA @ 31Hz)
- **SNR calculation** using Welch's method with adaptive windowing
- **Artifact detection** for EOG, EMG, and motion artifacts
- **Quality thresholds**: Excellent (<5kΩ), Good (<10kΩ), Fair (<25kΩ)

### ✅ Automatic Device Discovery

- **Serial**: FTDI/CH340 detection with auto baud rate
- **Bluetooth LE**: GATT service discovery, automatic pairing
- **WiFi**: mDNS/Bonjour zero-configuration networking
- **LSL**: Network-wide stream resolution with metadata

### ✅ WebSocket Event System

- **Real-time notifications** with <10ms latency
- **Typed events**: connection, impedance, quality, errors
- **Binary protocol** option for high-frequency streaming
- **Auto-reconnection** with exponential backoff

### ✅ Performance Achievements

- **Latency**: 50-80ms typical, <100ms guaranteed
- **Throughput**: 10,000+ channels @ 1kHz
- **CPU efficiency**: <5% per 100 channels
- **Memory**: ~1MB per 100 channel buffer

## 🚀 Platform Overview

### What is NeuraScale?

NeuraScale is a cloud-native BCI platform that enables:

- **🧠 Universal Device Support**: 30+ BCI devices from consumer to research grade
- **⚡ Real-Time Processing**: Sub-100ms latency for closed-loop applications
- **📊 Massive Scalability**: Handle 10,000+ channels simultaneously
- **🔒 Clinical Compliance**: HIPAA/GDPR compliant with end-to-end encryption
- **🤖 ML Integration**: Real-time inference and online learning capabilities

### Core Architecture

```
┌─────────────────────────────────────────────────────┐
│              User Applications                       │
│    (Research Tools, Clinical Apps, Consumer BCI)    │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────┐
│                 NeuraScale Platform                  │
├──────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Device  │  │Processing│  │  Data Management │  │
│  │ Manager  │→ │ Pipeline │→ │   & Storage      │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │WebSocket │  │ REST API │  │Machine Learning  │  │
│  │ Server   │  │(FastAPI) │  │   Engine         │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## 📚 Documentation Sections

### 🏁 Getting Started

- **[Quick Start Guide](/getting-started/)** - Set up NeuraScale in minutes
- **[Installation Guide](/docs/installation/)** - Detailed setup instructions
- **[First Recording](/docs/first-recording/)** - Record your first neural data

### 🧠 Neural Engine

- **[Neural Engine Overview](/neural-management-system/)** - Core processing system
- **[Device Integration](/docs/device-integration/)** - Connect BCI devices
- **[Signal Processing](/docs/signal-processing/)** - DSP algorithms and filters
- **[API Reference](/api-documentation/)** - Complete API documentation

### 🔧 Technical Specifications

#### Supported Devices

**Consumer BCIs**

- OpenBCI (Cyton, Ganglion, Cyton+Daisy)
- Emotiv (EPOC+, Insight)
- Muse (Muse 2, Muse S)
- NeuroSky MindWave

**Research Systems**

- g.tec (g.USBamp, g.Nautilus)
- BrainProducts (actiCHamp, LiveAmp)
- ANT Neuro (eego™)
- BioSemi ActiveTwo

**Clinical Arrays**

- Blackrock (Utah Array, CerePlex)
- Plexon OmniPlex
- Custom LSL streams

#### Performance Metrics

| Metric              | Specification                                          |
| ------------------- | ------------------------------------------------------ |
| Latency             | 50-80ms (typical), <100ms (guaranteed)                 |
| Sampling Rates      | Up to 30 kHz (spikes), 1-2 kHz (LFP), 250-500 Hz (EEG) |
| Channel Count       | 8 to 10,000+ channels                                  |
| Data Throughput     | 40 MB/s sustained                                      |
| Storage Compression | 10:1 with lossless algorithms                          |

### 🛠️ Developer Resources

- **[API Documentation](/api-documentation/)** - RESTful and WebSocket APIs
- **[SDK Reference](/docs/sdk/)** - Python, JavaScript, MATLAB clients
- **[Plugin Development](/docs/plugins/)** - Create custom device drivers
- **[Contributing Guide](/contributing/)** - Join the development

### 🏗️ Infrastructure

- **[Architecture Overview](/architecture/)** - System design and components
- **[Deployment Guide](/docs/deployment/)** - Production deployment
- **[Scaling Guide](/docs/scaling/)** - Handle enterprise workloads
- **[Security & Compliance](/security/)** - HIPAA/GDPR implementation

### 📊 Data Management

- **[Dataset Management](/dataset-management/)** - Handle neural datasets
- **[File Formats](/docs/file-formats/)** - EDF+, HDF5, custom binary
- **[Time Series Storage](/docs/timeseries/)** - TimescaleDB optimization
- **[Data Export](/docs/export/)** - Export for analysis

### 🤖 Machine Learning

- **[ML Pipeline](/docs/ml-pipeline/)** - Real-time inference
- **[Model Training](/docs/training/)** - Train BCI decoders
- **[Online Learning](/docs/online-learning/)** - Adaptive classifiers
- **[Pre-trained Models](/docs/models/)** - Ready-to-use models

## 🔬 Use Cases

### Research Applications

- **Motor Imagery**: Decode movement intentions
- **P300 Spellers**: Brain-controlled typing
- **SSVEP**: Steady-state visual stimuli
- **Neurofeedback**: Real-time brain training

### Clinical Applications

- **Seizure Detection**: Real-time epilepsy monitoring
- **Sleep Staging**: Automatic sleep analysis
- **Stroke Rehabilitation**: Motor recovery training
- **Locked-in Syndrome**: Communication interfaces

### Consumer Applications

- **Meditation Apps**: Track mental states
- **Gaming**: Mind-controlled games
- **Productivity**: Focus and attention monitoring
- **Wellness**: Stress and relaxation tracking

## 📈 Platform Status

### Implementation Progress

#### ✅ Completed Phases

- **Phase 1**: Platform Infrastructure
- **Phase 2**: Core BCI Applications
- **Phase 3**: ML Model Integration
- **Phase 4**: Cloud Deployment
- **Phase 5**: Security & Compliance
- **Phase 6**: Performance Optimization
- **Phase 7**: Device Interface Enhancements

#### 🚧 In Progress

- **Phase 8**: Edge Deployment (Q2 2025)
  - Raspberry Pi / Jetson Nano support
  - Offline processing capabilities
  - Power optimization

#### 📅 Upcoming

- **Phase 9**: Advanced ML (Q3 2025)

  - Transformer models for EEG
  - Self-supervised learning

- **Phase 10**: Clinical Integration (Q4 2025)
  - FDA 510(k) preparation
  - Hospital system integration

## 🚀 Quick Start

### Prerequisites

- Python 3.12.11 (exact version required)
- Node.js 18+ and pnpm 9+
- Docker & Docker Compose
- 8GB RAM minimum (16GB recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/identity-wael/neurascale.git
cd neurascale

# Set up virtual environments
./scripts/dev-tools/setup-venvs.sh

# Start infrastructure
docker-compose up -d

# Start Neural Engine
cd neural-engine
source venv/bin/activate
python -m src.main

# Start Console (new terminal)
cd console
npm run dev
```

Visit `http://localhost:3000` to access the NeuraScale console.

### Test with Synthetic Device

```bash
# Create synthetic device
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test", "device_type": "synthetic"}'

# Start streaming
curl -X POST http://localhost:8000/api/v1/devices/test/stream/start
```

## 🤝 Community & Support

### Getting Help

- 📚 **[Documentation](https://docs.neurascale.io)** - Comprehensive guides
- 💬 **[GitHub Discussions](https://github.com/identity-wael/neurascale/discussions)** - Ask questions
- 🐛 **[Issue Tracker](https://github.com/identity-wael/neurascale/issues)** - Report bugs
- 📧 **[Email Support](mailto:support@neurascale.io)** - Direct assistance

### Contributing

We welcome contributions! See our [Contributing Guide](/contributing/) for:

- Code style guidelines
- Development workflow
- Testing requirements
- Pull request process

### Roadmap

Track our progress and upcoming features:

- [GitHub Project Board](https://github.com/identity-wael/neurascale/projects/1)
- [Milestone Tracking](https://github.com/identity-wael/neurascale/milestones)
- [Release Notes](https://github.com/identity-wael/neurascale/releases)

## 📄 License

NeuraScale is open source under the MIT License. See [LICENSE](https://github.com/identity-wael/neurascale/blob/main/LICENSE) for details.

---

<div align="center">

**Built with ❤️ and 🧠 by the NeuraScale Team**

_Bridging Mind and World Through Advanced Neural Cloud Technology_

_Last updated: January 27, 2025_

</div>

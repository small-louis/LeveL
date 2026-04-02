# LeveL

Hardware and software for a gambling harm prevention wearable. LeveL uses galvanic skin response (GSR) monitoring and vibrotactile haptic feedback to help users recognise physiological arousal during gambling sessions.

Built as part of Innovation Design Engineering at Imperial College London and the Royal College of Art.

## What it does

The wearable measures skin conductance in real time via GSR electrodes. When arousal levels spike — which correlates with impulsive gambling behaviour — the device delivers haptic stimulation through a vibration motor to interrupt the cycle and prompt self-awareness.

## System architecture

- **Arduino firmware** — Reads GSR sensors via a multiplexer, drives a DRV2605 haptic motor, and communicates with a host over serial
- **Python host** — Tkinter GUI for real-time GSR plotting, haptic motor control, session recording, and data export
- **Slot machine simulator** — A test environment for running controlled user trials with the wearable

## Key files

| File | Description |
|------|-------------|
| `integrated_code.py` | Main GUI application combining GSR monitoring and haptic control |
| `integrated_code.ino` | Arduino firmware for the combined GSR + haptic system |
| `haptic_control.py` | Standalone haptic motor controller with CLI interface |
| `gsr_plotter.py` | Real-time GSR data plotter |
| `process_gsr_data.py` | Post-processing and analysis of recorded GSR sessions |
| `create_comparison_plots.py` | Cross-session comparison visualisations |
| `Slot-Machine with gui/` | Gambling simulator for user trials |
| `GSR-data/` | Raw and processed data from trial sessions |

## Hardware

- Arduino (ESP32 or similar)
- GSR electrodes
- Adafruit DRV2605 haptic driver
- ERM or LRA vibration motor
- Multiplexer for multi-channel GSR

## Setup

```bash
pip install -r requirements.txt
python integrated_code.py
```

## More

Project page: [louisbrouwer.com/level.html](https://louisbrouwer.com/level.html)

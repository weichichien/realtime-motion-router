# Realtime Motion Router

Realtime Motion Router is a lightweight routing layer for distributing real-time motion-analysis data to multiple computers and interactive systems.

The router is intentionally separated from motion-analysis software. Its job is not to calculate body-motion metrics, but to receive an existing metric stream, normalize the transport layer, and redistribute the data to one or more downstream systems.

## Purpose

The project is being developed as shared infrastructure for multi-computer interactive performance and research systems.

The initial data source is:

- [YukiHataRin/realtime-dance-analysis](https://github.com/YukiHataRin/realtime-dance-analysis)
- Input endpoint: `/ws/metrics`
- Transport: WebSocket / JSON

The first target transport will be OSC over UDP.

This separation allows the motion-analysis application and downstream projects to evolve independently.

## Architecture

```text
Motion analysis
(webcam / MediaPipe)
        |
        | WebSocket JSON
        v
Realtime Motion Router
        |
        +---- OSC/UDP ----> Performance computer
        |
        +---- OSC/UDP ----> Subproject A
        |
        +---- OSC/UDP ----> Subproject B
        |
        +---- future outputs / logging
```

The motion-analysis computer acts as the data publisher. Receiving computers do not need to request every value individually; the router pushes new motion data as it arrives.

## Current Metric Schema

The current source application provides nine motion descriptors:

| Field | Description |
| --- | --- |
| `energy` | Movement intensity based on weighted limb angular velocity |
| `sync_velocity` | Left/right movement-magnitude balance |
| `sync_correlation` | Temporal correlation between left/right movement activity |
| `expansion` | 3D body expansion based on joint convex-hull volume |
| `curvature` | Curvature of wrist and ankle trajectories |
| `height` | Current center-of-mass height proxy |
| `sway` | Horizontal center-of-mass displacement relative to the feet |
| `torque` | Effort proxy based on angular acceleration |
| `jerk` | Abruptness / smoothness cost based on angular jerk |

These names currently follow the upstream `realtime-dance-analysis` output. Metric definitions may be refined later, but the router should keep its transport interface as stable as possible.

## Network Model

Development can use Wi-Fi, but the intended performance setup is a dedicated Ethernet LAN.

Typical topology:

```text
Motion-analysis PC
        |
        | Ethernet
        v
     Network switch
      /    |     \
     /     |      \
    v      v       v
  Mac   Project A  Project B
```

A dedicated private subnet with static addresses or DHCP reservations is recommended for performance use. Internet access can remain on a separate Wi-Fi interface.

## Design Principles

- Keep motion analysis and data distribution as separate applications.
- Do not modify the source analysis application unless the analysis itself needs to change.
- Keep the router lightweight and suitable for real-time use.
- Support multiple independent receivers.
- Avoid making one downstream computer a mandatory relay for the others.
- Keep configuration separate from code where possible.
- Preserve a stable data contract even when metric calculations evolve.
- Prefer deterministic, inspectable behavior suitable for live performance.

## Initial Development Plan

1. Receive `/ws/metrics` from `realtime-dance-analysis`.
2. Verify and print the incoming JSON stream.
3. Send one metric over OSC/UDP to a second computer.
4. Send the complete metric frame.
5. Move destination addresses and ports into configuration.
6. Support multiple OSC targets.
7. Add timestamps / sequence IDs for diagnostics.
8. Add optional logging and connection-status reporting.
9. Evaluate additional input and output protocols if needed.

## Current Status

The upstream `realtime-dance-analysis` application has been reproduced successfully on Windows, including webcam pose tracking and live metric output.

A minimal external Python WebSocket client has also successfully received the `/ws/metrics` stream.

The next milestone is:

```text
WebSocket metrics -> Realtime Motion Router -> OSC/UDP -> second computer
```

## Repository Scope

This repository contains the routing/distribution layer only.

Motion tracking, pose estimation, and metric calculation remain in their respective source applications. This makes it possible to use future sources such as Kinect or other tracking systems without coupling downstream projects to a particular sensor or pose-estimation implementation.

## License

License to be determined before external distribution.

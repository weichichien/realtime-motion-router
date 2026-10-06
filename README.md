# Realtime Motion Router

Realtime Motion Router is a lightweight routing layer for distributing real-time motion-analysis data to multiple computers and interactive systems.

Realtime Motion Router 是一個輕量化的即時動作資料分配工具，用來把動作分析結果傳送到其他電腦或互動系統。

The router is intentionally separated from motion-analysis software. Its job is not to calculate body-motion metrics, but to receive an existing metric stream and redistribute the data to one or more downstream systems.

本專案刻意與動作分析程式分開。它本身不負責計算人體動作指標，而是接收已經計算好的資料，再把資料傳送給一台或多台其他電腦。

## Purpose / 專案用途

This project is being developed as shared infrastructure for multi-computer interactive performance and research systems.

本工具的目標是讓不同子計畫都能用相同方式測試與接收即時動作資料，而不需要依賴某一台特定的電腦。

The initial data source is:

- [YukiHataRin/realtime-dance-analysis](https://github.com/YukiHataRin/realtime-dance-analysis)
- Input endpoint: `/ws/metrics`
- Transport: WebSocket / JSON

The first target transport is OSC over UDP.

第一階段使用 OSC over UDP 把資料送到另一台電腦。

## Two Tools / 兩種工具

This repository provides two complementary tools.

這個 repository 會提供兩種互補的工具：

### 1. Sender / Router / 傳送端

The Sender runs on the computer that already has access to motion-analysis data.

傳送端執行在「有動作分析資料」的電腦上。

Responsibilities:

- Connect to `/ws/metrics`
- Receive live JSON motion metrics
- Convert the data to OSC messages
- Send the data to one or more receiver computers
- Later support configuration, multiple targets, logging, and diagnostics

主要工作：

- 連接 `/ws/metrics`
- 接收即時 JSON 動作資料
- 將資料轉成 OSC
- 把資料送到一台或多台接收電腦
- 未來可加入多個 target、設定檔、記錄與診斷功能

The Sender is not intended to be Windows-only. Windows is simply the current development platform.

Sender 並不是只能跑在 Windows；目前只是先以 Windows 作為開發與測試環境。

### 2. Receiver / Test Client / 接收端測試工具

The Receiver runs on another computer and listens for OSC data.

接收端執行在第二台電腦上，負責接收 OSC 資料。

Responsibilities:

- Listen on a selected UDP port
- Receive OSC messages
- Print incoming metric names and values
- Confirm that IP, port, Ethernet/Wi-Fi, firewall, and OSC transport are working correctly

主要工作：

- 監聽指定的 UDP port
- 接收 OSC 訊息
- 顯示收到的 metric 名稱與數值
- 確認 IP、port、Ethernet/Wi-Fi、防火牆與 OSC 傳輸是否正常

The Receiver is a reference and diagnostic tool. A downstream project may later integrate OSC reception directly into its own software.

Receiver 主要是標準測試與除錯工具。之後各子計畫可以把 OSC 接收功能直接整合進自己的程式，而不一定需要一直執行這個測試 Receiver。

## Independent Two-Computer Test / 各子計畫應自行完成兩台電腦測試

Each subproject should be able to test the complete pipeline using its own two computers.

每個子計畫都應該能使用自己的兩台電腦完成整套測試，不應依賴 AI PUNK 的 Windows 或 Mac。

Recommended test setup:

```text
Computer A
Motion analysis
    |
    | WebSocket / JSON
    v
Sender / Router
    |
    | OSC / UDP
    | Ethernet or Wi-Fi
    v
Computer B
Receiver / Test Client
```

The minimum validation procedure is:

1. Connect the two computers by Ethernet or place them on the same LAN.
2. Assign IP addresses in the same subnet.
3. Confirm that both computers can ping each other.
4. Start the motion-analysis application on Computer A.
5. Start the Sender on Computer A.
6. Start the Receiver on Computer B.
7. Move in front of the camera.
8. Confirm that changing motion metrics appear on Computer B.

最基本的測試流程：

1. 用 Ethernet 連接兩台電腦，或讓兩台電腦進入同一個區域網路。
2. 確認兩台電腦的 IP 在同一個 subnet。
3. 先用 `ping` 確認兩邊可以互相連線。
4. 在電腦 A 啟動動作分析程式。
5. 在電腦 A 啟動 Sender。
6. 在電腦 B 啟動 Receiver。
7. 在攝影機前移動。
8. 確認電腦 B 可以看到持續變化的動作數值。

If step 8 succeeds, the basic cross-computer motion-data pipeline is working.

如果第 8 步成功，就代表跨電腦的即時動作資料串流已經打通。

## Architecture / 系統架構

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

動作分析電腦是資料來源。接收端不需要一直主動詢問資料；只要有新的 motion data，Sender 就會主動送出。

## Current Metric Schema / 目前資料欄位

The current source application provides nine motion descriptors:

| Field | English description | 中文說明 |
| --- | --- | --- |
| `energy` | Movement intensity based on weighted limb angular velocity | 動作強度 |
| `sync_velocity` | Left/right movement-magnitude balance | 左右側動作強度平衡 |
| `sync_correlation` | Temporal correlation between left/right movement activity | 左右側動作活動的時間相關 |
| `expansion` | 3D body expansion based on joint convex-hull volume | 身體在三維空間中的展開程度 |
| `curvature` | Curvature of wrist and ankle trajectories | 手腕與腳踝運動軌跡的曲率 |
| `height` | Current center-of-mass height proxy | 重心高度的近似值 |
| `sway` | Horizontal center-of-mass displacement relative to the feet | 重心相對雙腳的水平偏移 |
| `torque` | Effort proxy based on angular acceleration | 以角加速度估算的動作 effort 指標 |
| `jerk` | Abruptness / smoothness cost based on angular jerk | 動作急促程度 / 平滑度代價 |

These names currently follow the upstream `realtime-dance-analysis` output. Metric definitions may be refined later, but the router should keep its transport interface as stable as possible.

目前欄位名稱沿用 `realtime-dance-analysis`。未來動作指標的計算方式可能會調整，但 Router 的資料介面應盡量維持穩定，避免下游子計畫一直修改程式。

## Network Model / 網路架構

Development can use Wi-Fi, but the intended performance setup is a dedicated Ethernet LAN.

開發測試時可以使用 Wi-Fi，但正式展演建議使用獨立的 Ethernet 區域網路。

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

Recommended practice:

- Use a dedicated private subnet for performance data.
- Use static IP addresses or DHCP reservations.
- Keep Internet access on a separate Wi-Fi interface when possible.
- Do not rely on venue Wi-Fi for critical real-time control.

建議做法：

- 即時表演資料使用獨立私有網段。
- 使用固定 IP 或 DHCP reservation。
- 若需要 Internet，可另外使用 Wi-Fi。
- 正式展演不要把關鍵即時控制依賴在場館 Wi-Fi 上。

Example:

```text
Motion PC   192.168.50.10
Receiver A  192.168.50.20
Receiver B  192.168.50.30
Subnet      255.255.255.0
```

## Basic Terms / 基礎名詞

| Term | 中文 | Simple explanation |
| --- | --- | --- |
| IP address | IP 位址 | A network address used to identify one computer |
| Subnet | 子網路 | A group of devices that can communicate directly on the same local network |
| Port | 連接埠 | A numbered communication endpoint used by software |
| UDP | 使用者資料包協定 | A fast network transport commonly used for real-time data |
| OSC | Open Sound Control | A message format widely used in interactive media and music systems |
| WebSocket | WebSocket | A persistent connection for continuously sending data between applications |
| Sender | 傳送端 | The program that sends data |
| Receiver | 接收端 | The program that receives data |
| LAN | 區域網路 | A local network connecting nearby devices |
| Ethernet | 乙太網路 | Wired networking, recommended for stable performance use |

## Design Principles / 設計原則

- Keep motion analysis and data distribution as separate applications.
- Do not modify the source analysis application unless the analysis itself needs to change.
- Keep the router lightweight and suitable for real-time use.
- Support multiple independent receivers.
- Avoid making one downstream computer a mandatory relay for the others.
- Keep configuration separate from code where possible.
- Preserve a stable data contract even when metric calculations evolve.
- Prefer deterministic, inspectable behavior suitable for live performance.

中文重點：

- 動作分析與資料分配程式分開。
- 除非真的要修改動作分析本身，否則不要改來源分析程式。
- Router 要保持輕量、即時。
- 支援多台獨立 Receiver。
- 不要讓某一台 downstream 電腦成為其他電腦必經的中繼站。
- 設定與程式碼盡量分離。
- 即使未來 metric 計算方式改變，資料介面也盡量保持穩定。
- 正式展演系統應該容易檢查、容易除錯。

## Initial Development Plan / 初始開發計畫

1. Receive `/ws/metrics` from `realtime-dance-analysis`.
2. Verify and print the incoming JSON stream.
3. Send one metric over OSC/UDP to a second computer.
4. Send the complete metric frame.
5. Move destination addresses and ports into configuration.
6. Support multiple OSC targets.
7. Add timestamps / sequence IDs for diagnostics.
8. Add optional logging and connection-status reporting.
9. Evaluate additional input and output protocols if needed.

## Current Status / 目前進度

Completed:

- The upstream `realtime-dance-analysis` application has been reproduced successfully on Windows.
- Webcam pose tracking is working.
- Live motion metrics are working.
- A minimal external Python WebSocket client has successfully received the `/ws/metrics` stream.
- A dedicated Ethernet link between two development computers has been tested successfully.

目前已完成：

- Windows 已成功復刻 `realtime-dance-analysis`。
- Webcam 人體姿態追蹤正常。
- 即時 motion metrics 正常。
- 外部 Python client 已成功讀取 `/ws/metrics`。
- 兩台開發電腦之間的獨立 Ethernet 連線已測試成功。

The next milestone is:

```text
WebSocket metrics
        ->
Realtime Motion Router Sender
        ->
OSC / UDP
        ->
Receiver on second computer
```

## Repository Scope / Repository 範圍

This repository contains the routing/distribution layer and its reference receiver tools.

Motion tracking, pose estimation, and metric calculation remain in their respective source applications.

本 repository 包含資料傳送、分配與標準 Receiver 測試工具。

人體追蹤、pose estimation 與 metric calculation 仍然由各自的來源程式負責。

This separation makes it possible to use future sources such as Kinect or other tracking systems without coupling downstream projects to a particular sensor or pose-estimation implementation.

因此未來即使改成 Kinect 或其他 motion tracking 系統，只要輸出資料格式一致，下游子計畫仍然可以繼續使用同一套 Router / Receiver。

## License

License to be determined before external distribution.

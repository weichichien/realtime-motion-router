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

## Project Structure / 專案結構

```text
realtime-motion-router/
├─ sender/
│  └─ websocket_to_osc.py
├─ receiver/
│  └─ osc_receiver.py
├─ config/
│  ├─ config.example.json
│  └─ README.md
├─ requirements.txt
├─ .gitignore
└─ README.md
```

- `sender/`: reads motion metrics and sends OSC / 讀取 motion metrics 並送出 OSC。
- `receiver/`: reference receiver for testing and diagnostics / 標準接收端測試與除錯工具。
- `config/`: network and target configuration / 網路與 target 設定。`config.example.json` 可提交，個別電腦使用的 `config.json` 不會被 Git 追蹤。
- `requirements.txt`: shared Python dependencies / Sender 與 Receiver 共用的 Python 套件需求。

## Minimal v0.4 Test / 最小版跨電腦測試

The current implementation sends all nine motion metrics as separate OSC addresses to every destination listed in `config/config.json`.

目前版本會把九個 motion metrics 分別以獨立 OSC address，同時傳送到 `config/config.json` 中列出的所有目的地。

### Install dependencies / 安裝套件

On each computer, open a terminal in this repository and create or activate a Python virtual environment if needed. Then run:

兩台電腦都要進入這個 repository，在需要時建立或啟用 Python virtual environment，然後執行：

```bash
python -m pip install -r requirements.txt
```

On macOS, use `python3` instead of `python` if that is how Python is installed.

若 macOS 的 Python 指令是 `python3`，請改用：

```bash
python3 -m pip install -r requirements.txt
```

### Create local configuration / 建立本機設定檔

After pulling the repository, copy the example configuration once on **each computer**.

每台電腦第一次設定時，都要先複製一份本機設定檔。

Windows PowerShell:

```powershell
Copy-Item config/config.example.json config/config.json
```

macOS / Linux:

```bash
cp config/config.example.json config/config.json
```

Then edit `config/config.json`. For the current two-computer Ethernet test:

接著修改 `config/config.json`。目前兩台電腦 Ethernet 測試可使用：

```json
{
  "motion_source": {
    "websocket_url": "ws://127.0.0.1:8000/ws/metrics"
  },
  "osc_outputs": [
    {
      "name": "Mac receiver",
      "destination_ip": "192.168.50.20",
      "destination_port": 9000
    },
    {
      "name": "Project B receiver",
      "destination_ip": "192.168.50.30",
      "destination_port": 9000
    }
  ],
  "osc_receiver": {
    "listen_interface": "all",
    "listen_port": 9000
  }
}
```

The local `config/config.json` is ignored by Git. This prevents different computers' IP settings from creating Git conflicts.

本機的 `config/config.json` 不會被 Git 追蹤，因此不同電腦可以保留自己的 IP / port 設定，不會造成 Git conflict。

### Configuration design toward the final system / 與正式版本一致的設定方式

The **configuration approach introduced in v0.3 is intended to remain in the final system**:

v0.3 開始採用的 **設定方式會延續到正式版本**：

- Network addresses and ports are stored in `config/config.json`, not hard-coded in Python.
- `config/config.example.json` is tracked by Git as a template.
- Each computer keeps its own `config/config.json`, which is ignored by Git.
- The motion-data source, OSC destinations, and local OSC receiving settings remain separate concepts.
- Field names are written from the user's point of view: `destination_ip` means the remote computer that receives the data; `listen_interface` means the local interfaces on which this computer accepts OSC.
- `listen_interface: "all"` hides the socket-specific `0.0.0.0` value from normal users.
- For performance use, the same configuration mechanism can be used with a dedicated Ethernet LAN and fixed/private IP addresses.

- IP、port 等網路參數放在 `config/config.json`，不寫死在 Python 程式裡。
- `config/config.example.json` 會由 Git 管理，作為所有人的範例。
- 每台電腦保留自己的 `config/config.json`，且不會被 Git 追蹤。
- motion-data source、OSC 傳送目的地、以及本機 OSC 接收設定會維持分離。
- 欄位名稱改成從使用者角度理解：`destination_ip` 是「資料要送到的對方 IP」；`listen_interface` 是「這台電腦在哪些本機網路介面接收 OSC」。
- 一般使用者只需要使用 `listen_interface: "all"`，不需要理解 socket 的 `0.0.0.0`。
- 正式展演使用 dedicated Ethernet 與固定/private IP 時，仍然使用同一套 config 機制。

In v0.4, `osc_outputs` is an active multi-target list. The Sender creates one OSC client per destination and fans every metric out to all configured receivers. Adding a receiver requires only another config entry; no Python edit is needed.

v0.4 中，`osc_outputs` 已經是實際運作的 multi-target 清單。Sender 會為每個 destination 建立 OSC client，並把每項 metric 同時送給所有接收端。增加 Receiver 時只需要新增 config 項目，不需要修改 Python。

For students and subprojects, the practical rule is:

對學生與各子計畫而言，可以直接記住：

> **Change network settings in `config/config.json`; do not edit Sender/Receiver Python files just to change IP addresses or ports.**  
> **需要換 IP 或 port 時，只改 `config/config.json`，不要為了網路設定去修改 Sender / Receiver 的 Python 程式。**

### Computer B: start Receiver first / 電腦 B：先啟動 Receiver

```bash
python receiver/osc_receiver.py
```

macOS:

```bash
python3 receiver/osc_receiver.py
```

Expected startup message / 預期畫面：

```text
Listening for OSC on all interfaces, port 9000
Expected addresses:
  /motion/energy
  /motion/sync_velocity
  /motion/sync_correlation
  /motion/expansion
  /motion/curvature
  /motion/height
  /motion/sway
  /motion/torque
  /motion/jerk
Press Ctrl+C to stop.
```

### Computer A: start motion analysis / 電腦 A：啟動動作分析

Start `realtime-dance-analysis` and confirm that the dashboard shows changing live metrics.

啟動 `realtime-dance-analysis`，確認 webcam、pose tracking 與即時 metrics 都正常變動。

### Computer A: start Sender / 電腦 A：啟動 Sender

Set the receiving computer's Ethernet or LAN IP as `osc_outputs[].destination_ip` in `config/config.json`, then start the Sender:

先把接收端電腦實際的 Ethernet 或 LAN IP 填入 `osc_outputs[].destination_ip`，再啟動 Sender：

```bash
python sender/websocket_to_osc.py
```

The Sender reads `motion_source.websocket_url` and every destination in `osc_outputs` from `config/config.json`.

Sender 會從 `config/config.json` 讀取 `motion_source.websocket_url`，以及 `osc_outputs` 中的所有 destination。

It sends:

送出：

```text
/motion/energy
/motion/sync_velocity
/motion/sync_correlation
/motion/expansion
/motion/curvature
/motion/height
/motion/sway
/motion/torque
/motion/jerk

UDP port: 9000
```

If the complete path is working, the Receiver computer should continuously display complete snapshots such as:

如果整條資料鏈正常，接收端應持續看到完整九項資料，例如：

```text
energy=11.358 | sync_velocity=0.587 | sync_correlation=0.809 | expansion=0.355 | curvature=0.343 | height=0.175 | sway=0.079 | torque=80.961 | jerk=168370257.298
```

Move in front of the camera and confirm that multiple values change.

在攝影機前移動，確認多個數值會隨動作改變。

### Success criterion / 成功標準

```text
camera
  ->
realtime-dance-analysis
  ->
/ws/metrics
  ->
Sender
  ->
OSC / UDP
  ->
Ethernet or LAN
  ->
Receiver
```

If complete nine-metric snapshots appear on every configured receiver and change with movement, the v0.4 multi-target pipeline is working.

只要所有已設定的 Receiver 都能看到完整九項資料，而且數值會隨動作變化，就代表 v0.4 multi-target 資料傳輸成功。

## Initial Development Plan / 初始開發計畫

1. Receive `/ws/metrics` from `realtime-dance-analysis`.
2. Verify and print the incoming JSON stream.
3. Send one metric over OSC/UDP to a second computer.
4. Send the complete metric frame.
5. Move destination addresses and ports into configuration.
6. Support multiple OSC targets. **Completed in v0.4.**
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

The v0.2 nine-metric Ethernet test and v0.3 configuration milestone have been completed successfully. v0.4 adds real multi-target fan-out: one Sender can now transmit the same nine metrics directly to multiple independent OSC receivers.

v0.2 的九項 metric Ethernet 跨電腦測試與 v0.3 config milestone 已完成。v0.4 正式加入 multi-target fan-out：一個 Sender 現在可以把相同九項 metrics 直接傳送給多台彼此獨立的 OSC Receiver。

## Repository Scope / Repository 範圍

This repository contains the routing/distribution layer and its reference receiver tools.

Motion tracking, pose estimation, and metric calculation remain in their respective source applications.

本 repository 包含資料傳送、分配與標準 Receiver 測試工具。

人體追蹤、pose estimation 與 metric calculation 仍然由各自的來源程式負責。

This separation makes it possible to use future sources such as Kinect or other tracking systems without coupling downstream projects to a particular sensor or pose-estimation implementation.

因此未來即使改成 Kinect 或其他 motion tracking 系統，只要輸出資料格式一致，下游子計畫仍然可以繼續使用同一套 Router / Receiver。

## License

License to be determined before external distribution.

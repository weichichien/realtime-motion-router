# Realtime Motion Router

Realtime Motion Router is a lightweight routing layer for distributing real-time motion-analysis data to multiple computers and interactive systems.

Realtime Motion Router 是一個輕量化的即時動作資料分配工具，用來把動作分析結果傳送到其他電腦或互動系統。

The router is intentionally separated from motion-analysis software. Its job is not to calculate body-motion metrics, but to receive an existing metric stream and redistribute the data to one or more downstream systems.

本專案刻意與動作分析程式分開。它本身不負責計算人體動作指標，而是接收已經計算好的資料，再把資料傳送給一台或多台其他電腦。

## Purpose / 專案用途

This project is being developed as shared infrastructure for multi-computer interactive performance and research systems.

本工具的目標是讓不同子計畫都能用相同方式測試與接收即時動作資料，而不需要依賴某一台特定的電腦。

The current AI PUNK motion-analysis source is:

- [weichichien/realtime-motion-analysis](https://github.com/weichichien/realtime-motion-analysis) — AI PUNK fork used for current development
- Upstream parent: [YukiHataRin/realtime-dance-analysis](https://github.com/YukiHataRin/realtime-dance-analysis)
- Input endpoint: `/ws/metrics`
- Input transport: WebSocket / JSON
- Output transport: OSC over UDP

目前 AI PUNK 使用的動作分析來源是：

- [weichichien/realtime-motion-analysis](https://github.com/weichichien/realtime-motion-analysis) — 目前 AI PUNK 使用與修改的 fork
- 原始 upstream：[YukiHataRin/realtime-dance-analysis](https://github.com/YukiHataRin/realtime-dance-analysis)
- 輸入 endpoint：`/ws/metrics`
- 輸入傳輸：WebSocket / JSON
- 輸出傳輸：OSC over UDP

For live-performance use, the motion-analysis application can run with Preview OFF / analysis-only mode so pose analysis and metrics continue without returning and rendering processed preview frames.

正式展演時，動作分析程式可使用 Preview OFF / analysis-only mode：MediaPipe 與 metrics 會持續運作，但不再回傳與顯示 processed preview，以降低不必要的顯示負擔。

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
- Read source and destination settings from local configuration
- Fan out the same metric stream to multiple independent OSC targets
- Future work: logging and diagnostics

主要工作：

- 連接 `/ws/metrics`
- 接收即時 JSON 動作資料
- 將資料轉成 OSC
- 把資料送到一台或多台接收電腦
- 從本機設定檔讀取 source 與 destination
- 將同一份 metric stream 同時送往多個彼此獨立的 OSC target
- 後續可加入 logging 與 diagnostics

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

## Initialize for a New Subproject / 新子計畫初始化

This section is the recommended starting point for another AI PUNK subproject. The first goal is not to integrate OSC directly into the subproject code. First, use the reference Receiver in this repository to prove that the computer and network can receive the motion stream correctly.

這一節是其他 AI PUNK 子計畫建議採用的初始化流程。第一步不是立刻把 OSC 寫進自己的程式，而是先使用本 repository 內建的標準 Receiver，確認該電腦與網路可以正確收到 motion stream。

### 1. Decide the role / 先確認這台電腦的角色

- **Most downstream subprojects should start as Receiver only.** They receive OSC from the central motion-analysis / Sender computer.
- **Only the computer connected to the motion-analysis source needs to run the Sender.**

- **大多數下游子計畫只需要先當 Receiver。** 它們從中央 motion-analysis / Sender 電腦接收 OSC。
- **只有連接 motion-analysis source 的電腦需要執行 Sender。**

Typical system:

```text
Motion-analysis computer
  realtime-motion-analysis
          |
          | WebSocket / JSON
          v
  realtime-motion-router Sender
       /        |        \
      /         |         \
 OSC/UDP     OSC/UDP     OSC/UDP
    v           v           v
Project A    Project B    Project C
Receiver     Receiver     Receiver
```

### 2. Prerequisites / 前置需求

- Git
- Python 3 with `venv` support. Current development has been tested with Python 3.10.
- A network connection to the Sender computer. Dedicated Ethernet is recommended for performance use.
- GitHub access to this repository if the repository is not public.

- Git
- 支援 `venv` 的 Python 3。目前開發環境已使用 Python 3.10 驗證。
- 能連到 Sender 電腦的網路。正式展演建議使用 dedicated Ethernet。
- 若 repository 不是公開的，需先取得 GitHub 存取權限。

### 3. Clone the repository / Clone repository

```bash
git clone https://github.com/weichichien/realtime-motion-router.git
cd realtime-motion-router
```

### 4. Create a local Python environment / 建立本機 Python 環境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The virtual environment is local to this repository. Do not share or commit `.venv`.

這個 virtual environment 只屬於這份 repository，不要分享或提交 `.venv`。

### 5. Create the local config / 建立本機 config

Copy the example file once:

Windows PowerShell:

```powershell
Copy-Item config/config.example.json config/config.json
```

macOS / Linux:

```bash
cp config/config.example.json config/config.json
```

`config/config.json` is intentionally ignored by Git. Each computer keeps its own IP and port settings.

`config/config.json` 刻意不進 Git。每台電腦各自保存自己的 IP 與 port 設定。

### 6. Receiver setup for a subproject / 子計畫 Receiver 設定

For a normal Receiver computer, the important section is:

一般 Receiver 電腦真正需要注意的是：

```json
{
  "osc_receiver": {
    "listen_interface": "all",
    "listen_port": 9000
  }
}
```

The Receiver does **not** need the Sender IP in its own config. It simply listens on its local UDP port.

Receiver 自己的 config **不需要填 Sender IP**；它只需要在本機 UDP port 等待資料。

The Sender computer must add this Receiver computer to its own `osc_outputs`, for example:

Sender 電腦則必須把這台 Receiver 加入自己的 `osc_outputs`，例如：

```json
{
  "name": "Project A",
  "destination_ip": "192.168.50.30",
  "destination_port": 9000
}
```

The destination IP is the Receiver computer IP, not the Sender IP.

`destination_ip` 是 Receiver 電腦的 IP，不是 Sender 自己的 IP。

### 7. Check the network before running the app / 執行前先確認網路

The Sender and Receiver must be able to reach each other on the selected LAN. For a direct Ethernet setup, they should use addresses in the same subnet, for example:

Sender 與 Receiver 必須位於可以互相連線的 LAN。若使用直接 Ethernet，可使用同一 subnet，例如：

```text
Sender       192.168.50.10
Project A    192.168.50.30
Subnet       255.255.255.0
```

Before testing OSC, confirm basic connectivity with `ping`.

測試 OSC 前，先使用 `ping` 確認基本網路連線。

### 8. Start the reference Receiver / 啟動標準 Receiver

From the repository root:

在 repository root 執行：

```bash
python receiver/osc_receiver.py
```

On macOS, use `python3` if your environment requires it.

若 macOS 環境使用 `python3`，請改用 `python3 receiver/osc_receiver.py`。

Expected startup message:

預期啟動畫面：

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

### 9. Sender startup / Sender 啟動

On the motion-analysis computer:

在 motion-analysis 電腦上：

1. Start `realtime-motion-analysis`.
2. Enable the camera and confirm that its metrics are changing.
3. For live use, Preview OFF / analysis-only mode is recommended after visual verification.
4. Confirm the dashboard WebSocket status is connected. If it shows `WS DISCONNECTED`, refresh the browser page.
5. Start the Router Sender:

1. 啟動 `realtime-motion-analysis`。
2. 啟用 camera，確認 metrics 正在變化。
3. 視覺確認完成後，正式即時使用建議切到 Preview OFF / analysis-only mode。
4. 確認 dashboard 的 WebSocket 狀態已連線；若顯示 `WS DISCONNECTED`，重新整理瀏覽器頁面。
5. 啟動 Router Sender：

```bash
python sender/websocket_to_osc.py
```

The Sender should list every configured output at startup.

Sender 啟動時應列出所有已設定的 destination。

### 10. Initialization success criterion / 初始化成功標準

A new subproject is considered initialized when the reference Receiver continuously prints complete nine-metric snapshots and the values change when the performer moves.

當標準 Receiver 能持續印出完整九項 metrics，而且表演者移動時數值會跟著變化，就可以視為這個新子計畫已完成基本初始化。

Only after this test succeeds should the subproject replace the reference Receiver with OSC reception inside its own application.

只有這個測試成功之後，子計畫才建議把標準 Receiver 換成自己程式內的 OSC 接收功能。

> **Important:** Normally, do not run the reference Receiver and another application bound to the same UDP port on the same computer at the same time. Stop the reference Receiver before testing the subproject application on port 9000.
>
> **重要：** 一般情況下，同一台電腦不要同時讓標準 Receiver 與另一個程式綁定同一個 UDP port。若子計畫程式也使用 9000，測試前請先停止標準 Receiver。

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

Start `realtime-motion-analysis` and confirm that the dashboard shows changing live metrics. After visual verification, Preview OFF / analysis-only mode is recommended for lower preview overhead during live use.

啟動 `realtime-motion-analysis`，確認 webcam、pose tracking 與即時 metrics 都正常變動。完成視覺確認後，正式即時使用建議切換到 Preview OFF / analysis-only mode，以降低 preview 額外負擔。

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
realtime-motion-analysis
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

1. Receive `/ws/metrics` from the motion-analysis source.
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

- The AI PUNK fork `realtime-motion-analysis` is running successfully on Windows.
- Webcam pose tracking and the nine live motion metrics are working.
- Preview OFF now provides an analysis-only mode that keeps pose analysis and metrics active while skipping processed-preview drawing/return.
- A minimal external Python WebSocket client has successfully received the `/ws/metrics` stream.
- A dedicated Ethernet link between two development computers has been tested successfully.
- Router v0.4 can fan out every metric to every destination listed in `osc_outputs`.
- The v0.4 Sender has been verified with the existing Mac Receiver after the multi-target change.

目前已完成：

- AI PUNK fork `realtime-motion-analysis` 已在 Windows 正常運作。
- Webcam 人體姿態追蹤與九項即時 motion metrics 正常。
- Preview OFF 已改為 analysis-only mode：保留 pose analysis 與 metrics，但停止 processed preview 的繪製與回傳。
- 外部 Python client 已成功讀取 `/ws/metrics`。
- 兩台開發電腦之間的獨立 Ethernet 連線已測試成功。
- Router v0.4 會把每項 metric fan-out 到 `osc_outputs` 中列出的所有 destination。
- v0.4 multi-target 修改後，既有 Mac Receiver 已再次驗證可正常接收資料。

The current single-Receiver v0.4 test is stable. Simultaneous multi-Receiver validation will be completed when a second downstream computer/subproject is connected. Timing diagnostics remain a later task if periodic stalls need to be investigated.

目前 v0.4 的單一 Receiver 測試穩定。等第二台 downstream 電腦／子計畫接入時，再完成真正的多 Receiver 同時驗證。若之後再出現週期性停頓，timing diagnostics 保留為後續工作。

## Repository Scope / Repository 範圍

This repository contains the routing/distribution layer and its reference receiver tools.

Motion tracking, pose estimation, and metric calculation remain in their respective source applications.

本 repository 包含資料傳送、分配與標準 Receiver 測試工具。

人體追蹤、pose estimation 與 metric calculation 仍然由各自的來源程式負責。

This separation makes it possible to use future sources such as Kinect or other tracking systems without coupling downstream projects to a particular sensor or pose-estimation implementation.

因此未來即使改成 Kinect 或其他 motion tracking 系統，只要輸出資料格式一致，下游子計畫仍然可以繼續使用同一套 Router / Receiver。

## License / 授權

This project is released under the MIT License. See [LICENSE](LICENSE).

本專案採用 MIT License。詳細內容請參考 [LICENSE](LICENSE)。

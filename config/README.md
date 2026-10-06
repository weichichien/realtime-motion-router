# Configuration / 設定

Version v0.4 keeps the v0.3 configuration model and adds real multi-target OSC transmission. Every item in `osc_outputs` is now active.

v0.4 延續 v0.3 的設定方式，並正式加入 multi-target OSC 傳送。`osc_outputs` 中的每一個項目現在都會實際收到資料。

## First setup / 第一次設定

Copy the example file:

先複製範例設定檔：

### Windows PowerShell

```powershell
Copy-Item config/config.example.json config/config.json
```

### macOS / Linux

```bash
cp config/config.example.json config/config.json
```

Then edit `config/config.json`.

接著修改 `config/config.json`。

`config/config.json` is ignored by Git, so each computer can keep its own local network settings without creating Git conflicts.

`config/config.json` 不會被 Git 追蹤，因此每台電腦可以保存自己的 IP / port 設定，不會因為不同電腦的網路設定造成 Git conflict。

## Current schema / 目前格式

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

### `motion_source`

Where motion data comes from.

動作分析資料從哪裡來。

- `websocket_url`: WebSocket endpoint provided by the motion-analysis application / 動作分析程式提供的 WebSocket 位址。

### `osc_outputs`

Where this computer sends OSC data.

這台電腦要把 OSC 資料送到哪裡。

- `name`: Human-readable label for the destination / 給人看的名稱。
- `destination_ip`: **IP address of the receiving computer** / **接收資料的對方電腦 IP**。
- `destination_port`: UDP port on that receiving computer / 對方接收 OSC 的 UDP port。

The name `destination_ip` is deliberate: it is not the Sender computer's own IP.

`destination_ip` 這個命名是刻意的：它不是 Sender 自己的 IP，而是「資料要送到的目的地 IP」。

`osc_outputs` is a list of active destinations. In v0.4, the Sender creates one OSC client per item and sends every available motion metric to every configured destination.

`osc_outputs` 是實際啟用的目的地清單。v0.4 Sender 會為每一個項目建立 OSC client，並把每一項可用的 motion metric 同時送到所有目的地。

### `osc_receiver`

How this computer listens for incoming OSC.

這台電腦如果要當 Receiver，要如何接收 OSC。

- `listen_interface: "all"`: listen on all local network interfaces / 在這台電腦所有本機網路介面接收。
- `listen_port`: local UDP port used by the Receiver / Receiver 使用的本機 UDP port。

For normal use, keep:

一般使用時請維持：

```json
"listen_interface": "all"
```

The program converts `"all"` internally to the socket bind address `0.0.0.0`. Users therefore do not need to configure or understand `0.0.0.0`.

程式會在內部把 `"all"` 轉換成 socket bind address `0.0.0.0`，一般使用者不需要直接設定或理解 `0.0.0.0`。

If there is a specific technical reason to bind only one local interface, `listen_interface` may instead contain **this Receiver computer's own local IP address**.

只有在確實需要綁定特定網路介面時，`listen_interface` 才需要改成 **Receiver 這台電腦自己的本機 IP**。

## Sender and Receiver use different sections / Sender 與 Receiver 讀不同區塊

The same repository can run either role:

同一個 repository 可以執行兩種角色：

- Sender reads `motion_source` + `osc_outputs`.
- Receiver reads `osc_receiver`.

- Sender 讀取 `motion_source` + `osc_outputs`。
- Receiver 讀取 `osc_receiver`。

This is why a computer running only the Sender still has an `osc_receiver` section in its local config, and vice versa. Unused sections are simply ignored by that program.

因此即使某台電腦目前只跑 Sender，它的 config 中仍會看到 `osc_receiver`；反過來亦然。該程式不使用的區塊會直接忽略。

## Port matching / Port 必須一致

The selected output's `destination_port` must match the receiving computer's `osc_receiver.listen_port`.

Sender 使用的 `destination_port` 必須與接收端電腦的 `osc_receiver.listen_port` 一致。

Example:

```text
Windows Sender                         Mac Receiver
192.168.50.10                         192.168.50.20

osc_outputs[0].destination_ip ------> 192.168.50.20
osc_outputs[0].destination_port ----> 9000
                                      osc_receiver.listen_interface = "all"
                                      osc_receiver.listen_port      = 9000
```

## Long-term configuration model / 正式版本的設定原則

This configuration mechanism is intended to remain in the final system:

這套 config 機制預計會延續到正式版本：

- IP addresses and ports stay outside Python source code.
- `config.example.json` is tracked by Git.
- Each machine keeps its own `config.json`, ignored by Git.
- Wi-Fi development and dedicated-Ethernet performance setups use the same configuration mechanism.
- `osc_outputs` is already structured for multiple destinations.
- Users should change network values in config, not modify Sender / Receiver source code.

- IP 與 port 不寫死在 Python source code。
- Git 中保留 `config.example.json`。
- 每台電腦自己的 `config.json` 留在本機，不進 Git。
- Wi-Fi 開發與 dedicated Ethernet 展演都使用同一套設定機制。
- `osc_outputs` 已經預留多個 destination 的結構。
- 使用者更換網路設定時只修改 config，不修改 Sender / Receiver 程式碼。

## Multi-target behavior / Multi-target 行為

In v0.4, every item in `osc_outputs` is active. To add another receiver, add another object to the list. No Python source-code change is required.

v0.4 中，`osc_outputs` 裡的每一個項目都會啟用。若要增加接收端，只要在 list 中新增一個 object，不需要修改 Python 程式。

Example:

```json
"osc_outputs": [
  {
    "name": "Mac receiver",
    "destination_ip": "192.168.50.20",
    "destination_port": 9000
  },
  {
    "name": "Visual computer",
    "destination_ip": "192.168.50.30",
    "destination_port": 9000
  },
  {
    "name": "AI computer",
    "destination_ip": "192.168.50.40",
    "destination_port": 9000
  }
]
```

Each receiver remains independent. One receiver does not relay data to the others.

每個 Receiver 都是獨立的，不需要由其中一台再轉送給其他電腦。

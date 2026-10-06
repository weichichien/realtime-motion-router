# Configuration / 設定

Version v0.3 moves network settings out of the Python source code.

v0.3 開始把網路設定移出 Python 程式碼，使用者不需要修改 Sender / Receiver 原始碼。

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

## Fields / 欄位

```json
{
  "source": {
    "websocket_url": "ws://127.0.0.1:8000/ws/metrics"
  },
  "sender": {
    "target_ip": "192.168.50.20",
    "target_port": 9000
  },
  "receiver": {
    "listen_host": "0.0.0.0",
    "listen_port": 9000
  }
}
```

- `source.websocket_url`: WebSocket source provided by the motion-analysis application / 動作分析程式提供的 WebSocket 位址。
- `sender.target_ip`: IP address of the receiving computer / 接收端電腦的 IP。
- `sender.target_port`: UDP port used by the Sender / Sender 要送到的 UDP port。
- `receiver.listen_host`: Local interface used by the Receiver. Keep `0.0.0.0` unless there is a specific reason to bind one interface / Receiver 的監聽介面，一般保持 `0.0.0.0`。
- `receiver.listen_port`: UDP port used by the Receiver / Receiver 監聽的 UDP port。

The Sender target port and Receiver listen port must match.

Sender 的 `target_port` 與 Receiver 的 `listen_port` 必須一致。

## Current limitation / 目前限制

v0.3 supports one OSC target. Multiple receivers will be added in a later version.

v0.3 先支援一個 OSC target；多接收端會在後續版本加入。

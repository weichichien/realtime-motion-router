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

## Long-term configuration model / 正式版本的設定原則

The v0.3 configuration mechanism is not a temporary testing workaround. It is the intended configuration model for the project.

v0.3 的 config 機制不是暫時測試用的 workaround，而是本專案預計沿用到正式版本的設定方式。

The stable parts are:

- Keep IP addresses and ports outside Python source code.
- Track `config.example.json` in Git.
- Keep each machine's `config.json` local and ignored by Git.
- Use the same mechanism for Wi-Fi development and dedicated-Ethernet performance setups.
- Let each subproject maintain its own local network values without changing shared source code.

會維持不變的原則：

- IP 與 port 不寫死在 Python source code。
- Git 中保留 `config.example.json`。
- 每台電腦自己的 `config.json` 留在本機，不進 Git。
- 開發時用 Wi-Fi、展演時用 dedicated Ethernet，都沿用相同設定機制。
- 各子計畫只修改自己的網路參數，不需要修改共用程式碼。

The only planned schema change is the Sender destination section. v0.3 has one target; a later multi-target version will represent destinations as a list. Users will still configure targets in `config/config.json`.

唯一預計會再調整的是 Sender 的目的地格式：v0.3 只有一個 target；之後 multi-target 版本會改成 target list。但使用者仍然只需要在 `config/config.json` 設定。

## Current limitation / 目前限制

v0.3 supports one OSC target. Multiple receivers will be added in a later version.

v0.3 先支援一個 OSC target；多接收端會在後續版本加入。

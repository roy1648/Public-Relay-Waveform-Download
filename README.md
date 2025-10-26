# Relay 波形下載工具

本工具提供系統化的保護電驛波形資料下載流程，核心以命令列腳本為主，並搭配 GUI 外殼方便現場操作。由於依賴多項 Windows 專用套件（如 `pywin32` 與 Win32 Tk 介面）以及 telnet 控制台事件處理，**僅支援於 Windows 平台執行**。

- **命令列核心**：`01-src/SEL relay download core.py` 內含完整事件擷取與檔案落地流程，並與通訊模組協作處理 ACC / PASS / HIS 及 SER / CEV 下載。
- **Telnet 通訊模組**：`01-src/module.py` 的 `TelnetClient` 類別負責與 SEL 裝置建立連線、解析 CHI 清單、擴展事件 ID，以及檔名清理與儲存路徑維護。
- **GUI 外殼**：`01-src/SEL relay download.py` 與 `01-src/Sel_GUI.py` 封裝 Tk 介面，提供事件瀏覽、目錄選取、狀態顯示與錯誤提示的互動式流程。

## 系統需求 / Installation

本專案以 Conda 建置 Windows 執行環境，依賴清單請參考 `02-env/sel_osc_down.yml`：

```yaml
name: sel_osc_down
channels:
  - defaults
dependencies:
  - python=3.10.13
  - tk=8.6.14
  - pywin32=306
  - telnetlib3=2.0.4
  - pandas=2.2.2
  - wxpython=4.2.2
  - tqdm=4.66.4
  - ...（其餘依賴請見 yml 完整內容）
```

請於 **Windows 命令列** 執行以下步驟建置環境：

```powershell
conda env create -f 02-env/sel_osc_down.yml
conda activate sel_osc_down
```

若需更新依賴，可使用 `conda env update --file 02-env/sel_osc_down.yml --prune` 重新同步。

## 使用方式

### 命令列執行

1. 啟用 Conda 環境後執行核心腳本：
   ```powershell
   python "01-src/SEL relay download core.py" -i 192.168.1.10 -p 23 -s all -c 60 -eid 1-5,7 -d "D:\\SEL_Data" -log INFO
   ```
2. 參數說明：
   - `-i/--ip`：SEL 繼電器位址，若未提供會於執行時互動式輸入。
   - `-p/--port`：Telnet 連線埠（預設 23）。
   - `-s/--samples`：波形取樣（`4` 或 `all`）。
   - `-c/--cyles`：SER 下載的事件長度（循環數）。
   - `-eid/--event_id`：事件 ID（支援逗號分隔與區間語法，如 `1,2,5-8`）。
   - `-d/--dir`：波形與文字檔輸出路徑，未指定時會開啟資料夾選擇視窗。
   - `-log`：記錄檔等級（`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`）。
3. 輸出檔案：
   - `his+ser_*.txt`：儲存 ACC、PASS、HIS 與 SER 查詢紀錄。
   - `*.cev`：對應事件的波形檔，命名包含裝置 ID、事件時間與 Trip 事件描述。
   - 所有檔案皆寫入指定資料夾，日誌則存放於工作目錄下的隱藏資料夾 `SEL download log`（如 GUI 則為 `SEL download log\UI log`）。

### GUI 操作

1. 於啟用環境後執行 `01-src/SEL relay download.py`，由 `Sel_GUI.py` 初始化 Tk 視窗。
2. 在 GUI 中填入繼電器 IP、Port、事件長度與取樣設定，或點選事件 ID 清單進行展開與篩選。
3. 使用「選擇資料夾」按鈕呼叫 `tkinter.filedialog.askdirectory` 選擇輸出路徑，系統會自動正規化並驗證目錄可寫入。
4. 按下「開始下載」後，介面會驅動命令列核心流程並即時顯示 ACC / PASS / HIS 查詢、SER 抓取與 CEV 波形下載進度。
5. 執行完畢後，輸出目錄會產生 `his+ser_*.txt` 與 `*.cev`；日誌檔案集中存放於隱藏資料夾 `SEL download log`。

## 事件流程說明

1. **ACC / PASS / HIS 擷取**：核心模組依序發送 ACC、PASS、HIS 命令收集事件紀錄並寫入 `his+ser` 回應清單。
2. **CHI 篩選事件**：呼叫 `TelnetClient.send_command("CHI")` 再由 `parse_chi_response` 過濾事件，GUI 亦會根據結果展開事件 ID 樹狀結構。
3. **SER 下載**：以有效事件日期批次請求 SER，若回應包含 `invalid` 或 `No SER Data` 會改以 `SER 50` 回補歷史紀錄。
4. **CEV 波形擷取**：對每個事件呼叫 `download_waveform` 產出波形內容，檔名含事件時間與 Trip 描述。
5. **Tk 目錄選取**：透過 `select_folder` 將使用者在 GUI 或 CLI 指定的路徑正規化，並確保目錄存在。
6. **錯誤與取消**：若使用者中斷（例如 GUI 關閉或 CLI 輸入 `exit`），會產生 `his+ser_cancel.txt` 作為取消標記並寫入日誌，方便後續除錯。

## Debug / Logging

- **GUI 快捷鍵**：在 GUI 視窗按下 `Ctrl+Shift+Alt+D`，並輸入密碼可開啟隱藏除錯面板以檢視 Telnet 命令與背景狀態。
- **CLI 記錄等級**：`-log` 參數可調整記錄層級；未指定時僅啟用錯誤記錄以避免無效輸出。
- **隱藏資料夾機制**：`module.get_or_create_sel_download_log_folder()` 會在工作目錄建立 `SEL download log`，並透過 Win32 API 設為隱藏，以集中管理 CLI 與 GUI 產生的記錄檔。

## 授權

本專案採用 [MIT License](LICENSE)。如需進一步協助，可連絡專案開發者。

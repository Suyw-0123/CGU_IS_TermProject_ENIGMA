
包含兩個基於 Python 的 Enigma 加密機模擬器，並結合 OpenAI GPT 進行暴力破解分析。適合學習密碼學、Enigma 機制與現代 AI 輔助解密。

## 檔案說明

- enigma_gpt_rotor_only_v3.2.py：  
  單轉子版本，支援暴力破解 26 種轉子初始位置，並可將所有結果交給 GPT 分析最可能的明文。

- enigma_gpt_RotorAndPlugboard_v6.2.py：  
  進階版，支援轉子與 Plugboard（插線板）設定，暴力破解時會嘗試多組 Plugboard 配對，總共可能性約2000000種，並可將候選結果交給 GPT 進行語意分析。

## 安裝需求

請先安裝以下 Python 套件：

```sh
pip install openai tk tk-tools scrolledtext
```

## 使用方式

1. **設定 OpenAI API 金鑰**  
   - 在 enigma_gpt_rotor_only_v3.2.py 第 120 行  
   - 在 enigma_gpt_RotorAndPlugboard_v6.2.py 第 439 行  
   將 `"your_api_key_here"` 替換為你的 OpenAI API 金鑰。

2. **執行程式**  
   於終端機輸入：
   ```sh
   python enigma_gpt_rotor_only_v3.2.py
   ```
   或
   ```sh
   python enigma_gpt_RotorAndPlugboard_v6.2.py
   ```

3. **操作說明**  
   - 輸入轉子、反射器、Plugboard 設定與訊息。
   - 點擊「加密 / 解密」可進行加解密。
   - 點擊「暴力破解」可嘗試所有可能組合並顯示結果。
   - 點擊「GPT 分析」可將暴力破解結果交給 GPT，協助判斷最可能的明文。
   - 使用 enigma_gpt_rotor_only 時請將Plugboard位置留空，因為這個模擬只考慮一個轉子裡26個初始位置
   - 使用enigma_gpt_RotorAndPlugboard 時請將Plugboard位置填入兩組組合，例如: AU CG

## 注意事項

- OpenAI GPT 服務需付費，請妥善保管你的 API 金鑰。
- 進階版暴力破解組合數量龐大，可能運算較久，請耐心等候。

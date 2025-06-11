# 請在運行此代碼前確保已安裝以下庫:
# pip install openai tkinter
# pip install tk scrolledtext

# 注意: 這個代碼需要一個有效的OpenAI API密鑰才能運行GPT分析功能。
# 這是一個Enigma機模擬器，包含暴力破解功能和GPT分析。
# 這個代碼模擬了Enigma機的加密過程，並提供了一個GUI界面來進行加密、暴力破解和GPT分析。


#########################################
# 請在 439 行處替換為您的OpenAI API密鑰。 #
#########################################



import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import string
import openai
import itertools
import threading
import time
from collections import Counter

class Rotor:
    def __init__(self, wiring, position=0):
        self.wiring = wiring
        self.position = position

    def step(self):
        self.position = (self.position + 1) % 26

    def encode_forward(self, c):
        idx = (ord(c) - ord('A') + self.position) % 26
        substituted = self.wiring[idx]
        return chr((ord(substituted) - ord('A') - self.position) % 26 + ord('A'))

    def encode_backward(self, c):
        shifted_c = chr((ord(c) - ord('A') + self.position) % 26 + ord('A'))
        idx = self.wiring.index(shifted_c)
        return chr((idx - self.position) % 26 + ord('A'))

    def reset(self, position=0):
        self.position = position

class Reflector:
    def __init__(self, wiring):
        self.wiring = wiring

    def reflect(self, c):
        return self.wiring[ord(c) - ord('A')]

class Plugboard:
    def __init__(self, swaps):
        self.mapping = {c: c for c in string.ascii_uppercase}
        for pair in swaps:
            if len(pair) == 2:
                a, b = pair[0], pair[1]
                self.mapping[a] = b
                self.mapping[b] = a

    def swap(self, c):
        return self.mapping.get(c, c)

class EnigmaMachine:
    def __init__(self, rotor, reflector, plugboard):
        self.rotor = rotor
        self.reflector = reflector
        self.plugboard = plugboard

    def encrypt(self, text):
        result = ""
        for c in text.upper():
            if c not in string.ascii_uppercase:
                result += c
                continue
            self.rotor.step()
            c = self.plugboard.swap(c)
            c = self.rotor.encode_forward(c)
            c = self.reflector.reflect(c)
            c = self.rotor.encode_backward(c)
            c = self.plugboard.swap(c)
            result += c
        return result

def run_enigma_gui():
    root = tk.Tk()
    root.title("Enigma 模擬器 (進階暴力破解 + GPT分析)")
    root.geometry("800x700")

    # 設置框架
    settings_frame = tk.LabelFrame(root, text="Enigma 設定", padx=10, pady=10)
    settings_frame.pack(fill="x", padx=10, pady=5)
    
    input_frame = tk.LabelFrame(root, text="輸入/輸出", padx=10, pady=10)
    input_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # 設定區域
    tk.Label(settings_frame, text="選擇轉子:").grid(row=0, column=0, sticky="e")
    rotor_combo = ttk.Combobox(settings_frame, values=["I", "II", "III", "IV", "V"], width=5)
    rotor_combo.grid(row=0, column=1, sticky="w")
    rotor_combo.set("I")

    tk.Label(settings_frame, text="初始轉子位置 (0~25):").grid(row=0, column=2, sticky="e")
    rotor_pos_entry = tk.Entry(settings_frame, width=5)
    rotor_pos_entry.grid(row=0, column=3, sticky="w")
    rotor_pos_entry.insert(0, "0")

    tk.Label(settings_frame, text="Reflector wiring:").grid(row=1, column=0, sticky="e")
    reflector_entry = tk.Entry(settings_frame, width=30)
    reflector_entry.grid(row=1, column=1, columnspan=3, sticky="we")
    reflector_entry.insert(0, "YRUHQSLDPXNGOKMIEBFZCWVJAT")

    tk.Label(settings_frame, text="Plugboard 對換 (請只輸入兩組，如 AG BT):").grid(row=2, column=0, sticky="e")
    plug_entry = tk.Entry(settings_frame, width=30)
    plug_entry.grid(row=2, column=1, columnspan=3, sticky="we")
    
    # 輸入/輸出區域
    tk.Label(input_frame, text="輸入訊息:").grid(row=0, column=0, sticky="w")
    input_entry = tk.Entry(input_frame, width=50)
    input_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
    
    encrypt_btn = tk.Button(input_frame, text="加密 / 解密")
    encrypt_btn.grid(row=0, column=2, padx=5)
    
    output_label = tk.Label(input_frame, text="輸出加密結果:", font=("Courier", 12))
    output_label.grid(row=1, columnspan=3, pady=5, sticky="w")
    
    # 暴力破解區域
    brute_frame = tk.LabelFrame(root, text="暴力破解", padx=10, pady=10)
    brute_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(brute_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill="x", pady=5)
    
    status_label = tk.Label(brute_frame, text="就緒")
    status_label.pack(anchor="w")
    
    tk.Label(brute_frame, text="候選結果 (本地過濾後):").pack(anchor="w")
    candidate_text = scrolledtext.ScrolledText(brute_frame, height=8)
    candidate_text.pack(fill="both", expand=True)
    candidate_text.config(state=tk.DISABLED)
    
    # 控制按鈕
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    brute_btn = tk.Button(btn_frame, text="🔍 開始暴力破解")
    brute_btn.pack(side="left", padx=5)
    
    gpt_btn = tk.Button(btn_frame, text="🧠 GPT 分析候選結果", state=tk.DISABLED)
    gpt_btn.pack(side="left", padx=5)
    
    # GPT分析結果區域
    gpt_frame = tk.LabelFrame(root, text="GPT 分析結果", padx=10, pady=10)
    gpt_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    gpt_text = scrolledtext.ScrolledText(gpt_frame, height=6)
    gpt_text.pack(fill="both", expand=True)
    gpt_text.config(state=tk.DISABLED)
    
    # 常見英文單詞列表
    COMMON_WORDS = [
        "THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I",
        "IT", "FOR", "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT",
        "THIS", "BUT", "HIS", "BY", "FROM", "THEY", "WE", "SAY", "HER", "SHE",
        "OR", "AN", "WILL", "MY", "ONE", "ALL", "WOULD", "THERE", "THEIR", "WHAT",
        "SO", "UP", "OUT", "IF", "ABOUT", "WHO", "GET", "WHICH", "GO", "ME",
        "WHEN", "MAKE", "CAN", "LIKE", "TIME", "NO", "JUST", "HIM", "KNOW", "TAKE",
        "PEOPLE", "INTO", "YEAR", "YOUR", "GOOD", "SOME", "COULD", "THEM", "SEE", "OTHER",
        "THAN", "THEN", "NOW", "LOOK", "ONLY", "COME", "ITS", "OVER", "THINK", "ALSO",
        "BACK", "AFTER", "USE", "TWO", "HOW", "OUR", "WORK", "FIRST", "WELL", "WAY",
        "EVEN", "NEW", "WANT", "BECAUSE", "ANY", "THESE", "GIVE", "DAY", "MOST", "US"
    ]
    
    # 二戰常見軍事術語
    MILITARY_TERMS = [
        "ATTACK", "DEFEND", "RETREAT", "ADVANCE", "POSITION", "ENEMY", "FORCES", 
        "BATTALION", "DIVISION", "COMPANY", "SQUAD", "RECON", "INTEL", "ORDERS",
        "MISSION", "OBJECTIVE", "TARGET", "WEAPONS", "AMMO", "SUPPLY", "LOGISTICS",
        "CASUALTIES", "WOUNDED", "KIA", "MIA", "POW", "HQ", "COMMAND", "OFFICER",
        "SOLDIER", "TROOPS", "FRONT", "FLANK", "REINFORCE", "AMBUSH", "SURRENDER",
        "CAPTURE", "SECURE", "HOLD", "REPORT", "STATUS", "IMMEDIATE", "URGENT",
        "CONFIRM", "DENY", "AWAIT", "PROCEED", "CANCEL", "ABORT", "SUCCESS", "FAILURE"
    ]
    
    # 初始化變量
    candidates = []
    is_brute_force_running = False
    
    def get_enigma_settings():
        """獲取當前Enigma設定"""
        rotor_map = {
            "I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
            "II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",
            "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
            "IV":  "ESOVPZJAYQUIRHXLNFTGKDCMWB",
            "V":   "VZBRGITYUPSDNHLXAWMJQOFECK"
        }
        
        rotor_wiring = rotor_map.get(rotor_combo.get(), rotor_map["I"])
        
        try:
            rotor_pos = int(rotor_pos_entry.get())
            if not (0 <= rotor_pos <= 25): 
                raise ValueError()
        except:
            messagebox.showerror("錯誤", "轉子位置必須是 0~25 的整數")
            return None
        
        reflector_wiring = reflector_entry.get().strip().upper()
        if len(reflector_wiring) != 26:
            messagebox.showerror("錯誤", "Reflector 必須是 26 個大寫字母")
            return None
        
        plug_pairs = plug_entry.get().strip().upper().split()
        
        return {
            "rotor_wiring": rotor_wiring,
            "rotor_pos": rotor_pos,
            "reflector_wiring": reflector_wiring,
            "plug_pairs": plug_pairs
        }
    
    def on_encrypt():
        """加密/解密按鈕處理"""
        settings = get_enigma_settings()
        if settings is None:
            return
            
        rotor = Rotor(settings["rotor_wiring"])
        reflector = Reflector(settings["reflector_wiring"])
        plugboard = Plugboard(settings["plug_pairs"])
        enigma = EnigmaMachine(rotor, reflector, plugboard)
        
        rotor.reset(settings["rotor_pos"])
        plaintext = input_entry.get().upper()
        ciphertext = enigma.encrypt(plaintext)
        output_label.config(text="🔐 輸出加密結果: " + ciphertext)
    
    def generate_plugboard_pairs(n_pairs=2):
        """生成所有可能的n對接線板配對"""
        alphabet = string.ascii_uppercase
        pairs = []
        
        # 第一步: 選擇2n個字母
        for letters in itertools.combinations(alphabet, 2 * n_pairs):
            letters = list(letters)
            # 第二步: 生成所有配對方式
            for pair_perm in itertools.combinations(letters, 2):
                remaining = [c for c in letters if c not in pair_perm]
                if remaining:
                    for second_pair in itertools.combinations(remaining, 2):
                        pairs.append([pair_perm, second_pair])
        return pairs
    
    def is_english_like(text, threshold=2):
        """檢查文本是否像英文"""
        # 只保留字母
        clean_text = ''.join(filter(str.isalpha, text)).upper()
        if len(clean_text) < 5:  # 太短的文本無法判斷
            return False
        
        # 檢查常見英文單詞
        word_count = 0
        for word in COMMON_WORDS + MILITARY_TERMS:
            if word in clean_text:
                word_count += 1
                if word_count >= threshold:
                    return True
                    
        # 檢查字母頻率 (英文中最常見的字母: E, T, A, O, I, N)
        letter_freq = Counter(clean_text)
        common_letters = ['E', 'T', 'A', 'O', 'I', 'N']
        common_count = sum(letter_freq.get(letter, 0) for letter in common_letters)
        common_ratio = common_count / len(clean_text)
        
        # 如果常見字母比例高於40%，則認為像英文
        return common_ratio > 0.4
    
    def brute_force_worker(ciphertext, rotor_wiring, reflector_wiring, plugboard_pairs_list):
        """在後台執行暴力破解"""
        nonlocal candidates, is_brute_force_running
        
        candidates = []
        total = len(plugboard_pairs_list) * 26
        processed = 0
        
        for plug_pairs in plugboard_pairs_list:
            if not is_brute_force_running:  # 如果用戶取消了
                break
                
            for pos in range(26):
                # 更新進度
                processed += 1
                progress = (processed / total) * 100
                root.after(0, lambda p=progress: progress_var.set(p))
                root.after(0, lambda: status_label.config(
                    text=f"處理中: {processed}/{total} ({progress:.1f}%)"
                ))
                
                # 創建Enigma實例
                rotor = Rotor(rotor_wiring, pos)
                reflector = Reflector(reflector_wiring)
                plugboard = Plugboard(plug_pairs)
                enigma = EnigmaMachine(rotor, reflector, plugboard)
                
                # 解密
                decrypted = enigma.encrypt(ciphertext)
                
                # 本地過濾
                if is_english_like(decrypted):
                    candidates.append({
                        "position": pos,
                        "plugboard": plug_pairs,
                        "text": decrypted
                    })
                    # 更新候選列表
                    root.after(0, update_candidate_display)
        
        # 完成後更新狀態
        root.after(0, lambda: status_label.config(
            text=f"完成! 找到 {len(candidates)} 個候選結果"
        ))
        root.after(0, lambda: brute_btn.config(text="🔍 開始暴力破解", state=tk.NORMAL))
        root.after(0, lambda: gpt_btn.config(state=tk.NORMAL if candidates else tk.DISABLED))
        is_brute_force_running = False
    
    def update_candidate_display():
        """更新候選結果顯示"""
        candidate_text.config(state=tk.NORMAL)
        candidate_text.delete(1.0, tk.END)
        
        for i, candidate in enumerate(candidates, 1):
            plug_str = " ".join(f"{a}{b}" for a, b in candidate["plugboard"])
            candidate_text.insert(tk.END, 
                f"{i}. 位置: {candidate['position']}, Plugboard: {plug_str}\n"
                f"   結果: {candidate['text']}\n\n"
            )
        
        candidate_text.config(state=tk.DISABLED)
    
    def start_brute_force():
        """啟動暴力破解"""
        nonlocal is_brute_force_running
        
        settings = get_enigma_settings()
        if settings is None:
            return
            
        ciphertext = input_entry.get().upper()
        if not ciphertext:
            messagebox.showerror("錯誤", "請輸入要破解的密文")
            return
        
        # 生成所有可能的接線板配對
        plugboard_pairs_list = generate_plugboard_pairs(2)
        total_combinations = len(plugboard_pairs_list) * 26
        
        # 顯示警告（因為組合數量很大）
        if total_combinations > 10000:
            proceed = messagebox.askyesno(
                "警告", 
                f"將要測試 {total_combinations} 種組合，可能需要較長時間。\n確定要繼續嗎？"
            )
            if not proceed:
                return
        
        # 重置UI狀態
        is_brute_force_running = True
        candidates.clear()
        candidate_text.config(state=tk.NORMAL)
        candidate_text.delete(1.0, tk.END)
        candidate_text.config(state=tk.DISABLED)
        gpt_btn.config(state=tk.DISABLED)
        brute_btn.config(text="⏹ 停止破解", state=tk.NORMAL)
        progress_var.set(0)
        status_label.config(text="準備中...")
        
        # 在後台線程中執行暴力破解
        thread = threading.Thread(
            target=brute_force_worker,
            args=(
                ciphertext,
                settings["rotor_wiring"],
                settings["reflector_wiring"],
                plugboard_pairs_list
            ),
            daemon=True
        )
        thread.start()
    
    def stop_brute_force():
        """停止暴力破解"""
        nonlocal is_brute_force_running
        is_brute_force_running = False
        status_label.config(text="已停止")
        brute_btn.config(text="🔍 開始暴力破解", state=tk.NORMAL)
    
    def toggle_brute_force():
        """切換暴力破解狀態"""
        if is_brute_force_running:
            stop_brute_force()
        else:
            start_brute_force()
    
    def ask_gpt_guess():
        """將候選結果發送給GPT分析"""
        if not candidates:
            messagebox.showwarning("警告", "沒有候選結果可供分析")
            return
        
        settings = get_enigma_settings()
        if settings is None:
            return
            
        # 準備候選結果字符串
        candidates_str = ""
        for i, candidate in enumerate(candidates[:10], 1):  # 只發送前10個候選
            plug_str = " ".join(f"{a}{b}" for a, b in candidate["plugboard"])
            candidates_str += (
                f"候選 {i}:\n"
                f"- 轉子位置: {candidate['position']}\n"
                f"- Plugboard: {plug_str}\n"
                f"- 解密文本: {candidate['text']}\n\n"
            )
        
        # 禁用按鈕防止重複點擊
        gpt_btn.config(state=tk.DISABLED)
        gpt_text.config(state=tk.NORMAL)
        gpt_text.delete(1.0, tk.END)
        gpt_text.insert(tk.END, "正在分析，請稍候...")
        gpt_text.config(state=tk.DISABLED)
        root.update()
        
        try:
            # 請替換為您自己的API密鑰
            client = openai.OpenAI(api_key="your_api_key_here")

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是二戰時期的密碼分析專家，專門破解Enigma加密訊息。"
                            "以下是一些暴力破解的候選結果，請根據語言特徵、歷史背景和軍事術語分析"
                            "哪個結果最有可能是正確的明文。"
                            "請按以下格式回答：\n"
                            "1. 最可能的結果編號\n"
                            "2. 理由（包含語言特徵分析）\n"
                            "3. 可能的上下文含義"
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Enigma設定：\n"
                            f"- 轉子接線: {settings['rotor_wiring']}\n"
                            f"- Reflector: {settings['reflector_wiring']}\n"
                            f"- 原始密文: {input_entry.get().upper()}\n\n"
                            f"候選解密結果：\n{candidates_str}\n\n"
                            f"請分析哪個結果最有可能是正確的明文，並說明理由。"
                        )
                    }
                ]
            )
            
            # 顯示GPT回應
            analysis = response.choices[0].message.content
            gpt_text.config(state=tk.NORMAL)
            gpt_text.delete(1.0, tk.END)
            gpt_text.insert(tk.END, analysis)
            gpt_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"GPT分析失敗: {str(e)}")
        finally:
            gpt_btn.config(state=tk.NORMAL)
    
    # 綁定事件處理
    encrypt_btn.config(command=on_encrypt)
    brute_btn.config(command=toggle_brute_force)
    gpt_btn.config(command=ask_gpt_guess)
    
    root.mainloop()

if __name__ == "__main__":
    run_enigma_gui()
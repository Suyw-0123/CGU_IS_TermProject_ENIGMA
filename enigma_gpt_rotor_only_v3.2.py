#使用前請先安裝以下套件：
# pip install openai
# pip install tk
# pip install tk-tools

#######################################
# 請在 120 行處填入你的 OpenAI API 金鑰 #
#######################################

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, scrolledtext
import string
import openai
import os

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
    root.title("Enigma 模擬器 (單轉子 + GPT 解密分析)")

    tk.Label(root, text="選擇轉子:").grid(row=0, column=0)
    rotor_combo = ttk.Combobox(root, values=["I", "II", "III", "IV", "V"])
    rotor_combo.grid(row=0, column=1)
    rotor_combo.set("I")

    tk.Label(root, text="初始轉子位置 (0~25):").grid(row=1, column=0)
    rotor_pos_entry = tk.Entry(root)
    rotor_pos_entry.grid(row=1, column=1)
    rotor_pos_entry.insert(0, "0")

    tk.Label(root, text="Reflector wiring:").grid(row=2, column=0)
    reflector_entry = tk.Entry(root, width=30)
    reflector_entry.grid(row=2, column=1)
    reflector_entry.insert(0, "YRUHQSLDPXNGOKMIEBFZCWVJAT")

    tk.Label(root, text="Plugboard 對換 (請將這裡留空):").grid(row=3, column=0)
    plug_entry = tk.Entry(root)
    plug_entry.grid(row=3, column=1)

    tk.Label(root, text="輸入訊息:").grid(row=4, column=0)
    input_entry = tk.Entry(root, width=40)
    input_entry.grid(row=4, column=1)

    output_label = tk.Label(root, text="輸出加密結果:", font=("Courier", 12))
    output_label.grid(row=6, columnspan=2, pady=10)
    
    # 新增暴力破解結果的顯示區域
    brute_frame = tk.Frame(root)
    brute_frame.grid(row=7, columnspan=2, padx=10, pady=5, sticky="nsew")
    
    tk.Label(brute_frame, text="暴力破解結果 (26種位置):", font=("Arial", 10)).pack(anchor="w")
    brute_text = scrolledtext.ScrolledText(brute_frame, width=50, height=8)
    brute_text.pack(fill="both", expand=True)
    brute_text.config(state=tk.DISABLED)


    # 新增：將多個暴力破解結果交給GPT分析
    def ask_gpt_brute_force_analysis(results, wiring, reflector_wiring, plugboard_pairs):
        try:
            client = openai.OpenAI(api_key="your_api_key_here")  # 請填入你的 OpenAI API 金鑰
            plug_text = ' '.join(plugboard_pairs) if plugboard_pairs else "（無）"
            brute_texts = "\n".join([f"位置 {pos:2d}: {text}" for pos, text in results])
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是專業的密碼分析師，熟悉歷史上的 Enigma 加密機制。"
                        "你已知 Enigma 的加密流程如下："
                        "- 明文經過 plugboard（先假設加密者並沒有使用plugboard）"
                        "- 經過一個轉子（wiring 已知，初始位置未知）"
                        "- 經過反射器（wiring 已知）"
                        "- 再經過一個轉子（逆向）"
                        "- 最後再經過 plugboard（假設加密者並沒有使用plugboard）"
                        "請根據使用者提供的設定與密文，嘗試推論明文的可能內容與用途。"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"我使用了以下 Enigma 設定進行暴力破解：\n"
                        f"1. Rotor wiring: {wiring}\n"
                        f"2. Reflector wiring: {reflector_wiring}\n"
                        f"3. Plugboard 對換: {plug_text}\n"
                        f"以下是26種初始位置下的解密結果：\n{brute_texts}\n"
                        f"這些結果中，哪一個最有可能是原文？請直接給出你認為最可能的明文與對應的位置，並簡要說明理由。"
                    )
                }
            ]
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 發生錯誤：{e}"

    def on_encrypt():
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
            if not (0 <= rotor_pos <= 25): raise ValueError()
        except:
            messagebox.showerror("錯誤", "轉子位置必須是 0~25 的整數")
            return

        reflector_wiring = reflector_entry.get().strip().upper()
        if len(reflector_wiring) != 26:
            messagebox.showerror("錯誤", "Reflector 必須是 26 個大寫字母")
            return

        plug_pairs = plug_entry.get().strip().upper().split()
        rotor = Rotor(rotor_wiring)
        reflector = Reflector(reflector_wiring)
        plugboard = Plugboard(plug_pairs)
        enigma = EnigmaMachine(rotor, reflector, plugboard)

        rotor.reset(rotor_pos)
        plaintext = input_entry.get().upper()
        ciphertext = enigma.encrypt(plaintext)
        output_label.config(text="🔐 輸出加密結果: " + ciphertext)

        # 執行暴力破解
        brute_force_decrypt(ciphertext, rotor_wiring, reflector_wiring, plug_pairs)

    def brute_force_decrypt(ciphertext, rotor_wiring, reflector_wiring, plug_pairs):
        """Brute force decrypt the ciphertext by trying all 26 rotor positions."""
        brute_text.config(state=tk.NORMAL)
        brute_text.delete(1.0, tk.END)
        
        results = []
        for pos in range(26):
            rotor = Rotor(rotor_wiring, pos)
            reflector = Reflector(reflector_wiring)
            plugboard = Plugboard(plug_pairs)
            enigma = EnigmaMachine(rotor, reflector, plugboard)
            
            # 注意：這裡使用相同的加密函數來解密
            decrypted = enigma.encrypt(ciphertext)
            results.append((pos, decrypted))
            
            # 在文本框中顯示結果
            brute_text.insert(tk.END, f"位置 {pos:2d}: {decrypted}\n")
        
        brute_text.config(state=tk.DISABLED)
        
        # 自動分析最可能的結果
        analyze_brute_force_results(ciphertext, results, rotor_wiring, reflector_wiring, plug_pairs)

        # 新增：將結果暫存到 root 以便按鈕調用
        root.brute_results = results
        root.brute_wiring = rotor_wiring
        root.brute_reflector = reflector_wiring
        root.brute_plug = plug_pairs

    def analyze_brute_force_results(ciphertext, results, rotor_wiring, reflector_wiring, plug_pairs):
        """分析暴力破解結果，找出最可能的明文"""
        english_words = ["THE", "AND", "YOU", "THAT", "HAVE", "FOR", "WITH", "THIS", "ARE", "FROM"]
        
        best_score = 0
        best_position = 0
        best_text = ""
        
        # 計算每個結果的分數（基於常見英文單詞出現次數）
        for pos, text in results:
            score = 0
            clean_text = ''.join(filter(str.isalpha, text)).upper()
            
            for word in english_words:
                if word in clean_text:
                    score += 1
            
            # 偏好較短的單詞和常見的問候語
            if "HELLO" in clean_text:
                score += 3
            if "HI " in clean_text:
                score += 2
            if "HOW" in clean_text and "YOU" in clean_text:
                score += 3
                
            if score > best_score:
                best_score = score
                best_position = pos
                best_text = text
        
        # 顯示最佳結果
        if best_score > 0:
            brute_text.config(state=tk.NORMAL)
            brute_text.insert(tk.END, f"\n 最可能結果 (位置 {best_position}): {best_text}\n")
            brute_text.config(state=tk.DISABLED)
            
            # 自動使用最佳結果進行GPT分析
            rotor_pos_entry.delete(0, tk.END)
            rotor_pos_entry.insert(0, str(best_position))
            input_entry.delete(0, tk.END)
            input_entry.insert(0, best_text)
        else:
            messagebox.showinfo("分析結果", "無法確定最可能的解密結果，請手動檢查")

    # 新增暴力破解按鈕
    tk.Button(root, text="加密 / 解密", command=on_encrypt).grid(row=5, columnspan=2, pady=5)
    tk.Button(root, text="🔍 暴力破解26種位置", 
             command=lambda: brute_force_decrypt(
                 input_entry.get().upper(),
                 rotor_map.get(rotor_combo.get(), rotor_map["I"]),
                 reflector_entry.get().strip().upper(),
                 plug_entry.get().strip().upper().split())
             ).grid(row=9, columnspan=2, pady=5)

    # 新增：GPT 分析暴力破解結果按鈕
    def on_gpt_brute_analysis():
        if not hasattr(root, "brute_results"):
            messagebox.showinfo("提示", "請先執行暴力破解")
            return
        analysis = ask_gpt_brute_force_analysis(
            root.brute_results,
            root.brute_wiring,
            root.brute_reflector,
            root.brute_plug
        )
        messagebox.showinfo("🧠 GPT 分析暴力破解結果", analysis)

    tk.Button(root, text="🧠 GPT 分析暴力破解結果", command=on_gpt_brute_analysis).grid(row=10, columnspan=2, pady=5)

    root.mainloop()

run_enigma_gui()
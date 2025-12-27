import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import random
import threading
import shutil
import yt_dlp
import re
import whisper
import datetime

# Konfigurasi Tema Tampilan
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class UltimateClipper(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gemini Clipper: Dual Mode (Random & Custom)")
        self.geometry("700x820")
        self.resizable(False, False)

        self.video_path = ""
        self.output_folder = ""
        self.model = None 

        # --- DATABASE RESOLUSI ---
        self.res_map = {
            "360p (Data Saver)": 360,
            "480p (SD)": 480,
            "720p (HD - Standard)": 720,
            "1080p (Full HD)": 1080,
            "1440p (2K QHD)": 1440,
            "2160p (4K UHD)": 2160
        }

        # --- JUDUL ---
        self.label_title = ctk.CTkLabel(self, text="AI Video Clipper & Subtitle Generator", font=("Roboto", 22, "bold"))
        self.label_title.pack(pady=(20, 10))

        # --- TAB MENU UTAMA ---
        self.tab_view = ctk.CTkTabview(self, width=650, height=400)
        self.tab_view.pack(pady=10)
        
        self.tab_yt = self.tab_view.add("YouTube Downloader")
        self.tab_local = self.tab_view.add("Local File (N/A)")

        # --- KONTEN TAB YOUTUBE ---
        
        # 1. Input URL
        self.entry_yt_url = ctk.CTkEntry(self.tab_yt, placeholder_text="Paste Link YouTube Disini...", width=500, height=40)
        self.entry_yt_url.pack(pady=(20, 10))

        # 2. Pilihan Resolusi
        self.frame_res = ctk.CTkFrame(self.tab_yt, fg_color="transparent")
        self.frame_res.pack(pady=5)
        self.label_res = ctk.CTkLabel(self.frame_res, text="Kualitas Video:")
        self.label_res.pack(side="left", padx=10)
        self.combo_res = ctk.CTkComboBox(self.frame_res, values=list(self.res_map.keys()), width=200)
        self.combo_res.set("720p (HD - Standard)")
        self.combo_res.pack(side="left")

        # 3. SWITCH MODE (PENTING)
        self.label_mode = ctk.CTkLabel(self.tab_yt, text="Pilih Mode Potong:", font=("Arial", 14, "bold"), text_color="#4CB5F5")
        self.label_mode.pack(pady=(20, 5))

        self.mode_var = ctk.StringVar(value="Random")
        # Ini tombol untuk ganti mode
        self.mode_switch = ctk.CTkSegmentedButton(self.tab_yt, values=["Mode Random (Otomatis)", "Mode Custom (Manual)"], 
                                                  command=self.toggle_ui_mode, variable=self.mode_var, width=400, height=35)
        self.mode_switch.pack(pady=5)

        # --- A. CONTAINER UNTUK MODE RANDOM ---
        self.frame_random = ctk.CTkFrame(self.tab_yt, fg_color="#2B2B2B", border_color="gray", border_width=1)
        # Akan di-pack secara default nanti
        
        self.lbl_rand_info = ctk.CTkLabel(self.frame_random, text="Pengaturan Acak (AI akan memilih momen random)", text_color="gray")
        self.lbl_rand_info.grid(row=0, column=0, columnspan=6, pady=(10,5))

        self.lbl_cnt = ctk.CTkLabel(self.frame_random, text="Jumlah Klip:")
        self.lbl_cnt.grid(row=1, column=0, padx=10, pady=10)
        self.entry_count = ctk.CTkEntry(self.frame_random, placeholder_text="4", width=60)
        self.entry_count.grid(row=1, column=1, padx=10)

        self.lbl_min = ctk.CTkLabel(self.frame_random, text="Min Durasi (s):")
        self.lbl_min.grid(row=1, column=2, padx=10)
        self.entry_min = ctk.CTkEntry(self.frame_random, placeholder_text="10", width=60)
        self.entry_min.grid(row=1, column=3, padx=10)

        self.lbl_max = ctk.CTkLabel(self.frame_random, text="Max Durasi (s):")
        self.lbl_max.grid(row=1, column=4, padx=10)
        self.entry_max = ctk.CTkEntry(self.frame_random, placeholder_text="30", width=60)
        self.entry_max.grid(row=1, column=5, padx=10)

        # --- B. CONTAINER UNTUK MODE CUSTOM ---
        self.frame_custom = ctk.CTkFrame(self.tab_yt, fg_color="#2B2B2B", border_color="gray", border_width=1)
        # Hidden by default

        self.lbl_cust_info = ctk.CTkLabel(self.frame_custom, text="Pengaturan Manual (Potong di waktu spesifik)", text_color="gray")
        self.lbl_cust_info.grid(row=0, column=0, columnspan=4, pady=(10,5))

        self.lbl_start = ctk.CTkLabel(self.frame_custom, text="Waktu Mulai:")
        self.lbl_start.grid(row=1, column=0, padx=10, pady=15)
        self.entry_start = ctk.CTkEntry(self.frame_custom, placeholder_text="00:01:30", width=120)
        self.entry_start.grid(row=1, column=1, padx=10)

        self.lbl_end = ctk.CTkLabel(self.frame_custom, text="Waktu Akhir:")
        self.lbl_end.grid(row=1, column=2, padx=10)
        self.entry_end = ctk.CTkEntry(self.frame_custom, placeholder_text="00:02:45", width=120)
        self.entry_end.grid(row=1, column=3, padx=10)

        self.lbl_hint = ctk.CTkLabel(self.frame_custom, text="Format: Jam:Menit:Detik (01:20:30) atau Menit:Detik (10:45)", font=("Arial", 10), text_color="#F59E0B")
        self.lbl_hint.grid(row=2, column=0, columnspan=4, pady=(0,10))

        # --- AREA OUTPUT & EKSEKUSI ---
        self.frame_bottom = ctk.CTkFrame(self)
        self.frame_bottom.pack(pady=10, padx=20, fill="x")

        self.btn_out = ctk.CTkButton(self.frame_bottom, text="📂 Pilih Folder Simpan", command=self.browse_folder, fg_color="green", width=200)
        self.btn_out.pack(side="left", padx=10, pady=15)
        self.label_out = ctk.CTkLabel(self.frame_bottom, text="Belum ada folder dipilih...", text_color="gray")
        self.label_out.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.btn_run = ctk.CTkButton(self, text="MULAI PROSES", command=self.start_thread, height=50, width=300, font=("Roboto", 16, "bold"), fg_color="#1F6AA5")
        self.btn_run.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Status: Menunggu Perintah", text_color="silver")
        self.status_label.pack(pady=5)

        # Set default UI state
        self.toggle_ui_mode("Mode Random (Otomatis)")


    # --- LOGIC UI ---
    def toggle_ui_mode(self, value):
        """Fungsi ini menyembunyikan/menampilkan menu berdasarkan pilihan mode"""
        if value == "Mode Random (Otomatis)":
            self.frame_custom.pack_forget() # Sembunyikan menu custom
            self.frame_random.pack(pady=10, padx=20, fill="x") # Tampilkan menu random
        else:
            self.frame_random.pack_forget() # Sembunyikan menu random
            self.frame_custom.pack(pady=10, padx=20, fill="x") # Tampilkan menu custom

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.label_out.configure(text=folder)

    # --- LOGIC BACKEND ---
    
    def parse_time(self, time_str):
        """Ubah string waktu (01:20:30) jadi detik integer"""
        try:
            parts = list(map(int, time_str.strip().split(':')))
            if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
            if len(parts) == 2: return parts[0]*60 + parts[1]
            if len(parts) == 1: return parts[0]
            return None
        except: return None

    def format_srt_time(self, seconds):
        """Ubah detik jadi format timestamp SRT"""
        td = datetime.timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def create_srt(self, segments, base_filename):
        """Bikin file subtitle .srt"""
        path = f"{base_filename}.srt"
        with open(path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                start = self.format_srt_time(seg['start'])
                end = self.format_srt_time(seg['end'])
                text = seg['text'].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def load_model(self):
        if not self.model:
            self.status_label.configure(text="Sedang memuat AI (Whisper)...", text_color="yellow")
            self.model = whisper.load_model("base")

    def start_thread(self):
        if not self.output_folder:
            messagebox.showerror("Error", "Pilih folder output dulu!")
            return
        
        # Validasi Input sebelum mulai thread
        self.active_mode = self.mode_var.get()
        
        if "Custom" in self.active_mode:
            s = self.parse_time(self.entry_start.get())
            e = self.parse_time(self.entry_end.get())
            if s is None or e is None:
                messagebox.showerror("Error", "Format waktu salah! Gunakan Jam:Menit:Detik")
                return
            if s >= e:
                messagebox.showerror("Error", "Waktu Mulai harus lebih kecil dari Waktu Akhir")
                return
            self.cust_start, self.cust_end = s, e

        threading.Thread(target=self.process).start()

    def process(self):
        self.btn_run.configure(state="disabled")
        try:
            self.load_model()
            url = self.entry_yt_url.get()
            if not url: raise Exception("URL Kosong!")

            res_label = self.combo_res.get()
            
            # --- JALUR LOGIKA ---
            if "Custom" in self.active_mode:
                self.run_custom_mode(url, res_label)
            else:
                self.run_random_mode(url, res_label)

            self.status_label.configure(text="SELESAI! Semua file tersimpan.", text_color="#2CC985")
            messagebox.showinfo("Sukses", "Download & Transkripsi Selesai.")

        except Exception as e:
            self.status_label.configure(text="Terjadi Error!", text_color="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_run.configure(state="normal")
            self.progress_bar.set(0)

    # --- MODE 1: CUSTOM ---
    def run_custom_mode(self, url, res_label):
        self.status_label.configure(text=f"Mode Custom: Download {self.cust_start}s - {self.cust_end}s...", text_color="cyan")
        
        temp_file = os.path.join(self.output_folder, "temp_custom.mp4")
        if os.path.exists(temp_file): os.remove(temp_file)

        # Download
        success = self.dl_clip(url, self.cust_start, self.cust_end, temp_file, res_label)
        if not success: raise Exception("Gagal download segment custom")

        # Transcribe
        self.status_label.configure(text="AI sedang membuat subtitle...", text_color="orange")
        result = self.model.transcribe(temp_file, fp16=False)
        
        # Rename & Save
        clean_name = self.generate_name(result["text"], "Custom_Clip")
        final_base = os.path.join(self.output_folder, clean_name)
        
        if os.path.exists(f"{final_base}.mp4"): os.remove(f"{final_base}.mp4")
        os.rename(temp_file, f"{final_base}.mp4")
        self.create_srt(result["segments"], final_base)
        self.progress_bar.set(1.0)

    # --- MODE 2: RANDOM ---
    def run_random_mode(self, url, res_label):
        self.status_label.configure(text="Mengambil info durasi video...", text_color="cyan")
        
        # Get Duration
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            info = ydl.extract_info(url, download=False)
            total_dur = info.get('duration')

        count = int(self.entry_count.get() or 4)
        min_d = int(self.entry_min.get() or 10)
        max_d = int(self.entry_max.get() or 30)

        for i in range(count):
            c_dur = random.uniform(min_d, max_d)
            start = random.uniform(0, max(0, total_dur - c_dur))
            end = start + c_dur
            
            temp_file = os.path.join(self.output_folder, f"temp_{i}.mp4")
            
            self.status_label.configure(text=f"Clip {i+1}/{count}: Download...", text_color="yellow")
            if self.dl_clip(url, start, end, temp_file, res_label):
                
                self.status_label.configure(text=f"Clip {i+1}: Generate Subtitle...", text_color="orange")
                result = self.model.transcribe(temp_file, fp16=False)
                
                clean_name = self.generate_name(result["text"], f"Random_{i+1}")
                final_base = os.path.join(self.output_folder, f"{i+1}_{clean_name}")
                
                if os.path.exists(f"{final_base}.mp4"): os.remove(f"{final_base}.mp4")
                os.rename(temp_file, f"{final_base}.mp4")
                self.create_srt(result["segments"], final_base)
            
            self.progress_bar.set((i+1)/count)

    # --- HELPER LAIN ---
    def dl_clip(self, url, s, e, path, res_label):
        h = self.res_map.get(res_label, 720)
        fmt = f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[height<={h}]/best"
        opts = {
            'format': fmt,
            'download_ranges': yt_dlp.utils.download_range_func(None, [(s, e)]),
            'force_keyframes_at_cuts': True,
            'outtmpl': path,
            'quiet': True, 'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            return True
        except: return False

    def generate_name(self, text, default):
        clean = re.sub(r'[^\w\s]', '', text).strip()
        if not clean: return default
        return "_".join(clean.split()[:5])

if __name__ == "__main__":
    if shutil.which("ffmpeg") is None: print("PERINGATAN: Install FFmpeg dulu!")
    app = UltimateClipper()
    app.mainloop()

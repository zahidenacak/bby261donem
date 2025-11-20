import tkinter as tk
from tkinter import Listbox, Frame, Label, Button, Scrollbar, END, messagebox, Entry, Toplevel, filedialog
import os
import json
import random
from datetime import datetime
from PIL import Image, ImageTk

AFIS_KLASORU = "afisler"

if not os.path.exists(AFIS_KLASORU):
    os.makedirs(AFIS_KLASORU) 


DEFAULT_DATA = {
    "A Clockwork Orange": { "director": "Stanley Kubrick", "year": "1971", "imdb": "8.3", "summary": "Otomatik Portakal: Şiddet bağımlısı bir gencin rehabilitasyon deneyi.", "poster_path": "clockwork.jpg" },
    "The Shining": { "director": "Stanley Kubrick", "year": "1980", "imdb": "8.4", "summary": "Cinnet: Kışın kapalı bir otelde ailesiyle kalan yazarın delirme süreci.", "poster_path": "shining.jpg" },
    "Where is the Friend's House?": { "director": "Abbas Kiarostami", "year": "1987", "imdb": "7.9", "summary": "Arkadaşının Ev Nerede?: Arkadaşının defterini yanlışlıkla alan çocuğun yolculuğu.", "poster_path": "friend.jpg" },
    "Taste of Cherry": { "director": "Abbas Kiarostami", "year": "1997", "imdb": "7.7", "summary": "Kirazın Tadı: İntihar etmek isteyen bir adamın kendisine yardım edecek birini araması.", "poster_path": "cherry.jpg" },
    "The Godfather": { "director": "Francis Ford Coppola", "year": "1972", "imdb": "9.2", "summary": "Baba: Bir mafya ailesinin reisi olan babanın, yerini oğluna bırakma süreci.", "poster_path": "godfather.jpg" },
    "Inception": { "director": "Christopher Nolan", "year": "2010", "imdb": "8.8", "summary": "Başlangıç: Rüyaların içine girerek sırları çalan bir hırsızın hikayesi.", "poster_path": "inception.jpg" },
    "Pulp Fiction": { "director": "Quentin Tarantino", "year": "1994", "imdb": "8.9", "summary": "Ucuz Roman: Yeraltı dünyasındaki farklı karakterlerin yollarının kesişmesi.", "poster_path": "pulp.jpg" },
    "Interstellar": { "director": "Christopher Nolan", "year": "2014", "imdb": "8.7", "summary": "Yıldızlararası: İnsanlığın hayatta kalması için yeni bir gezegen arayışı.", "poster_path": "interstellar.jpg" },
    "Parasite": { "director": "Bong Joon Ho", "year": "2019", "imdb": "8.5", "summary": "Parazit: Fakir bir ailenin zengin bir ailenin evine sızması.", "poster_path": "parasite.jpg" },
    "Spirited Away": { "director": "Hayao Miyazaki", "year": "2001", "imdb": "8.6", "summary": "Ruhların Kaçışı: Ruhların dünyasında çalışmak zorunda kalan küçük Chihiro.", "poster_path": "spirited.jpg" }
}

# RENK PALETİ 
BG_COLOR = "#0f172a"
SIDEBAR_COLOR = "#1e293b"
TEXT_COLOR = "#f1f5f9"
ACCENT_COLOR = "#f59e0b" 
BTN_DICE = "#8b5cf6"
BTN_ADD = "#10b981"

class CinemaArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CINE-LOG: Akıllı Film Asistanı")
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)

        self.json_file = "filmler.json"      
        self.watched_file = "izlediklerim.txt" 
        
        self.archive_data = self.load_archive()
        self.current_suggestion = None 
        self.selected_history_item = None 

        # SOL PANEL (GEÇMİŞ) 
        self.left_frame = Frame(root, width=350, bg=SIDEBAR_COLOR)
        self.left_frame.pack(side="left", fill="y")

        Label(self.left_frame, text="İZLEDİĞİM FİLMLER", bg=SIDEBAR_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 14, "bold")).pack(pady=20)

        list_frame = Frame(self.left_frame, bg=SIDEBAR_COLOR)
        list_frame.pack(fill="both", expand=True, padx=10)
        
        scrollbar = Scrollbar(list_frame, bg=SIDEBAR_COLOR)
        self.history_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 11), bg="#334155", fg="white", selectbackground=ACCENT_COLOR, bd=0)
        scrollbar.config(command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.pack(side="left", fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_click)

        Button(self.left_frame, text="+ FİLM EKLE", bg=BTN_ADD, fg="white", font=("Arial", 10, "bold"), command=self.open_add_window, pady=10, relief="flat").pack(fill="x", padx=10, pady=20)

        # SAĞ PANEL
        self.right_frame = Frame(root, bg=BG_COLOR)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Üst Bar
        self.top_bar = Frame(self.right_frame, bg=BG_COLOR)
        self.top_bar.pack(fill="x", pady=10)
        
        self.dice_btn = Button(self.top_bar, text="🎲 Ne İzlesem? (Zar At)", bg=BTN_DICE, fg="white", font=("Arial", 12, "bold"), command=self.roll_dice, padx=20, pady=8)
        self.dice_btn.pack(side="left")

        # Düzenleme Butonları
        self.history_btns_frame = Frame(self.top_bar, bg=BG_COLOR)
        Button(self.history_btns_frame, text="Düzenle ✏️", bg="#3b82f6", fg="white", command=self.edit_history_item).pack(side="left", padx=5)
        Button(self.history_btns_frame, text="Sil 🗑️", bg="#ef4444", fg="white", command=self.delete_from_history).pack(side="left", padx=5)

        # İçerik Alanı
        self.content_frame = Frame(self.right_frame, bg=BG_COLOR)
        self.content_frame.pack(side="top", fill="x", anchor="n", pady=(10,0)) 

        self.poster_lbl = Label(self.content_frame, bg=BG_COLOR)
        self.poster_lbl.pack(pady=10)

        self.title_lbl = Label(self.content_frame, text="👆 İzlenecek film bulmak için Zara bas!", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg="white", wraplength=700)
        self.title_lbl.pack(pady=2)

        self.meta_lbl = Label(self.content_frame, text="", font=("Arial", 12), bg=BG_COLOR, fg="#94a3b8", justify="center")
        self.meta_lbl.pack(pady=(5, 5))

        self.plot_lbl = Label(self.content_frame, text="", font=("Georgia", 12, "italic"), bg=BG_COLOR, fg=TEXT_COLOR, wraplength=700, justify="center")
        self.plot_lbl.pack(pady=(10, 15))

        # ALT AKSİYON ALANI
        self.suggestion_action_frame = Frame(self.right_frame, bg=BG_COLOR)
        
        # Adım 1
        self.step1_frame = Frame(self.suggestion_action_frame, bg=BG_COLOR)
        self.step1_frame.pack()
        Button(self.step1_frame, text="👁️ İzledim (Puanla)", bg=ACCENT_COLOR, fg="black", font=("Arial", 11, "bold"), width=20, command=self.show_rating_step).pack(side="left", padx=10)
        Button(self.step1_frame, text="📅 Listeme Ekle", bg="#64748b", fg="white", font=("Arial", 11, "bold"), width=20, command=self.add_watchlist).pack(side="left", padx=10)

        # Adım 2
        self.step2_frame = Frame(self.suggestion_action_frame, bg=BG_COLOR)
        Label(self.step2_frame, text="İzlediğin Tarih:", bg=BG_COLOR, fg="white").pack()
        self.date_entry = Entry(self.step2_frame, justify="center", font=("Arial", 11))
        self.date_entry.pack(pady=5)
        Label(self.step2_frame, text="Puanın:", bg=BG_COLOR, fg="white").pack(pady=(10, 5))
        self.stars_frame = Frame(self.step2_frame, bg=BG_COLOR)
        self.stars_frame.pack()
        for i in range(1, 6):
            Button(self.stars_frame, text=f"★ {i}", bg="gold", font=("Arial", 11, "bold"), width=4, command=lambda r=i: self.finalize_rating(r)).pack(side="left", padx=4)

        self.refresh_history_list()

    # VERİ YÜKLEME
    def load_archive(self):
        create_new = False
        if not os.path.exists(self.json_file):
            create_new = True
        else:
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not data: create_new = True
                    else: return data
            except:
                create_new = True

        if create_new:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
            return DEFAULT_DATA.copy()

    def save_archive(self):
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.archive_data, f, ensure_ascii=False, indent=4)

    def refresh_history_list(self):
        self.history_listbox.delete(0, END)
        if os.path.exists(self.watched_file):
            try:
                with open(self.watched_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        self.history_listbox.insert(END, line.strip())
            except:
                pass

    # ZAR VE ÖNERİ
    def roll_dice(self):
        self.history_listbox.selection_clear(0, END)
        self.history_btns_frame.pack_forget()
        self.selected_history_item = None

        if not self.archive_data:
            messagebox.showinfo("Bitti", "Arşivdeki tüm filmler izlendi!")
            self.clear_display()
            return
        
        titles = list(self.archive_data.keys())
        choice = random.choice(titles)
        self.current_suggestion = choice
        
        self.display_suggestion(choice)
        
        self.suggestion_action_frame.pack(side="top", pady=20)
        self.step1_frame.pack()
        self.step2_frame.pack_forget()

    def show_rating_step(self):
        self.step1_frame.pack_forget()
        self.step2_frame.pack()
        today = datetime.now().strftime("%d.%m.%Y")
        self.date_entry.delete(0, END)
        self.date_entry.insert(0, today)

    def finalize_rating(self, rating):
        if not self.current_suggestion: return
        date_watched = self.date_entry.get()
        
        director = "Bilinmiyor"
        if self.current_suggestion in self.archive_data:
             director = self.archive_data[self.current_suggestion].get("director", "Bilinmiyor")

        entry_text = f"{self.current_suggestion} ({director}) - Puan: {rating}/5 - Tarih: {date_watched}"
        
        try:
            with open(self.watched_file, "a", encoding="utf-8") as f:
                f.write(entry_text + "\n")
        except:
            pass
        
        if self.current_suggestion in self.archive_data:
            del self.archive_data[self.current_suggestion]
            self.save_archive()
        
        messagebox.showinfo("Kaydedildi", f"{self.current_suggestion} geçmişe eklendi!")
        self.refresh_history_list()
        self.clear_display()

    def add_watchlist(self):
        messagebox.showinfo("Not", "Film izlenecekler listesine not edildi.")

    # GÖSTERİM 
    def on_history_click(self, event):
        try:
            idx = self.history_listbox.curselection()[0]
            self.selected_history_item = self.history_listbox.get(idx)
            
            self.clear_display(keep_selection=True)
            self.suggestion_action_frame.pack_forget()
            self.current_suggestion = None
            self.history_btns_frame.pack(side="right", padx=10)
            
            full_text = self.selected_history_item
            
            score = "?/5"
            date = "?"
            director = ""
            title = full_text
            
            if " - Puan: " in full_text:
                parts = full_text.split(" - Puan: ")
                title_director_part = parts[0]
                rest_part = parts[1]
                
                if " - Tarih: " in rest_part:
                    score_date = rest_part.split(" - Tarih: ")
                    score = score_date[0]
                    date = score_date[1]
                else:
                    score = rest_part
                
                if " (" in title_director_part and title_director_part.endswith(")"):
                    split_name = title_director_part.rsplit(" (", 1)
                    title = split_name[0]
                    director = split_name[1].replace(")", "")
                else:
                    title = title_director_part

            self.title_lbl.config(text=title)
            
            meta_text = ""
            if director and director != "Bilinmiyor": meta_text += f"🎬 Yönetmen: {director}\n"
            meta_text += f"⭐ Puan: {score}\n"
            meta_text += f"📅 Tarih: {date}"
            
            self.meta_lbl.config(text=meta_text)
            self.plot_lbl.config(text="") 
            
            # Afiş temizliği
            self.poster_lbl.config(image='', text="") 
            self.poster_lbl.image = None 

        except IndexError:
            pass

    def display_suggestion(self, title):
        movie_data = self.archive_data.get(title) or DEFAULT_DATA.get(title)
            
        if movie_data:
            self.title_lbl.config(text=title)
            self.meta_lbl.config(text=f"🎬 {movie_data['director']}  |  📅 {movie_data['year']}  |  ⭐ IMDb: {movie_data['imdb']}")
            self.plot_lbl.config(text=f"“{movie_data['summary']}”")
            
            # YENİ RESİM YÜKLEME (Yerel Dosyadan)
            image_filename = movie_data.get('poster_path', '')
            self.load_local_image(image_filename)
        else:
            self.title_lbl.config(text=title)
            self.meta_lbl.config(text="")
            self.plot_lbl.config(text="")
            self.poster_lbl.config(image='', text="")

    def load_local_image(self, filename):
        """afisler klasöründen resim yükler."""
        if not filename:
            self.poster_lbl.config(image='', text="(Afiş Tanımlı Değil)")
            return

        file_path = os.path.join(AFIS_KLASORU, filename)
        
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img = img.resize((200, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.poster_lbl.config(image=photo, text="")
                self.poster_lbl.image = photo
            except Exception as e:
                self.poster_lbl.config(image='', text=f"(Resim Hatası: {e})")
        else:
            self.poster_lbl.config(image='', text="(Afiş Dosyası Bulunamadı)")

    def clear_display(self, keep_selection=False):
        self.current_suggestion = None
        if not keep_selection:
            self.title_lbl.config(text="Film seçin veya Zar atın")
            self.meta_lbl.config(text="")
        
        self.plot_lbl.config(text="")
        self.poster_lbl.config(image='', text="")
        self.poster_lbl.image = None 
        self.suggestion_action_frame.pack_forget()
        self.history_btns_frame.pack_forget()

    # DÜZENLEME VE SİLME
    def delete_from_history(self):
        if not self.selected_history_item: return
        if messagebox.askyesno("Sil", "Geçmişten silinsin mi?"):
            try:
                with open(self.watched_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(self.watched_file, "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip() != self.selected_history_item:
                            f.write(line)
                self.refresh_history_list()
                self.clear_display()
            except:
                pass

    def edit_history_item(self):
        if not self.selected_history_item: return
        item_text = self.selected_history_item
        
        name = item_text
        score = "1"
        date = datetime.now().strftime("%d.%m.%Y")
        director_in_name = ""

        if " - Puan: " in item_text:
            parts = item_text.split(" - Puan: ")
            name_and_director_part = parts[0]
            rest = parts[1]
            
            if " (" in name_and_director_part and name_and_director_part.endswith(")"):
                name_parts = name_and_director_part.rsplit(" (", 1)
                name = name_parts[0]
                director_in_name = name_parts[1].replace(")", "")
            else:
                name = name_and_director_part

            if " - Tarih: " in rest:
                score_date = rest.split(" - Tarih: ")
                score = score_date[0].split("/")[0]
                date = score_date[1]
            else:
                score = rest.split("/")[0]

        edit_win = Toplevel(self.root)
        edit_win.title("Düzenle")
        edit_win.geometry("350x400")
        edit_win.configure(bg=SIDEBAR_COLOR)

        Label(edit_win, text=f"{name}\nDüzenleniyor", bg=SIDEBAR_COLOR, fg=ACCENT_COLOR, font=("Arial", 10, "bold")).pack(pady=10)
        
        Label(edit_win, text="Film Adı:", bg=SIDEBAR_COLOR, fg="white").pack()
        name_entry = Entry(edit_win)
        name_entry.insert(0, name)
        name_entry.pack(pady=5)

        Label(edit_win, text="Yönetmen:", bg=SIDEBAR_COLOR, fg="white").pack()
        director_entry = Entry(edit_win)
        director_entry.insert(0, director_in_name)
        director_entry.pack(pady=5)
        
        Label(edit_win, text="Puan (1-5):", bg=SIDEBAR_COLOR, fg="white").pack()
        score_entry = Entry(edit_win)
        score_entry.insert(0, score)
        score_entry.pack(pady=5)
        
        Label(edit_win, text="Tarih (GG.AA.YYYY):", bg=SIDEBAR_COLOR, fg="white").pack()
        date_entry = Entry(edit_win)
        date_entry.insert(0, date)
        date_entry.pack(pady=5)
        
        def save_edit():
            new_name = name_entry.get()
            new_director = director_entry.get()
            new_score = score_entry.get()
            new_date = date_entry.get()

            if not new_name or not new_score:
                messagebox.showwarning("Eksik", "Film adı ve Puan zorunludur.")
                return

            display_name = f"{new_name} ({new_director})" if new_director else new_name
            new_line = f"{display_name} - Puan: {new_score}/5 - Tarih: {new_date}"
            
            try:
                with open(self.watched_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(self.watched_file, "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip() == self.selected_history_item:
                            f.write(new_line + "\n")
                        else:
                            f.write(line)
                
                self.refresh_history_list()
                edit_win.destroy()
                messagebox.showinfo("Tamam", "Güncellendi.")
                self.selected_history_item = new_line
                self.on_history_click(None)
            except:
                pass

        Button(edit_win, text="KAYDET", bg=BTN_ADD, fg="white", command=save_edit).pack(pady=20)

    # FİLM EKLE PENCERESİ
    def open_add_window(self):
        top = Toplevel(self.root)
        top.title("Film Ekle")
        top.geometry("350x450")
        top.configure(bg=SIDEBAR_COLOR)

        entries = {}
        fields = ["Film Adı", "Yönetmen", "Tarih (GG.AA.YYYY)", "Puan (1-5)"]
        
        for f in fields:
            Label(top, text=f, bg=SIDEBAR_COLOR, fg="white").pack(pady=(10,0))
            e = Entry(top, width=30)
            e.pack()
            if "Tarih" in f:
                e.insert(0, datetime.now().strftime("%d.%m.%Y"))
            entries[f] = e

        def save_manual():
            name = entries["Film Adı"].get()
            director = entries["Yönetmen"].get()
            date = entries["Tarih (GG.AA.YYYY)"].get()
            score = entries["Puan (1-5)"].get()

            if not name or not score:
                messagebox.showwarning("Eksik", "Film adı ve Puan zorunludur.")
                return

            display_name = f"{name} ({director})" if director else name
            entry_text = f"{display_name} - Puan: {score}/5 - Tarih: {date}"

            try:
                with open(self.watched_file, "a", encoding="utf-8") as f:
                    f.write(entry_text + "\n")
            except:
                pass

            self.refresh_history_list()
            top.destroy()
            messagebox.showinfo("Başarılı", "Film geçmişe eklendi!")

        Button(top, text="KAYDET", bg=BTN_ADD, fg="white", command=save_manual).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaArchiveApp(root)
    root.mainloop()
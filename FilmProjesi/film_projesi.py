import tkinter as tk
from tkinter import Listbox, Frame, Label, Button, Scrollbar, END, messagebox, Entry
import os
import requests
from PIL import Image, ImageTk  # <-- Pillow kütüphanesini kullanmak için
from io import BytesIO          # <-- Resim verilerini işlemek için

# 1. VERİ YAPISI: Filmlerin tüm bilgilerini burada saklıyoruz.
# Gerçek projede bu bilgileri bir JSON veya veritabanından çekmek daha iyidir.
FILM_DATA = {
    # Stanley Kubrick
    "2001: A Space Odyssey": {
        "director": "Stanley Kubrick", "year": 1968, "imdb": 8.3,
        "summary": "İnsanlığın evrimini ve uzaydaki yolculuğunu anlatan, görsel bir şölen sunan bilim kurgu başyapıtı.",
        "poster_url": "https://m.media-amazon.com/images/I/71QpPXjVsVL._AC_UF894,1000_QL80_.jpg"
    },
    "A Clockwork Orange": {
        "director": "Stanley Kubrick", "year": 1971, "imdb": 8.3,
        "summary": "Yakın gelecekte geçen, 'ultra-şiddet' bağımlısı bir çete liderinin yakalanıp bir deneyin parçası olmasını konu alır.",
        "poster_url": "https://m.media-amazon.com/images/I/71EPjPo0UUL._AC_UF894,1000_QL80_.jpg"
    },
    "The Shining": {
        "director": "Stanley Kubrick", "year": 1980, "imdb": 8.4,
        "summary": "Kışın kapalı olan bir otele bakıcılık yapmaya giden bir yazarın ve ailesinin, otelin karanlık güçleri etkisiyle delirmesini anlatır.",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BNmM5ZThhY2ItOGRjOS00NzZiLWEwYTItNDgyMjFkOTgxMmRiXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    # Wes Anderson
    "The Royal Tenenbaums": {
        "director": "Wes Anderson", "year": 2001, "imdb": 7.6,
        "summary": "Parçalanmış ve 'dahi' çocuklardan oluşan bir ailenin, babalarının hastalığı üzerine yıllar sonra tekrar bir araya gelmesini konu alır.",
        "poster_url": "https://m.media-amazon.com/images/I/71SVQ56sfIL._UF894,1000_QL80_.jpg"
    },
    "Fantastic Mr. Fox": {
        "director": "Wes Anderson", "year": 2009, "imdb": 7.9,
        "summary": "Üç kötü çiftçiye karşı ailesini ve dostlarını korumak için kurnazca planlar yapan Bay Tilki'nin stop-motion animasyon macerası.",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BYTA1ZTIxZDUtNGFjYS00YTc5LTgzNDMtZWNjYjBlMzI2OTk3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    "The Grand Budapest Hotel": {
        "director": "Wes Anderson", "year": 2014, "imdb": 8.1,
        "summary": "Avrupa'da iki savaş arasında kalan ünlü bir otelin efsanevi konsiyerji Gustave H. ve lobi görevlisi Zero Moustafa'nın hikayesi.",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2MTMEcy4vObeAp-O--c7tShFgon6U3ncN1w&s"
    },
    # Abbas Kiarostami
    "Where is the Friend's House?": {
        "director": "Abbas Kiarostami", "year": 1987, "imdb": 7.9,
        "summary": "Arkadaşının defterini yanlışlıkla alan küçük bir çocuğun, onu geri vermek için komşu köye yaptığı masumane yolculuğu anlatır.",
        "poster_url": "https://m.media-amazon.com/images/M/MV5BMDFhMDg2NTEtMTgxMi00YmRjLWEyNGEtYmVmYjQ0ZmQxOGNkXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg"
    },
    "Close-Up": {
        "director": "Abbas Kiarostami", "year": 1990, "imdb": 8.2,
        "summary": "Kendisini ünlü yönetmen Mohsen Makhmalbaf olarak tanıtan bir sinema aşığının, bir aileyi kandırması ve sonrasındaki yargılanma sürecini konu alır.",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS9kye1OBy2rWZgHGdNgl88HS04JRR-pX2L_Q&s"
    },
    "Taste of Cherry": {
        "director": "Abbas Kiarostami", "year": 1997, "imdb": 7.6,
        "summary": "Tahran'ın dış mahallelerinde arabasıyla dolaşarak intihar ettikten sonra mezarına toprak atacak birini arayan bir adamın hikayesi.",
        "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBWI7nVtid6YcLMJUhfF9gYgf3Ps0tGN9GIw&s"
    }
}

# 2. UYGULAMA SINIFI
class FilmLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("bby261donem - Film Loglama Projesi")
        self.root.geometry("1000x700")

        self.watched_file = "izlediklerim.txt"
        self.will_watch_file = "izleyeceklerim.txt"
        self.selected_film_title = None

        # --- Arayüzü Oluşturma ---
        
        # 1. Sol Çerçeve (Arama ve Film Listesi)
        self.left_frame = Frame(root, width=300, bg='lightgrey')
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        Label(self.left_frame, text="Film Ara:", font=("Arial", 12), bg='lightgrey').pack(pady=(5,0))
        self.search_var = tk.StringVar()
        self.search_entry = Entry(self.left_frame, textvariable=self.search_var, font=("Arial", 11), width=38)
        self.search_entry.pack(pady=5, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_film)

        Label(self.left_frame, text="Tüm Filmler", font=("Arial", 14, "bold"), bg='lightgrey').pack(pady=(10,5))
        scrollbar = Scrollbar(self.left_frame, orient="vertical")
        self.listbox = Listbox(self.left_frame, yscrollcommand=scrollbar.set, height=30, width=40, font=("Arial", 11))
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        for title in FILM_DATA:
            self.listbox.insert(END, title)
        self.listbox.bind("<<ListboxSelect>>", self.show_details)

        # 2. Sağ Çerçeve (Film Detayları)
        self.right_frame = Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Seçimi Temizle ("Anasayfaya Dön") butonu
        self.clear_btn = Button(self.right_frame, text="Seçimi Temizle / Anasayfa", command=self.clear_selection)
        self.clear_btn.pack(anchor="ne", pady=5) # 'ne' -> North-East (Sağ Üst)

        # Afişin gösterileceği yer
        self.poster_label = Label(self.right_frame)
        self.poster_label.pack(pady=5)
        
        self.title_label = Label(self.right_frame, text="Bir film seçin...", font=("Arial", 18, "bold"), wraplength=600)
        self.title_label.pack(pady=5)
        
        self.info_label = Label(self.right_frame, text="", font=("Arial", 12), justify="left")
        self.info_label.pack(pady=5)
        
        self.summary_label = Label(self.right_frame, text="Özet burada görünecek.", font=("Arial", 11), wraplength=600, justify="left")
        self.summary_label.pack(pady=10)

        # "İzleyeceğim" Butonu
        self.will_watch_btn = Button(self.right_frame, text="İzleyeceğim'e Ekle", command=self.add_to_will_watch, bg='lightblue')
        self.will_watch_btn.pack(pady=10)

        # Puanlama Sistemi
        Label(self.right_frame, text="İzledim (Puanla ve Kaydet):", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        
        self.rating_frame = Frame(self.right_frame)
        self.rating_frame.pack()

        for rating in range(1, 6):
            btn_text = f"★ {rating}"
            btn = Button(
                self.rating_frame, 
                text=btn_text, 
                font=("Arial", 10, "bold"),
                bg="gold",
                command=lambda r=rating: self.add_to_watched_with_rating(r)
            )
            btn.pack(side="left", padx=5)

        # HTML Aktarma Butonu
        self.export_btn = Button(self.right_frame, text="İzlediklerimi HTML Olarak Aktar", font=("Arial", 12, "bold"), bg="darkblue", fg="white", command=self.export_to_html)
        self.export_btn.pack(pady=30)


    # --- Fonksiyonlar ---

    def clear_selection(self):
        """Sağdaki detay panelini temizler ve listbox seçimini kaldırır."""
        self.listbox.selection_clear(0, END)
        self.poster_label.config(image=None, text="") # Afişi kaldır
        self.poster_label.image = None # Referansı temizle (çok önemli)
        self.title_label.config(text="Bir film seçin...")
        self.info_label.config(text="")
        self.summary_label.config(text="Özet burada görünecek.")
        self.selected_film_title = None

    def search_film(self, event):
        """Arama çubuğuna yazılan metne göre film listesini filtreler."""
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, END)
        if not search_term:
            for title in FILM_DATA:
                self.listbox.insert(END, title)
            return
        for title in FILM_DATA:
            if search_term in title.lower() or search_term in FILM_DATA[title]['director'].lower(): # Yönetmen adını da arar
                self.listbox.insert(END, title)
    
    def show_details(self, event):
        """Listbox'tan seçilen filmin detaylarını, AFİŞİNİ ve diğer bilgilerini sağ çerçevede gösterir."""
        try:
            selected_index = self.listbox.curselection()[0]
            self.selected_film_title = self.listbox.get(selected_index)
            film_info = FILM_DATA[self.selected_film_title]
            
            # Metin bilgilerini güncelle
            self.title_label.config(text=self.selected_film_title)
            info_text = f"Yönetmen: {film_info['director']}\n" \
                        f"Yıl: {film_info['year']}\n" \
                        f"IMDb Puanı: {film_info['imdb']}"
            self.info_label.config(text=info_text)
            self.summary_label.config(text=film_info['summary'])

            # Afişi indir ve göster
            self.load_poster(film_info['poster_url'])

        except IndexError:
            # Liste boşsa veya seçim kalkarsa
            pass

    def load_poster(self, url):
        """Verilen URL'den afişi indirir ve ekranda gösterir."""
        try:
            response = requests.get(url)
            img_data = Image.open(BytesIO(response.content))
            
            # Resmi yeniden boyutlandır
            img_data = img_data.resize((250, 370), Image.LANCZOS) 
            
            # Tkinter'in anlayacağı formata çevir
            img_tk = ImageTk.PhotoImage(img_data)
            
            # Afişi Label'a yerleştir
            self.poster_label.config(image=img_tk)
            
            # ÇOK ÖNEMLİ: Tkinter'in "garbage collector" (çöp toplayıcı) mekanizması
            # nedeniyle bu referansı saklamazsak resim görünmez.
            self.poster_label.image = img_tk 
            
        except Exception as e:
            print(f"Afiş yüklenemedi: {e}")
            self.poster_label.config(image=None, text="Afiş Yüklenemedi") # Hata durumunda boş ve metinli göster

    def add_to_watched_with_rating(self, rating):
        """Seçili filmi, verilen puan ile birlikte 'izlediklerim.txt' dosyasına ekler."""
        if not self.selected_film_title:
            messagebox.showwarning("Hata", "Lütfen önce bir film seçin.")
            return
        
        line_to_write = f"{self.selected_film_title} - Puan: {rating}/5\n"
        
        try:
            with open(self.watched_file, "a", encoding="utf-8") as f:
                f.write(line_to_write)
            
            messagebox.showinfo("Başarılı", f"'{self.selected_film_title}' izlendi olarak eklendi ve {rating}/5 puan verildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosyaya yazılırken hata oluştu: {e}")

    def add_to_will_watch(self):
        """Seçili filmi 'izleyeceklerim.txt' dosyasına ekler."""
        if not self.selected_film_title:
            messagebox.showwarning("Hata", "Lütfen önce bir film seçin.")
            return
        
        line_to_write = f"{self.selected_film_title}\n"
        try:
            with open(self.will_watch_file, "a", encoding="utf-8") as f:
                f.write(line_to_write)
            messagebox.showinfo("Başarılı", f"'{self.selected_film_title}' izleme listesine eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosyaya yazılırken hata oluştu: {e}")

    def export_to_html(self):
        """'izlediklerim.txt' dosyasını okur ve puanları da içeren bir HTML raporu oluşturur."""
        
        if not os.path.exists(self.watched_file):
            messagebox.showerror("Hata", "'izlediklerim.txt' dosyası bulunamadı. Önce film ekleyin.")
            return

        try:
            with open(self.watched_file, "r", encoding="utf-8") as f:
                # set() kullanarak aynı filmi 5 kere eklesen bile raporda 1 kez görünmesini sağla
                watched_list = sorted(list(set(f.readlines()))) 
            
            if not watched_list:
                messagebox.showinfo("Bilgi", "İzlenenler listeniz boş.")
                return
            
            html_content = """
            <!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
            <title>İzlediğim Filmler Raporu</title><style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
            h1 { color: #333; } ul { list-style-type: none; padding: 0; }
            li { background-color: #fff; border: 1px solid #ddd; margin-top: -1px; padding: 12px; }
            </style></head><body><h1>İzlediğim Filmler Listesi</h1><ul>
            """
            
            for line in watched_list:
                line = line.strip()
                if not line: continue 

                film_title = line
                rating_str = ""
                
                if " - Puan: " in line:
                    parts = line.split(" - Puan: ")
                    film_title = parts[0]
                    rating_part = parts[1]
                    rating_str = f" - <b>Puan: {rating_part}</b>" 

                if film_title in FILM_DATA:
                    film_info = FILM_DATA[film_title]
                    html_content += f"<li><b>{film_title}</b> ({film_info['year']}) - <i>{film_info['director']}</i>{rating_str}</li>\n"
                else:
                    html_content += f"<li>{line}</li>\n"

            html_content += "</ul></body></html>"
            
            output_filename = "izlediklerim_rapor.html"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            messagebox.showinfo("Başarı!", f"'{output_filename}' başarıyla oluşturuldu.")
        except Exception as e:
            messagebox.showerror("Hata", f"HTML oluşturulurken bir hata oluştu: {e}")

# 3. UYGULAMAYI BAŞLATMA
if __name__ == "__main__":
    root = tk.Tk()
    app = FilmLogApp(root)
    root.mainloop()
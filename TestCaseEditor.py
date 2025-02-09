import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class TestUygulamasi:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Test Case Yazıcı")
        
            # Pencereyi ekranın %80'i boyutunda başlat
        ekran_genislik = self.pencere.winfo_screenwidth()
        ekran_yukseklik = self.pencere.winfo_screenheight()
        pencere_genislik = int(ekran_genislik * 0.8)
        pencere_yukseklik = int(ekran_yukseklik * 0.8)
        
        # Pencereyi ortala
        x = (ekran_genislik - pencere_genislik) // 2
        y = (ekran_yukseklik - pencere_yukseklik) // 2
        self.pencere.geometry(f"{pencere_genislik}x{pencere_yukseklik}+{x}+{y}")
        
        # Pencere yeniden boyutlandırılabilir
        self.pencere.grid_rowconfigure(0, weight=1)
        self.pencere.grid_columnconfigure(0, weight=1)
        
        self.test_basligi = ""
        self.test_maddeleri = []
        self.secili_madde_index = None
        
        # Tests dizini kontrolü
        self.tests_dizini = "tests"
        if not os.path.exists(self.tests_dizini):
            os.makedirs(self.tests_dizini)
            
        self.ana_menu_olustur()
        
    def ana_menu_olustur(self):
        for widget in self.pencere.winfo_children():
            widget.destroy()
            
        self.pencere.title("Test Case Yazıcı - Ana Menü")
        
        # Ana frame'i genişleyebilir yap
        ana_frame = ttk.Frame(self.pencere, padding="10")
        ana_frame.grid(row=0, column=0, sticky="nsew")
        ana_frame.grid_rowconfigure(2, weight=1)
        ana_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık
        ttk.Label(ana_frame, text="Test Case Yazıcı", 
                 font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        # Yeni test butonu
        ttk.Button(ana_frame, text="Yeni Test Oluştur", 
                  command=self.yeni_test_baslat).grid(row=1, column=0, pady=5)
        
        # Geçmiş testler frame
        testler_frame = ttk.LabelFrame(ana_frame, text="Geçmiş Testler", padding="5")
        testler_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        testler_frame.grid_rowconfigure(0, weight=1)
        testler_frame.grid_columnconfigure(0, weight=1)
        
        # Liste ve scrollbar container
        liste_frame = ttk.Frame(testler_frame)
        liste_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        liste_frame.grid_rowconfigure(0, weight=1)
        liste_frame.grid_columnconfigure(0, weight=1)
        
        # Test listesi
        self.test_listbox = tk.Listbox(liste_frame)
        self.test_listbox.grid(row=0, column=0, sticky="nsew")
        self.test_listbox.bind('<Double-Button-1>', self.test_ac_listeden)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(liste_frame, orient="vertical", command=self.test_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.test_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Butonlar frame
        butonlar_frame = ttk.Frame(testler_frame)
        butonlar_frame.grid(row=1, column=0, pady=5)
        
        ttk.Button(butonlar_frame, text="Seçili Testi Aç", 
                  command=self.test_ac_buton).grid(row=0, column=0, padx=5)
        ttk.Button(butonlar_frame, text="Seçili Testi Sil", 
                  command=self.test_sil).grid(row=0, column=1, padx=5)
        
        self.testleri_listele()

    def testleri_listele(self):
        self.test_listbox.delete(0, tk.END)
        for dosya in sorted(os.listdir(self.tests_dizini)):
            if dosya.endswith('.json'):
                with open(os.path.join(self.tests_dizini, dosya), 'r', encoding='utf-8') as f:
                    test_verisi = json.load(f)
                    self.test_listbox.insert(tk.END, test_verisi["baslik"])

    def test_ac_listeden(self, event):
        if self.test_listbox.curselection():
            self.test_ac_buton()

    def test_ac_buton(self):
        if not self.test_listbox.curselection():
            messagebox.showwarning("Uyarı", "Lütfen bir test seçin!")
            return
            
        secili_test = self.test_listbox.get(self.test_listbox.curselection())
        dosya_adi = os.path.join(self.tests_dizini, f"{secili_test}.json")
        
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as f:
                test_verisi = json.load(f)
            
            self.test_basligi = test_verisi["baslik"]
            self.test_maddeleri = test_verisi["maddeler"]
            self.test_penceresi_olustur()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Test açılırken bir hata oluştu: {str(e)}")

    def test_sil(self):
        if not self.test_listbox.curselection():
            messagebox.showwarning("Uyarı", "Lütfen bir test seçin!")
            return
            
        secili_test = self.test_listbox.get(self.test_listbox.curselection())
        if messagebox.askyesno("Onay", f"{secili_test} testini silmek istediğinizden emin misiniz?"):
            dosya_adi = os.path.join(self.tests_dizini, f"{secili_test}.json")
            try:
                os.remove(dosya_adi)
                self.testleri_listele()
                messagebox.showinfo("Başarılı", "Test başarıyla silindi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Test silinirken bir hata oluştu: {str(e)}")

    def yeni_test_baslat(self):
        self.test_basligi = ""
        self.test_maddeleri = []
        self.baslik_penceresi_olustur()

    def baslik_penceresi_olustur(self):
        # Mevcut widget'ları temizle
        for widget in self.pencere.winfo_children():
            widget.destroy()
            
        self.pencere.title("Test Oluştur - Başlık")
        
        baslik_frame = ttk.Frame(self.pencere, padding="20")
        baslik_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(baslik_frame, text="Test Başlığını Giriniz:", 
                 font=("Arial", 12)).grid(row=0, column=0, pady=10)
        
        self.baslik_giris = ttk.Entry(baslik_frame, width=40)
        self.baslik_giris.grid(row=1, column=0, pady=10)
        
        butonlar_frame = ttk.Frame(baslik_frame)
        butonlar_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(butonlar_frame, text="Ana Menüye Dön", 
                  command=self.ana_menu_olustur).grid(row=0, column=0, padx=5)
        ttk.Button(butonlar_frame, text="Devam Et", 
                  command=self.test_penceresi_olustur).grid(row=0, column=1, padx=5)

    def test_penceresi_olustur(self):
        if not self.test_basligi and not self.baslik_giris.get().strip():
            messagebox.showerror("Hata", "Lütfen bir test başlığı giriniz!")
            return
                    
        if not self.test_basligi:
            self.test_basligi = self.baslik_giris.get()

        # Mevcut widget'ları temizle
        for widget in self.pencere.winfo_children():
            widget.destroy()

        # Ana frame
        self.ana_frame = ttk.Frame(self.pencere, padding="10")
        self.ana_frame.grid(row=0, column=0, sticky="nsew")
        self.ana_frame.grid_rowconfigure(1, weight=1)
        self.ana_frame.grid_columnconfigure(0, weight=1)
        self.ana_frame.grid_columnconfigure(1, weight=1)

        # Ana frame'e tıklama eventi ekle
        self.ana_frame.bind('<Button-1>', self.frame_tiklama)
        #baslik
        ttk.Label(self.ana_frame, text=f"Test: {self.test_basligi}", 
            font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        # Sol panel'e tıklama eventi ekle
        sol_panel = ttk.LabelFrame(self.ana_frame, text="Test Maddesi", padding="5")
        sol_panel.grid(row=1, column=0, sticky="nsew", padx=5)
        sol_panel.grid_columnconfigure(0, weight=1)
        sol_panel.bind('<Button-1>', self.frame_tiklama)
            # Tüm label'lara tıklama eventi ekle
        for label in sol_panel.winfo_children():
            if isinstance(label, ttk.Label):
                label.bind('<Button-1>', self.frame_tiklama)
                
        # Madde girişi
        ttk.Label(sol_panel, text="Madde:").grid(row=0, column=0, sticky="w", pady=2)
        self.madde_giris = ttk.Entry(sol_panel)
        self.madde_giris.grid(row=1, column=0, sticky="ew", pady=2)
        
        # Açıklama
        ttk.Label(sol_panel, text="Açıklama:").grid(row=2, column=0, sticky="w", pady=2)
        self.aciklama_giris = ScrolledText(sol_panel, height=4)
        self.aciklama_giris.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Adımlar
        ttk.Label(sol_panel, text="Adımlar:").grid(row=4, column=0, sticky="w", pady=2)
        self.adimlar_giris = ScrolledText(sol_panel, height=4)
        self.adimlar_giris.grid(row=5, column=0, sticky="ew", pady=2)
        
        # Input
        ttk.Label(sol_panel, text="Input:").grid(row=6, column=0, sticky="w", pady=2)
        self.input_giris = ScrolledText(sol_panel, height=4)
        self.input_giris.grid(row=7, column=0, sticky="ew", pady=2)

        # output
        ttk.Label(sol_panel, text="Output:").grid(row=8, column=0, sticky="w", pady=2)
        self.output_giris = ScrolledText(sol_panel, height=4)
        self.output_giris.grid(row=9, column=0, sticky="ew", pady=2)
        
        # Madde butonları
        madde_butonlar = ttk.Frame(sol_panel)
        madde_butonlar.grid(row=10, column=0, pady=5)
        madde_butonlar.bind('<Button-1>', self.frame_tiklama)
        
        self.ekle_buton = ttk.Button(madde_butonlar, text="Madde Ekle", command=self.madde_ekle)
        self.ekle_buton.grid(row=0, column=0, padx=2)
        
        self.guncelle_buton = ttk.Button(madde_butonlar, text="Maddeyi Güncelle", 
                                        command=self.madde_guncelle, state='disabled')
        self.guncelle_buton.grid(row=0, column=1, padx=2)
        
        # Sağ panel (Madde Listesi)
        sag_panel = ttk.LabelFrame(self.ana_frame, text="Test Maddeleri", padding="5")
        sag_panel.grid(row=1, column=1, sticky="nsew", padx=5)
        sag_panel.grid_rowconfigure(0, weight=1)
        sag_panel.grid_columnconfigure(0, weight=1)
        sag_panel.bind('<Button-1>', self.frame_tiklama)
        
        # Madde listesi
        self.madde_listbox = tk.Listbox(sag_panel)
        self.madde_listbox.grid(row=0, column=0, sticky="nsew", pady=5)
        self.madde_listbox.bind('<<ListboxSelect>>', self.madde_sec)
        
        # Madde listesi scrollbar
        liste_scrollbar = ttk.Scrollbar(sag_panel, orient="vertical", 
                                    command=self.madde_listbox.yview)
        liste_scrollbar.grid(row=0, column=1, sticky="ns")
        self.madde_listbox.configure(yscrollcommand=liste_scrollbar.set)
        
        # Madde kontrol butonları
        kontrol_frame = ttk.Frame(sag_panel)
        kontrol_frame.grid(row=1, column=0, columnspan=2, pady=5)
        kontrol_frame.bind('<Button-1>', self.frame_tiklama)
        
        ttk.Button(kontrol_frame, text="Yukarı Taşı", 
                command=self.yukari_tasi).grid(row=0, column=0, padx=2)
        ttk.Button(kontrol_frame, text="Aşağı Taşı", 
                command=self.asagi_tasi).grid(row=0, column=1, padx=2)
        ttk.Button(kontrol_frame, text="Sil", 
                command=self.madde_sil).grid(row=0, column=2, padx=2)
        
        # Alt butonlar
        alt_butonlar = ttk.Frame(self.ana_frame)
        alt_butonlar.grid(row=2, column=0, columnspan=2, pady=5)
        alt_butonlar.bind('<Button-1>', self.frame_tiklama)
        
        ttk.Button(alt_butonlar, text="Kaydet ve Ana Menüye Dön", 
                command=self.kaydet_ve_don).grid(row=0, column=0, padx=5)
        ttk.Button(alt_butonlar, text="Ana Menüye Dön", 
                command=self.ana_menuye_don_sor).grid(row=0, column=1, padx=5)
        
        ttk.Button(alt_butonlar, text="Paylaş", 
            command=self.test_paylas).grid(row=0, column=2, padx=5)

        # Mevcut maddeleri listele
        self.madde_listesini_guncelle()

    def frame_tiklama(self, event):
        # Event'in kaynağını kontrol et
        widget = event.widget
        
        # Eğer tıklanan widget input alanlarından biri değilse
        if not isinstance(widget, (ttk.Entry, ScrolledText)):
            # Seçili maddeyi temizle
            self.secili_madde_index = None
            # Güncelle butonunu deaktif et
            self.guncelle_buton.config(state='disabled')
            # Ekle butonunu aktif et
            self.ekle_buton.config(state='normal')
            # Listbox seçimini temizle
            self.madde_listbox.selection_clear(0, tk.END)

    def madde_sec(self, event):
        if not self.madde_listbox.curselection():
            return
            
        self.secili_madde_index = self.madde_listbox.curselection()[0]
        madde = self.test_maddeleri[self.secili_madde_index]
        
        # Form alanlarını doldur
        self.alanlari_temizle()
        self.madde_giris.insert(0, madde['madde'])
        self.aciklama_giris.insert("1.0", madde['aciklama'])
        self.adimlar_giris.insert("1.0", madde['adimlar'])
        self.input_giris.insert("1.0", madde['input'])
        self.output_giris.insert("1.0", madde['output'])
        
        # Güncelle butonunu aktif et
        self.guncelle_buton.config(state='normal')
        self.ekle_buton.config(state='disabled')

    def madde_guncelle(self):
        if self.secili_madde_index is None:
            return
            
        yeni_madde = {
            "madde": self.madde_giris.get(),
            "aciklama": self.aciklama_giris.get("1.0", tk.END).strip(),
            "adimlar": self.adimlar_giris.get("1.0", tk.END).strip(),
            "input": self.input_giris.get("1.0", tk.END).strip(),
            "output": self.output_giris.get("1.0", tk.END).strip()
        }
        
        self.test_maddeleri[self.secili_madde_index] = yeni_madde
        self.madde_listesini_guncelle()
        self.alanlari_temizle()
        self.secili_madde_index = None
        self.guncelle_buton.config(state='disabled')
        self.ekle_buton.config(state='normal')

    def yukari_tasi(self):
        if not self.madde_listbox.curselection() or self.madde_listbox.curselection()[0] == 0:
            return
            
        idx = self.madde_listbox.curselection()[0]
        self.test_maddeleri[idx], self.test_maddeleri[idx-1] = \
            self.test_maddeleri[idx-1], self.test_maddeleri[idx]
        self.madde_listesini_guncelle()
        self.madde_listbox.selection_set(idx-1)

    def asagi_tasi(self):
        if not self.madde_listbox.curselection() or \
           self.madde_listbox.curselection()[0] == len(self.test_maddeleri) - 1:
            return
            
        idx = self.madde_listbox.curselection()[0]
        self.test_maddeleri[idx], self.test_maddeleri[idx+1] = \
            self.test_maddeleri[idx+1], self.test_maddeleri[idx]
        self.madde_listesini_guncelle()
        self.madde_listbox.selection_set(idx+1)

    def madde_sil(self):
        if not self.madde_listbox.curselection():
            return
            
        if messagebox.askyesno("Onay", "Seçili maddeyi silmek istediğinizden emin misiniz?"):
            idx = self.madde_listbox.curselection()[0]
            del self.test_maddeleri[idx]
            self.madde_listesini_guncelle()
            self.alanlari_temizle()
            self.secili_madde_index = None
            self.guncelle_buton.config(state='disabled')
            self.ekle_buton.config(state='normal')

    def madde_listesini_guncelle(self):
        self.madde_listbox.delete(0, tk.END)
        for i, madde in enumerate(self.test_maddeleri, 1):
            self.madde_listbox.insert(tk.END, f"{i}. {madde['madde']}")

    def madde_ekle(self):
        if not self.madde_giris.get().strip():
            messagebox.showerror("Hata", "Lütfen bir test maddesi giriniz!")
            return
            
        yeni_madde = {
            "madde": self.madde_giris.get(),
            "aciklama": self.aciklama_giris.get("1.0", tk.END).strip(),
            "adimlar": self.adimlar_giris.get("1.0", tk.END).strip(),
            "input": self.input_giris.get("1.0", tk.END).strip(),
            "output": self.output_giris.get("1.0", tk.END).strip()
        }
        
        self.test_maddeleri.append(yeni_madde)
        self.madde_listesini_guncelle()
        self.alanlari_temizle()
        
    def alanlari_temizle(self):
        self.madde_giris.delete(0, tk.END)
        self.aciklama_giris.delete("1.0", tk.END)
        self.adimlar_giris.delete("1.0", tk.END)
        self.input_giris.delete("1.0", tk.END)
        self.output_giris.delete("1.0", tk.END)
        
    def kaydet_ve_don(self):
        if not self.test_maddeleri:
            messagebox.showerror("Hata", "Lütfen en az bir test maddesi ekleyiniz!")
            return
            
        test_verisi = {
            "baslik": self.test_basligi,
            "maddeler": self.test_maddeleri,
            "son_guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        dosya_adi = os.path.join(self.tests_dizini, f"{self.test_basligi}.json")
        
        try:
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                json.dump(test_verisi, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Başarılı", "Test başarıyla kaydedildi!")
            self.ana_menu_olustur()
        except Exception as e:
            messagebox.showerror("Hata", f"Test kaydedilirken bir hata oluştu: {str(e)}")

    def ana_menuye_don_sor(self):
        if messagebox.askyesno("Onay", "Kaydedilmemiş değişiklikler kaybolacak. Devam etmek istiyor musunuz?"):
            self.ana_menu_olustur()

    def baslat(self):
        self.pencere.mainloop()

    def madde_penceresi_olustur(self):
        try:
            self.alt_butonlar_frame = ttk.Frame(self.sag_frame)
            self.alt_butonlar_frame.grid(row=14, column=0, pady=10, sticky="ew")
            
            self.ana_menu_btn = ttk.Button(self.alt_butonlar_frame, text="Ana Menüye Dön", command=self.ana_menuye_don)
            self.ana_menu_btn.pack(side=tk.LEFT, padx=5)
            
            self.paylas_btn = ttk.Button(self.alt_butonlar_frame, text="Paylaş")
            self.paylas_btn.pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            print(f"Madde penceresi oluşturma hatası: {str(e)}")

    def test_paylas(self):
        try:
            if not self.test_maddeleri:
                messagebox.showerror("Hata", "Paylaşılacak test maddesi bulunamadı!")
                return
                
            alici_mail = simpledialog.askstring("Mail Adresi", 
                "Lütfen alıcı mail adresini girin:")
                
            if not alici_mail:
                return
                
            if not '@' in alici_mail or not '.' in alici_mail:
                messagebox.showerror("Hata", "Geçersiz mail adresi!")
                return
                
            test_data = {
                'baslik': self.test_basligi,
                'test_maddeleri': self.test_maddeleri,
                'tarih': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            json_data = json.dumps(test_data, indent=4, ensure_ascii=False)
            
            self.mail_gonder(alici_mail, json_data)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Test paylaşımı sırasında bir hata oluştu: {str(e)}")

    def mail_gonder(self, alici_mail, json_data):
        try:
            gonderen_mail = "" #mail addresses
            mail_sifre = "" #1 time password
            
            msg = MIMEMultipart()
            msg['From'] = gonderen_mail
            msg['To'] = alici_mail
            msg['Subject'] = "Test Paylaşımı"
            
            body = f"""
            Merhaba,
            
            {self.test_basligi} başlıklı test verilerini ekte bulabilirsiniz.
            
            İyi çalışmalar.
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            json_attachment = MIMEApplication(json_data.encode('utf-8'))
            json_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename=f'{self.test_basligi}_test_verileri.json')
            msg.attach(json_attachment)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Güvenli bağlantı
                server.login(gonderen_mail, mail_sifre)
                server.sendmail(gonderen_mail, alici_mail, msg.as_string())

            messagebox.showinfo("Başarılı", f"Test verileri {alici_mail} adresine gönderildi!")
            
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Hata", 
                "Mail gönderimi için kimlik doğrulama başarısız! \n"
                "Lütfen mail adresinizi ve uygulama şifrenizi kontrol edin.")
        
        except smtplib.SMTPException as e:
            messagebox.showerror("Hata", 
                f"Mail gönderimi sırasında SMTP hatası oluştu: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Hata", 
                f"Mail gönderimi sırasında beklenmeyen bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    uygulama = TestUygulamasi()
    uygulama.baslat()
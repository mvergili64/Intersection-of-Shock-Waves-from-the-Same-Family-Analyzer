import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from Same_Family_Shock_Solver import Aynı_Aileden_Şok_Dalgalarının_Kesişmesi_
from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
from Graphics import plot_pressure_theta_analysis
from Animation import supersonic_animation_tkinter

# -------------------- ANALYZER --------------------
analyzer_obs = ObliqueShockAnalyzer()
analyzer_pm = PrandtlMeyerExpansion()

# -------------------- PENCERE --------------------
root = tk.Tk()
root.title("Aynı Aileden Şok Dalgalarının Kesişmesi")
root.geometry("1920x1080")

# -------------------- LEFT FRAME --------------------
left_frame = tk.Frame(root, width=350, height=1080, bg="#CACACA")
left_frame.pack(side=tk.LEFT, fill=tk.Y)
left_frame.pack_propagate(False)

# Entry değişkenleri
mach_inlet = tk.DoubleVar()
Teta1_var = tk.DoubleVar()
Teta_plus_var = tk.DoubleVar()

# -------------------- MIDDLE FRAME --------------------
middle_frame = tk.Frame(root, width=700, height=1080, bg="#EDEDED")
middle_frame.pack(side=tk.LEFT, fill=tk.Y)
middle_frame.pack_propagate(False)

# Bölge seçin Combobox
tk.Label(middle_frame, text="Bölge seçin", font=("Arial", 14), bg="#EDEDED").pack(pady=15)
bolge_secim = ["Bölge 1", "Bölge 2", "Bölge 3", "Bölge 4"]
bolge_combobox = ttk.Combobox(middle_frame, values=bolge_secim, font=("Arial", 14), width=30, state="readonly",
                              background="#EDEDED")
bolge_combobox.current(0)
bolge_combobox.pack(pady=10)

# Entry'leri DoubleVar ile bağlayalım
Beta_var = tk.DoubleVar()
Mach_var = tk.DoubleVar()
T_var = tk.DoubleVar()
P_var = tk.DoubleVar()
density_var = tk.DoubleVar()
total_pres_var = tk.DoubleVar()
Teta_region_var = tk.DoubleVar()
Durum_var = tk.StringVar()

entries_labels = ["Mach Sayısı", "Sıcaklık Oranı", "Yoğunluk Oranı", "Beta",
                  "Basınç Oranı", "Toplam Basınç Oranı", "Teta"]
entries_vars = [Mach_var, T_var, density_var, Beta_var, P_var, total_pres_var, Teta_region_var]

for lbl, var in zip(entries_labels, entries_vars):
    tk.Label(middle_frame, text=lbl, font=("Arial", 14), bg="#EDEDED").pack(pady=10)
    tk.Entry(middle_frame, font=("Arial", 14), width=35, textvariable=var, state="readonly").pack(pady=5)

tk.Label(middle_frame, text="DURUM", font=("Arial", 14), bg="#EDEDED").pack(pady=10)
tk.Label(middle_frame, textvariable=Durum_var, font=("Arial", 14), bg="#EDEDED", wraplength=650, justify="center").pack(
    pady=65)
tk.Label(middle_frame, text="Hesaplanan Oranlar Giriş Bölgesine Olan Oranlardır.",
         font=("Arial", 14), bg="#EDEDED", wraplength=650, justify="center").pack(pady=30)

# -------------------- HESAPLANAN DEĞERLER --------------------
hesaplanan_degerler = {}
photo1 = None
photo2 = None
teta_iter = 0
teta_iter2 = 0
Durum = 0


def guncelle_entries(bolge):
    if bolge in hesaplanan_degerler:
        Beta_var.set(round(hesaplanan_degerler[bolge][0], 4))
        Mach_var.set(round(hesaplanan_degerler[bolge][1], 4))
        T_var.set(round(hesaplanan_degerler[bolge][2], 4))
        P_var.set(round(hesaplanan_degerler[bolge][3], 4))
        density_var.set(round(hesaplanan_degerler[bolge][4], 4))
        total_pres_var.set(round(hesaplanan_degerler[bolge][5], 4))
        Teta_region_var.set(round(hesaplanan_degerler[bolge][6], 4))


def hesapla():
    global photo1, photo2, teta_iter, teta_iter2, Durum, iteration_count_val

    # Error mesajını temizle
    error_label.config(text="", fg="red")

    ITER_NUM = 1000
    iteration_count_val = float('inf')  # Varsayılan değer
    sonuc = None  # sonuc değişkenini önceden tanımla

    try:
        Mach_inlet_val = mach_inlet.get()
        Teta_val = Teta1_var.get()
        Teta_plus_val = Teta_plus_var.get()

        # Fonksiyon çağrısı
        sonuc = Aynı_Aileden_Şok_Dalgalarının_Kesişmesi_(
            Mach_inlet_val, Teta_val, Teta_plus_val, ITER_NUM
        )

        # iteration_count kontrolü
        iteration_count_val = sonuc[-1]  # Son eleman her zaman iteration_count olmalı

        # Sonuçları unpack et
        [Mach_inlet_out, Teta_out, Teta_plus_out, Beta1, M_2, T2_over_T1_2, P2_over_P1,
         density_ratio_2, total_pres_ratio_2, Beta2, M_3, T3_over_T2, P3_over_P1,
         density_ratio_3, total_pres_ratio_3, Beta3, M_4, T4_over_T1, P4_over_P1, rho4_over_rho1,
         total_pres_ratio_4, Beta4, M_5, T5_over_T1, P5_over_P1, rho5_over_rho1, total_pres_ratio_5,
         Durum, teta_iter, teta_iter2, _] = sonuc

        # Hesaplanan değerleri kaydet
        hesaplanan_degerler["Bölge 1"] = [Beta1, M_2, T2_over_T1_2, P2_over_P1, density_ratio_2, total_pres_ratio_2,
                                          Teta_val]
        hesaplanan_degerler["Bölge 2"] = [Beta2, M_3, T3_over_T2, P3_over_P1, density_ratio_3, total_pres_ratio_3,
                                          Teta_plus_val]
        hesaplanan_degerler["Bölge 3"] = [Beta3, M_5, T5_over_T1, P5_over_P1, rho5_over_rho1, total_pres_ratio_5,
                                          teta_iter2]
        hesaplanan_degerler["Bölge 4"] = [Beta4, M_4, T4_over_T1, P4_over_P1, rho4_over_rho1, total_pres_ratio_4,
                                          teta_iter]

        # Durum mesajı
        if Durum == 0:
            Durum_var.set("Şok Oluşur")
        else:
            Durum_var.set("Genişleme dalgası oluşur")

        guncelle_entries("Bölge 1")

        # Grafik hesaplama ve gösterme
        P3_over_P2 = P3_over_P1 / P2_over_P1
        Teta_Total = Teta_val + Teta_plus_val
        plot_pressure_theta_analysis(Mach_inlet_val, M_2, M_3, Teta_val, Teta_Total,
                                     P2_over_P1, P3_over_P2, Durum, analyzer_obs, analyzer_pm,
                                     True, (10, 6))

        img1_tmp = Image.open("grafik.png").resize((820, 400))
        photo1 = ImageTk.PhotoImage(img1_tmp)
        canvas1.create_image(0, 0, anchor=tk.NW, image=photo1)

        img2_tmp = Image.open("grafik_zoomed.png").resize((820, 400))
        photo2 = ImageTk.PhotoImage(img2_tmp)
        canvas2.create_image(0, 0, anchor=tk.NW, image=photo2)

    except UnboundLocalError as e:
        if "Beta3" in str(e):
            if sonuc is not None and len(sonuc) > 0:
                try:
                    iteration_count_val = sonuc[-1]
                except (IndexError, TypeError):
                    pass
            if ITER_NUM <= iteration_count_val:
                error_label.config(text="İterasyon sayısını artırın")
                print(f"Iteration count: {iteration_count_val}")
            else:
                error_label.config(text="Girdiğiniz theta açısı max theta açısından büyük, ayrık şok oluşur!")
        else:
            error_label.config(text=f"Değişken Hatası: {str(e)}")

    except ValueError as e:
        error_label.config(text=f"Girdi Hatası: {str(e)}")
    except FileNotFoundError as e:
        error_label.config(text=f"Dosya Bulunamadı: {str(e)}")
    except Exception as e:
        error_label.config(text=f"Hata: {str(e)}")



# -------------------- LEFT FRAME --------------------
tk.Label(left_frame, text="Mach", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=mach_inlet, font=("Arial", 14), width=25).pack(pady=10)

tk.Label(left_frame, text="Teta1", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=Teta1_var, font=("Arial", 14), width=25).pack(pady=10)

tk.Label(left_frame, text="Teta2", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=Teta_plus_var, font=("Arial", 14), width=25).pack(pady=10)

tk.Button(left_frame, text="Hesapla", font=("Arial", 14), bg="#FBFBFB", command=hesapla).pack(pady=20)

# Hesapla butonunun altına fotoğraf
photo_label = tk.Label(left_frame, bg="lightgray")
photo_label.pack(pady=10)
photo_img = Image.open("photo.png")
photo_img = photo_img.resize((300, 200))
photo_img_tk = ImageTk.PhotoImage(photo_img)
photo_label.config(image=photo_img_tk)  # type: ignore
photo_label.image = photo_img_tk


# -------------------- Akış Animasyonu Butonu --------------------
def animasyon_calistir():
    if not hesaplanan_degerler:
        error_label.config(text="Önce hesaplama yapılmalıdır!")
        return

    try:
        Teta_out_val = hesaplanan_degerler["Bölge 1"][6]
        Teta_plus_out_val = Teta_plus_var.get()
        Beta1_val = hesaplanan_degerler["Bölge 1"][0]
        Beta2_val = hesaplanan_degerler["Bölge 2"][0]
        Beta3_val = hesaplanan_degerler["Bölge 3"][0]
        Beta4_val = hesaplanan_degerler["Bölge 4"][0]
        supersonic_animation_tkinter(
            Teta_out_val,
            Teta_plus_out_val,
            Beta1_val,
            Beta2_val + Teta_out_val,
            Beta4_val,
            Beta3_val + Teta_out_val,
            teta_iter,
            Durum,
            1,
            2500
        )
        # Animasyon başarıyla çalıştırıldıysa error mesajını temizle
        error_label.config(text="")
    except Exception as e:
        error_message = f"Animasyon Hatası: {str(e)}"
        error_label.config(text=error_message)


tk.Button(left_frame, text="Akış Animasyonu için Tıklayınız", font=("Arial", 14), bg="#FBFBFB",
          command=animasyon_calistir).pack(pady=30)

# Error mesajı için label (Akış Animasyonu butonunun altında)
error_label = tk.Label(left_frame, text="", font=("Arial", 12), bg="#CACACA", fg="red", wraplength=300,
                       justify="center")
error_label.pack(pady=10)

# -------------------- RIGHT FRAME --------------------
right_frame = tk.Frame(root, width=870, height=1080, bg="#EDEDED")
right_frame.pack(side=tk.LEFT, fill=tk.Y)
right_frame.pack_propagate(False)

tk.Label(right_frame, text="Basınç Sapma Açısı Diyagramı", font=("Arial", 14), bg="#EDEDED").pack(pady=15)
canvas1 = tk.Canvas(right_frame, width=820, height=400, bg="white")
canvas1.pack(pady=10)

canvas2 = tk.Canvas(right_frame, width=820, height=400, bg="white")
canvas2.pack(pady=10)

bolge_combobox.bind("<<ComboboxSelected>>", lambda event: guncelle_entries(bolge_combobox.get()))

# -------------------- START APP --------------------
root.mainloop()
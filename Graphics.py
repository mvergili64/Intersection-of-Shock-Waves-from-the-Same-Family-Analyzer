from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve


def plot_pressure_theta_analysis(M1, M2, M3, Teta1, Teta2, P2_over_P1, P3_over_P2,
                                 Durum, analyzer_obs, analyzer_pm, show_plot=True, figsize=(10, 6)):
    """
    Basınç-sapma açısı grafiği çizer ve kesişim noktalarını bulur.

    """

    # Renk listesi
    color_list = ["r", "g", "b", "purple", "black", "yellow", "cyan"]

    # İç fonksiyonları tanımla
    analyzer_obs = ObliqueShockAnalyzer()
    analyzer_pm = PrandtlMeyerExpansion()

    def plot_pressure_vs_teta(M, Teta=0, P2_over_P1=1, color=0):
        max_theta_value, _ = analyzer_obs.max_theta(M)
        Teta_list = np.arange(0.01, max_theta_value, 0.1)

        pr_normal = [analyzer_obs.pressure_ratio(M, t) * P2_over_P1 for t in Teta_list]
        pr_strong = [analyzer_obs.pressure_ratio_strong(M, t) * P2_over_P1 for t in Teta_list]
        pr_normal[-1] = pr_strong[-1]  # Max Theta Noktasını Kapatmak İçin

        if show_plot:
            plt.plot(Teta_list + Teta, pr_normal, color_list[color], label=f"MACH {M:.2f}")
            plt.plot(-1 * (Teta_list - Teta), pr_normal, color_list[color])
            plt.plot(Teta_list + Teta, pr_strong, color_list[color])
            plt.plot(-1 * (Teta_list - Teta), pr_strong, color_list[color])

        return pr_normal, pr_strong, max_theta_value

    def plot_pressure_vs_teta_pm(M, Teta=0, P2_over_P1=1, color=0):
        Teta_list = np.arange(0, 90, 0.1)

        pr_normal_pm = [analyzer_pm.pressure_ratio_pm(M, t) * P2_over_P1 for t in Teta_list]

        if show_plot:
            plt.plot(Teta_list + Teta, pr_normal_pm, color_list[color], label=f"MACH {M:.2f}")
            plt.plot(-1 * (Teta_list - Teta), pr_normal_pm, color_list[color])

        return pr_normal_pm

    def difference(x):
        return f1(x) - f2(x)

    # Grafik ayarları
    if show_plot:
        plt.figure(figsize=figsize)

    if Durum == 0:
        # NORMAL ŞOK DURUMU (MACH 3 İLE MACH 1 Eğrisi Kesişir Yansıma Şok Oluşur)
        print("Grafik Çiziliyor...")

        # MACH 1
        pr1, pr1s, max_theta_value1 = plot_pressure_vs_teta(M1)

        # MACH 2
        pr2, pr2s, max_theta_value2 = plot_pressure_vs_teta(M2, Teta=Teta1, P2_over_P1=P2_over_P1, color=1)

        # MACH 3
        pr3, pr3s, max_theta_value3 = plot_pressure_vs_teta(M3, Teta=Teta2, P2_over_P1=P2_over_P1 * P3_over_P2, color=2)

        if show_plot:
            plt.xlabel("Theta")
            plt.ylabel("Pressure Ratio")
            plt.title("Pressure Ratio vs Theta")
            plt.legend()
            plt.grid(True)

        # MACH 1 VE MACH 3 KESİŞİM NOKTASININ BULUNMASI
        # Eğri Mach1
        x1 = np.arange(0.01, max_theta_value1, 0.1)
        y1 = pr1

        # Eğri Mach3
        x2 = (np.arange(0.01, max_theta_value3, 0.1) - Teta2) * -1
        y2 = pr3

    elif Durum == 1:
        # GENİŞLEME DALGASI DURUMU (MACH 3 İLE MACH 1 Eğrisi KESİŞİR Genişleme Dalgası OLUŞUR)
        print("Grafik Çiziliyor...")

        # MACH 1
        pr1, pr1s, max_theta_value1 = plot_pressure_vs_teta(M1)

        # MACH 2
        pr2, pr2s, max_theta_value2 = plot_pressure_vs_teta(M2, Teta=Teta1, P2_over_P1=P2_over_P1, color=1)

        # MACH 3 (Prandtl-Meyer)
        pr3_pm = plot_pressure_vs_teta_pm(M3, Teta=Teta2, P2_over_P1=P2_over_P1 * P3_over_P2, color=2)

        # MACH 1 VE MACH 3 KESİŞİM NOKTASININ BULUNMASI
        # Eğri Mach1
        x1 = np.arange(0.01, max_theta_value1, 0.1)
        y1 = pr1

        # Eğri Mach3
        x2 = np.arange(0, 90, 0.1) + Teta2
        y2 = pr3_pm

        if show_plot:
            plt.xlabel("Theta")
            plt.ylabel("Pressure Ratio")
            plt.title("Pressure Ratio vs Theta")
            plt.legend()
            plt.grid(True)

    else:
        raise ValueError("Durum parametresi 0 veya 1 olmalıdır!")

    # Kesişim noktası hesaplama
    try:
        # İki eğriyi interpolasyon fonksiyonu olarak tanımlama
        f1 = interp1d(x1, y1, kind='linear', fill_value="extrapolate")
        f2 = interp1d(x2, y2, kind='linear', fill_value="extrapolate")

        # Başlangıç tahmini
        x_common = np.linspace(max(min(x1), min(x2)), min(max(x1), max(x2)), 1000)
        x0 = x_common[np.argmin(np.abs(f1(x_common) - f2(x_common)))]

        # Kök çözümü
        x_intersect = fsolve(difference, x0)[0]
        y_intersect = f1(x_intersect)

        print(f"Teta5 = {x_intersect:.4f}, P4/P1=P5/P1 = {y_intersect:.4f}")

        # Kesişim noktasını işaretle
        if show_plot:
            plt.plot(x_intersect, y_intersect, 'ro', label="Kesişim Noktası")

    except Exception as e:
        print(f"Kesişim noktası bulunamadı: {e}")

    plt.savefig("grafik.png")

    x_center=x_intersect
    y_center=y_intersect
    x_range = 0.5
    y_range = 0.3
    plt.xlim(x_center - x_range, x_center + x_range)
    plt.ylim(y_center - y_range, y_center + y_range)
    plt.savefig("grafik_zoomed.png")

    # Grafik göster
    if show_plot:
        plt.show(block=False)  # Grafiği açar ama kod çalışmaya devam eder
        plt.close()

    return x_intersect,y_intersect



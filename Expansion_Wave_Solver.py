import numpy as np
from scipy.optimize import fsolve


class PrandtlMeyerExpansion:
    """
    Prandtl-Meyer genişleme dalgası hesaplamaları için sınıf
    """

    def __init__(self, gamma=1.4):
        """
        Sınıfı başlat
        """
        self.gamma = gamma

    def prandtl_meyer_angle(self, M):
        """
        Verilen Mach sayısı için Prandtl-Meyer genişleme açısını hesapla
        """
        if M <= 1:
            raise ValueError("Prandtl–Meyer fonksiyonu sadece M > 1 için tanımlıdır.")

        term1 = np.sqrt((self.gamma + 1) / (self.gamma - 1))
        term2 = np.arctan(np.sqrt((self.gamma - 1) / (self.gamma + 1) * (M ** 2 - 1)))
        term3 = np.arctan(np.sqrt(M ** 2 - 1))

        nu_rad = term1 * term2 - term3  # Radyan cinsinden
        nu_deg = np.degrees(nu_rad)  # Dereceye çevir

        return nu_deg

    def mach_from_expansion(self, M1, theta_deg):
        """
        Genişleme dalgası sonrası Mach sayısını hesapla
        """
        nu1 = self.prandtl_meyer_angle(M1)
        nu_target = nu1 + theta_deg  # hedef genişleme açısı

        # Çözülecek denklem: prandtl_meyer(M2) - nu_target = 0
        def func(M2):
            return self.prandtl_meyer_angle(M2) - nu_target

        M2_guess = M1 + 0.5  # Başlangıç tahmini
        M2_solution = fsolve(func, M2_guess)[0]

        return M2_solution

    def pressure_ratio_pm(self, M1, theta_deg):
        """
        Genişleme dalgası sonrası basınç oranını hesapla (p2/p1)
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        num = 1 + (self.gamma - 1) / 2 * M1 ** 2
        den = 1 + (self.gamma - 1) / 2 * M2 ** 2
        p_ratio = (num / den) ** (self.gamma / (self.gamma - 1))
        return p_ratio

    def temperature_ratio_pm(self, M1, theta_deg):
        """
        Genişleme dalgası sonrası sıcaklık oranını hesapla (T2/T1)
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        num = 1 + (self.gamma - 1) / 2 * M1 ** 2
        den = 1 + (self.gamma - 1) / 2 * M2 ** 2
        return num / den

    def density_ratio_pm(self, M1, theta_deg):
        """
        Genişleme dalgası sonrası yoğunluk oranını hesapla (rho2/rho1)
        """
        p_ratio = self.pressure_ratio_pm(M1, theta_deg)
        T_ratio = self.temperature_ratio_pm(M1, theta_deg)
        return p_ratio / T_ratio

    def calculate_all_ratios(self, M1, theta_deg):
        """
        Tüm oranları ve sonuç Mach sayısını hesapla
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        p_ratio = self.pressure_ratio_pm(M1, theta_deg)
        T_ratio = self.temperature_ratio_pm(M1, theta_deg)
        rho_ratio = self.density_ratio_pm(M1, theta_deg)

        return {
            'M2': M2,
            'pressure_ratio': p_ratio,
            'temperature_ratio': T_ratio,
            'density_ratio': rho_ratio,
            'nu1': self.prandtl_meyer_angle(M1),
            'nu2': self.prandtl_meyer_angle(M2)
        }


# Kullanım örneği:
if __name__ == "__main__":
    # Sınıfı oluştur
    pm = PrandtlMeyerExpansion(gamma=1.4)

    # Örnek hesaplama
    M1 = 2.0
    theta = 10.0  # derece

    print(f"Başlangıç Mach sayısı: M1 = {M1}")
    print(f"Genişleme açısı: θ = {theta}°")
    print("-" * 40)

    # Tüm sonuçları hesapla
    results = pm.calculate_all_ratios(M1, theta)

    print(f"Sonuç Mach sayısı: M2 = {results['M2']:.4f}")
    print(f"Basınç oranı: p2/p1 = {results['pressure_ratio']:.4f}")
    print(f"Sıcaklık oranı: T2/T1 = {results['temperature_ratio']:.4f}")
    print(f"Yoğunluk oranı: ρ2/ρ1 = {results['density_ratio']:.4f}")
    print(f"Başlangıç PM açısı: ν1 = {results['nu1']:.4f}°")
    print(f"Sonuç PM açısı: ν2 = {results['nu2']:.4f}°")



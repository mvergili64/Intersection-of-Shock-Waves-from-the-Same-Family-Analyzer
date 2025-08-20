import numpy as np
from scipy.optimize import fsolve


class ObliqueShockAnalyzer:


    def __init__(self, gamma=1.4):
        """

        ObliqueShockAnalyzer sınıfını başlatır.

        """
        self.gamma = gamma

    def theta_from_beta(self, M1, beta):
        """
        Mach sayısı ve beta açısına bağlı theta açısını hesaplar.

        """
        beta_rad = np.radians(beta)
        term1 = 2 * (1 / np.tan(beta_rad))
        term2 = (M1 ** 2 * (np.sin(beta_rad)) ** 2 - 1) / (M1 ** 2 * (self.gamma + np.cos(2 * beta_rad)) + 2)
        theta_rad = np.arctan(term1 * term2)
        return np.degrees(theta_rad)

    def max_theta(self, M1):
        """
        Verilen Mach sayısı için maksimum theta açısını hesaplar.

        """
        beta_min = np.degrees(np.arcsin(1 / M1)) + 0.001 #Hata Oluşmaması İçin
        beta_max = 90.0
        beta_vals = np.linspace(beta_min, beta_max, 1000)
        theta_vals = [self.theta_from_beta(M1, b) for b in beta_vals]

        max_theta_value = max(theta_vals)
        beta_at_max_theta = beta_vals[theta_vals.index(max_theta_value)]

        return max_theta_value, beta_at_max_theta

    def _theta_beta_m_relation(self, beta, M1, theta):
        """
        Theta-Beta-Mach sayısı ilişkisi.

        """
        beta_rad = np.radians(beta)
        theta_rad = np.radians(theta)
        lhs = np.tan(theta_rad)
        rhs = 2 * (1 / np.tan(beta_rad)) * ((M1 ** 2 * (np.sin(beta_rad)) ** 2 - 1) /
                                            (M1 ** 2 * (self.gamma + np.cos(2 * beta_rad)) + 2))
        return lhs - rhs

    def solve_beta_angle(self, M1, theta):
        """
        Mach sayısına ve theta açısına bağlı olarak beta açısını hesaplar.

        """
        if M1 < 1:
            raise ValueError(
                f"Girdiğiniz mach sayısı ({M1:.3f}°) 1'den küçük şok oluşmaz.")
        theta_max, beta_for_theta_max = self.max_theta(M1)
        if theta > theta_max:
            raise ValueError(
                f"Girdiğiniz theta açısı ({theta:.3f}°) max theta açısından ({theta_max:.3f}°) büyük, ayrık şok oluşur!")

        beta_guess_weak = theta + 5
        beta_weak = fsolve(self._theta_beta_m_relation, beta_guess_weak, args=(M1, theta))[0]

        return beta_weak

    def mach_after_shock(self, M1, theta_deg):
        """
        Eğik şok sonrası Mach sayısını hesaplar.

        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        theta = np.radians(theta_deg)

        M1n = M1 * np.sin(beta)
        numerator = 1 + ((self.gamma - 1) / 2) * M1n ** 2
        denominator = self.gamma * M1n ** 2 - (self.gamma - 1) / 2
        M2n = np.sqrt(numerator / denominator)

        M2 = M2n / np.sin(beta - theta)
        return M2

    def pressure_ratio(self, M1, theta_deg):
        """
        Eğik şok sonrası basınç oranını hesaplar.

        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1 = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        return p2_over_p1

    def temperature_ratio(self, M1, theta_deg):
        """
        Eğik şok sonrası sıcaklık oranını hesaplar.

        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1 = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        rho2_rho1 = ((self.gamma + 1) * M1n ** 2) / ((self.gamma - 1) * M1n ** 2 + 2)
        T2_over_T1 = p2_over_p1 / rho2_rho1
        return T2_over_T1

    def density_ratio(self, M1, theta_deg):
        """
        Eğik şok sonrası yoğunluk oranını hesaplar.

        """
        p2_over_p1 = self.pressure_ratio(M1, theta_deg)
        T2_over_T1 = self.temperature_ratio(M1, theta_deg)
        rho2_over_rho1 = p2_over_p1 / T2_over_T1
        return rho2_over_rho1

    def total_pressure_ratio(self, M1, theta_deg):
        """
        Eğik şok sonrası toplam basınç oranını hesaplar.

        """
        beta_deg = self.solve_beta_angle(M1, theta_deg)
        beta = np.radians(beta_deg)

        Mn1 = M1 * np.sin(beta)

        term1 = ((self.gamma + 1) * Mn1 ** 2) / ((self.gamma - 1) * Mn1 ** 2 + 2)
        term1 = term1 ** (self.gamma / (self.gamma - 1))

        term2 = ((self.gamma + 1) / (2 * self.gamma * Mn1 ** 2 - (self.gamma - 1))) ** (1 / (self.gamma - 1))

        pt2_over_pt1 = term1 * term2

        return pt2_over_pt1

    def complete_analysis(self, M1, theta_deg):
        """
        Verilen koşullar için kapsamlı eğik şok analizi yapar.

        """
        try:
            beta = self.solve_beta_angle(M1, theta_deg)
            M2 = self.mach_after_shock(M1, theta_deg)
            p_ratio = self.pressure_ratio(M1, theta_deg)
            T_ratio = self.temperature_ratio(M1, theta_deg)
            rho_ratio = self.density_ratio(M1, theta_deg)
            pt_ratio = self.total_pressure_ratio(M1, theta_deg)

            results = {
                'giriş_mach': M1,
                'theta_açısı': theta_deg,
                'beta_açısı': beta,
                'çıkış_mach': M2,
                'basınç_oranı': p_ratio,
                'sıcaklık_oranı': T_ratio,
                'yoğunluk_oranı': rho_ratio,
                'toplam_basınç_oranı': pt_ratio
            }

            return results

        except ValueError as e:
            return {'hata': str(e)}

    def solve_beta_angle_strong(self, M1, theta):
        """
        Mach sayısına ve theta açısına bağlı olarak beta açısını hesaplar.

        """
        beta_guess_strong = 89.9
        beta_strong = fsolve(self._theta_beta_m_relation, beta_guess_strong, args=(M1, theta))[0]

        return beta_strong

    def pressure_ratio_strong(self, M1, theta_deg):
        """
        Eğik şok sonrası basınç oranını hesaplar.

        """
        beta = np.radians(self.solve_beta_angle_strong(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1_strong = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        return p2_over_p1_strong


# Kullanım örneği
if __name__ == "__main__":
    # Sınıfı başlat
    shock_analyzer = ObliqueShockAnalyzer()

    # Örnek analiz
    M1 = 2.0
    theta = 15.0

    print("=== Eğik Şok Analizi ===")
    print(f"Giriş Mach sayısı: {M1}")
    print(f"Theta açısı: {theta}°")

    # Kapsamlı analiz
    results = shock_analyzer.complete_analysis(M1, theta)

    if 'hata' not in results:
        print("\n--- Sonuçlar ---")
        print(f"Beta açısı: {results['beta_açısı']:.2f}°")
        print(f"Çıkış Mach sayısı: {results['çıkış_mach']:.3f}")
        print(f"Basınç oranı (P2/P1): {results['basınç_oranı']:.3f}")
        print(f"Sıcaklık oranı (T2/T1): {results['sıcaklık_oranı']:.3f}")
        print(f"Yoğunluk oranı (ρ2/ρ1): {results['yoğunluk_oranı']:.3f}")
        print(f"Toplam basınç oranı (Pt2/Pt1): {results['toplam_basınç_oranı']:.3f}")
    else:
        print(f"Hata: {results['hata']}")

    # Maksimum theta açısını kontrol et
    max_theta_val, beta_at_max = shock_analyzer.max_theta(M1)
    print(f"\nMaksimum theta açısı: {max_theta_val:.2f}°")
    print(f"Maksimum theta'daki beta açısı: {beta_at_max:.2f}°")
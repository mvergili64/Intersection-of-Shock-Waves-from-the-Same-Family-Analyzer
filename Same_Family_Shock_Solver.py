from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
import time
import pandas as pd

def save_to_csv(results, filename="sonuclar.csv"):
    """Sonuçları CSV dosyasına kaydet"""
    try:
        df = pd.DataFrame([results])
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f" Sonuçlar '{filename}' dosyasına kaydedildi.")
        return True
    except PermissionError:
        print(f"❌ '{filename}' dosyası açık olabilir. Dosyayı kapatıp tekrar deneyin.")
        return False
    except Exception as e:
        print(f"❌ CSV dosyası kaydedilemedi: {e}")
        return False

def Aynı_Aileden_Şok_Dalgalarının_Kesişmesi_(Mach_inlet,Teta,Teta_plus,ITER_NUM=1000):
    start_time = time.time()
    analyzer_obs = ObliqueShockAnalyzer()
    analyzer_pm = PrandtlMeyerExpansion()

    # İlk Şok sonrası akış özellikleri
    Beta1=analyzer_obs.solve_beta_angle(Mach_inlet,Teta)
    M_2 = analyzer_obs.mach_after_shock(Mach_inlet, Teta)
    T2_over_T1_2 = analyzer_obs.temperature_ratio(Mach_inlet, Teta)
    P2_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Teta)
    density_ratio_2 = analyzer_obs.density_ratio(Mach_inlet, Teta)
    total_pres_ratio_2 = analyzer_obs.total_pressure_ratio(Mach_inlet, Teta)

    # İkinci Şok Sonrası Akış Özellikleri
    Beta2=analyzer_obs.solve_beta_angle(M_2,Teta_plus)
    M_3 = analyzer_obs.mach_after_shock(M_2, Teta_plus)
    T3_over_T2 = analyzer_obs.temperature_ratio(M_2, Teta_plus)
    P3_over_P2 = analyzer_obs.pressure_ratio(M_2, Teta_plus)
    density_ratio_3 = analyzer_obs.density_ratio(M_2, Teta_plus)
    total_pres_ratio_3 = analyzer_obs.total_pressure_ratio(M_2, Teta_plus)

    # Parametreler
    TOLERANCE = 0.001
    STEP_SIZE = 0.001
    MAX_ITERATIONS = ITER_NUM

    # Genişleme Dalgası Oluşması Durumunda
    teta_iter = 0.001
    P4_over_P1 = 10
    P5_over_P1 = 1
    Teta_total = Teta + Teta_plus
    A = 0
    iteration_count = 0

    print("🔄 Genişleme dalgası analizi başlatılıyor...")

    try:
        while abs(P4_over_P1 - P5_over_P1) > TOLERANCE and iteration_count < MAX_ITERATIONS:
            P4_over_P1 = analyzer_pm.pressure_ratio_pm(M_3, teta_iter) * P2_over_P1 * P3_over_P2
            P5_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Teta_total + teta_iter)
            teta_iter += STEP_SIZE
            iteration_count += 1

        if iteration_count < MAX_ITERATIONS:
            M_4 = analyzer_pm.mach_from_expansion(M_3, teta_iter)
            M_5 = analyzer_obs.mach_after_shock(Mach_inlet, Teta_total - teta_iter)
            T4_over_T1 = analyzer_pm.temperature_ratio_pm(M_3, teta_iter) * T2_over_T1_2 * T3_over_T2
            T5_over_T1 = analyzer_obs.temperature_ratio(Mach_inlet, Teta_total - teta_iter)
            rho4_over_rho1 = analyzer_pm.density_ratio_pm(M_3, teta_iter) * density_ratio_3 * density_ratio_2
            rho5_over_rho1 = analyzer_obs.density_ratio(Mach_inlet, Teta_total - teta_iter)
            total_pres_ratio_4 = 1 * total_pres_ratio_3 * total_pres_ratio_2
            total_pres_ratio_5 = analyzer_obs.total_pressure_ratio(Mach_inlet, Teta_total - teta_iter)
            Beta4 = analyzer_obs.solve_beta_angle(M_3, teta_iter)
            Beta3 = analyzer_obs.solve_beta_angle(Mach_inlet, Teta_total - teta_iter)

            A = 1
            end_time = time.time()
            elapsed_time = end_time - start_time
            results = {
                "Durum": "Genişleme Dalgası",
                "Giriş Mach": Mach_inlet,
                "İlk Rampa Açısı": Teta,
                "Rampa Artış Açısı": Teta_plus,
                "Mach 2": M_2,
                "Mach 3": M_3,
                "Beta1":Beta1,
                "Beta2":Beta2,
                "Beta3":Beta3,
                "Beta4":Beta4,
                "P2/P1": P2_over_P1,
                "P3/P1": P3_over_P2 * P2_over_P1,
                "P4/P1": P4_over_P1,
                "P5/P1": P5_over_P1,
                "Teta": teta_iter,
                "Mach 4": M_4,
                "Mach 5": M_5,
                "T4/T1": T4_over_T1,
                "T5/T1": T5_over_T1,
                "rho4/rho1": rho4_over_rho1,
                "rho5/rho1": rho5_over_rho1,
                "Pt4/Pt1": total_pres_ratio_4,
                "Pt5/Pt1": total_pres_ratio_5,
                "İterasyon Sayısı": iteration_count,
                "Çalışma Süresi (s)": elapsed_time
            }
            save_to_csv(results)
            for key, value in results.items():
                print(f"{key}: {value}")
        else:
            print(f"⚠️  Genişleme dalgası için çözüm bulunamadı. ({MAX_ITERATIONS} iterasyon)")

    except Exception as e:
        print(f"❌ Genişleme dalgası hesaplamasında hata: {e}")

    if A == 0:
        # Şok Oluşması Durumunda
        print("🔄 Şok dalgası analizi başlatılıyor...")
        P4_over_P1 = 10
        P5_over_P1 = 1
        teta_iter = 0.001
        iteration_count = 0

        try:
            while abs(P4_over_P1 - P5_over_P1) > TOLERANCE and iteration_count < MAX_ITERATIONS:
                P4_over_P1 = analyzer_obs.pressure_ratio(M_3, teta_iter) * P2_over_P1 * P3_over_P2
                P5_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Teta_total - teta_iter)
                teta_iter += STEP_SIZE
                iteration_count += 1

            if iteration_count < MAX_ITERATIONS:
                M_4 = analyzer_obs.mach_after_shock(M_3, teta_iter)
                M_5 = analyzer_obs.mach_after_shock(Mach_inlet, Teta_total - teta_iter)
                T4_over_T1 = analyzer_obs.temperature_ratio(M_3, teta_iter) * T2_over_T1_2 * T3_over_T2
                T5_over_T1 = analyzer_obs.temperature_ratio(Mach_inlet, Teta_total - teta_iter)
                rho4_over_rho1 = analyzer_obs.density_ratio(M_3, teta_iter) * density_ratio_3 * density_ratio_2
                rho5_over_rho1 = analyzer_obs.density_ratio(Mach_inlet, Teta_total - teta_iter)
                total_pres_ratio_4 = analyzer_obs.total_pressure_ratio(M_3,teta_iter) * total_pres_ratio_3 * total_pres_ratio_2
                total_pres_ratio_5 = analyzer_obs.total_pressure_ratio(Mach_inlet, Teta_total - teta_iter)
                Beta4 = analyzer_obs.solve_beta_angle(M_3, teta_iter)
                Beta3 = analyzer_obs.solve_beta_angle(Mach_inlet, Teta_total - teta_iter)
                teta_iter=teta_iter*-1

                end_time = time.time()
                elapsed_time = end_time - start_time

                results = {
                    "Durum": "Şok Dalgası",
                    "Giriş Mach": Mach_inlet,
                    "İlk Rampa Açısı": Teta,
                    "Rampa Artış Açısı": Teta_plus,
                    "Mach 2": M_2,
                    "Mach 3": M_3,
                    "Beta1":Beta1,
                    "Beta2":Beta2,
                    "Beta3":Beta3,
                    "Beta4":Beta4,
                    "P2/P1": P2_over_P1,
                    "P3/P1": P3_over_P2 * P2_over_P1,
                    "P4/P1": P4_over_P1,
                    "P5/P1": P5_over_P1,
                    "Teta": teta_iter,
                    "Mach 4": M_4,
                    "Mach 5": M_5,
                    "T4/T1": T4_over_T1,
                    "T5/T1": T5_over_T1,
                    "rho4/rho1": rho4_over_rho1,
                    "rho5/rho1": rho5_over_rho1,
                    "Pt4/Pt1": total_pres_ratio_4,
                    "Pt5/Pt1": total_pres_ratio_5,
                    "İterasyon Sayısı": iteration_count,
                    "Çalışma Süresi (s)": elapsed_time
                }
                for key, value in results.items():
                    print(f"{key}: {value}")
                save_to_csv(results)
            else:
                print(f"⚠️  Şok dalgası için çözüm bulunamadı. ({MAX_ITERATIONS} iterasyon)")

        except Exception as e:
            print(f"❌ Şok dalgası hesaplamasında hata: {e}")
    return Mach_inlet,Teta,Teta_plus,Beta1,M_2,T2_over_T1_2,P2_over_P1,density_ratio_2,total_pres_ratio_2,Beta2,M_3,T3_over_T2*T2_over_T1_2,P3_over_P2*P2_over_P1,density_ratio_3*density_ratio_2,total_pres_ratio_3*total_pres_ratio_2,Beta3,M_4,T4_over_T1,P4_over_P1,rho4_over_rho1,total_pres_ratio_4,Beta4,M_5,T5_over_T1,P5_over_P1,rho5_over_rho1,total_pres_ratio_5,A,teta_iter,teta_iter+Teta+Teta_plus,iteration_count
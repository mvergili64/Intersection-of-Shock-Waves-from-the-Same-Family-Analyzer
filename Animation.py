import tkinter as tk
import turtle
import math
import numpy as np

def supersonic_animation_tkinter(Teta1=10, Teta2=12, Beta1=39, Beta2=62,
                                 Beta3=57.06, Beta4=57.58, teta_iter=0.27,
                                 Durum=0, speedt=1, step_num=2500):

    root = tk.Tk()
    root.title("Supersonic Animation")
    root.geometry("1366x768")

    canvas = tk.Canvas(root, width=1366, height=500)
    canvas.pack()

    screen = turtle.TurtleScreen(canvas)
    screen.tracer(0)

    # Flaglar
    running = tk.BooleanVar(value=False)
    step = tk.IntVar(value=0)

    # Animasyon parametreleri global tutulacak
    turtles = {}
    paths = {}

    def setup_scene():
        """Zemin + tüm başlangıç turtle ve yolları kur"""
        nonlocal turtles, paths

        screen.clearscreen()  # her reset'te temizle
        screen.tracer(0)

        # === Zemin ===
        zemin = turtle.RawTurtle(screen)
        zemin.hideturtle()
        zemin.speed(0)
        zemin.penup()
        zemin.goto(-680, -200)
        zemin.pendown()
        zemin.forward(200)
        teta1_start = zemin.pos()
        zemin.left(Teta1)
        zemin.forward(200)
        teta2_start = zemin.pos()
        zemin.left(Teta2)
        zemin.forward(400)

        # Fonksiyonlar
        def find_x_for_y(y_target, x0, y0, angle_deg):
            angle_rad = np.radians(angle_deg)
            m = np.tan(angle_rad)
            x_target = x0 + (y_target - y0) / m
            return x_target, y_target

        def intersect(p1, angle1, p2, angle2):
            a1 = math.radians(angle1)
            a2 = math.radians(angle2)
            x1, y1 = p1
            x2, y2 = p2
            dx1, dy1 = math.cos(a1), math.sin(a1)
            dx2, dy2 = math.cos(a2), math.sin(a2)
            det = dx1 * (-dy2) - dy1 * (-dx2)
            if abs(det) < 1e-6:
                return None
            t = ((x2 - x1) * (-dy2) - (y2 - y1) * (-dx2)) / det
            xi = x1 + t * dx1
            yi = y1 + t * dy1
            return (xi, yi)

        # === Şok kesişim noktası ===
        P1 = intersect(teta1_start, Beta1, teta2_start, Beta2)

        # === Kırmızı çizgiler ===
        kirmizi = turtle.RawTurtle(screen)
        kirmizi.hideturtle()
        kirmizi.color("red")
        kirmizi.speed(0)

        if P1:
            kirmizi.pensize(2)
            kirmizi.penup(); kirmizi.goto(teta1_start); kirmizi.pendown(); kirmizi.goto(P1)
            kirmizi.penup(); kirmizi.goto(teta2_start); kirmizi.pendown(); kirmizi.goto(P1)

            if Durum == 0:
                my_color="red"
                kirmizi.penup(); kirmizi.goto(P1); kirmizi.color(my_color); kirmizi.setheading(0)
                kirmizi.pendown()
                P_1 = intersect(P1, 180 - Beta3, teta2_start, Teta1 + Teta2)
                kirmizi.goto(P_1)
            else:
                my_color="purple"
                for t in range(-1,2,1):
                    kirmizi.penup(); kirmizi.goto(P1); kirmizi.color(my_color); kirmizi.setheading(0)
                    kirmizi.pendown()
                    P_1 = intersect(P1, 180 - Beta3+(t*5), teta2_start, Teta1 + Teta2)
                    kirmizi.goto(P_1)

            kirmizi.color("red")
            kirmizi.penup(); kirmizi.goto(P1); kirmizi.setheading(0)
            kirmizi.pendown(); kirmizi.left(Beta4); kirmizi.forward(200)

            # Slip-line
            kirmizi.color("black")
            kirmizi.penup(); kirmizi.goto(P1); kirmizi.setheading(0)
            kirmizi.pendown(); kirmizi.left(Teta1+Teta2+teta_iter)
            for _ in range(int(200/20/2)):
                kirmizi.pendown(); kirmizi.forward(20)
                kirmizi.penup(); kirmizi.forward(20)

        # === Akış turtle'ları ===
        baslangicy = P1[1] - 50
        Akış = turtle.RawTurtle(screen)
        Akış.hideturtle(); Akış.color("blue"); Akış.speed(0)
        Akış.penup(); Akış.goto(-600, baslangicy); Akış.pendown(); Akış.pensize(3)

        Akış1 = turtle.RawTurtle(screen)
        Akış1.hideturtle(); Akış1.color("blue"); Akış1.speed(0)
        Akış1.penup(); Akış1.goto(-600, P1[1] + 50); Akış1.pendown(); Akış1.pensize(3)

        # === Hedef yollar ===
        akış_yollar = []
        P = find_x_for_y(baslangicy, teta1_start[0], teta1_start[1], Beta1)
        akış_yollar.append(P)
        P = intersect(teta2_start, Beta2, P, Teta1)
        akış_yollar.append(P)
        P = intersect(P1, 180 - Beta3, P, Teta1 + Teta2)
        akış_yollar.append(P)

        akış1_yollar = []
        P = find_x_for_y(P1[1] + 50, P1[0], P1[1], Beta4)
        akış1_yollar.append(P)

        # Parametreleri sakla
        turtles = {
            "Akış": Akış, "Akış1": Akış1
        }
        paths = {
            "akış_yollar": akış_yollar,
            "akış1_yollar": akış1_yollar,
            "Akış_final_angle": Teta1+Teta2+teta_iter,
            "Akış1_final_angle": Teta1+Teta2+teta_iter,
            "Akış_final_distance": 150,
            "Akış1_final_distance": 150,
            "Akış_final_started": False,
            "Akış1_final_started": False
        }
        screen.update()

    # === Animasyon ===
    def animate():
        if not running.get():
            return
        if step.get() >= step_num:
            return

        Akış = turtles["Akış"]
        Akış1 = turtles["Akış1"]

        # Akış hareketi
        if paths["akış_yollar"]:
            target = paths["akış_yollar"][0]
            Akış.setheading(Akış.towards(target))
            Akış.forward(speedt)
            if Akış.distance(target) < speedt:
                Akış.goto(target)
                paths["akış_yollar"].pop(0)
                if not paths["akış_yollar"]:
                    paths["Akış_final_started"] = True
                    Akış.setheading(paths["Akış_final_angle"])
        elif paths["Akış_final_started"] and paths["Akış_final_distance"] > 0:
            step_move = min(speedt, paths["Akış_final_distance"])
            Akış.forward(step_move)
            paths["Akış_final_distance"] -= step_move

        # Akış1 hareketi
        if paths["akış1_yollar"]:
            target = paths["akış1_yollar"][0]
            Akış1.setheading(Akış1.towards(target))
            Akış1.forward(speedt)
            if Akış1.distance(target) < speedt:
                Akış1.goto(target)
                paths["akış1_yollar"].pop(0)
                if not paths["akış1_yollar"]:
                    paths["Akış1_final_started"] = True
                    Akış1.setheading(paths["Akış1_final_angle"])
        elif paths["Akış1_final_started"] and paths["Akış1_final_distance"] > 0:
            step_move = min(speedt, paths["Akış1_final_distance"])
            Akış1.forward(step_move)
            paths["Akış1_final_distance"] -= step_move

        step.set(step.get()+1)
        screen.update()
        root.after(10, animate)

    # === Butonlar ===
    def start_anim():
        if not running.get():
            running.set(True)
            animate()

    def stop_anim():
        running.set(False)

    def reset_anim():
        running.set(False)
        step.set(0)
        setup_scene()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Button(frame, text="Başlat", command=start_anim, width=10).pack(side="left", padx=5)
    tk.Button(frame, text="Durdur", command=stop_anim, width=10).pack(side="left", padx=5)
    tk.Button(frame, text="Sıfırla", command=reset_anim, width=10).pack(side="left", padx=5)

    # Başlangıçta zemin hemen çizilsin
    setup_scene()

    root.mainloop()





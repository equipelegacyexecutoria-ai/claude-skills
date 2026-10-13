"""Modelo Manim: curva de crescimento de JAN a DEZ com área, grade e selo de meta.
Usado no Criativo Motion Black (Plano 2027). Trocar cores, meses, pontos e o texto do selo.

Render (1424x600, 30 fps, fundo igual ao cartão onde vai entrar):
  manim -r 1424,600 --fps 30 --format mp4 --media_dir <pasta temporária> -o grafico manim_grafico.py Plano2027
"""
from manim import *

AZUL = "#3c83f6"
CIANO = "#17adfd"
TINTA = "#141826"
CINZA = "#9aa3b5"
LINHA = "#e4e8f1"

config.background_color = "#ffffff"


class Plano2027(Scene):
    def construct(self):
        eixos = Axes(
            x_range=[0, 11, 1], y_range=[0, 10, 2.5], x_length=11.4, y_length=3.6, tips=False,
            axis_config={"color": LINHA, "stroke_width": 3, "include_ticks": False},
            y_axis_config={"stroke_opacity": 0},
        ).shift(DOWN * 0.15)
        grade = VGroup(*[
            DashedLine(eixos.c2p(0, y), eixos.c2p(11, y), color=LINHA, stroke_width=2, dash_length=0.12)
            for y in (2.5, 5, 7.5)
        ])
        meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        rotulos = VGroup(*[
            Text(m, font="Inter", font_size=18, color=CINZA, weight=BOLD).next_to(eixos.c2p(i, 0), DOWN, buff=0.18)
            for i, m in enumerate(meses)
        ])

        # crescimento com um tropeço no meio (realista) e arrancada no fim
        pontos = [1.2, 1.6, 2.3, 2.1, 3.0, 3.8, 4.4, 5.3, 6.1, 7.0, 8.1, 9.3]
        curva = eixos.plot_line_graph(
            x_values=list(range(12)), y_values=pontos, line_color=AZUL,
            add_vertex_dots=False, stroke_width=7,
        )["line_graph"]
        curva.set_color_by_gradient(AZUL, CIANO)
        area = eixos.get_area(
            eixos.plot(lambda x: pontos[min(int(x), 10)] + (pontos[min(int(x) + 1, 11)] - pontos[min(int(x), 10)]) * (x - int(x)),
                       x_range=[0, 11]),
            x_range=[0, 11], color=[AZUL, "#ffffff"], opacity=0.18,
        )
        ponto = Dot(eixos.c2p(11, pontos[-1]), radius=0.13, color=CIANO)
        halo = Circle(radius=0.3, color=CIANO, stroke_width=4).move_to(ponto)
        selo = VGroup(
            RoundedRectangle(corner_radius=0.18, width=2.5, height=0.62, fill_color=TINTA, fill_opacity=1, stroke_width=0),
            Text("META 2027", font="Inter", font_size=22, color="#ffffff", weight=BOLD),
        ).next_to(ponto, LEFT, buff=0.35).shift(UP * 0.35)

        self.add(eixos, grade)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rotulos], lag_ratio=0.05), run_time=0.6)
        self.play(Create(curva), FadeIn(area), run_time=1.9, rate_func=rate_functions.ease_in_out_cubic)
        self.play(GrowFromCenter(ponto), Create(halo), FadeIn(selo, shift=RIGHT * 0.2), run_time=0.45)
        self.play(halo.animate.scale(1.6).set_opacity(0), run_time=0.5)
        self.wait(2.2)

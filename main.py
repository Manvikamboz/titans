"""Visual DFA simulator.  Run:  python main.py
Keys: 1/2/3 pick a DFA | type 0 or 1 | BACKSPACE delete | ENTER run | ESC quit
"""
import math
import pygame
from dfa import EXAMPLES

W, H, R = 900, 640, 34
STEP_MS = 700
BG, INK, MUTED = (245, 247, 250), (30, 42, 58), (120, 130, 145)
TEAL, RED, GREEN = (31, 158, 148), (214, 80, 64), (46, 160, 90)


def layout(dfa):
    cx, cy, rad = W // 2, 270, 170
    n = len(dfa.states)
    if n == 1:
        return {dfa.states[0]: (cx, cy)}
    return {s: (cx + rad * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
                cy + rad * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
            for i, s in enumerate(dfa.states)}


def head(screen, color, tip, ang):
    pts = [tip] + [(tip[0] - 12 * math.cos(ang + d), tip[1] - 12 * math.sin(ang + d))
                   for d in (0.4, -0.4)]
    pygame.draw.polygon(screen, color, pts)


def draw_edges(screen, font, dfa, pos, hot):
    edges = {}
    for (s, a), t in dfa.transitions.items():
        edges.setdefault((s, t), []).append(a)
    for (s, t), syms in edges.items():
        color = RED if hot == (s, t) else INK
        label = font.render(",".join(syms), True, color)
        x, y = pos[s]
        if s == t:                                   # self-loop, drawn outside the circle
            ux, uy = (x - W // 2) or 0.001, (y - 270) or 0.001
            norm = math.hypot(ux, uy)
            ux, uy = ux / norm, uy / norm
            lc = (x + ux * (R + 8), y + uy * (R + 8))
            pygame.draw.circle(screen, color, lc, 18, 2)
            screen.blit(label, (lc[0] + ux * 26 - label.get_width() / 2,
                                lc[1] + uy * 26 - label.get_height() / 2))
            continue
        x2, y2 = pos[t]
        ang = math.atan2(y2 - y, x2 - x)
        off = 12 if (t, s) in edges else 0           # separate two-way arrows
        ox, oy = -math.sin(ang) * off, math.cos(ang) * off
        a = (x + math.cos(ang) * R + ox, y + math.sin(ang) * R + oy)
        b = (x2 - math.cos(ang) * R + ox, y2 - math.sin(ang) * R + oy)
        pygame.draw.line(screen, color, a, b, 2)
        head(screen, color, b, ang)
        mx, my = (a[0] + b[0]) / 2 + ox * 1.8, (a[1] + b[1]) / 2 + oy * 1.8
        screen.blit(label, (mx - label.get_width() / 2, my - label.get_height() / 2 - (0 if off else 14)))


def draw_states(screen, font, dfa, pos, current):
    sx, sy = pos[dfa.start]
    pygame.draw.line(screen, INK, (sx - R - 40, sy), (sx - R, sy), 2)
    head(screen, INK, (sx - R, sy), 0)
    for s, (x, y) in pos.items():
        pygame.draw.circle(screen, TEAL if s == current else (255, 255, 255), (x, y), R)
        pygame.draw.circle(screen, INK, (x, y), R, 2)
        if s in dfa.accepting:
            pygame.draw.circle(screen, INK, (x, y), R - 6, 2)
        txt = font.render(s, True, (255, 255, 255) if s == current else INK)
        screen.blit(txt, (x - txt.get_width() / 2, y - txt.get_height() / 2))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("DFA Simulator")
    font, big = pygame.font.SysFont(None, 26), pygame.font.SysFont(None, 38)
    clock = pygame.time.Clock()

    def load(i):
        d = EXAMPLES[i]()
        return d, layout(d)

    idx = 0
    dfa, pos = load(idx)
    text, consumed, current, trace, result, hot, last = "", 0, dfa.start, [], None, None, 0
    running_anim = False

    def reset(clear_text=False):
        nonlocal text, consumed, current, trace, result, hot, running_anim
        if clear_text:
            text = ""
        consumed, current, trace, result, hot, running_anim = 0, dfa.start, [], None, None, False

    run = True
    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    run = False
                elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3) and not running_anim:
                    idx = e.key - pygame.K_1
                    dfa, pos = load(idx)
                    reset(clear_text=True)
                elif e.key == pygame.K_RETURN:
                    reset()
                    _, trace = dfa.run(text)
                    running_anim, last = True, pygame.time.get_ticks()
                elif e.key == pygame.K_BACKSPACE and not running_anim:
                    text = text[:-1]
                    reset()
                elif e.unicode in dfa.alphabet and not running_anim and len(text) < 24:
                    text += e.unicode
                    reset()

        now = pygame.time.get_ticks()
        if running_anim and now - last >= STEP_MS:
            last = now
            if consumed < len(trace):
                src, _, dst = trace[consumed]
                current, hot, consumed = dst, (src, dst), consumed + 1
            if consumed == len(trace):
                running_anim = False
                result = current in dfa.accepting

        screen.fill(BG)
        screen.blit(big.render(f"{idx + 1}. {dfa.name}", True, INK), (20, 14))
        screen.blit(font.render(dfa.description, True, MUTED), (20, 48))
        draw_edges(screen, font, dfa, pos, hot)
        draw_states(screen, font, dfa, pos, current)

        x = 20
        screen.blit(font.render("Input:", True, MUTED), (x, 520))
        x += 70
        for i, ch in enumerate(text):
            c = MUTED if i < consumed else INK
            surf = big.render(ch, True, c)
            screen.blit(surf, (x, 512))
            if i == consumed and running_anim:
                pygame.draw.line(screen, TEAL, (x, 546), (x + surf.get_width(), 546), 3)
            x += 24
        if result is not None:
            msg, col = ("ACCEPTED", GREEN) if result else ("REJECTED", RED)
            screen.blit(big.render(msg, True, col), (20, 560))
        screen.blit(font.render("1/2/3 pick DFA | type 0 or 1 | ENTER run | BACKSPACE delete",
                                True, MUTED), (20, 605))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()

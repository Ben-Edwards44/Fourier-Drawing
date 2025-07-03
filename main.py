import svg
import fourier

import math
import pygame
import random


PRESETS = (
    ("images/8thNote.svg", 8),
    ("images/he.svg", 10),
    ("images/omega.svg", 8),
    ("images/Omega.svg", 8),
    ("images/pi.svg", 8),
    ("images/Sigma.svg", 8),
    ("images/lambda.svg", 8),
    ("images/mu.svg", 8)
)

USED_PRESET = -1  #-1 for random

NUM_FOURIER_COEFFS = 400

T_STEP = 0.0005

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

MIN_DIST_SQ = 1
POINT_TTL = int(1 / T_STEP)


pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class Vector:
    COLOUR = (150, 150, 150)

    ARROWHEAD_ANGLE = 30
    ARROWHEAD_SCALE = 0.25

    def __init__(self, start_x, end_x, start_y, end_y):
        self.start_x = int(start_x)
        self.end_x = int(end_x)

        self.start_y = int(start_y)
        self.end_y = int(end_y)

        self.length = math.sqrt((start_x - end_x)**2 + (start_y - end_y)**2)

    def draw_circle(self):
        cent_x = (self.start_x + self.end_x) // 2
        cent_y = (self.start_y + self.end_y) // 2

        r = int(self.length) // 2

        pygame.draw.circle(window, Vector.COLOUR, (cent_x, cent_y), r, 1)

    def draw_arrowhead(self):
        start_x = self.end_x - (self.end_x - self.start_x) * Vector.ARROWHEAD_SCALE
        start_y = self.end_y - (self.end_y - self.start_y) * Vector.ARROWHEAD_SCALE

        perp_length = Vector.ARROWHEAD_SCALE * self.length * math.tan(math.radians(Vector.ARROWHEAD_ANGLE))
        perp_scale = perp_length / self.length

        #NOTE: x, y seem to be flipped (and x negated) because we are rotating angle by 90 degrees
        perp_x = -(self.end_y - self.start_y) * perp_scale
        perp_y = (self.end_x - self.start_x) * perp_scale

        point1 = (self.end_x, self.end_y)
        point2 = (start_x + perp_x, start_y + perp_y)
        point3 = (start_x - perp_x, start_y - perp_y)

        pygame.draw.polygon(window, Vector.COLOUR, (point1, point2, point3))

    def draw(self):
        self.draw_circle()
        self.draw_arrowhead()

        pygame.draw.line(window, Vector.COLOUR, (self.start_x, self.start_y), (self.end_x, self.end_y), 2)


def get_samples():
    if USED_PRESET == -1:
        filename, scale = random.choice(PRESETS)
    else:
        filename, scale = PRESETS[USED_PRESET]

    return svg.parse_svg(filename, scale)


def get_sample_offsets(x_samples, y_samples):
    desired_cent_x = SCREEN_WIDTH // 2
    desired_cent_y = SCREEN_HEIGHT // 2

    cent_x = sum(x_samples) / len(x_samples)
    cent_y = sum(y_samples) / len(y_samples)

    return desired_cent_x - cent_x, desired_cent_y - cent_y


def construct_vecs(components, t, offset_x, offset_y):
    start_x = offset_x
    start_y = offset_y

    vecs = []
    for i in components:
        end_x = start_x + i.get_real(t)
        end_y = start_y + i.get_imaginary(t)

        vecs.append(Vector(start_x, end_x, start_y, end_y))

        start_x = end_x
        start_y = end_y

    return vecs


def add_end_coords(vecs, end_coords):
    new_x = vecs[-1].end_x
    new_y = vecs[-1].end_y

    if len(end_coords) == 0:
        add = True
    else:
        prev_x, prev_y, _ = end_coords[-1]
        dist_sq = (new_x - prev_x)**2 + (new_y - prev_y)**2

        add = dist_sq >= MIN_DIST_SQ
        
    if add:
        end_coords.append([new_x, new_y, POINT_TTL])


def update_end_coords(end_coords):
    filter_func = lambda i: i[2] > 0
    decrement_ttl = lambda i: i[:2] + [i[2] - 1]

    decremented = map(decrement_ttl, end_coords)
    pruned = list(filter(filter_func, decremented))

    return pruned


def draw(vecs, end_coords):
    window.fill((0, 0, 0))

    for i in vecs:
        i.draw()

    for i, x in enumerate(end_coords):
        if i == 0:
            continue

        colour = [255 * x[2] / POINT_TTL] * 3

        pygame.draw.line(window, colour, x[:2], end_coords[i - 1][:2])

    pygame.display.update()


def main():
    x_samples, y_samples = get_samples()
    offset_x, offset_y = get_sample_offsets(x_samples, y_samples)

    """
    from time import sleep

    for x, y in zip(x_samples, y_samples):
        pygame.draw.circle(window, (255, 255, 255), (x + offset_x, y + offset_y), 2)

        pygame.display.update()
        #sleep(0.01)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()
    #"""
                
    components = fourier.fourier_transform(x_samples, y_samples, NUM_FOURIER_COEFFS)

    end_coords = []

    t = 0
    while True:
        t += T_STEP

        vecs = construct_vecs(components, t, offset_x, offset_y)
        draw(vecs, end_coords)

        add_end_coords(vecs, end_coords)

        end_coords = update_end_coords(end_coords)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()


main()
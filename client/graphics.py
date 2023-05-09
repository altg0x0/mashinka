import math
import pygame


def create_rotated_rect(center, angle, width, height):
    rect = pygame.Rect(0, 0, width, height)
    rotated_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    rotated_surface.fill((255, 50, 0))
    rotated_rect = rect.copy()
    rotated_rect.center = center
    rotated_surface = pygame.transform.rotate(rotated_surface, -angle * 180 / math.pi)
    return rotated_surface, rotated_rect

def draw_rotated_rect(surface, center, size, angle):
    rect = pygame.Surface(size, pygame.SRCALPHA)
    rect.fill((255, 200, 0))
    rotated_rect = pygame.transform.rotate(rect, -angle * 180 / math.pi)
    rect_center = (center[0] - rotated_rect.get_width() // 2, center[1] - rotated_rect.get_height() // 2)
    surface.blit(rotated_rect, rect_center)
    return pygame.Rect(rect_center, rotated_rect.get_size())
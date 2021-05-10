from loader.initialization import init_game_variables
from loader.data_loader import load_game
from render import render_img
from loader.data_loader import quit_game
from input_handlers import InputHandler
from typing import Optional, Any
from interactables import MouseInteractable
from util import create_surface_with_text

import pygame
import color
import tcod
import time
import random
import option
import credits

class TitleInputHandler(InputHandler):
    """
    Handles every inputs that are made in the title screen.
    """
    def __init__(self, screen):
        super().__init__(screen=screen)
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        font_size = 32
        font = pygame.font.Font("./resources/fonts/NanumMyeongjo.ttf", font_size)
        font_enhanced = pygame.font.Font("./resources/fonts/NanumMyeongjo.ttf", int(font_size * 1.25))

        self.add_mouse_interactable(MouseInteractable((center_x, center_y), {
            "default": create_surface_with_text("New Game", color.white, None, font),
            "mouse_on": create_surface_with_text("New Game", color.white, None, font_enhanced)}, None, mouse_down_return="new_game"))
        self.add_mouse_interactable(MouseInteractable((center_x, center_y + font_size * 2), {
            "default": create_surface_with_text("Load Game", color.white, None, font),
            "mouse_on": create_surface_with_text("Load Game", color.white, None, font_enhanced)}, None, mouse_down_return="load_game"))
        self.add_mouse_interactable(MouseInteractable((center_x, center_y + font_size * 4), {
            "default": create_surface_with_text("Options", color.white, None, font),
            "mouse_on": create_surface_with_text("Options", color.white, None, font_enhanced)}, None, mouse_down_return="options"))
        self.add_mouse_interactable(MouseInteractable((center_x, center_y + font_size * 6), {
            "default": create_surface_with_text("Credits", color.white, None, font),
            "mouse_on": create_surface_with_text("Credits", color.white, None, font_enhanced)}, None, mouse_down_return="credits"))
        self.add_mouse_interactable(MouseInteractable((center_x, center_y + font_size * 8), {
            "default": create_surface_with_text("Quit Game", color.white, None, font),
            "mouse_on": create_surface_with_text("Quit Game", color.white, None, font_enhanced)}, None, mouse_down_return="quit_game"))

    def ev_keydown(self, event: pygame.event.Event, pressed) -> Optional[str]:
        if event.key == pygame.K_n:  # New Game
            return "new_game"
        elif event.key == pygame.K_l:  # Load Game
            return "load_game"
        elif event.key == pygame.K_o:  # Option
            return "options"
        elif event.key == pygame.K_c:  # Credits
            return "credits"
        elif event.key == pygame.K_q:  # Quit Game
            return "quit_game"
        return None

    def handle_title_event(self, event_id: str, screen, cfg) -> Any:
        if event_id == "new_game":
            player, engine = init_game_variables(screen, cfg)
            engine.message_log.add_message(f"{player.name}님, 지오파이트의 세계에 오신 것을 환영합니다!", color.welcome_text)
            return player, engine
        elif event_id == "load_game":
            try:
                player, engine = load_game(cfg)
                engine.message_log.add_message(f"{player.name}님, 지오파이트의 세계에 돌아오신 것을 환영합니다!", color.welcome_text)
                return player, engine
            except:
                # console.print(5, 5, string="세이브 파일을 찾지 못했습니다.", fg=color.red)
                return None
        elif event_id == "options":
            # TODO
            # option.option_event_handler(console=console, context=context, game_started=False)
            render_title(screen)
        elif event_id == "credits":
            # TODO
            # credits.credit_event_handler(console=console, context=context)
            render_title(screen)
        elif event_id == "quit_game":
            quit_game()


def render_titlescreen(eventhandler, screen) -> None:
    eventhandler.render_interactables(pygame.mouse.get_pos())
    pygame.display.update()
    screen.fill((0, 0, 0))


def title_event_handler(screen, cfg) -> Optional:
    """
    Core function that handles most of the things related to the title screen.
    Title screen loop is handled here.
    """
    # Title screen loop
    title_input_handler = TitleInputHandler(screen=screen)

    while True:
        render_titlescreen(title_input_handler, screen)
        pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            title_action = title_input_handler.handle_title_event(title_input_handler.dispatch_event(event, pressed), screen, cfg)
            if title_action:
                return title_action


def render_title(screen) -> None:
    """
    Render title screen.
    """
    pass

# DO NOT modify or add any import statements
from a2_support import *
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, Callable

# Name: Bao Ho
# Student Number: 42279879
# ----------------

# Write your classes and functions here

class Tile:
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return "T"

    def get_tile_name(self):
        return self.__class__.__name__

    def is_blocking(self):
        return False

class Ground(Tile):
    def __str__(self):
        return " "

class Mountain(Tile):
    def __str__(self):
        return "M"

    def is_blocking(self):
        return True

class Building(Tile):
    def __init__(self, initial_health):
        self.health = initial_health

    def __str__(self):
        return str(self.health)

    def is_blocking(self):
        return self.health > 0

    def is_destroyed(self):
        return self.health == 0

    def damage(self, damage):
        self.health -= damage
        self.health = max(0, min(self.health, 9))

class Board:
    def __init__(self, board):
        self.tiles = [[self._create_tile(tile_str) for tile_str in row] for row in board]

    def __repr__(self):
        return f"Board({self.tiles})"

    def __str__(self):
        return "\n".join("".join(str(tile) for tile in row) for row in self.tiles)

    def get_dimensions(self):
        return len(self.tiles), len(self.tiles[0])

    def get_tile(self, position):
        row, col = position
        return self.tiles[row][col]

    def get_buildings(self):
        buildings = {}
        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):
                if isinstance(tile, Building):
                    buildings[(row_index, col_index)] = tile
        return buildings

    def _create_tile(self, tile_str):
        if tile_str == " ":
            return Ground()
        elif tile_str == "M":
            return Mountain()
        elif tile_str.isdigit():
            return Building(int(tile_str))
        else:
            raise ValueError("Invalid tile string")

class Entity:
    def __init__(self, position, health, speed, strength):
        self.position = position
        self.health = health
        self.speed = speed
        self.strength = strength

    def __repr__(self):
        return f"{self.__class__.__name__}({self.position}, {self.health}, {self.speed}, {self.strength})"

    def __str__(self):
        return f"{self.get_symbol()},{self.position[0]},{self.position[1]},{self.health},{self.speed},{self.strength}"

    def get_symbol(self):
        return 'E'

    def get_name(self):
        return self.__class__.__name__

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_health(self):
        return self.health

    def get_speed(self):
        return self.speed

    def get_strength(self):
        return self.strength

    def damage(self, damage):
        self.health = max(0, self.health - damage)

    def is_alive(self):
        return self.health > 0

    def is_friendly(self):
        return False

    def get_targets(self):
        row, col = self.position
        return [(row, col + 1), (row, col - 1), (row + 1, col), (row - 1, col)]

    def attack(self, entity):
        entity.damage(self.strength)


class Mech(Entity):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)
        self.active = True
        self.old_position = position

    def get_old_position(self):
        return self.old_position

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def is_active(self):
        return self.active

    def set_position(self, position):
        self.old_position = self.position
        self.position = position

    def is_friendly(self):
        return True


class TankMech(Mech):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)

    def get_symbol(self):
        return 'T'

    def get_targets(self):
        row, col = self.position
        return [(row, col + i) for i in range(-5, 6)]


class HealMech(Mech):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)

    def get_symbol(self):
        return 'H'

    def get_strength(self):
        return -self.strength

    def attack(self, entity):
        if entity.is_friendly():
            entity.damage(-self.strength)


class Enemy(Entity):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)
        self.objective = position

    def get_objective(self):
        return self.objective

    def update_objective(self, entities, buildings):
        self.objective = self.position

    def is_friendly(self):
        return False


class Scorpion(Enemy):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)

    def get_symbol(self):
        return 'S'

    def get_targets(self):
        row, col = self.position
        return [(row, col + 1), (row, col - 1), (row + 1, col), (row - 1, col), 
                (row, col + 2), (row, col - 2), (row + 2, col), (row - 2, col)]


class Firefly(Enemy):
    def __init__(self, position, health, speed, strength):
        super().__init__(position, health, speed, strength)

    def get_symbol(self):
        return 'F'

    def get_targets(self):
        row, col = self.position
        return [(row + i, col) for i in range(-5, 6)]

    
class BreachModel:
    def __init__(self, board, entities):
        self.board = board
        self.entities = entities

    def __str__(self):
        entities_str = '\n'.join(str(entity) for entity in self.entities)
        return str(self.board) + '\n\n' + entities_str

    def get_board(self):
        return self.board

    def get_entities(self):
        return self.entities

    def has_won(self) -> bool:
        # Check if all enemies are destroyed
        if all(entity.entity_type == EntityType.ENEMY for entity in self.entities if entity.health <= 0):
            # Check if at least one mech is not destroyed
            if any(entity.entity_type == EntityType.MECH and entity.health > 0 for entity in self.entities):
                # Check if at least one building on the board is not destroyed
                if any(tile.tile_type == "building" and tile.health > 0 for row in self.board for tile in row):
                    return True
        return False

    def has_lost(self) -> bool:
        # Check if all buildings on the board are destroyed
        if all(tile.tile_type == "building" and tile.health <= 0 for row in self.board for tile in row):
            return True
        # Check if all mechs are destroyed
        if all(entity.entity_type == EntityType.MECH and entity.health <= 0 for entity in self.entities):
            return True
        return False

    

    def initialize_game(self):
        # Implement game reinitialization logic here
        pass

    def entity_positions(self):
        return {(entity.get_position()): entity for entity in self.entities}

    def get_valid_movement_positions(self, entity):
        # Implement based on game rules
        pass

    def attempt_move(self, entity, position):
        # Implement based on game rules
        pass

    def undo_move(self):
        # Implement based on game rules
        pass

    def ready_to_save(self):
        # Implement based on game rules
        pass

    def assign_objectives(self):
        # Implement based on game rules
        pass

    def move_enemies(self):
        # Implement based on game rules
        pass

    def make_attack(self, entity):
        # Implement based on game rules
        pass

    def end_turn(self):
        # Implement based on game rules
        pass

from a2_support import AbstractGrid


class GameGrid(AbstractGrid):
    def __init__(self, master, dimensions, size):
        super().__init__(master, dimensions, size)

    def redraw(self, board, entities, highlighted=None, movement=False):
        # Implement the redraw method to display the game grid
        pass

    def bind_click_callback(self, click_callback):
        # Implement binding of click events to a callback function
        pass

class SideBar(AbstractGrid):
    def __init__(self, master, dimensions, size):
        super().__init__(master, dimensions, size)

    def display(self, entities):
        # Implement the display method to show entity properties on the sidebar
        pass

class ControlBar(tk.Frame):
    def __init__(self, master, save_callback=None, load_callback=None, undo_callback=None, turn_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.save_button = tk.Button(self, text="Save", command=save_callback)
        self.load_button = tk.Button(self, text="Load", command=load_callback)
        self.undo_button = tk.Button(self, text="Undo", command=undo_callback)
        self.turn_button = tk.Button(self, text="End Turn", command=turn_callback)
        self.save_button.pack(side=tk.LEFT)
        self.load_button.pack(side=tk.LEFT)
        self.undo_button.pack(side=tk.LEFT)
        self.turn_button.pack(side=tk.LEFT)



class BreachView:
    def __init__(self, root, board_dims, save_callback=None, load_callback=None, undo_callback=None, turn_callback=None):
        self.root = root
        self.root.title("Into The Breach")

        self.game_grid = GameGrid(self.root, board_dims, (PIXEL_SCALE * GRID_SIZE, PIXEL_SCALE * GRID_SIZE))
        self.side_bar = SideBar(self.root, board_dims, (PIXEL_SCALE * GRID_SIZE // 4, PIXEL_SCALE * GRID_SIZE))
        self.control_bar = ControlBar(self.root, save_callback, load_callback, undo_callback, turn_callback)

        self.game_grid.grid(row=1, column=1)
        self.side_bar.grid(row=1, column=2)
        self.control_bar.grid(row=2, column=1, columnspan=2)

    def bind_click_callback(self, click_callback):
        self.game_grid.bind_click_callback(click_callback)

    def redraw(self, board, entities, highlighted=None, movement=False):
        self.game_grid.redraw(board, entities, highlighted, movement)
        self.side_bar.display(entities)

import os

class IntoTheBreach:
    def __init__(self, root: tk.Tk, game_file: str) -> None:
        self.root = root
        self.model = BreachModel.load(game_file)
        self.view = BreachView(self.root, self.model.get_board().get_dimensions(), self.save_game, self.load_game, self.undo_move, self.end_turn)
        self.focussed_entity: Optional[Entity] = None

    def redraw(self) -> None:
        self.view.redraw(self.model.get_board(), self.model.get_entities(), self.model.get_valid_movement_positions(self.focussed_entity))

    def set_focussed_entity(self, entity: Optional[Entity]) -> None:
        self.focussed_entity = entity
        self.redraw()

    def make_move(self, position: tuple[int, int]) -> None:
        if self.focussed_entity:
            self.model.attempt_move(self.focussed_entity, position)
            self.set_focussed_entity(None)

    def load_model(self, file_path: str) -> None:
        try:
            self.model = BreachModel.load(file_path)
            self.redraw()
        except IOError as e:
            messagebox.showerror("IOError", str(e))

    def save_game(self) -> None:
        if self.model.ready_to_save():
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if file_path:
                self.model.save(file_path)
        else:
            messagebox.showerror("Error", "You can only save at the beginning of your turn.")

    def load_game(self) -> None:
        file_path = filedialog.askopenfilename(defaultextension=".txt")
        if file_path:
            self.load_model(file_path)

    def undo_move(self) -> None:
        self.model.undo_move()
        self.redraw()

    def end_turn(self) -> None:
        self.model.end_turn()
        if self.model.has_won():
            messagebox.showinfo("Win", "You won!")
        elif self.model.has_lost():
            messagebox.showinfo("Loss", "You lost!")
        else:
            self.redraw()

    def handle_click(self, position: tuple[int, int]) -> None:
        if self.model.get_board().is_valid_position(position):
            entity = self.model.entity_at_position(position)
            if entity:
                self.set_focussed_entity(entity)
            else:
                self.make_move(position)

def play_game(root: tk.Tk, file_path: str) -> None:
    game = IntoTheBreach(root, file_path)
    root.mainloop()

# Additional entity classes can be added as needed



def main() -> None:
    """The main function"""
    root = tk.Tk()
    play_game(root, "/Users/BaoHo/Downloads/a2/levels/level1.txt")
    pass

if __name__ == "__main__":
    main()

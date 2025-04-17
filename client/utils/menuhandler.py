from utils.ui import panel, text
from typing_extensions import overload

class menu:
    def __init__(self, elements:list[panel, text]):
        self.elements = elements

    def render(self):
        for element in self.elements:
            element.render()


class menuHandler:
    def __init__(self, menus:dict[str,menu]):
        self.menus = menus
  
    def render_menu_index(self, index:int):
        list(self.menus.values())[index].render()
  
    def render_menu_name(self, name:str):
        self.menus[name].render()
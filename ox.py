
from blessed import Terminal
from rich import print as rprint
from rich.text import Text
from rich.layout import Layout
from rich.repr import rich_repr
from rich.panel import Panel
from rich.console import Console
from rich.highlighter import ReprHighlighter
import cached_object

console = Console()

highlighter = ReprHighlighter()

PUBLIC = "PUBLIC"
PRIVATE = "PRIVATE"
_term = Terminal()

# TODO methods filter
# or just a type filter?
# Move to next type with {}


class Explorer:
    def __init__(self, obj):
        obj = cached_object.CachedObject(obj)
        # Figure out all the attributes of the current obj's attributes
        obj.cache_attributes()
        self.head_obj = obj
        self.current_obj = obj
        self.obj_stack = []
        self.term = _term

    @property
    def panel_height(self):
        return self.term.height - 8

    def explore(self):
        key = None
        print(self.term.clear, end='')
        with self.term.cbreak(), self.term.hidden_cursor():
            while key not in ('q', 'Q'):
                self.draw()
                key = self.term.inkey()

                # Switch between public and private attributes
                if key in ("[", "]"):
                    if self.current_obj.attribute_type == PUBLIC:
                        self.current_obj.attribute_type = PRIVATE

                    elif self.current_obj.attribute_type == PRIVATE:
                        self.current_obj.attribute_type = PUBLIC

                # move selected attribute down
                elif key == "j":
                    self.current_obj.move_down(self.panel_height)

                # move selected attribute up
                elif key == "k":
                    self.current_obj.move_up()

                elif key == "g":
                    self.current_obj.move_top()

                elif key == "G":
                    self.current_obj.move_bottom(self.panel_height)

                # Enter
                elif key in ["\n", "l"]:
                    if self.current_obj.attribute_type == PUBLIC:
                        new_cached_obj = self.current_obj[self.current_obj.selected_public_attribute]
                        if new_cached_obj.obj and not callable(new_cached_obj.obj):
                            self.obj_stack.append(self.current_obj)
                            self.current_obj = new_cached_obj
                            self.current_obj.cache_attributes()

                    elif self.current_obj.attribute_type == PRIVATE:
                        new_cached_obj = self.current_obj[self.current_obj.selected_private_attribute]
                        if new_cached_obj.obj and not callable(new_cached_obj.obj):
                            self.obj_stack.append(self.current_obj)
                            self.current_obj = new_cached_obj
                            self.current_obj.cache_attributes()

                # Escape
                elif key in ["\x1b", "h"] and self.obj_stack:
                    self.current_obj = self.obj_stack.pop()

                elif key == "b":
                    breakpoint()

    def draw(self):
        print(self.term.home)
        layout = Layout()
        layout.split_column(
            Layout(name="head", size=1),
            Layout(name="body")
        )

        # TODO use highlighter
        layout["head"].update(highlighter(f"{self.current_obj.obj!r}"))

        layout["body"].split_row(
            Layout(name="explorer"),
            Layout(name="preview")
        )
        layout["body"]["preview"].ratio = 3
        current_obj_attributes = self.current_obj.get_current_obj_attr_panel()
        layout["body"]["explorer"].update(
            current_obj_attributes
        )
        layout["body"]["preview"].update(
            Panel(
                self.current_obj.selected_cached_attribute.preview,
            )
        )
        object_explorer = Panel(
            layout,
            padding=0,
            title="Object Explorer",
            height=self.term.height - 2
        )
        rprint(object_explorer, end='')


def ox(obj):
    explorer = Explorer(obj)
    explorer.explore()


if __name__ == "__main__":
    from importlib import reload
    reload(cached_object)
    ex = Explorer("hello")
    ox(ex)

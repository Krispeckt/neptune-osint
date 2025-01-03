from __future__ import annotations

from typing import TYPE_CHECKING

from anytree import Node, RenderTree

from utils import gradient_colorize, log_colorize, collect_modules
from utils.consts import BANNER

if TYPE_CHECKING:
    from utils.abc import BaseModule


def main() -> None:
    modules_dict = collect_modules("./modules")

    print(gradient_colorize(BANNER, start_color=0x5386E5, end_color=0xA1CAE3))
    print(log_colorize("Starting utility", color=0x5386E5, prefix=">"))

    modules_node = Node("modules")

    module_number = 1
    module_mapping: dict[int, BaseModule] = {}
    for module_name, module_list in modules_dict.items():
        parent_node = Node(f"{module_name}", parent=modules_node)
        for module in module_list:
            module_with_number = f"{module.name} (#{module_number})"
            Node(module_with_number, parent=parent_node)
            module_mapping[module_number] = module
            module_number += 1

    tree = ""
    for pre, fill, node in RenderTree(modules_node):
        tree += f">          {pre}{node.name}\n"

    print(gradient_colorize(tree[:len(tree) - 1], start_color=0x5386E5, end_color=0xA1CAE3))

    try:
        print(log_colorize("Choose a module", color=0x5386E5, prefix="<"), end="")
        selected_number = int(input())
        if selected_number in module_mapping:
            with module_mapping[selected_number] as module:
                module: BaseModule
                module.run()
        else:
            print("Invalid module number.")
    except ValueError:
        print("Please enter a valid number.")


if __name__ == '__main__':
    while True:
        main()

        print()
        print(log_colorize("Do you want to run another utility?", color=0x5386E5, prefix="<"), end="")
        awaiting = input()
        if awaiting.lower() not in ["yes", "y"]:
            break

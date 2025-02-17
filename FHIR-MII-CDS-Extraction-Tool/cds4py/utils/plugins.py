import importlib.util
import os
import logging

from cds4py.plugins.basecondition import BaseCondition
from cds4py.plugins.basemodifier import BaseModifier

logger = logging.getLogger(__name__)
def load_plugins():
    plugins = []
    plugin_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins", "conditions")
    print("plugin_folder", plugin_folder)
    for filename in os.listdir(plugin_folder):
        if filename.endswith(".py"):
            plugin_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugin_folder, filename))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr in dir(module):
                plugin_class = getattr(module, attr)
                if isinstance(plugin_class, type) and issubclass(plugin_class, BaseCondition) and plugin_class is not BaseCondition:
                    plugin_instance = plugin_class()
                    plugins.append(plugin_instance)
    return plugins


def load_modifiers():
    modifiers = []
    modifier_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins", "modifiers")
    for filename in os.listdir(modifier_folder):
        if filename.endswith(".py"):
            modifier_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(modifier_name, os.path.join(modifier_folder, filename))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr in dir(module):
                modifier_class = getattr(module, attr)
                if isinstance(modifier_class, type) and issubclass(modifier_class, BaseModifier) and modifier_class is not BaseModifier:
                    modifier_instance = modifier_class()
                    modifiers.append(modifier_instance)
    return modifiers


def apply_condition(value, condition, condition_value):
    if condition == "None" or not condition or condition == "":
        return True

    plugins = load_plugins()
    for plugin in plugins:
        if plugin.name == condition:
            return plugin.evaluate(value, condition_value)
    return False


def apply_modifier(value, modifier, modifier_value):
    if modifier == "None":
        return value
    if modifier_value is None:
        modifier_value = ""
    if modifier == "Prefix":
        return modifier_value + value
    if modifier == "Suffix":
        return value + modifier_value
    modifiers = load_modifiers()
    for mod in modifiers:
        if mod.name == modifier:
            return mod.modify(modifier_value, value)
    available_modifiers = [m.name for m in modifiers]
    logger.warning(f"Modifier {modifier} not found", available_modifiers)
    return value

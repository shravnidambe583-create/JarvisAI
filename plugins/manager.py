import os
import sys
import importlib.util
from typing import Dict, List, Callable

class BasePlugin:
    """Base class that all JARVIS X plugins must inherit from."""
    name = "BasePlugin"
    description = "Description of the plugin"
    version = "1.0.0"
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def get_commands(self) -> Dict[str, Callable]:
        """
        Returns a dictionary mapping phrase trigger keywords to execution callbacks.
        Example: {'check stocks': self.check_stocks}
        """
        return {}

class PluginManager:
    """Loads, registers, and manages custom JARVIS X plugins dynamically from the plugins folder."""
    
    def __init__(self, orchestrator, plugins_dir="plugins"):
        self.orchestrator = orchestrator
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), plugins_dir)
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Add plugins dir to sys path
        if self.plugins_dir not in sys.path:
            sys.path.append(self.plugins_dir)
            
        self.plugins: Dict[str, BasePlugin] = {}
        self.command_hooks: Dict[str, Callable] = {}

    def load_plugins(self):
        """Scans the plugins directory and dynamically loads all valid plugins."""
        self.plugins.clear()
        self.command_hooks.clear()
        
        print(f"[Plugins] Scanning for custom plugins in {self.plugins_dir}...")
        
        if not os.path.exists(self.plugins_dir):
            return
            
        for file in os.listdir(self.plugins_dir):
            if file.endswith(".py") and file != "__init__.py" and not file.startswith("base"):
                module_name = file[:-3]
                file_path = os.path.join(self.plugins_dir, file)
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None or spec.loader is None:
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for subclasses of BasePlugin inside the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr is not BasePlugin):
                            
                            # Instantiate the plugin
                            plugin_instance = attr(self.orchestrator)
                            self.plugins[plugin_instance.name] = plugin_instance
                            
                            # Register its command hooks
                            commands = plugin_instance.get_commands()
                            for cmd, callback in commands.items():
                                self.command_hooks[cmd.lower().strip()] = callback
                                
                            print(f"  ✅ Loaded Plugin: {plugin_instance.name} (v{plugin_instance.version}) - {len(commands)} commands registered")
                except Exception as e:
                    print(f"  ❌ Failed to load plugin {file}: {e}")

    def execute_plugin_command(self, phrase: str) -> str:
        """
        Checks if the voice phrase matches any registered plugin keywords.
        Executes the callback and returns response if found, else None.
        """
        phrase = phrase.lower().strip()
        for trigger, callback in self.command_hooks.items():
            if trigger in phrase:
                print(f"[Plugins] Trigger '{trigger}' matched! Executing plugin callback...")
                try:
                    # Pass the query phrase to the plugin
                    return callback(phrase)
                except Exception as e:
                    return f"Error executing plugin command: {e}"
        return None

    def get_plugin_list(self) -> List[Dict[str, str]]:
        """Returns a list of dicts summarizing loaded plugins for the marketplace UI."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "version": p.version,
                "commands": ", ".join(p.get_commands().keys())
            } for p in self.plugins.values()
        ]

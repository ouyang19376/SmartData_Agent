from typing import Callable, Any

Tool = Callable[..., Any]

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._descriptions: dict[str, str] = {}

    def register(self, name: str, description: str, func: Tool) -> None:
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = func
        self._descriptions[name] = description

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    @property
    def descriptions(self) -> dict[str, str]:
        return dict(self._descriptions)

    @property
    def names(self) -> set[str]:
        return set(self._tools)

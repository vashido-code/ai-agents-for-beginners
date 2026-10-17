from .base import Provider


def get_provider(name: str) -> Provider:
    if name == "mock":
        from .mock import MockProvider
        return MockProvider()
    if name == "kling":
        from .kling import KlingProvider
        return KlingProvider()
    if name == "comfyui":
        from .comfyui import ComfyUIProvider
        return ComfyUIProvider()
    raise ValueError(f"Unknown provider '{name}'. Use mock, kling or comfyui.")

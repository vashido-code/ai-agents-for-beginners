from pathlib import Path
from typing import Protocol


class Provider(Protocol):
    """A generation backend. Both calls block until the file is written to `out`."""

    name: str

    def try_on(self, person: Path, garment: Path, category: str, out: Path) -> Path:
        """Dress the person in `person` in the garment from `garment`."""
        ...

    def image_to_video(self, image: Path, prompt: str, negative: str, seconds: int, out: Path) -> Path:
        """Animate `image` into a short clip."""
        ...

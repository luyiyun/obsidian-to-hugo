import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class FrontMatterBase:
    fm_type: Literal["yaml", "toml", "json"] = "yaml"

    def __post_init__(self):
        if self.fm_type != "yaml":
            raise ValueError(f"Unsupported format {self.fm_type}.")
        # re.DAOTALL令.可以匹配到换行符
        # ^表示开头，\s*?表示任意空白字符
        self.regex = re.compile(r"^\s*?---\n(.*?)\n---\n", re.DOTALL)

    def __call__(self, fn: Path, content: str) -> str:
        raise NotImplementedError

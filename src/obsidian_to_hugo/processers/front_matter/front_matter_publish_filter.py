import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from .base import FrontMatterBase


logger = logging.getLogger(__name__)


@dataclass
class PublishFilter(FrontMatterBase):
    def __call__(self, fn: Path, content: str) -> bool:
        match = self.regex.search(content)
        if not match:
            logger.info(f"No front matter found in {fn}.")
            return False

        front_matter = match.group(1)  # 匹配到的内容
        fm_dict = yaml.load(front_matter, Loader=yaml.FullLoader)
        return fm_dict.get("publish", False)

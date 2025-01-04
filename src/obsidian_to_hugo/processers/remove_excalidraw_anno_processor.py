import re
import logging
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class ExcalidrawAnnotationProcessor:
    def __post_init__(self):
        # re.DAOTALL令.可以匹配到换行符
        self.regex = re.compile(r"%%.*?Edit in Excalidraw.*?%%")

    def __call__(self, fn: Path, content: str) -> str:
        if not self.regex.search(content):
            logger.info(f"No Excalidraw annotation found in {fn}.")
            return content

        logger.info(
            f"{len(self.regex.findall(content))} Excalidraw annotations found in {fn}."
        )
        content = self.regex.sub("", content)
        return content

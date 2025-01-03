import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from datetime import datetime

import yaml


logger = logging.getLogger(__name__)


@dataclass
class MathFormulaProcessor:
    def __post_init__(self):
        # re.DAOTALL令.可以匹配到换行符
        self.block_reg = re.compile(r"\$\$.*?\$\$.*?\n", re.DOTALL)

    def __call__(self, fn: Path, content: str) -> str:
        # blocks = self.block_reg.findall(content)
        if not self.block_reg.search(content):
            logger.info(f"No block math formula found in {fn}.")
            return content

        blocks = self.block_reg.findall(content)
        others = self.block_reg.split(content)
        print(len(blocks))
        print(len(others))
        content = ""
        for block, other in zip(blocks, others):
            # fixit对于公式，需要加上{{< raw >}}{{< /raw >}}
            content += other
            if other.endswith("\n> "):
                content += "{{< raw >}}\n"
                content += block.replace("\n> ", "\n")
                content += "{{< /raw >}}\n"
            else:
                content += "\n{{< raw >}}\n"
                content += block
                content += "{{< /raw >}}\n"
        return content

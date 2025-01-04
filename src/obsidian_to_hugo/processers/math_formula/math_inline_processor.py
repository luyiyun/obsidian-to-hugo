import re
import logging
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class InlineMathEquationProcessor:
    def __post_init__(self):
        # self.regex = re.compile(r"\n(.*?)(\$.+?\$.*?)\n")
        self.reg_equ = re.compile(r"\$(.+?)\$")
        self.regs_sub = [(re.compile(r"_"), "\\_"), (re.compile(r"\^"), ("\\^"))]

    def __call__(self, fn: Path, content: str) -> str:
        # blocks = self.block_reg.findall(content)
        if not self.reg_equ.search(content):
            logger.info(f"No inline math formula found in {fn}.")
            return content

        # 这里我们不再使用{{< raw >}} {{< /raw >}}进行包裹的方式，因为
        # 1. 如果只包裹一行中的公式部分，会导致包裹部分被渲染为单独的一行
        # 2. 如果直接包裹一行，则会让一行中其他的格式失效，比如****将不会渲染为粗体
        # 这里我们选择的方式是，对其他可能进行转义处理的部分再进行一次转义，这里使用
        # 正则表达式的方式来实现。
        # 这里主要进行的改变是：_ -> \_ 和 ^ -> \^。
        # 目前都达到了我想要的效果。
        parts = self.reg_equ.split(content)
        others = parts[::2]
        equations = parts[1::2]
        logger.info(f"{len(equations)} lines with inline math equation found in {fn}.")
        content = ""
        for equa, other in zip(equations, others):
            content += other
            for reg, sub in self.regs_sub:
                equa = reg.sub(sub, equa)
            content += f" \\\\({equa}\\\\) "
        content += others[-1]  # others比分隔符多一个，需要加上
        return content

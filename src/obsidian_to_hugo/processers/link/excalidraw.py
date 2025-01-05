import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class ExcalidrawProcessor:
    ob_asset_dir: Path | str
    hugo_asset_dir: Path | str
    insert_type: Literal["inline", "file"] = "file"
    # NOTE: inline模式无法在外面套div来进行居中操作。

    def __post_init__(self):
        if isinstance(self.ob_asset_dir, str):
            self.ob_asset_dir = Path(self.ob_asset_dir)
        if isinstance(self.hugo_asset_dir, str):
            self.hugo_asset_dir = Path(self.hugo_asset_dir)
        # self.regex = re.compile(r"!\[\[(.+?)\.excalidraw(((?!png).)*?)\]\]")
        self.regex = re.compile(r"!\[\[(.+?)\.excalidraw((?!png).)*?\]\]")
        self.regex_excali = re.compile(r"```json(.+?)```", re.DOTALL)

    def __call__(self, fn: Path, content: str) -> str:
        if not self.regex.search(content):
            logger.info(f"No excalidraw link found in {fn}.")
            return content

        parts = self.regex.split(content)
        others = parts[::3]
        fn_prefixs = parts[1::3]
        logger.info(f"Found {len(fn_prefixs)} excalidraw links in {fn}.")

        # 读取excalidraw文件，并提取出其中的绘图json代码
        insert_contents = []
        for fn_prefix in fn_prefixs:
            excalidraw_full_fn = list(
                self.ob_asset_dir.rglob(f"{fn_prefix}.excalidraw.md")
            )
            if not excalidraw_full_fn:
                logger.warning(
                    f"Excalidraw file not found for {fn_prefix}.excalidraw in {fn}."
                )
                continue
            if len(excalidraw_full_fn) > 1:
                logger.warning(
                    f"Multiple excalidraw files found for {fn_prefix}.excalidraw in {fn}, "
                    "only the first one will be used."
                )

            excalidraw_full_fn = excalidraw_full_fn[0]
            with open(excalidraw_full_fn, "r", encoding="utf-8") as f:
                excalidraw_content = f.read()
            excalidraw_json = self.regex_excali.search(excalidraw_content)
            if not excalidraw_json:
                logger.warning(
                    f"Excalidraw file {excalidraw_full_fn} does not contain a valid json code."
                )
                insert_contents.append(f"![[{fn_prefix}.excalidraw]]")
                continue

            json_content = excalidraw_json.group(1)

            if self.insert_type == "inline":
                insert_contents.append(
                    "{{< kroki _type=excalidraw >}}\n"
                    f"{json_content}"
                    "{{< /kroki >}}\n"
                )
            else:
                excalidraw_relat_fn = str(
                    excalidraw_full_fn.relative_to(self.ob_asset_dir)
                )
                excalidraw_relat_fn = Path(
                    ".".join(excalidraw_relat_fn.split(".")[:-1]) + ".json"
                )
                excalidraw_target_fn = self.hugo_asset_dir / excalidraw_relat_fn
                if not excalidraw_target_fn.parent.exists():
                    excalidraw_target_fn.parent.mkdir(parents=True, exist_ok=True)
                excalidraw_target_fn.write_text(json_content, encoding="utf-8")
                logger.info(
                    f"Copying valid excalidraw content from {excalidraw_full_fn} into {excalidraw_target_fn}."
                )
                # NOTE: _name那里必须是双引号，不然会报错
                insert_contents.append(
                    "<div align='center'>\n"
                    f'{{{{< kroki _type=excalidraw _name="{excalidraw_relat_fn.as_posix()}" >}}}}\n'
                    "</div>\n"
                )

        # 将新的链接和其他内容组合成新的content
        content = ""
        for icontent, other in zip(insert_contents, others):
            content += other
            content += icontent
        content += others[-1]  # others比分隔符多一个，需要加上
        return content

import os
import re
import shutil
import logging
from dataclasses import dataclass
from pathlib import Path

from .utils import split_content_by_regex


logger = logging.getLogger(__name__)


@dataclass
class ImageLinkProcessor:
    ob_asset_dir: Path | str
    hugo_asset_dir: Path | str

    def __post_init__(self):
        if isinstance(self.ob_asset_dir, str):
            self.ob_asset_dir = Path(self.ob_asset_dir)
        if isinstance(self.hugo_asset_dir, str):
            self.hugo_asset_dir = Path(self.hugo_asset_dir)
        self.regex = re.compile(r"!\[\[(.+?)\]\]", re.DOTALL)

    def __call__(self, fn: Path, content: str) -> str:
        if not self.regex.search(content):
            logger.info(f"No obsidian-style image link found in {fn}.")
            return content

        others, img_links = split_content_by_regex(self.regex, content, True)
        logger.info(f"Found {len(img_links)} obsidian-style image links in {fn}.")

        new_links = []
        for linki in img_links:  # findall直接找到的就是()中匹配的模式
            if "|" in linki:
                link_parts = linki.split("|")
                img_fn = link_parts[0]
                # TODO: 解析其他参数
            else:
                img_fn = linki

            img_full_path = list(self.ob_asset_dir.rglob(img_fn))
            if not img_full_path:
                logger.warning(f"Image {img_fn} not found in {self.ob_asset_dir}.")
                new_links.append(f"![[{linki}]]")  # 原样输出
                continue
            if len(img_full_path) > 1:
                logger.warning(
                    f"Multiple images {img_fn} found in {self.ob_asset_dir}, use the first one."
                )
            img_full_path = img_full_path[0]
            img_relative_path = img_full_path.relative_to(self.ob_asset_dir)
            img_target_path = self.hugo_asset_dir / img_relative_path
            logger.info(f"Paste image {img_full_path} to {self.hugo_asset_dir}.")
            os.makedirs(img_target_path.parent, exist_ok=True)
            shutil.copy(img_full_path, img_target_path)

            # as_posix()会把路径中的斜杠替换成反斜杠，适合作为url
            new_linki = f'{{{{< figure src="/{img_relative_path.as_posix()}" >}}}}'
            new_links.append(new_linki)

        content = ""
        for linki, other in zip(new_links, others):
            content += other
            content += linki
        content += others[-1]  # others比分隔符多一个，需要加上
        return content

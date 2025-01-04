import os
import re
import shutil
import logging
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class ImageLinkProcessor:
    ob_asset_dir: Path | str
    hugo_asset_dir: Path | str
    img_exts: tuple[str] = (".png", ".jpeg", ".gif", ".svg", ".jpg")

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

        # 将content分成两部分，第一部分是其他内容，第二部分是图片链接
        parts = self.regex.split(content)
        others = parts[::2]
        img_links = parts[1::2]
        logger.info(f"Found {len(img_links)} obsidian-style image links in {fn}.")

        # 处理图片链接
        new_links = []
        for linki in img_links:  # findall直接找到的就是()中匹配的模式
            # 解析图片链接的各个部分，包括src、title、width
            img_item = {}
            if "|" in linki:
                link_parts = linki.split("|")
                img_item["src"] = link_parts[0]
                for parti in link_parts[1:]:
                    if parti.isdigit():  # 这是宽度
                        img_item["width"] = parti
                    else:  # 这是title
                        img_item["title"] = parti

            else:
                img_item["src"] = linki

            # 找到图片的扩展名，并判断是否支持
            for ext in self.img_exts:
                if img_item["src"].endswith(ext):
                    break
            else:
                logger.warning(
                    f"Image {img_item["src"]} of {fn} has an unsupported extension."
                )
                new_links.append(f"![[{linki}]]")  # 原样输出
                continue

            # 找到图片的绝对路径，并复制到hugo的静态资源目录
            img_full_path = list(self.ob_asset_dir.rglob(img_item["src"]))
            if not img_full_path:
                logger.warning(
                    f"Image {img_item["src"]} not found in {self.ob_asset_dir}."
                )
                new_links.append(f"![[{linki}]]")  # 原样输出
                continue
            if len(img_full_path) > 1:
                logger.warning(
                    f"Multiple images {img_item["src"]} found in {self.ob_asset_dir}, use the first one."
                )
            img_full_path = img_full_path[0]
            img_relative_path = img_full_path.relative_to(self.ob_asset_dir)
            img_target_path = self.hugo_asset_dir / img_relative_path
            logger.info(f"Paste image {img_full_path} to {self.hugo_asset_dir}.")
            os.makedirs(img_target_path.parent, exist_ok=True)
            shutil.copy(img_full_path, img_target_path)

            # 将图片相对于hugo的静态资源目录的路径作为src，其他属性作为参数，构建新的链接
            # as_posix()会把路径中的斜杠替换成反斜杠，适合作为url
            img_item["src"] = img_relative_path.as_posix()
            new_link_content = " ".join([f'{k}="{v}"' for k, v in img_item.items()])
            new_linki = f"{{{{< figure {new_link_content} >}}}}"
            new_links.append(new_linki)

        # 将新的链接和其他内容组合成新的content
        content = ""
        for linki, other in zip(new_links, others):
            content += other
            content += linki
        content += others[-1]  # others比分隔符多一个，需要加上
        return content

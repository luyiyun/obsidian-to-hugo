"""
Utilities to process obsidian notes and convert them to hugo ready content files.
"""

import os
import os.path as osp
import logging
from pathlib import Path
from dataclasses import dataclass
from shutil import rmtree

from .processers import (
    FrontMatterProcessor,
    MathFormulaProcessor,
    ImageLinkProcessor,
    ExcalidrawAnnotationProcessor,
    PublishFilter,
)


logger = logging.getLogger(__name__)


@dataclass
class ObsidianToHugo:
    """
    Process the obsidian vault and convert it to hugo ready content.
    """

    obsidian_vault_dir: str
    hugo_root_dir: str
    processors: list = None
    include_files: list[str] | None = None
    exclude_files: list[str] | None = None
    author_name: str = ""
    author_link: str = ""
    author_email: str = ""
    author_avatar: str = ""
    # default_draft: bool = False
    clean_hugo_content: bool = False
    obsidian_asset_dir: str = "附件"

    def __post_init__(self):
        self.ob_root = Path(self.obsidian_vault_dir)
        self.hugo_root = Path(self.hugo_root_dir)
        self.hugo_content_dir = self.hugo_root / "content/posts"
        self.hugo_asset_dir = self.hugo_root / "assets"

        self._publish_filter = PublishFilter()

        self._front_matter_processor = FrontMatterProcessor(
            author_name=self.author_name,
            author_link=self.author_link,
            author_email=self.author_email,
            author_avatar=self.author_avatar,
            draft=False,  # NOTE: 默认全部都不是草稿
        )
        self._math_formula_processor = MathFormulaProcessor()
        self._image_link_processor = ImageLinkProcessor(
            ob_asset_dir=self.ob_root / self.obsidian_asset_dir,
            hugo_asset_dir=self.hugo_asset_dir,
        )
        self._excalidraw_anno_processor = ExcalidrawAnnotationProcessor()

    def run(self) -> None:
        """
        Delete the hugo content directory and copy the obsidian vault to the
        hugo content directory, then process the content so that the wiki links
        are replaced with the hugo links.
        """
        if self.clean_hugo_content:
            self.clear_hugo_dir()

        md_files = self.get_publish_md()
        logger.info(f"Found {len(md_files)} markdown files to process.")

        for fn in md_files:
            relat_fn = fn.relative_to(self.ob_root)
            logger.info(f"Start to process {relat_fn}.")
            target_fn = self.hugo_content_dir / relat_fn
            with open(fn, "r", encoding="utf-8") as f:
                content = f.read()

            # 查看front matter来决定是否发布
            logger.info(f"Check if {relat_fn} is published.")
            if not self._publish_filter(fn, content):
                logger.info(f"{relat_fn} is not published, skip it.")
                continue

            # 处理front matter
            logger.info(f"Process front matter of {relat_fn}.")
            content = self._front_matter_processor(fn, content)

            # 处理公式
            logger.info(f"Process math formulas of {relat_fn}.")
            content = self._math_formula_processor(fn, content)

            # 处理图片链接
            logger.info(f"Process image links of {relat_fn}.")
            content = self._image_link_processor(fn, content)

            # 取消内容中出现的excadraw注解
            logger.info(f"Remove excalidraw annotations of {relat_fn}.")
            content = self._excalidraw_anno_processor(fn, content)

            # 保存文件内容
            logger.info(f"Save {target_fn}.")
            os.makedirs(target_fn.parent, exist_ok=True)
            with open(target_fn, "w", encoding="utf-8") as f:
                f.write(content)

    def get_publish_md(self) -> list[Path]:
        res = []
        if self.include_files is not None:
            for ifile in self.include_files:
                res.extend(self.ob_root.rglob(ifile))
        else:
            res.extend(self.ob_root.glob("**/*.md"))

        if self.exclude_files is not None:
            for efile in self.exclude_files:
                res = [f for f in res if not f.match(efile)]

        return res

    def clear_hugo_dir(self) -> None:
        """
        Delete the whole content directory.
        NOTE: The folder itself gets deleted and recreated.
        """
        if osp.exists(self.hugo_content_dir):
            logger.info(f"Clean the hugo content directory: {self.hugo_content_dir}.")
            rmtree(self.hugo_content_dir)
        if osp.exists(self.hugo_asset_dir):
            logger.info(f"Clean the hugo asset directory: {self.hugo_asset_dir}.")
            rmtree(self.hugo_asset_dir)

    #
    # def copy_obsidian_vault_to_hugo_content_dir(self) -> None:
    #     """
    #     Copy all files and directories from the obsidian vault to the hugo content directory.
    #     """
    #     copytree(
    #         self.obsidian_vault_dir,
    #         self.hugo_content_dir,
    #         ignore=ignore_patterns(".obsidian"),
    #     )

    # def process_content(self) -> None:
    #     """
    #     Looping through all files in the hugo content directory and replace the
    #     wiki links of each matching file.
    #     """
    #     for root, dirs, files in os.walk(self.hugo_content_dir):
    #         for file in files:
    #             if file.endswith(".md"):
    #                 with open(os.path.join(root, file), "r", encoding="utf-8") as f:
    #                     content = f.read()
    #                 # If the file matches any of the filters, delete it.
    #                 keep_file = True
    #                 for filter in self.filters:
    #                     if not filter(content, file):
    #                         os.remove(os.path.join(root, file))
    #                         keep_file = False
    #                         break
    #                 if not keep_file:
    #                     continue
    #                 for processor in self.processors:
    #                     content = processor(content)
    #                 with open(os.path.join(root, file), "w", encoding="utf-8") as f:
    #                     f.write(content)

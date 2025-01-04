"""
Utilities to process obsidian notes and convert them to hugo ready content files.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from .processers.front_matter_processor import FrontMatterProcessor
from .processers.math_formula_processer import MathFormulaProcessor
from shutil import rmtree  # , copytree, ignore_patterns
# from .wiki_links_processor import replace_wiki_links
# from .md_mark_processor import replace_md_marks


logger = logging.getLogger(__name__)


@dataclass
class ObsidianToHugo:
    """
    Process the obsidian vault and convert it to hugo ready content.
    """

    obsidian_vault_dir: str
    hugo_content_dir: str
    processors: list = None
    include_files: list[str] | None = None
    exclude_files: list[str] | None = None
    author_name: str = ""
    author_link: str = ""
    author_email: str = ""
    author_avatar: str = ""
    default_draft: bool = False
    clean_hugo_content: bool = False

    def __post_init__(self):
        self.ob_root = Path(self.obsidian_vault_dir)
        self.hugo_root = Path(self.hugo_content_dir)

        self._front_matter_processor = FrontMatterProcessor(
            author_name=self.author_name,
            author_link=self.author_link,
            author_email=self.author_email,
            author_avatar=self.author_avatar,
            draft=self.default_draft,
        )
        self._math_formula_processor = MathFormulaProcessor()

    def run(self) -> None:
        """
        Delete the hugo content directory and copy the obsidian vault to the
        hugo content directory, then process the content so that the wiki links
        are replaced with the hugo links.
        """
        if self.clean_hugo_content:
            logger.info(f"Clean the hugo content directory: {self.hugo_content_dir}.")
            self.clear_hugo_content_dir()

        md_files = self.get_publish_md()
        logger.info(f"Found {len(md_files)} markdown files to process.")

        for fn in md_files:
            relat_fn = fn.relative_to(self.ob_root)
            logger.info(f"Start to process {relat_fn}.")
            target_fn = self.hugo_root / relat_fn
            with open(fn, "r", encoding="utf-8") as f:
                content = f.read()

            # 处理front matter
            logger.info(f"Process front matter of {relat_fn}.")
            content = self._front_matter_processor(fn, content)

            # 处理公式
            logger.info(f"Process math formulas of {relat_fn}.")
            content = self._math_formula_processor(fn, content)

            # 保存文件内容
            logger.info(f"Save {target_fn}.")
            os.makedirs(target_fn.parent, exist_ok=True)
            with open(target_fn, "w", encoding="utf-8") as f:
                f.write(content)
            # If the file matches any of the filters, delete it.
            # keep_file = True
            # for filter in self.filters:
            #     if not filter(content, file):
            #         os.remove(os.path.join(root, file))
            #         keep_file = False
            #         break
            # if not keep_file:
            #     continue
            # for processor in self.processors:
            #     content = processor(content)
            # with open(os.path.join(root, file), "w", encoding="utf-8") as f:
            #     f.write(content)

        # self.clear_hugo_content_dir()
        # self.copy_obsidian_vault_to_hugo_content_dir()
        # self.process_content()

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

    def clear_hugo_content_dir(self) -> None:
        """
        Delete the whole content directory.
        NOTE: The folder itself gets deleted and recreated.
        """
        rmtree(self.hugo_content_dir)

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

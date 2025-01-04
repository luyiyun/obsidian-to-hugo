import logging
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import yaml

from .base import FrontMatterBase

logger = logging.getLogger(__name__)


@dataclass
class FrontMatterProcessor(FrontMatterBase):
    replace: tuple[str, str] = (("created", "date"), ("updated", "lastmod"))
    author_name: str = ""
    author_link: str = ""
    author_email: str = ""
    author_avatar: str = ""
    draft: bool = False

    def __call__(self, fn: Path, content: str) -> str:
        match = self.regex.search(content)
        if not match:
            logger.info(f"No front matter found in {fn}.")
            return content

        front_matter = match.group(1)  # 匹配到的内容
        fm_dict = yaml.load(front_matter, Loader=yaml.FullLoader)
        fm_dict["title"] = fn.parts[-1].replace(".md", "")
        for k, v in self.replace:
            fm_dict[v] = fm_dict.pop(k)
        # 日期格式需要整理
        fm_dict["date"] = str(datetime.fromisoformat(fm_dict["date"]).date())
        fm_dict["lastmod"] = str(datetime.fromisoformat(fm_dict["lastmod"]).date())
        # 增加作者信息
        fm_dict["author"] = {
            "name": self.author_name,
            "link": self.author_link,
            "email": self.author_email,
            "avatar": self.author_avatar,
        }
        # 自动添加draft标记
        if "draft" not in fm_dict:
            fm_dict["draft"] = self.draft
        logger.info(f"The draft flag of {fn} is {fm_dict['draft']}.")
        # 自动添加KATex渲染
        fm_dict["math"] = True

        new_front_matter = yaml.dump(fm_dict, allow_unicode=True)
        # yaml.dump会多生成一个空行，所以相比于regex少用一个\n
        content = self.regex.sub(f"---\n{new_front_matter}---\n", content, count=1)
        return content

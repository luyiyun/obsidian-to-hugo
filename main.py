from ipaddress import collapse_addresses
import re
from typing import Iterable, Self, Any, Union
from dataclasses import dataclass
import mistune

import yaml


class ASTnode:
    def __init__(
        self,
        name: str,
        pattern: re.Pattern | None = None,
        raw: str = "",  # store the raw text
        children: list[
            "ASTnode"
        ] = None,  # NOTE: do not use mutable default value for children
        parent: Union["ASTnode", None] = None,
        data: dict[str, Any] = None,  # store the meta fields
    ) -> None:
        self.name = name
        self.pattern = pattern
        self.raw = raw
        self.children = children or []
        self.parent = parent
        self.data = data or {}
        self.leaf = name in ["text", "math_block"]

    def __repr__(self) -> str:
        return f"<ASTNode: {self.name}>"

    def filter(self, name: str) -> Iterable["ASTnode"]:
        for child in self.children:
            if child.name == name:
                yield child
            else:
                yield from child.filter(name)

    def print(self, indent: int = 0):
        print(
            f"{indent *' '}{self.name}: {str(self.data)[:20]}"  # ": {self.raw[:100] if self.raw is not None else ''}"
        )
        if len(self.children) > 0:
            for child in self.children:
                child.print(indent + 2)


def preprocess(text: str) -> str:
    return text.strip(" \t\n\r")


class FrontMatterParser:
    def __init__(self) -> None:
        self.pattern = re.compile(r"---(\n*?)(.*?)(\n*?)---\n", re.DOTALL)

    def __call__(self, text: str) -> tuple[str | None, ASTnode | None, str | None]:
        text = preprocess(text)
        match = self.pattern.search(text)
        if not match:
            return None, None, text

        forward = text[: match.start()] if match.start() > 0 else None
        backward = text[match.end() :] if match.end() < len(text) else None
        raw = match.group(2)
        data = yaml.load(raw, Loader=yaml.FullLoader)
        return (
            forward,
            ASTnode("front_matter", pattern=self.pattern, raw=raw, data=data),
            backward,
        )


class SectionParser:
    def __init__(self, level: int = 1):
        self.level = level
        # (?m:^)表示启用多行模式的^，此时其不表示文本的开始，而是每一行的开始
        # 启用多行模式另一种用法是使用flag re.M，此时整个pattern中的所有^$
        # 都表示每一行的开始和结束，而不是整个文本的开始和结束
        # 这里，我们匹配的对象可能直接到达文本末尾，因此需要使用$来匹配
        self.pattern = re.compile(
            r"((?m:^)\s*?"
            + ("#" * level)
            + r" "
            + r"(?s:.)*?)"
            + r"((?m:^)\s*?"
            + ("#" * level)
            + r" |$)",
        )

    def __call__(self, text: str) -> tuple[str | None, ASTnode | None, str | None]:
        text = preprocess(text)
        match = self.pattern.search(text)
        if not match:
            return None, None, text

        forward = text[: match.start()] if match.start() > 0 else None
        backward = text[match.end(1) :] if match.end(1) < len(text) else None
        raw = match.group(1)

        # 将标题提取出来，只将后面的内容放到raw中，不然会陷入死循环
        title_match = re.search(r"^#+\s*(.*?)\s*\n", raw)
        raw = raw[title_match.end(1) :]

        return (
            forward,
            ASTnode(
                f"Section{self.level}",
                pattern=self.pattern,
                raw=raw,
                data={"title": title_match.group(1)},
            ),
            backward,
        )


class MathBlockParser:
    def __init__(self) -> None:
        self.pattern = re.compile(r"^\s*\$\$(.*?)\$\$\s*\n", re.DOTALL | re.M)

    def __call__(self, text: str) -> tuple[str | None, ASTnode | None, str | None]:
        text = preprocess(text)
        match = self.pattern.search(text)
        if not match:
            return None, None, text

        forward = text[: match.start()] if match.start() > 0 else None
        backward = text[match.end() :] if match.end() < len(text) else None
        raw = match.group(1)

        return (
            forward,
            ASTnode(
                "math_block",
                pattern=self.pattern,
                raw=raw,
            ),
            backward,
        )


class CalloutParser:
    def __init__(self) -> None:
        self.pattern = re.compile(
            r"(?m:^)\s*?>\s*\[\!(.*?)\]([-+]?)(.*?)\n((?s:.)*?)((?m:^)\s*?[^>]|$)"
        )

    def __call__(self, text: str) -> tuple[str | None, ASTnode | None, str | None]:
        text = preprocess(text)
        match = self.pattern.search(text)
        if not match:
            return None, None, text

        forward = text[: match.start()] if match.start() > 0 else None
        backward = text[match.end(4) :] if match.end(4) < len(text) else None
        category = match.group(1).strip()
        collapase = match.group(2).strip()
        title = match.group(3).strip()
        raw = match.group(4)

        return (
            forward,
            ASTnode(
                "callout",
                pattern=self.pattern,
                raw=raw,
                data={
                    "category": category,
                    "collapse": collapase,
                    "title": title,
                },
            ),
            backward,
        )


class ImageLinkParser:
    def __init__(self) -> None:
        self.pattern = re.compile(
            r"(\!\[\[(?P<wiki>.+?)\]\])|(\!\[(?P<title>.*?)]\((?P<link>.+?)\))"
        )

    def __call__(self, text: str) -> tuple[str | None, ASTnode | None, str | None]:
        text = preprocess(text)
        match = self.pattern.search(text)
        if not match:
            return None, None, text

        forward = text[: match.start()] if match.start() > 0 else None
        backward = text[match.end() :] if match.end() < len(text) else None
        data = {}
        if match["wiki"]:
            split_res = match["wiki"].split("|")
            data["link"] = split_res.pop(0)
            for s in split_res:
                if s.isdigit():
                    data["width"] = int(s)
                elif s == "center":
                    data["position"] = s
                else:
                    data["title"] = s
            data["wiki"] = True
        else:
            data["link"] = match["link"]
            data["title"] = match["title"]
            data["wiki"] = False

        if data["link"].endswith(".excalidraw"):
            data["category"] = "excalidraw"
        else:
            data["category"] = "img"

        return (
            forward,
            ASTnode(
                "image_link",
                pattern=self.pattern,
                data=data,
            ),
            backward,
        )


class ListParser:
    def __init__(self, order: bool = False) -> None:
        # TODO:
        # List:
        #  - ListItem 可能还有children
        #   - children
        #  - ListItem
        if order:
            pass
            # pattern = (
            #     r'^(?P<list_1>\s*?)'
            #     r'(?P<list_2>[\*\+-]|\d{1,9}[.)])'
            #     r'(?P<list_3>[ \t]*|[ \t].+)$'
            # )
            # self.pattern =


class ObsidianMarkdownParser:
    def __init__(self):
        self.block_parsers = (
            [
                FrontMatterParser(),
            ]
            + [SectionParser(i) for i in range(1, 6)]
            + [
                MathBlockParser(),
                CalloutParser(),
                ImageLinkParser(),
                lambda text: (
                    None,
                    ASTnode("paragraph", None, raw=preprocess(text)),
                    None,
                ),  # default parser
            ]
        )

        self.inline_parsers = []

    def __call__(self, text: str, parent: ASTnode = None, append: bool = True):
        if parent is None:
            parent = ASTnode("root", None)  # root node

        parsers = (
            self.inline_parsers if parent.name == "paragraph" else self.block_parsers
        )

        for parser in parsers:
            forward, node, backward = parser(text)
            if node is not None:
                node.parent = parent
                if append:
                    parent.children.append(node)
                else:
                    parent.children.insert(0, node)
                if forward is not None:
                    self.__call__(forward, parent=parent, append=False)
                if backward is not None:
                    self.__call__(backward, parent=parent, append=True)
                if not node.leaf:
                    self.__call__(node.raw, parent=node, append=True)
                    node.raw = None  # clear the raw text to avoid duplication
                break
            else:
                text = backward

        return parent


# class Section(ASTnode):
#     def __init__(self, level: int, content: str, children: list[ASTnode] = []) -> None:
#         super().__init__(content, children)
#         self.pattern =
#     pattern: re.Pattern = re.compile( r"^(#+)(.*?)(\n|$)" + r"|(\n|^)## (.*?)\n", re.DOTALL
#     )


def print_ast(ast: list[dict[str, Any]], indent: int = 0):
    for node in ast:
        if "children" in node:
            print_ast(node["children"], indent + 2)
            continue
        print(f"{indent * ' '}{node['type']}: {node.get("raw", "")}")


def main():
    example_markdown = "C:/Users/admin/OneDrive/obsidian/专题学习/狄里克雷混合模型.md"
    with open(example_markdown, "r", encoding="utf-8") as f:
        content = f.read()

    ast = ObsidianMarkdownParser()(content)
    ast.print()
    for node in ast.filter("image_link"):
        print(node.raw)
        print(node.data)
        print()
    __import__("ipdb").set_trace()
    # markdown = mistune.Markdown()
    # res = markdown(content)
    # print_ast(res)


if __name__ == "__main__":
    main()

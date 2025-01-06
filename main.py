import re
from typing import Self, Any, Union
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

    def __repr__(self) -> str:
        return f"<ASTNode: {self.name}>"

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


class ObsidianMarkdownParser:
    def __init__(self):
        self.parsers = [
            FrontMatterParser(),
        ]
        for i in range(1, 6):
            self.parsers.append(SectionParser(i))

    def __call__(self, text: str, parent: ASTnode = None, append: bool = True):
        if parent is None:
            parent = ASTnode("root", None)  # root node

        for parser in self.parsers:
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
                self.__call__(node.raw, parent=node, append=True)
                node.raw = None  # clear the raw text to avoid duplication
                break
            else:
                text = backward

        else:
            # if no parser is matched, treat the remaining text as a plain text node
            node = ASTnode("text", None, text, parent=parent)
            if append:
                parent.children.append(node)
            else:
                parent.children.insert(0, node)

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
    __import__("ipdb").set_trace()
    # markdown = mistune.Markdown()
    # res = markdown(content)
    # print_ast(res)


if __name__ == "__main__":
    main()

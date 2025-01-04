"""
Obsidian to Hugo CLI
"""

import argparse
import os
import yaml
import logging
from .obsidian_to_hugo import ObsidianToHugo


def main() -> None:
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--version",
    #     "-v",
    #     action="version",
    #     version=f"obsidian-to-hugo {__version__}",
    #     help="Show the version and exit.",
    # )
    # parser.add_argument(
    #     "--hugo-content-dir",
    #     help="Directory of your Hugo content directory, the obsidian notes should be processed into.",
    #     type=str,
    # )
    #
    # parser.add_argument(
    #     "--obsidian-vault-dir",
    #     help="Directory of the Obsidian vault, the notes should be processed from.",
    #     type=str,
    # )
    parser.add_argument(
        "--config_file",
        help="Path to the config file, default is ./ob2hugo.yaml",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--log_level",
        help="Log level, default is INFO",
        type=str,
        default="INFO",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s",
    )

    if args.config_file is None:
        args.config_file = "./ob2hugo.yaml"
    if not os.path.isfile(args.config_file):
        raise FileNotFoundError(f"The config file {args.config_file} does not exist.")
    with open(args.config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    print(config)

    if ("obsidian_vault_dir" not in config) or (
        not os.path.isdir(config["obsidian_vault_dir"])
    ):
        parser.error("The obsidian vault directory does not exist.")
    if ("hugo_content_dir" not in config) or (
        not os.path.isdir(config["hugo_content_dir"])
    ):
        parser.error("The hugo content directory does not exist.")

    author = config.get("author", {})
    obsidian_to_hugo = ObsidianToHugo(
        obsidian_vault_dir=config["obsidian_vault_dir"],
        hugo_content_dir=config["hugo_content_dir"],
        include_files=config.get("include_files", None),
        exclude_files=config.get("exclude_files", None),
        author_name=author.get("name", ""),
        author_link=author.get("link", ""),
        author_email=author.get("email", ""),
        author_avatar=author.get("avatar", ""),
        default_draft=config.get("default_draft", True),
        clean_hugo_content=config.get("clean_hugo_content", False),
    )
    obsidian_to_hugo.run()


if __name__ == "__main__":
    main()

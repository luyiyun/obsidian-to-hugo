"""
Obsidian to Hugo CLI
"""

import argparse
import os
import yaml
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
        default="./ob2hugo.yaml",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise FileNotFoundError(f"The config file {args.config_file} does not exist.")
    with open(args.config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # if not args.hugo_content_dir or not os.path.isdir(args.hugo_content_dir):
    #     parser.error("The hugo content directory does not exist.")
    # if not args.obsidian_vault_dir or not os.path.isdir(args.obsidian_vault_dir):
    #     parser.error("The obsidian vault directory does not exist.")
    obsidian_to_hugo = ObsidianToHugo(
        obsidian_vault_dir=config["obsidian_vault_dir"],
        hugo_content_dir=config["hugo_content_dir"],
    )
    obsidian_to_hugo.run()


if __name__ == "__main__":
    main()

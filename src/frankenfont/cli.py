import argparse

from frankenfont.create import create_custom_font, install_font


def main():
    parser = argparse.ArgumentParser(
        prog="frankenfont",
        description="Create a custom font by merging glyphs from multiple fonts based on a configuration file.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # `create` command
    create_parser = subparsers.add_parser(
        "create", help="Create a custom font based on configuration"
    )
    create_parser.add_argument(
        "config", type=str, help="Path to the TOML configuration file"
    )
    create_parser.add_argument(
        "-i", "--install", action="store_true", help="Install the font after creation"
    )

    args = parser.parse_args()

    if args.command == "create":
        font_path = create_custom_font(args.config)

        if args.install:
            install_font(font_path)


if __name__ == "__main__":
    main()

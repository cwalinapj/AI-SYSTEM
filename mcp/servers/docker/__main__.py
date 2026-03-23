from pprint import pprint

from . import PROMPTS, RESOURCES, SERVER_NAME, TOOLS


def main() -> None:
    pprint(
        {
            "server": SERVER_NAME,
            "tools": TOOLS,
            "resources": RESOURCES,
            "prompts": PROMPTS,
        }
    )


if __name__ == "__main__":
    main()

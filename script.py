from argparse import ArgumentParser
from src import parser
from src import documentation
import json

if __name__ == "__main__":
    arg_parser = ArgumentParser(description="Scrape the Discord API into JSON")

    # add required arguments
    arg_parser.add_argument("output", type=str, help="The path of the file to store the resulting JSON in")
    arg_parser.add_argument("repo", nargs='?', type=str, help="The GitHub repository (default is discord/discord-api-docs)")

    args = arg_parser.parse_args()
    archive = documentation.download(args.repo or "discord/discord-api-docs")
    md = documentation.get(archive)

    result = {}

    for file_path in md:
        p = parser.Parser(md[file_path])
        structures, requests = p.parse()
        name = file_path.split("/")[-1][:-3]

        if len(structures) != 0 or len(requests) != 0:
            result[name] = {}

        if len(structures) != 0:
            if "structures" not in result[name]:
                result[name]["structures"] = []

            result[name]["structures"].append(structures)

        if len(requests) != 0:
            if "requests" not in result[name]:
                result[name]["requests"] = []

            result[name]["requests"].append(requests)

    with open(args.output, "w+") as f:
        f.write(json.dumps(result))
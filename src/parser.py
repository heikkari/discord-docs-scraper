from typing import Dict, Tuple, List
import re


class Parser:
    def __init__(self, markdown: str):
        self.lines = [ln.decode("utf-8") for ln in markdown.splitlines()]
        self.structure_pos = {}
        self.request_pos = []

    def parse_as_structure(self, pos: int) -> Dict[str, str]:
        link_regex = r"\[(.*)\]\(.*\)"
        table = self.parse_md_table(pos)
        types = []

        if len(table) == 0:
            return

        for type in (table.get("Type") or table.get("Value")):
            maybe_match = re.search(link_regex, type)

            if maybe_match:
                type = type.replace(maybe_match.group(0), maybe_match.group(1))

            types.append(type)

        obj = zip(table.get("Field") or table.get("Name"), types)
        return dict(obj)

    def parse(self) -> Tuple[Dict[str, Dict[str, str]], List[dict]]:
        """
            Returns the structures and requests documented within the markdown content.
        """

        structures = {}
        requests = []

        self.mark_positions()

        for name in self.structure_pos.keys():
            pos = self.structure_pos[name]
            obj = self.parse_as_structure(pos + 1)

            if obj:
                structures[name] = obj

        for type, pos in self.request_pos:
            if type == "url":
                parts = self.lines[pos].split("%")
                name = parts[0][3:].strip()

                # ---
                parts = parts[1].split(" ")
                method = parts[1].strip()

                # clean url
                url = parts[2].strip()
                results = re.findall("#[A-Za-z_\/-]*", url)
                for entry in results:
                    url = url.replace(entry, "")

                # ---
                requests.append({
                    "name": name,
                    "method": method,
                    "url": url
                })

            elif type == "params":
                obj = self.parse_as_structure(pos)

                if obj and len(requests) != 0:
                    requests[-1]["json"] = obj

        return (structures, requests)

    def mark_positions(self):
        """
            Mark the structures', parameters', and requests' positions by finding the titles above
            or adjacent to them.
        """

        for idx, line in enumerate(self.lines):
            if line[:6] == "######":
                parts = line.split(' ')
                label = parts[-1].lower().strip()

                if label == "structure":
                    self.structure_pos["".join(parts[1:-1])] = idx + 1

                if label == "params":
                    self.request_pos.append((label, idx + 1))
            else:
                if line[:2] == "##" and "%" in line:
                    self.request_pos.append(("url", idx))

    def parse_md_table(self, start_pos: int) -> dict:
        result = {}

        for line in self.lines[start_pos:]:
            stripped = line.strip()

            if stripped == "": continue
            if not stripped.startswith("|"): break

            parts = [p.strip() for p in line.split("|") if p.strip() != ""]

            if len(result) == 0:
                for part in parts:
                    result[part] = []
            else:
                columns = list(result.keys())

                for idx, part in enumerate(parts):
                    if "".join(set(part)) == '-': continue
                    result[columns[idx]].append(part)

        return result
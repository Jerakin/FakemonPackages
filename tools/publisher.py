import argparse
import zipfile
import json
import shutil
from pathlib import Path

__version__ = "0.1"


class IncompletePackage(Exception):
    pass


def options():
    parser = argparse.ArgumentParser(description='Commandline tool to publish Fakemon Package')
    sub_parsers = parser.add_subparsers(dest="command")
    parser.add_argument('--version', action='version', version="Publisher {}".format(__version__))

    sub_parsers.add_parser("peek", help="Echo information about the package")
    _add = sub_parsers.add_parser("add", help="Add the package")
    _add.add_argument("package", help="Package to add")
    _add.add_argument("-pi", "--package_index", dest="package_index", help="Root path of the package repository")
    input_args = parser.parse_args()

    return input_args


def add(package_path, package_index):
    if not package_index.exists:
        print("Path to the package index doesn't exists")
        return
    if not package_path.exists:
        print("Package not found")
        return

    package_path = Path(package_path)
    package_index = Path(package_index)
    z = zipfile.ZipFile(package_path)
    if "index.json" not in [x.filename for x in z.filelist]:
        raise IncompletePackage

    with z.open("index.json") as f:
        index_json = json.load(f)
        package_name = index_json["name"].lower().replace(" ", "_") + ".fkmn"

    try:
        shutil.copy(str(package_path), str((package_index / "packages" / package_name).with_suffix('.fkmn')))
        index_json["path"] = "packages/" + package_name
    except shutil.SameFileError:
        print("Skipping moving because of SameFileError")

    package_index_file = package_index / "index.json"
    with package_index_file.open() as fp:
        package_index_json = json.load(fp)

    for package in package_index_json:
        if package["name"] == index_json["name"]:
            package["name"] = index_json["name"]
            package["author"] = index_json["author"]
            package["description"] = index_json["description"]

            if package["version"] == index_json["version"]:
                print("Package have the same version", index_json["version"])
                package["version"] = package["version"] + 1
            else:
                package["version"] = index_json["version"]
            break
    else:  # NoBreak
        entry = {
            "name": index_json["name"],
            "path": "packages/" + package_name,
            "author": index_json["author"],
            "description": index_json["description"],
            "version": index_json["version"]
        }
        package_index_json.append(entry)

    with package_index_file.open("w") as fp:
        json.dump(package_index_json, fp, indent="  ", ensure_ascii=False)
    print("Finished")


def print_help():
    print("Usage: publisher <command> [<args>]\n")
    print("The commands are:")
    print("    add     Add the package to the index")
    print("    peek    NotImplementedError")

    print("See `publisher <command> --help` for information on a specific command.")


def main():
    _options = options()
    if _options.command == "add":
        package_index = Path(_options.package_index) if _options.package_index else Path(__file__).absolute().parent.parent
        add(Path(_options.package), package_index)
    elif _options.command == "peek":
        raise NotImplementedError
    else:
        print_help()


if __name__ == "__main__":
    main()

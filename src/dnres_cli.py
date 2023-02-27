import click
from dnres import DnRes
import os
import pandas as pd
import json


def _check_path_in_structure(res, path):
    if not os.path.exists(os.path.join(res.structure, path)):
        exit("Path not in structure")


@click.group(invoke_without_command=True)
@click.argument("config")
@click.pass_context
def dnres(ctx, config):
    """
    \b
    Prints the contents of the structure if no command is passed.
    """

    res = DnRes(config)
    ctx.obj = res

    if ctx.invoked_subcommand is None:
        print(res)


@dnres.command()
@click.option('--path', '-p', help='Path to show information about.')
@click.pass_obj
def info(res, path):
    """
    \b
    Shows information for given path.
    """

    res.info(path)


@dnres.command()
@click.option('--tag', '-t', help='Tag for path')
@click.option('--path', '-p', help='Path to be tagged.')
@click.pass_obj
def tag(res, tag, path):
    """
    \b
    Add tag to given path.
    """

    _check_path_in_structure(res, path)
    res.tag(tag, path)


@dnres.command()
@click.option('--path', '-p', help='Path to set info.')
@click.option('--datatype', '-d', required=False, help='Datatype of path.')
@click.option('--description', '-i', required=False, help='Short description about the data.')
@click.option('--source', '-s', required=False, help='Source that generated the data.')
@click.pass_obj
def set_info(res, path, datatype, description, source):
    """
    \b
    For existing paths, it sets information for given path.
    For new paths, it registers it to the database and sets the provided information. 
    """

    _check_path_in_structure(res, path)
    res.set_info(path, datatype, description, source)


@dnres.command()
@click.option('--path', '-p', help='Path to be removed.')
@click.pass_obj
def remove_from_db(res, path):
    """
    \b
    Removes path from database.
    """

    res.remove_from_db(path)


@dnres.command()
@click.option('--tag', '-t', help='Tag to be removed.')
@click.option('--path', '-p', help='Path to remove tag from.')
@click.pass_obj
def remove_tag(res, tag, path):
    """
    \b
    Removes tag from given path.
    """

    res.remove_tag(tag, path)


@dnres.command()
@click.option('--path', '-p', help='Path to show absolute path.')
@click.pass_obj
def ls(res, path):
    """
    \b
    Prints the absolute path of the provided path.
    """

    filepath = os.path.join(res.structure, path)
    print(filepath)



@dnres.command()
@click.option('--path', '-p', help='Path to show data from.')
@click.option('--backend', '-b', required=True, type=click.Choice(['pandas', 'none']), 
              default='none', show_default=True, help="Backend to use in order to load and print objects or files.")
@click.option('--delimiter', required=False, type=click.Choice(['tab', 'comma']), help="Delimiter for csv or tsv files.")
@click.option('--sheet', type=int, required=False, help="Sheet number for excel files.")
@click.pass_obj
def cat(res, path, backend, delimiter, sheet):
    """
    \b
    It prints the contents of the stored object or path. 
    Prints filepath if stored data are not supported for printing.
    """

    _check_path_in_structure(path)

    # Identify object is serialized
    if filename.endswith(".json") or filename.endswith(".pickle"):
        serialization = True
    else:
        serialization = False
   
    if serialization:
        data = res.load(path)

        if isinstance(data, list) or isinstance(data, tuple) or isinstance(data, set):
            for item in data:
                print(item)

        elif isinstance(data, dict):
            print(json.dumps(data))

        elif isinstance(data, str):
            print(data)

        elif isinstance(data, pd.core.frame.DataFrame):
            print(data.to_csv(index=False, sep='\t'))

        else:
            print(os.path.join(res.structure, path))

    else:
        filepath = res.load(path)

        # Action for TXT files
        if filepath.endswith('.txt'):
            if backend and backend != 'none':
                raise Exception('For txt file backend should be none.')
            with open(filepath, 'r') as inf:
                for line in inf:
                    line = line.strip("\n")
                    print(line)

        # Action for CSV or TSV files
        elif filepath.endswith('.csv') or filepath.endswith('.tsv'):
            if backend == 'none':
                with open(filepath, 'r') as inf:
                    for line in inf:
                        line = line.strip("\n")
                        if not delimiter or delimiter == 'tab':
                            line = line.split('\t')
                        elif delimiter == 'comma':
                            line = line.split(',')
                        print('\t'.join(line))
            elif backend == 'pandas':
                if not delimiter or delimiter == 'tab':
                    df = pd.read_csv(filepath, sep='\t')
                elif delimiter == 'comma':
                    df = pd.read_csv(filepath, sep=',')
                print(df.to_string())

        # Action for EXCEL files
        elif filepath.endswith('.xls') or filepath.endswith('.xlsx'):
            if backend == 'none':
                raise Exception("For excel files, backend cannot be none.")
            elif backend == 'pandas':
                if not sheet:
                    raise Exception("Sheet number should be passed for excel files.")
                df = pd.read_excel(filepath, sheet_name=sheet)
                print(df.to_string())

        else:
            print(filepath)


if __name__ == "__main__":
    dnres()

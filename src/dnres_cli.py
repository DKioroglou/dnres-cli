import click
from dnres import DnRes
import configparser
import os
import pandas as pd


@click.group(invoke_without_command=True)
@click.argument("config")
@click.pass_context
def dnres(ctx, config):
    """
    \b
    Prints the contents of the structure is no command is passed.
    """

    res = DnRes(config)
    ctx.obj = res
    if ctx.invoked_subcommand is None:
        print(res)


@dnres.command()
@click.option('--directory', '-d', required=True, help='Name of directory.')
@click.option('--filename', '-f', required=False, help='Filename in directory.')
@click.pass_obj
def info(res, directory, filename):
    """
    \b
    Shows information for directory or filename.
    Otherwise, it shows information for the passed filename of the passed directory.
    """

    if not filename:
        res.info_directory(directory)
    else:
        res.info_filename(directory, filename)


@dnres.command()
@click.option('--directory', '-d', required=True, help='Name of directory.')
@click.option('--filename', '-f', required=True, help='Filename in directory.')
@click.pass_obj
def ls(res, directory, filename):
    """
    \b
    Prints the filepath of the stored object or file.
    """

    filepath = os.path.join(res.structure[directory], filename)
    print(filepath)


@dnres.command()
@click.option('--data', required=True, help='Name of data to store.')
@click.option('--directory', '-d', required=True, help='Name of directory to store to.')
@click.option('--filename', '-f', required=True, help='Filename under which data will be stored.')
@click.option('--description', '-i', required=False, help='Brief description about the data.')
@click.option('--source', '-s', required=False, help='Where data came from.')
@click.option('--overwrite', is_flag=True, help='Flag for overwriting previously stored data under same filename.')
@click.pass_obj
def store(res, data, directory, filename, description, source, overwrite):
    """
    \b
    Stores data in structure and database.
    """
    
    res.store(data=data,
              directory=directory,
              filename=filename,
              source=source,
              description=description,
              isfile=True,
              overwrite=overwrite)


@dnres.command()
@click.option('--directory', '-d', required=True, help='Name of directory.')
@click.option('--filename', '-f', required=True, help='Filename in directory.')
@click.option('--backend', '-b', required=True, type=click.Choice(['pandas', 'none']), 
              default='none', show_default=True, help="Backend to use in order to load and print objects or files.")
@click.option('--delimiter', required=False, type=click.Choice(['tab', 'comma']), help="Delimiter for csv or tsv files.")
@click.option('--sheet', type=int, required=False, help="Sheet number for excel files.")
@click.pass_obj
def cat(res, directory, filename, backend, delimiter, sheet):
    """
    \b
    It prints the contents of the stored object or file. 
    """

    # Identify object is serialized
    if filename.endswith(".json") or filename.endswith(".pickle"):
        serialization = True
    else:
        serialization = False
   
    if serialization:
        data = res.load(directory, filename)

        if isinstance(data, list) or isinstance(data, tuple) or isinstance(data, set):
            for item in data:
                print(item)

        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}\t{value}")

        if isinstance(data, str):
            print(data)

        else:
            valid_instances = ['list', 'tuple', 'str', 'dict', 'str']
            print('Object is not an instance of:')
            print('\n'.join(valid_instances))

    else:
        filepath = res.load(directory, filename)

        # Action for TXT files
        if filename.endswith('.txt'):
            if backend and backend != 'none':
                raise Exception('For txt file backend should be none.')
            with open(filepath, 'r') as inf:
                for line in inf:
                    line = line.strip("\n")
                    print(line)

        # Action for CSV or TSV files
        elif filename.endswith('.csv') or filename.endswith('.tsv'):
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
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
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

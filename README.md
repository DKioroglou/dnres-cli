# dnres-cli

Command line utility to be used along with [dnres](https://github.com/DKioroglou/dnres) python package.

# Usage

## Parse config

```console
$ dnres config.ini
```

## Print contents of stored/tagged data

```console
$ dnres config.ini cat --help 
```

For files, the following filetypes are supported for printing:  

* `.csv` 
* `.tsv` 
* `.xls` 
* `.xlsx`

For python objects, the following classes are supported: 

* `dict` 
* `list` 
* `tuple` 
* `set` 
* `str`

If filetype or class is not supported, the filepath of the stored data gets printed.

## Print absolute filepath of stored/tagged data

```console
$ dnres config.ini ls --help
```

## Other commands

The following `dnres` methods are exposed as cli commands: 

* `info`
* `tag`
* `remove-from-db`
* `remove-tag`

Information on these commands/methods can be found [here](https://dnres.readthedocs.io/en/latest/source/dnres.html).  
To get help on these commands run:  

```console
$ dnres config.ini COMMAND --help
```

## Installation

```
pip install dnres-cli
```

## License

BSD 3

import click
from dnres import DnRes
import os
import pandas as pd
import json
import contextlib
import sqlite3
from flask import Flask
from multiprocessing import Process


def htmlRenderer(projectDB, projectDescription):
        htmlUpper = """
        <!DOCTYPE html>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;400&display=swap" rel="stylesheet">
                <style>
                    body {
                      background-color: #212F3C;
                      font-family: 'JetBrains Mono', monospace;
                      font-size: 14px;
                      color: #fff;
                    }
                    button {
                      font-family: 'JetBrains Mono', monospace;
                      font-size: 14px;
                    }
                    p {
                      font-size: 14px;
                    }

                    h3 {

                      color:#B16824
                    }

                    .collapsible {
                      cursor: pointer;
                      padding: 6px;
                      width: 100%;
                      border: none;
                      text-align: left;
                      outline: none;
                      font-family: 'JetBrains Mono', monospace;
                      font-size: 14px;
                    }

                    .active, .collapsible:hover {
                      background-color: #555;
                    }

                    .content {
                      height: inherit;
                      padding: 10px;
                      display: none;
                      background-color: #f1f1f1;
                      color: #555;
                      font-family: 'JetBrains Mono', monospace;
                      word-wrap: break-word;
                    }

                    .is-hidden {
                        display: none;
                    }

                    .show-element {
                        display: inline-block;
                    }

                    #sectionFold {
                      background-color: #212F3C;
                      color: white;
                    }

                </style>
            </head>
            <body>
        """

        htmlLower = """
                <script>
                    var coll = document.getElementsByClassName("collapsible");
                    var i;

                    for (i = 0; i < coll.length; i++) {
                      coll[i].addEventListener("click", function() {
                        this.classList.toggle("active");
                        var content = this.nextElementSibling;
                        if (content.style.display === "block") {
                          content.style.display = "none";
                        } else {
                          content.style.display = "block";
                        }
                      });
                    }
                </script>

                <script>
                    function filterElements(ele) {
                        if(event.key === 'Enter') {
                            let search_query = document.getElementById("searchbox").value;
                            let searchTerms = search_query.toLowerCase().split(",");
                            searchTerms = searchTerms.map(element => { return element.trim(); });

                            let cardsTitles = document.querySelectorAll('.collapsible');
                            let cardsContents = document.querySelectorAll('.content');
                                
                            if (search_query.length === 0) {  
                                for (var i = 0; i < cardsContents.length; i++) {
                                    cardsTitles[i].classList.remove("is-hidden");
                                    cardsContents[i].classList.remove("show-element");
                                    cardsContents[i].classList.add("is-hidden");
                                }
                            } else {
                                //Use innerText if all contents are visible
                                //Use textContent for including hidden elements
                                for (var i = 0; i < cardsTitles.length; i++) {
                                    cardTitle = cardsTitles[i].textContent.toLowerCase();
                                    cardContent = cardsContents[i].textContent.toLowerCase();
                                    if (searchTerms.some(term => cardTitle.includes(term))) {
                                           cardsTitles[i].classList.remove("is-hidden");
                                    } else if (searchTerms.some(term => cardContent.includes(term))) {
                                           cardsTitles[i].classList.remove("is-hidden");
                                           cardsContents[i].classList.remove("is-hidden");
                                           cardsContents[i].classList.add("show-element");
                                    } else {
                                        cardsTitles[i].classList.add("is-hidden");
                                        cardsContents[i].classList.remove("show-element");
                                        cardsContents[i].classList.add("is-hidden");
                                    }
                                }
                            }
                        }
                    }
                </script>
            </body>
        </html>
        """

        htmlMiddle = f"""
        <div>
            <label for="searchbox" class="is-size-5">Search</label>
            <input class='input' type="search" id="searchbox" placeholder="keyword" onkeydown="filterElements(this)"/>
         </div>
        <div>
            <p style="color:#C39BD3">{projectDescription}</p>
        </div>

        <hr>
        """
        with contextlib.closing(sqlite3.connect(projectDB)) as conn:
            with contextlib.closing(conn.cursor()) as c:
                query = """
                SELECT * FROM data
                """
                c.execute(query)
                results = c.fetchall()

        if results:
            for res in results:
                date, path, datatype, description, source = res

                with contextlib.closing(sqlite3.connect(projectDB)) as conn:
                    with contextlib.closing(conn.cursor()) as c:
                        query = """
                        SELECT tag FROM tags WHERE path=(?)
                        """
                        c.execute(query, (path, ))
                        tags = c.fetchall()
                if tags:
                    tags = [t[0] for t in tags]
                    tags = ", ".join(tags)

                datatype = datatype.replace("<", "").replace(">", "")

                entryContent = f"""
                <b>Path</b>: {path}<br>
                <b>Datatype</b>: <code>{datatype}</code><br>
                <b>Tags</b>: {tags}<br>
                <b>Source</b>: {source}<br>
                <b>Date</b>: {date}
                """

                htmlMiddle += f"""
                <button type="button" id="sectionFold" class="collapsible"><span style="font-size:8px; position:relative; bottom:2px;">&#128994;</span> <span style='color:#85C1E9'>{description}</span></button>
                <div class="content">
                  <p>{entryContent}</p>
                </div>
                """
        else:
            htmlMiddle += """
            <div>
                <p>No results found for project.</p>
            </div>
            """
        html = htmlUpper + htmlMiddle + htmlLower
        return html


def _check_path_in_structure(res, path):
    if not os.path.exists(os.path.join(res.structure, path)):
        exit("Path not in structure")


@click.group(invoke_without_command=True)
@click.argument("config")
@click.argument("rendering", required=False)
@click.argument("renderer", required=False)
@click.pass_context
def dnres(ctx, config, rendering, renderer):
    """
    \b
    Prints the contents of the structure if no command is passed.
    """

    res = DnRes(config)
    ctx.obj = res

    if ctx.invoked_subcommand is None:
        if rendering and rendering == 'html':
            if not renderer:
                exit("You need to pass a renderer.")
            app = Flask(__name__)
            @app.route("/")
            def index():
                projectDescription = res.description
                projectDB = res.db
                html = htmlRenderer(projectDB, projectDescription)
                return html

            server = Process(target=app.run, kwargs={"port":8989})
            server.start()
            os.system(f"{renderer} http://127.0.0.1:8989")
            server.terminate()
            server.join()
        else:
            print(res)


@dnres.command()
@click.argument('path')
@click.pass_obj
def info(res, path):
    """
    \b
    Shows information for given path.
    """

    res.info(path)


@dnres.command()
@click.option('--path', '-p', help='Path to be tagged.')
@click.option('--tag', '-t', required=False, help='Tag for path')
@click.option('--datatype', '-d', required=False, help='Datatype of path.')
@click.option('--description', '-i', required=False, help='Short description about the data.')
@click.option('--source', '-s', required=False, help='Source that generated the data.')
@click.pass_obj
def tag(res, path, tag, datatype, description, source):
    """
    \b
    Add tag and/or info to given path.
    """

    _check_path_in_structure(res, path)
    res.tag(path, tag, datatype, description, source)


@dnres.command()
@click.argument('path')
@click.pass_obj
def remove_from_db(res, path):
    """
    \b
    Removes path from database.
    """

    res.remove_from_db(path)


@dnres.command()
@click.option('--path', '-p', required=False, help='Path to remove tag from.')
@click.argument('tag')
@click.pass_obj
def remove_tag(res, tag, path):
    """
    \b
    Removes tag from given path. If not path is provided, tag is removed from all paths.
    """

    res.remove_tag(tag, path)


@dnres.command()
@click.option('--old', '-o', help='Existing name of tag.')
@click.option('--new', '-n', help='New name of tag.')
@click.pass_obj
def rename_tag(res, old, new):
    """
    \b
    Rename tag from old name to new name.
    """

    res.rename_tag(old, new)


@dnres.command()
@click.argument('path')
@click.pass_obj
def ls(res, path):
    """
    \b
    Prints the absolute path of the provided path.
    """

    filepath = os.path.join(res.structure, path)
    print(filepath)



@dnres.command()
@click.option('--backend', '-b', required=True, type=click.Choice(['pandas', 'none']), 
              default='none', show_default=True, help="Backend to use in order to load and print objects or files.")
@click.option('--delimiter', required=False, type=click.Choice(['tab', 'comma']), help="Delimiter for csv or tsv files.")
@click.option('--sheet', type=int, required=False, help="Sheet number for excel files.")
@click.argument('path')
@click.pass_obj
def cat(res, path, backend, delimiter, sheet):
    """
    \b
    It prints the contents of the stored object or path. 
    Prints filepath if stored data are not supported for printing.
    """

    _check_path_in_structure(res, path)

    # Identify object is serialized
    if path.endswith(".json") or path.endswith(".pickle"):
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

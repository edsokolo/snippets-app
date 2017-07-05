import logging
import argparse
import psycopg2

#Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

#Connect to Snippets Database
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")


def put(name, snippet, hide, unhide):
    """
    Store a snippet with an associated name.
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    command = "insert into snippets values (%s, %s)"
    if hide or unhide:
        if hide:
            action = hide
        elif unhide:
            action = not unhide
        command = "insert into snippets values (%s, %s, %s)"
        try:
            with connection, connection.cursor() as cursor:
                cursor.execute(command, (name, snippet, action))
        except psycopg2.IntegrityError as e:
            command = "update snippets set message=%s, hidden=%s where keyword=%s"
            with connection, connection.cursor() as cursor:
                cursor.execute(command, (snippet, action, name))
    elif not(hide or unhide):
        try:
            with connection, connection.cursor() as cursor:
                cursor.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            command = "update snippets set message=%s where keyword=%s"
            with connection, connection.cursor() as cursor:
                cursor.execute(command, (snippet,name))

    logging.debug("Snippet stored successfully.")
    return name, snippet

def get(name):
    """Retrieve the snippet with a given name.

    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Getting a snippet from keyword {!r}".format(name))

    with connection, connection.cursor() as cursor:
        command = "select message from snippets where keyword = %s and not hidden"
        cursor.execute(command, (name,))
        row = cursor.fetchone()

    logging.debug("Snippet retrieved successfully.")
    if not row:
        return "404: Snippet Not Found"
    return row[0]

def catalog(asc,desc):
    """List all available keywords"""
    logging.info("Listing all keywords")
    keywords = []

    with connection, connection.cursor() as cursor:
        command = "Select keyword from snippets where not hidden"
        if desc:
            command = "Select keyword from snippets where not hidden order by keyword desc"
        elif asc:
            command = "Select keyword from snippets where not hidden order by keyword"
        cursor.execute(command)
        rows = cursor.fetchall()
    for row in rows:
        keywords.append(row[0])

    logging.debug("Keywords listed successfully.")
    return keywords

def search(search_term):
    """Search for snippets by providing search terms"""
    logging.info("Searching for {!r} from list of snippets".format(search_term))
    searchResults ={}
    search_term = "%{}%".format(search_term)

    with connection, connection.cursor() as cursor:
        command = "Select * from snippets where message ilike %s and not hidden"
        print(command % search_term)
        cursor.execute(command,(search_term,))
        rows = cursor.fetchall()
        for row in rows:
            searchResults[row[0]] = row[1]
    return searchResults

def main():
    """main functions"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    put_group = put_parser.add_mutually_exclusive_group()
    put_group.add_argument("-i","--hide",help="Hide a snippet", action="store_true")
    put_group.add_argument("-u", "--unhide", help="Unhide a snippet", action="store_true")

    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")

    catalog_parser = subparsers.add_parser("catalog", help="List all keywords")
    catalog_group = catalog_parser.add_mutually_exclusive_group()
    catalog_group.add_argument("-a","--asc", help="Sort in ascending order", action="store_true")
    catalog_group.add_argument("-d", "--desc", help="Sort in descending order", action="store_true")

    search_parser = subparsers.add_parser("search", help="Search snippets by providing text that is in the snippet")
    search_parser.add_argument("search_term", help="String to search for")

    arguments = parser.parse_args()
    #Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        if not arguments["hide"]:
            print("Stored {!r} as {!r}".format(snippet, name))
        elif arguments["hide"]:
            print("Stored hidden snippet {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command =="catalog":
        keywords = catalog(**arguments)
        print("Avaliable keywords:")
        for keyword in keywords:
            print(keyword)
    elif command =="search":
        results = search(**arguments)
        print("Search results:")
        for result in results:
            print("{!r}: {!r}".format(result, results[result]))
if __name__ == "__main__":
    main()


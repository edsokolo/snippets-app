import logging
import argparse
import psycopg2

#Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

#Connect to Snippets Database
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")


def put(name, snippet):
    """
    Store a snippet with an associated name.
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        command = "insert into snippets values (%s, %s)"
        try:
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
        command = "select message from snippets where keyword = %s"
        cursor.execute(command, (name,))
        row = cursor.fetchone()

    logging.debug("Snippet retrieved successfully.")
    if not row:
        return "404: Snippet Not Found"
    return row[0]

def catalog():
    """List all available keywords"""
    logging.info("Listing all keywords")
    keywords = []

    with connection, connection.cursor() as cursor:
        command = "Select keyword from snippets order by keyword"
        cursor.execute(command)
        rows = cursor.fetchall()
    for row in rows:
        keywords.append(row[0])

    logging.debug("Keywords listed successfully.")
    return keywords


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

    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")

    catalog_parser = subparsers.add_parser("catalog", help="List all keywords")
#    catalog_parser.add_argument("number", type="int", help="Number of keywords to return")
#    catalog_parser.add_argument("-s","--sort", help="Sort keyword list", action = "store_true")
#    group= parser.add_mutually_exclusive_group()
#    group.add_argument("-a","--asc", type=str, help="Sort in ascending order", action="store_true")
#    group.add_argument("-d", "--desc", type=str, help="Sort in descending order", action="store_true")


    arguments = parser.parse_args()
    #Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command =="catalog":
        keywords = catalog()
        print("Avaliable keywords:")
        for keyword in keywords:
            print(keyword)
if __name__ == "__main__":
    main()


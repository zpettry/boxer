#!/usr/bin/env python
"""
This is the main file for Boxer.
"""
import argparse
import classes


def main(
    urls,
    extension,
    list,
    database,
    timeout,
    response_codes,
    urlsavailable,
    server_address,
    start_server,
    host,
):

    print(
        """
    ______                    
    | ___ \                   
    | |_/ / _____  _____ _ __ 
    | ___ \/ _ \ \/ / _ \ '__|
    | |_/ / (_) >  <  __/ |   
    \____/ \___/_/\_\___|_|                         
            
     Directory Bruteforcer
        
                 Zack Pettry
        """
    )
    # Create Operations instance.
    operations = classes.Operations()

    # Ad-hoc directory bruteforce.
    if urls and list and not database:
        if ".txt" in urls:
            with open(urls) as f:
                urls = f.read().splitlines()
        else:
            urls = [urls]

        for url in urls:
            if ("http" or "https") not in url:
                url_http = "http://" + url
                url_https = "https://" + url
                urls.remove(url)
                urls.append(url_http)
                urls.append(url_https)

        with open(list) as l:
            word_list = l.read().splitlines()

        for url in urls:
            operations.start_bruteforce(
                url, extension, word_list, database, timeout, response_codes
            )

        exit()

    # Directory bruteforce with database persistence.
    if urls and list and database:
        if ".txt" in urls:
            with open(urls) as f:
                urls = f.read().splitlines()
        else:
            urls = [urls]

        for url in urls:
            if ("http" or "https") not in url:
                url_http = "http://" + url
                url_https = "https://" + url
                urls.remove(url)
                urls.append(url_http)
                urls.append(url_https)

        with open(list) as l:
            word_list = l.read().splitlines()

        all_results = []
        for url in urls:
            results = operations.start_bruteforce(
                url, extension, word_list, database, timeout, response_codes
            )
            for result in results:
                all_results.append(result)

        operations.create_database(urls, all_results, database)
        exit()

    # Query local database for url or get urls available to query.
    if (urls or urlsavailable) and database and not server_address:
        operations.query_locally(urls, database, urlsavailable)
        exit()

    # Query the remote server with url or get urls available to query.
    if (urls or urlsavailable) and server_address and not database:
        operations.query_server(urls, server_address, urlsavailable)
        exit()

    # Start the server to allow for querying directory database.
    if start_server and database and host:
        server = classes.Server()

        server.start(database, host)

    print("Please add an argument for parsing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Boxer. A directory bruteforce ecosystem."
    )
    parser.add_argument(
        "-u",
        dest="urls",
        # nargs="+",
        action="store",
        required=False,
        help="This is a list of URL(s).",
    )
    parser.add_argument(
        "-e",
        dest="extension",
        # nargs="+",
        action="store",
        required=False,
        help="This will add an additional query with the extension to all words in the wordlist.",
    )
    parser.add_argument(
        "-w",
        dest="list",
        action="store",
        required=False,
        help="This is the wordslist for directory bruteforcing",
    )
    parser.add_argument(
        "-d",
        dest="database",
        action="store",
        required=False,
        help="This is the title for the local database. Database will be stored in json automatically.",
    )
    parser.add_argument(
        "-t",
        dest="timeout",
        action="store",
        default=30,
        type=int,
        required=False,
        help="This is to choose how long to wait for replies from the HTTP/S server.",
    )
    parser.add_argument(
        "-r",
        dest="response_codes",
        nargs="+",
        action="store",
        default=[200, 204, 301, 302, 307, 403],
        type=int,
        required=False,
        help="This is to choose how long to wait for replies from the HTTP/S server.",
    )
    parser.add_argument(
        "-urlsavailable",
        dest="urlsavailable",
        action="store_true",
        required=False,
        help="This is to get all available urls to query for sub-directories.",
    )
    parser.add_argument(
        "-s",
        dest="server_address",
        action="store",
        required=False,
        help="This is the server address to query for the directory database.",
    )
    parser.add_argument(
        "-server",
        dest="start_server",
        action="store_true",
        required=False,
        help="This is for starting the web server.",
    )
    parser.add_argument(
        "-host",
        dest="host",
        action="store",
        default="127.0.0.1",
        type=str,
        required=False,
        help="This is host address for the web server.",
    )

    args = parser.parse_args()

main(**vars(args))

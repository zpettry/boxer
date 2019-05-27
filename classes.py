import argparse
import asyncio
import aiohttp
import flask
import json
import ssl
import time
import requests

# Ignore SSL warnings for HTTPS Flask server.
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Operations:
    async def request(self, session, url, database, timeout):

        try:
            async with session.get(url, allow_redirects=False) as response:

                # print(f"Testing: {url}")
                if response.status in response_codez:
                    print(f"Status: {response.status}   {url}")
                    return response.status, url

        except asyncio.TimeoutError:
            print(
                f"asyncio.TimeoutError after {timeout} seconds: {url} . Consider increasing the timeout from default."
            )
            pass

        except aiohttp.client_exceptions.ServerDisconnectedError:
            print(f"Server disconnected error: {url}")
            pass

        except aiohttp.client_exceptions.ClientConnectorError:
            print(f"Client connector error: {url}")
            pass

    async def run_quickly(self, url, extension, directory_list, database, timeout):

        start = time.time()

        # Default 30 seconds.
        timeout_aiohttp = aiohttp.ClientTimeout(total=timeout)
        connector = aiohttp.TCPConnector(verify_ssl=False)

        async with aiohttp.ClientSession(
            timeout=timeout_aiohttp, connector=connector
        ) as session:

            tasks = []
            for directory in directory_list:
                url_modified = url + "/" + directory
                if extension:
                    url_modified_extension = url_modified + extension
                count = url_modified.count("//")
                if count < 2:
                    task = asyncio.create_task(
                        self.request(session, url_modified, database, timeout)
                    )
                    tasks.append(task)
                    if extension:
                        task_extension = asyncio.create_task(
                            self.request(
                                session, url_modified_extension, database, timeout
                            )
                        )
                        tasks.append(task_extension)

            await asyncio.gather(*tasks, return_exceptions=False)

            end = time.time()
            print(f"\nTime: {end - start} seconds.")

        return tasks

    def ignore_ssl_error(self, loop, context):
        """Ignore aiohttp #3535 issue with SSL data after close

        There appears to be an issue on Python 3.7 and aiohttp SSL that throws a
        ssl.SSLError fatal error (ssl.SSLError: [SSL: KRB5_S_INIT] application data
        after close notify (_ssl.c:2609)) after we are already done with the
        connection. See GitHub issue aio-libs/aiohttp#3535

        Given a loop, this sets up a exception handler that ignores this specific
        exception, but passes everything else on to the previous exception handler
        this one replaces.

        If the current aiohttp version is not exactly equal to aiohttpversion
        nothing is done, assuming that the next version will have this bug fixed.

        This can be disabled by setting this parameter to None

        """
        if context.get("message") == "SSL error in data received":
            # validate we have the right exception, transport and protocol
            exception = context.get("exception")
            protocol = context.get("protocol")

            if (
                isinstance(exception, ssl.SSLError)
                and exception.reason == "KRB5_S_INIT"
                and isinstance(protocol, asyncio.sslproto.SSLProtocol)
                and isinstance(
                    protocol._app_protocol, aiohttp.client_proto.ResponseHandler
                )
            ):
                if loop.get_debug():
                    asyncio.log.logger.debug("Ignoring aiohttp SSL KRB5_S_INIT error")
                return
            orig_handler(context)

    def start_bruteforce(
        self, url, extension, word_list, database, timeout, response_codes
    ):

        global response_codez
        response_codez = response_codes

        print(
            f"\nStarting bruteforce on {url} for response code(s) {response_codes}...\n"
        )

        database = []

        """
        I will use this when the above function is no longer needed.
        responses = asyncio.run(
            self.run_quickly(urls, extension, word_list, i, database))
        
        """
        loop = asyncio.get_event_loop()

        loop.set_exception_handler(self.ignore_ssl_error)

        responses = loop.run_until_complete(
            self.run_quickly(url, extension, word_list, database, timeout)
        )

        urls = []

        for response in responses:
            response = response.result()
            if response != None:
                urls.append(response)

            if (response not in database) and (response != None):
                database.append(response)

        return urls

    def create_database(self, urls, results, database):

        print(f"Creating local database: {database}.json")

        database_dict = {}
        for url in urls:
            if url not in database_dict.keys():
                database_dict[url] = []

        for k, v in database_dict.items():
            for url in results:
                if k in url[1]:
                    database_dict[k].append(url)

        with open(f"{database}.json", "w") as outfile:
            json.dump(database_dict, outfile)

        print("Done.")

    def query_locally(self, url, database, urls_available):

        with open(database, "r") as json_file:
            database = json.load(json_file)

        if urls_available:
            print("Available URLS in database:\n")
            for k, v in database.items():
                print(k)
            exit()

        for k, v in database.items():
            if url in k:
                result = v

        for url in result:
            print(f"Status: {url[0]}   {url[1]}")

    def query_server(self, url, server, urls_available):

        if urls_available:
            # Define URL for Flask API endpoint.
            REST_API_URL = f"https://{server}:45000/urls_available"

        else:
            # Define URL for Flask API endpoint.
            REST_API_URL = f"https://{server}:45000/query"

        # Set the payload to JSON format.
        payload = {"url": url}

        # Submit the POST request.
        r = requests.post(REST_API_URL, json=payload, verify=False)
        response = r.json()

        # Ensure the request was sucessful.
        try:

            if response["directories"]:
                # Loop over the directories and display them.
                for url in response["directories"][0]["result"]:
                    print(f"Status: {url[0]}   {url[1]}")

        # Ensure the request was sucessful.
        except:

            # Loop over the directories and display them.
            for url in response["urls_available"][0]["result"]:
                print(url)


class Server:
    def start(self, database, host):

        # Initialize our Flask application.
        app = flask.Flask(__name__)

        # Initialize the directory database.
        with open(database, "r") as json_file:
            database = json.load(json_file)

        @app.route("/query", methods=["POST"])
        def query():

            # Initialize the dictionary for the response.
            data = {"success": False}

            # Check if POST request.
            if flask.request.method == "POST":

                # Grab and process the incoming json.
                incoming = flask.request.get_json()
                url = incoming["url"]

                # Search for url in directory database.
                data["directories"] = []

                for k, v in database.items():
                    if url in k:
                        result = v

                r = {"result": result, "url": url}

                data["directories"].append(r)

                # Show that the request was a success.
                data["success"] = True

            # Return the data as a JSON response.
            return flask.jsonify(data)

        @app.route("/urls_available", methods=["POST"])
        def urls_available():

            # Initialize the dictionary for the response.
            data = {"success": False}

            # Check if POST request.
            if flask.request.method == "POST":

                # Grab and process the incoming json.
                incoming = flask.request.get_json()
                url = incoming["url"]

                # Search for url in directory database.
                data["urls_available"] = []

                result = []
                for k, v in database.items():
                    result.append(k)

                r = {"result": result}

                data["urls_available"].append(r)

                # Show that the request was a success.
                data["success"] = True

            # Return the data as a JSON response.
            return flask.jsonify(data)

        app.run(host=host, port=45000, ssl_context="adhoc")


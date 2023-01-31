from concurrent.futures.process import _sendback_result
from http.server import HTTPServer, BaseHTTPRequestHandler

from io import BytesIO
from datetime import datetime,timezone
import os
import logging
import time
from urllib.parse import urlparse,parse_qs
from pathlib import Path
import importlib.util
import mimetypes


# Simple HTTP(s) web service to host files and be able to do simple request/response changes.
# Inspired by: https://blog.anvileight.com/posts/simple-python-http-server/


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # supress all standard logging.
    def log_message(self, format, *args):
        return

    def load_module(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


    def do_GET(self):
        # 192.168.1.1 - - [21/Apr/2021 10:22:45] "GET /favicon.ico HTTP/1.1" 200 -
        logging.debug("%s %s", self.client_address[0], self.requestline)

        # Let's do a little bit of security :-)
        if ".." in self.path:
            self.send_error(404, "Yea, so we can't do files with double dots....")
            return

        for header in self.headers:
            logging.info("HEADER %s:%s", header, self.headers[header])

        url = urlparse(self.path)
        if url.query:
            logging.info(parse_qs(url.query))
        logging.info("----------------------")

        try:
            filetoread = url.path[1:]

            if url.path.endswith(".slow.json") or url.path.endswith(".slow.py"):
                time.sleep(5)
            
            # If we have .py file we load it as a module and execute it as a method.
            # This allows us to create simple modules that can give dynamic responses.
            if url.path.endswith(".py"):
                if os.path.exists(filetoread):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    py = self.load_module(Path(filetoread).stem, filetoread)
                    runresult = py.RunMe(url)
                    self.wfile.write(runresult.encode())
                else:
                    logging.debug(f"file DOES NOT exists: {filetoread}")
                    self.send_error(404, f"File Not Found: {self.path}")
                    self.end_headers()
            else: # Must be anormal file?
                if os.path.exists(self.path[1:]):
                    filetoread = self.path[1:]

                if os.path.exists(filetoread):
                    self.send_response(200)
                    mimetype, encoding = mimetypes.guess_type(filetoread, strict=True)
                    logging.debug(f"MIMETYPE: {mimetype}; Encoding: {encoding}")
                    if mimetype != None:
                        self.send_header('Content-type', mimetype)
                    self.send_header('Content-length', os.path.getsize(filetoread))
                    self.end_headers()
                    f = open(filetoread, 'rb')
                    self.wfile.write(f.read())
                    f.close()
                else:
                    logging.debug(f"file DOES NOT exists: {filetoread}")
                    self.send_error(404, f"File Not Found: {self.path}")
                    self.end_headers()
        except BaseException as err:
            logging.error(err)
            self.send_error(500, f"Unexpected {err=}, {type(err)=}")

    def do_POST(self):
        # url = urlparse(self.path)
        # logging.debug("URL PATH: %s", url.path)
        # if (url.path == "/XtensionsConnector/response.json"):
        #     self.send_response(401)
        #     self.send_header("WWWAuthenticate", "NTLM")
        #     self.end_headers()
        #     return
        
        logging.debug("%s %s", self.client_address[0], self.requestline)
        for header in self.headers:
            logging.info("HEADER %s:%s", header, self.headers[header])
        logging.info("----------------------")

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(body)
        self.wfile.write(response.getvalue())
        # TODO: add name of tile to dump file.
        # TODO: Dump file to console in well formatted JSON ?
        print(body)
        f = open('dumps/%s.raw' % datetime.now(timezone.utc).isoformat(), "wb")
        f.write(body)
        f.close()


def main():
    logging.basicConfig(
        encoding='utf-8',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)8s %(module)s (%(funcName)s): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        )
    try:
        httpd = HTTPServer(('0.0.0.0', 8888), SimpleHTTPRequestHandler)
        logging.info("Started http-server on port 8888...")

        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("^C received, shutting down server")
        httpd.socket.close()

if __name__ == '__main__':
    main()

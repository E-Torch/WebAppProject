import json
import socketserver
import os
from util.request import Request
from util.response import Response
from pymongo import MongoClient

CURRPATH = os.path.dirname(__file__)

mongo_client = MongoClient("database")
db = mongo_client["cse312"]
chat_collection = db["chat"]


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        mimeTypes = {
            "js": "text/javascript",
            "css": "text/css",
            "ico": "image/x-icon",
            "jpg": "image/jpg",
            "/": "text/html; charset=UTF-8",
        }
        received_data = self.request.recv(2048)
        # print(self.client_address)
        # print("--- received data ---")
        # print(received_data)
        # print("--- end of data ---\n\n")
        request = Request(received_data)
        print(request.headers)
        print(request.body)
        if request.method == "GET" and request.path == "/":
            response = self.getIndex(mimeTypes, request)
            self.request.sendall(response.makeResponse())
            return
        if self.getOtherFiles(mimeTypes, request):
            return

        path_arr = request.path.replace("/", " ").strip().split(" ")
        path = ""
        path_id = ""

        if len(path_arr) == 2:

            path = path_arr.pop(0)
            path_id = path_arr.pop(0)
        else:
            path = path_arr.pop(0)

        if request.method == "GET" and path == "chat-messages" and path_id == "":
            array = []
            result = chat_collection.find({})
            for collection in result:
                message = {}
                message["message"] = collection["message"]
                message["username"] = collection["username"]
                message["id"] = collection["id"]
                array.append(message)
            array = json.dumps(array)
            response = Response("200 OK", array, "text/plain").makeResponse()
            self.request.sendall(response)

            return
        if request.method == "GET" and path == "chat-messages" and path_id != "":
            message = {}
            result = chat_collection.find({"id": path_id})
            for collection in result:

                message["message"] = collection["message"]
                message["username"] = collection["username"]
                message["id"] = collection["id"]

            if "id" in message:
                message = json.dumps(message)
                response = Response(
                    "200 OK", message, "application/json"
                ).makeResponse()
                self.request.sendall(response)
            else:
                self.send404(b"no message found")
            return

        if request.method == "DELETE" and path == "chat-messages" and path_id != "":
            result = chat_collection.delete_one({"id": path_id})
            if result.deleted_count:
                response = Response("204 No Content", b"", "text/plain").makeResponse()
                self.request.sendall(response)
            else:
                self.send404(b"no record exist to delete")
            return
        if request.method == "PUT" and path == "chat-messages" and path_id != "":
            request.html_escape_body()
            request.body = json.loads(request.body)
            query = {"id": path_id}
            update = {
                "message": request.body["message"],
                "username": request.body["username"],
            }
            result = chat_collection.update_one(query, update)
            if result.modified_count:
                result = chat_collection.find({"id": path_id})
                message = {}
                for collection in result:
                    message["message"] = collection["message"]
                    message["username"] = collection["username"]
                    message["id"] = collection["id"]
                message = json.dumps(message)
                response = Response(
                    "200 okay", message, "application/json"
                ).makeResponse()
                self.request.sendall(response)
            else:
                self.send404(b"no record exist to modify")
            return
        if request.method == "POST" and path == "chat-messages":
            request.html_escape_body()
            request.body = json.loads(request.body)
            chat_count = self.get_count(chat_collection)
            result = chat_collection.insert_one(
                {
                    "username": "Guest",
                    "message": request.body["message"],
                    "id": str(chat_count + 1),
                }
            )

            result = chat_collection.find({"_id": result.inserted_id})
            message = {}
            for collection in result:
                message["message"] = collection["message"]
                message["username"] = collection["username"]
                message["id"] = collection["id"]
            message = json.dumps(message)
            response = Response(
                "201 Created", message, "application/json"
            ).makeResponse()
            self.request.sendall(response)
            return

        self.send404(b"not found")

    def send404(self, msg):
        response = Response("404 Not Found", msg, "text/plain").makeResponse()
        self.request.sendall(response)

    def get_count(self, chat_collection):
        chat_count = 0
        for l in chat_collection.find({}):
            chat_count += 1
        return chat_count

    def getOtherFiles(self, MIME, request):
        path = os.path.join(CURRPATH, request.path[1:])
        if os.path.isfile(path):
            ext = request.path.split(".").pop()
            mime = MIME[ext]
            response = self.setPublicResponse(path, mime)
            self.request.sendall(response.makeResponse())
            return True
        return False

    def getIndex(self, MIME, request):
        path = os.path.join(CURRPATH, "public/index.html")
        mime = MIME[request.path]
        response = self.setPublicResponse(path, mime)
        response.body
        self.check_visits_cookie(request, response)
        return response

    def check_visits_cookie(self, request, response):
        if "visits" in request.cookies:
            response.setCookie("visits", str(int(request.cookies["visits"]) + 1))
            response.setCookie("Max-Age", "3600")
            response.replaceInBody(
                b"{{visits}}", str.encode(response.cookies["visits"])
            )
            response.setHeaders("Content-Length", str(len(response.body)))
        else:
            response.setCookie("visits", "1")
            response.setCookie("Max-Age", "3600")
            response.replaceInBody(
                b"{{visits}}", str.encode(response.cookies["visits"])
            )
            response.setHeaders("Content-Length", str(len(response.body)))

    def setPublicResponse(self, filepath, mime):
        f = open(
            filepath,
            "rb",
        )
        body = f.read()
        f.close()
        response = Response("200 OK", body, mime)
        return response


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()

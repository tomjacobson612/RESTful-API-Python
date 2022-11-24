import db
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

pw = 'REDACTED'
db_name = 'guids'
connection = db.connect_to_server("localhost", "root", pw, db_name)
items=[]


class Guid(RequestHandler):
    def get(self, slug):
        result = db.read_guid(slug)
        if result is None:
            self.write("Error: guid does not exist in database.")
            self.write(f"\n Status Code: {self.get_status()}")
        else:
            self.write(result)
            self.write(f"\n Status Code: {self.get_status()}")

    def post(self, slug):
        result = db.create(slug, self.request.body)

        if result is None:
            self.write("Error: Creation unsuccessful.")
            self.write(f"\n Status Code: {self.get_status()}")

        else:
            self.write(result)
            self.write(f"\n Status Code: {self.get_status()}")

    def put(self, slug):
        result = db.update_guid_metadata(slug, self.request.body)
        self.write(result)
        self.write(f"\n Status Code: {self.get_status()}")

    def delete(self, slug):
        db.delete(slug)
        self.write(f"\n Status Code: {self.get_status()}")


def make_app():
    urls = [
    ("/guid/([^/]+)?", Guid)
    ]
    return Application(urls, debug=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(3000)
    IOLoop.instance().start()
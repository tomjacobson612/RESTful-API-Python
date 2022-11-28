import db
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

pw = 'REDACTED'
db_name = 'guids'
connection = db.connect_to_server("localhost", "root", pw, db_name)


class Guid(RequestHandler):
    def get(self, slug):
        """Returns metadata associated with given GUID."""

        result = db.read_guid(slug)

        if result is None:
            RequestHandler.set_status(self, status_code=204)

        else:
            self.write(result)

    def post(self, slug):
        """Queries database for item with given GUID. If item already exists it is updated, otherwise it is created."""

        try:
            result = db.create_or_update(slug, self.request.body)

            if result == -1:
                RequestHandler.set_status(self, status_code=400)

            else:
                self.write(result)

        except KeyError as e:
            RequestHandler.set_status(self, status_code=400)

    def delete(self, slug):
        """Removes item with given GUID from database."""
        db.delete(slug)


def make_app():
    urls = [
    ("/guid/([^/]+)?", Guid)
    ]
    return Application(urls, debug=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(3000)
    IOLoop.instance().start()
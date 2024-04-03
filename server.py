from flask import Flask, request, abort

app = Flask(__name__)


# @app.get("/friend")
# def get_friends():
#     return "GOTCHA", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        print(request.json)
        return "Success", 201
    else:
        abort(400)


if __name__ == "__main__":
    app.run()

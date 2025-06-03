from flask import Flask, Response
import json
import time




app = Flask(__name__)





@app.route("/stream/evenrts")
def getSse():
    def generate():
        for i in range(10):
            data = {
                "writer": "vinit",
                "author": "ankush"

            }

        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(1)
    return Response(generate(), mimetype="text/event-stream" )



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080,)

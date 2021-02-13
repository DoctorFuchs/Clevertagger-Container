from flask import Flask, request, jsonify
import clevertagger

clever = clevertagger.Clevertagger()

api = Flask(__name__)

@api.route("/", methods=["POST", "GET"])
def index():
    final = {}
    text = ""
    if request.method == 'POST':
        text = request.form["text"]
        
    else:
        text = request.args.get("text")

    textsplit = text.split()

    for i in range(len(textsplit)):
        result = str(clever.tag([textsplit[i]]))
        result = result.split("\\t")
        result2 = result[1].split("']")
        final[str(textsplit[i])] = result2[0]

    return jsonify(final)
      
if __name__ == "__main__":
    api.run("0.0.0.0", port=80, debug=True)
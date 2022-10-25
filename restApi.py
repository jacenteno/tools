from flask import Falsk, jsonify 


app = Flask(__name__)

@app.route('/')
def index():
    return "Bienvenido al Curso de API con Flask"

if __name__=="__main__":
    app.run(deb)
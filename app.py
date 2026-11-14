"""API REST de mensagens. Os dados existem apenas em memoria."""

from flask import Flask, abort, jsonify, request, url_for
from werkzeug.exceptions import HTTPException


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False

    # Cada mensagem e um recurso, identificado pelo seu id na URL.
    mensagens = {1: {"id": 1, "texto": "Hello World!"}}
    proximo_id = 2

    def ler_texto():
        if not request.is_json:
            abort(415, description="Envie o corpo com Content-Type: application/json.")
        dados = request.get_json()
        if not isinstance(dados, dict):
            abort(400, description="Envie um objeto JSON com o campo texto.")
        texto = dados.get("texto")
        if not isinstance(texto, str) or not texto.strip():
            abort(400, description="O campo texto deve ser uma string nao vazia.")
        return texto.strip()

    def buscar_mensagem(mensagem_id):
        if mensagem_id not in mensagens:
            abort(404, description="Mensagem nao encontrada.")
        return mensagens[mensagem_id]

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        resposta = erro.get_response()
        resposta.data = app.json.dumps({"erro": erro.description})
        resposta.content_type = "application/json"
        return resposta

    @app.get("/")
    def hello_world():
        return jsonify({"mensagem": "Hello World!"})

    @app.get("/api/mensagens")
    def listar_mensagens():
        return jsonify(list(mensagens.values()))

    @app.get("/api/mensagens/<int:mensagem_id>")
    def consultar_mensagem(mensagem_id):
        return jsonify(buscar_mensagem(mensagem_id))

    @app.post("/api/mensagens")
    def criar_mensagem():
        nonlocal proximo_id
        texto = ler_texto()
        mensagem = {"id": proximo_id, "texto": texto}
        mensagens[proximo_id] = mensagem
        proximo_id += 1
        resposta = jsonify(mensagem)
        resposta.status_code = 201
        resposta.headers["Location"] = url_for("consultar_mensagem", mensagem_id=mensagem["id"])
        return resposta

    @app.put("/api/mensagens/<int:mensagem_id>")
    def atualizar_mensagem(mensagem_id):
        mensagem = buscar_mensagem(mensagem_id)
        mensagem["texto"] = ler_texto()
        return jsonify(mensagem)

    @app.delete("/api/mensagens/<int:mensagem_id>")
    def excluir_mensagem(mensagem_id):
        buscar_mensagem(mensagem_id)
        del mensagens[mensagem_id]
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)

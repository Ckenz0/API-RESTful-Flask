"""Testes do contrato HTTP, sem banco de dados ou servicos externos."""

import json
import unittest

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_raiz_da_api_retorna_json(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), {"mensagem": "Hello World!"})

    def test_lista_inicial_contem_mensagem(self):
        resposta = self.client.get("/api/mensagens")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), [{"id": 1, "texto": "Hello World!"}])

    def test_criacao_pode_ser_consultada_pelo_location(self):
        resposta = self.client.post("/api/mensagens", json={"texto": "Ola, Flask!"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.get_json(), {"id": 2, "texto": "Ola, Flask!"})
        consulta = self.client.get(resposta.headers["Location"])
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.get_json(), resposta.get_json())

    def test_atualizacao_persiste_na_consulta(self):
        resposta = self.client.put("/api/mensagens/1", json={"texto": "Mensagem atualizada"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.client.get("/api/mensagens/1").get_json(),
                         {"id": 1, "texto": "Mensagem atualizada"})

    def test_exclusao_remove_mensagem_e_retorna_corpo_vazio(self):
        resposta = self.client.delete("/api/mensagens/1")
        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(resposta.data, b"")
        self.assertEqual(self.client.get("/api/mensagens/1").status_code, 404)
        self.assertEqual(self.client.get("/api/mensagens").get_json(), [])

    def test_ids_nao_sao_reutilizados_apos_exclusao(self):
        self.client.delete("/api/mensagens/1")
        resposta = self.client.post("/api/mensagens", json={"texto": "Nova mensagem"})
        self.assertEqual(resposta.get_json()["id"], 2)

    def test_recurso_inexistente_retorna_404_em_json(self):
        for metodo in ("get", "put", "delete"):
            with self.subTest(metodo=metodo):
                resposta = self.client.open("/api/mensagens/999", method=metodo,
                                           json={"texto": "Ola"})
                self.assertEqual(resposta.status_code, 404)
                self.assertIn("erro", resposta.get_json())

    def test_post_e_put_rejeitam_texto_invalido_sem_alterar_dados(self):
        for metodo, url in (("POST", "/api/mensagens"), ("PUT", "/api/mensagens/1")):
            for corpo in ({}, {"texto": ""}, {"texto": "   "}, {"texto": 42},
                          {"texto": None}, [], ["Ola"], "Ola", None):
                with self.subTest(metodo=metodo, corpo=corpo):
                    resposta = self.client.open(url, method=metodo,
                                               data=json.dumps(corpo),
                                               content_type="application/json")
                    self.assertEqual(resposta.status_code, 400)
                    self.assertIn("erro", resposta.get_json())
        self.assertEqual(self.client.get("/api/mensagens").get_json(),
                         [{"id": 1, "texto": "Hello World!"}])

    def test_json_malformado_retorna_400(self):
        resposta = self.client.post("/api/mensagens", data='{"texto":',
                                    content_type="application/json")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.get_json())

    def test_envio_sem_content_type_json_retorna_415(self):
        resposta = self.client.post("/api/mensagens", data="texto=Ola")
        self.assertEqual(resposta.status_code, 415)
        self.assertIn("erro", resposta.get_json())

    def test_texto_tem_espacos_externos_removidos(self):
        resposta = self.client.post("/api/mensagens", json={"texto": "  Ola!  "})
        self.assertEqual(resposta.get_json()["texto"], "Ola!")


if __name__ == "__main__":
    unittest.main()

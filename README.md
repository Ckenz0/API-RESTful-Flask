# API RESTful Flask

API de mensagens feita com Python 3.12 e Flask. Permite criar, listar, consultar, atualizar e excluir mensagens, com respostas em JSON.

[API no Azure](https://api-restful-flask-akd2cqdwgcakefgk.brazilsouth-01.azurewebsites.net/) · [Coleção do Postman](postman/messages-api.postman_collection.json)

## Executar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Endereço local: `http://127.0.0.1:5000`.

## Rotas

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/` | Mensagem de boas-vindas |
| GET | `/api/mensagens` | Lista as mensagens |
| GET | `/api/mensagens/{id}` | Consulta uma mensagem |
| POST | `/api/mensagens` | Cria uma mensagem |
| PUT | `/api/mensagens/{id}` | Atualiza uma mensagem |
| DELETE | `/api/mensagens/{id}` | Exclui uma mensagem |

POST e PUT recebem `Content-Type: application/json` e um corpo como:

```json
{"texto": "Olá, Flask!"}
```

As mensagens ficam em memória e são apagadas quando a aplicação reinicia.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No Postman, importe a [coleção](https://raw.githubusercontent.com/Ckenz0/API-RESTful-Flask/main/postman/messages-api.postman_collection.json) e use **Run collection** para executar as requisições na ordem. A variável `baseUrl` já aponta para o Azure; para testar localmente, troque por `http://127.0.0.1:5000`.

## Deploy

O GitHub Actions executa os testes e publica a API no Azure App Service após alterações na `main`. No Azure, a aplicação roda com Gunicorn, iniciado pelo arquivo `startup.sh`.

Autor: Cauê Kenzo Adaniya.

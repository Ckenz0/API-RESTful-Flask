# API RESTful Flask

API de mensagens desenvolvida em Python 3.12 e Flask, com respostas JSON, testes automatizados e deploy contínuo no Azure App Service.

Autor: **Cauê Kenzo Adaniya**.

## Código e coleção

- [API publicada no Azure](https://api-restful-flask-akd2cqdwgcakefgk.brazilsouth-01.azurewebsites.net/)
- [Repositório](https://github.com/Ckenz0/API-RESTful-Flask)
- [Código da API](https://github.com/Ckenz0/API-RESTful-Flask/blob/main/app.py)
- [Coleção do Postman](https://github.com/Ckenz0/API-RESTful-Flask/blob/main/postman/messages-api.postman_collection.json)
- [JSON da coleção para importação por link](https://raw.githubusercontent.com/Ckenz0/API-RESTful-Flask/main/postman/messages-api.postman_collection.json)

## Executar localmente

Com Python instalado, abra um terminal na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

A API fica disponível em <http://127.0.0.1:5000/>. Para encerrar, pressione `Ctrl+C`. O servidor Flask é utilizado no desenvolvimento local; no Azure, `startup.sh` inicia o Gunicorn.

No VS Code, selecione o interpretador `.venv/Scripts/python.exe` e execute a configuração **API REST** pelo F5.

## Endpoints

| Método | Caminho | Operação | Status de sucesso |
| --- | --- | --- | --- |
| GET | `/` | Mensagem de boas-vindas em JSON | 200 |
| GET | `/api/mensagens` | Listar mensagens | 200 |
| GET | `/api/mensagens/{id}` | Consultar mensagem | 200 |
| POST | `/api/mensagens` | Criar mensagem | 201 |
| PUT | `/api/mensagens/{id}` | Atualizar mensagem | 200 |
| DELETE | `/api/mensagens/{id}` | Excluir mensagem | 204 |

POST e PUT recebem um objeto JSON com o cabeçalho `Content-Type: application/json`:

```json
{"texto": "Olá, Flask!"}
```

O POST retorna o recurso criado, por exemplo `{"id": 2, "texto": "Olá, Flask!"}`, e o cabeçalho `Location` com o caminho para consultá-lo. DELETE retorna um corpo vazio. A raiz retorna `{"mensagem": "Hello World!"}`.

O campo `texto` deve ser uma string não vazia; espaços externos são removidos e campos adicionais são ignorados. Erros retornam `{"erro": "descrição"}`:

- **400:** JSON malformado ou campo `texto` inválido.
- **404:** mensagem ou rota inexistente.
- **405:** método HTTP não permitido para a rota.
- **415:** corpo enviado sem `Content-Type: application/json`.

As mensagens ficam em memória. Cada inicialização começa com `{"id": 1, "texto": "Hello World!"}`; os dados são perdidos em reinicializações e novos deploys. Por isso, `startup.sh` usa um único worker e a aplicação deve permanecer em uma única instância.

## Testar no Postman

1. Abra o Postman e clique em **Import**.
2. Selecione `postman/messages-api.postman_collection.json` ou cole o link do JSON disponível acima.
3. Abra a coleção **Messages API** e confira a variável `baseUrl`, que já aponta para a API no Azure:
   - Local: `http://127.0.0.1:5000`.
   - Azure: `https://api-restful-flask-akd2cqdwgcakefgk.brazilsouth-01.azurewebsites.net`.
4. Salve a variável, clique em **Run collection** e execute as 11 requisições na ordem numerada, com uma iteração.
5. Confira o resultado: **23 verificações aprovadas**. As respostas 400, 404 e 415 são casos de erro esperados e fazem parte dos testes.

O POST salva automaticamente o identificador em `mensagemId`. As requisições seguintes consultam, atualizam e excluem somente a mensagem criada pela coleção. A mensagem inicial é preservada, permitindo repetir a execução.

Para compartilhar a coleção, use o link do arquivo JSON no GitHub. Também é possível importá-la em seu workspace do Postman e usar **Share → Copy link**, dando acesso ao destinatário.

## Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os 11 testes cobrem o contrato HTTP, operações sobre mensagens, validações, geração de IDs e respostas de erro.

Com Node.js instalado e a API local em execução, também é possível executar a coleção do Postman com Newman:

```powershell
npx --yes newman@6.2.3 run postman/messages-api.postman_collection.json --env-var "baseUrl=http://127.0.0.1:5000"
```

Para executar a coleção no Azure, use o endereço padrão salvo no arquivo:

```powershell
npx --yes newman@6.2.3 run postman/messages-api.postman_collection.json
```

## Deploy automático no Azure

Use um App Service com publicação de **Código**, sistema **Linux**, runtime **Python 3.12** e plano **Free F1**.

O App Service **API-RESTful-Flask** está conectado a este repositório pela Central de Implantação do Azure. A autenticação do workflow usa OpenID Connect (OIDC), com os identificadores cadastrados pelo Azure nos secrets do repositório.

O pipeline configura automaticamente `SCM_DO_BUILD_DURING_DEPLOYMENT=true` e o comando de inicialização `sh startup.sh` antes da publicação.

Em **Settings → Secrets and variables → Actions**, a variável `AZURE_WEBAPP_NAME` contém `API-RESTful-Flask`. Os secrets utilizados pela conexão OIDC são:

| Identificador | Secret |
| --- | --- |
| Cliente da identidade | `AZUREAPPSERVICE_CLIENTID_249D317F020E4E53A75149FD65ED73E7` |
| Diretório | `AZUREAPPSERVICE_TENANTID_2F9ADF9D15E9459BADCF64306BF9656F` |
| Assinatura | `AZUREAPPSERVICE_SUBSCRIPTIONID_4E9F7C0527464F9B913CB00DCD727A79` |

A identidade possui uma credencial federada para a branch `main` deste repositório e precisa de permissão de publicação no App Service. Se a conexão for recriada no portal, confira os nomes dos secrets gerados e atualize as referências do workflow. Valores de credenciais permanecem nos secrets.

O workflow `.github/workflows/azure-app-service.yml`:

1. Executa os testes Python e a coleção do Postman com Gunicorn em pull requests e pushes para `main`.
2. Empacota somente `app.py`, `requirements.txt` e `startup.sh`.
3. Publica o ZIP no Azure apenas após os testes passarem, em pushes para `main` ou execução manual na `main`, quando `AZURE_WEBAPP_NAME` estiver configurada.
4. Executa a coleção do Postman na URL pública após o deploy.
5. Disponibiliza os relatórios de teste na seção **Artifacts** da execução, por sete dias.

Acompanhe as execuções na [aba Actions](https://github.com/Ckenz0/API-RESTful-Flask/actions). Enquanto `AZURE_WEBAPP_NAME` não estiver configurada, somente os testes são executados e o job de deploy aparece como **Skipped**. Depois de configurar a variável e o secret, use **Actions → API Flask CI/CD → Run workflow** na branch `main` para fazer a primeira publicação. Mantenha um único workflow responsável pelo deploy para evitar publicações duplicadas com a Central de Implantação do Azure.

Referências: [Flask](https://flask.palletsprojects.com/), [GitHub Actions e App Service](https://learn.microsoft.com/azure/app-service/deploy-github-actions), [importar dados no Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data/) e [executar coleções com Newman](https://github.com/postmanlabs/newman).

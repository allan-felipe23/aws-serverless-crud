# ☁️ AWS Serverless CRUD API

Este projeto é um CRUD completo (Create, Read, Update, Delete) de produtos utilizando arquitetura Serverless na AWS.

## 🏗 Arquitetura

- **Frontend:** HTML5, JavaScript (Fetch API) e TailwindCSS.
- **Backend:** AWS Lambda (Python 3.14).
- **Banco de Dados:** Amazon DynamoDB (NoSQL).
- **API Gateway:** HTTP API para roteamento.

## 🚀 Como Executar

### Pré-requisitos
- Conta na AWS (Free Tier).
- Python 3 instalado (opcional, apenas para testes locais).

### Passos
1. Crie uma tabela no **DynamoDB** chamada `Produtos`.
2. Crie uma função **Lambda** e cole o código da pasta `backend/`.
3. Configure as permissões (IAM) para a Lambda acessar o DynamoDB.
4. Crie uma **HTTP API** no API Gateway e conecte à Lambda.
5. Copie a URL da API e cole no arquivo `frontend/index.html`.
6. Abra o `index.html` com Live Server.

## 📸 Screenshots

<img width="1916" height="972" alt="Captura de tela 2025-12-10 081849" src="https://github.com/user-attachments/assets/3d632a2b-de46-4848-a433-8003b7c3aec6" />


---
Desenvolvido por Allan Borges para fins de estudo sobre Arquitetura Cloud.

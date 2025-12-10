import json
import boto3
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

# Inicializa o DynamoDB
dynamodb = boto3.resource('dynamodb')
tabela_produtos = dynamodb.Table('Produtos')

# CONFIGURAÇÃO DE CORS
# Permite que o Front-end acesse os códigos de resposta corretamente
HEADERS_CORS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    try:
        # 1. Normalizar Entrada
        http = event.get('requestContext', {}).get('http', {})
        metodo = http.get('method') or event.get('httpMethod')
        caminho = event.get('rawPath') or event.get('path', '/')
        
        print(f"📨 Requisição: {metodo} {caminho}")

        # Tratamento de Preflight (CORS)
        if metodo == 'OPTIONS':
            return {'statusCode': 200, 'headers': HEADERS_CORS, 'body': ''}
        
        # 2. Roteamento
        if metodo == 'POST':
            return criar_produto(event)
        
        elif metodo == 'GET':
            caminho_limpo = caminho.rstrip('/')
            ultimo_item = caminho_limpo.split('/')[-1]
            
            if ultimo_item == 'produtos':
                return listar_produtos()
            else:
                return buscar_produto(ultimo_item)
        
        elif metodo == 'PUT':
            id_produto = caminho.rstrip('/').split('/')[-1]
            return atualizar_produto(id_produto, event)
        
        elif metodo == 'DELETE':
            id_produto = caminho.rstrip('/').split('/')[-1]
            return deletar_produto(id_produto)
        
        else:
            return resposta_erro(405, f"Método {metodo} não permitido")

    except Exception as erro:
        print(f"❌ Erro Crítico: {str(erro)}")
        return resposta_erro(500, f"Erro interno: {str(erro)}")

# CREATE (POST) -> Retorna 201
def criar_produto(event):
    try:
        # parse_float=Decimal é OBRIGATÓRIO para o DynamoDB
        corpo = json.loads(event['body'], parse_float=Decimal)
        
        # Validação de campos obrigatórios
        for campo in ['nome', 'preco', 'quantidade']:
            if campo not in corpo:
                return resposta_erro(400, f"Campo obrigatório faltando: {campo}")

        # Validação de valores negativos
        if corpo['preco'] < 0 or int(corpo['quantidade']) < 0:
             return resposta_erro(400, "Preço e quantidade não podem ser negativos")

        id_produto = str(uuid4())[:8]
        agora = datetime.now().isoformat()
        
        item = {
            'id': id_produto,
            'nome': corpo['nome'].strip(),
            'preco': corpo['preco'], # Já é Decimal
            'quantidade': int(corpo['quantidade']),
            'descricao': corpo.get('descricao', ''),
            'categoria': corpo.get('categoria', 'geral'),
            'ativo': True,
            'data_criacao': agora,
            'data_atualizacao': agora
        }
        
        tabela_produtos.put_item(Item=item)
        
        return {
            'statusCode': 201, # ✅ 201 Created
            'body': json.dumps({'mensagem': 'Produto criado com sucesso', 'produto': item}, default=str),
            'headers': HEADERS_CORS
        }
    except Exception as e: return resposta_erro(500, str(e))

# READ (GET) -> Retorna 200
def listar_produtos():
    try:
        resposta = tabela_produtos.scan()
        return {
            'statusCode': 200, # ✅ 200 OK
            'body': json.dumps(resposta.get('Items', []), default=str),
            'headers': HEADERS_CORS
        }
    except Exception as e: return resposta_erro(500, str(e))

def buscar_produto(id_produto):
    try:
        resposta = tabela_produtos.get_item(Key={'id': id_produto})
        item = resposta.get('Item')
        
        if not item: 
            return resposta_erro(404, "Produto não encontrado") # ❌ 404 Not Found
        
        return {
            'statusCode': 200, # ✅ 200 OK
            'body': json.dumps(item, default=str),
            'headers': HEADERS_CORS
        }
    except Exception as e: return resposta_erro(500, str(e))

# UPDATE (PUT) -> Retorna 200
def atualizar_produto(id_produto, event):
    try:
        corpo = json.loads(event['body'], parse_float=Decimal)
        
        # Verificar existência antes de tentar atualizar
        if 'Item' not in tabela_produtos.get_item(Key={'id': id_produto}):
            return resposta_erro(404, "Produto não encontrado")

        # Construção Dinâmica da Query
        update_expr = 'SET data_atualizacao = :data'
        expr_values = {':data': datetime.now().isoformat()}
        expr_names = {} 

        tem_campos = False
        for campo in ['nome', 'preco', 'quantidade', 'descricao', 'categoria', 'ativo']:
            if campo in corpo:
                update_expr += f', #{campo} = :{campo}'
                expr_values[f':{campo}'] = corpo[campo]
                expr_names[f'#{campo}'] = campo
                tem_campos = True
        
        if not tem_campos:
            return resposta_erro(400, "Nenhum campo enviado para atualizar")

        tabela_produtos.update_item(
            Key={'id': id_produto},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names
        )
        
        return {
            'statusCode': 200, # ✅ 200 OK (Atualizado)
            'body': json.dumps({'mensagem': 'Atualizado com sucesso'}, default=str),
            'headers': HEADERS_CORS
        }
    except Exception as e: return resposta_erro(500, str(e))

# DELETE (DELETE) -> Retorna 200
def deletar_produto(id_produto):
    try:
        # Tenta deletar direto (DynamoDB não reclama se o ID não existir, mas podemos verificar antes se quisermos ser estritos)
        # Para simplificar e ser idempotente, mandamos deletar.
        
        tabela_produtos.delete_item(Key={'id': id_produto})
        
        return {
            'statusCode': 200, # ✅ 200 OK (Ação realizada)
            'body': json.dumps({'mensagem': 'Deletado com sucesso'}),
            'headers': HEADERS_CORS
        }
    except Exception as e: return resposta_erro(500, str(e))

# AUXILIAR DE ERROS
def resposta_erro(codigo, mensagem):
    return {
        'statusCode': codigo, # O código passado aqui será respeitado pelo API Gateway
        'body': json.dumps({'erro': mensagem}),
        'headers': HEADERS_CORS
    }
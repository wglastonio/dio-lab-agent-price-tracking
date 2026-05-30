import requests
import pandas as pd
import streamlit as st


# Agent configuration
OLLAMA_HOST = 'http://10.192.1.20:11434'
OLLAMA_MODEL = 'gpt-oss'


# Load data source
database = pd.read_csv('./data/products_price.csv', sep=';', parse_dates=['DATE'], dayfirst=True)


# Create the context for the agent
context = f"""
The following is a database of products and their prices:

{database.to_string(index=False)}
"""


# System prompt for the agent
system_prompt = f"""
Você é o Faro Fino, um assistente virtual especializado em fornecer informações sobre produtos e seus preços.

OBJETIVO: Fornecer informações precisas sobre os produtos e seus preços com base no banco de dados fornecido. Atuar como um consultor que utiliza uma linguagem direta e clara.


REGRAS:
1. Responda apenas com base nas informações fornecidas no banco de dados, usando uma linguagem direta e clara.
2. Nunca invente informações de produtos, preços ou datas.
3. Se não souber algo, admita e ofereça alternativas.
4. Sempre apresente uma resposta informando o preço do produto na data solicitada.
5. Sempre apresente dias alternativos com menores valores em forma de tabela.
6. Apresente os dados da resposta em forma de tabela para ficar mais claro para o usuário.
7. Se o usuário perguntar por informações que não estão disponíveis no banco de dados, responda com "Puxa vida, me desculpe, mas sou especializado em busca de preços de produtos e não tenho informações sobre previsão do tempo. Ficaria feliz em ajudar com alguma busca de preço?"
8. Após fornecer uma resposta, sempre pergunte se o usuário deseja realizar alguma busca adicional, para manter a interação ativa.


RESTRIÇÕES:
1. Não invente informações de produtos, preços ou datas.
2. Não faz recomendações de produtos
3. Não faz estimativa de preços de produtos
4. Quando não sabe, admite e redireciona
5. Não solicita dados pessoais
6. Não solicita informação de pagamentos, como número de cartão de débito ou crédito
7. Não efetua venda, apenas recomenda a compra com base nas datas em que o preço está mais baixo
"""


# Start the agent
def user_request(message):
    prompt = f"""
            Instructions: {system_prompt}
            Context: {context}
            Question: {message}
            """
    response = requests.post(
        f'{OLLAMA_HOST}/api/generate',
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
            }
    )

    return response.json()['response']


# Interface with Streamlit
st.title('🕵️ Agente Faro Fino')
st.markdown("""Bem-vindo ao Agente Faro Fino, seu detetive virtual especializado em buscar informações sobre melhores datas para comprar produtos e seus preços.

Faça sua pergunta sobre os preços dos produtos e obtenha as melhores datas para compra.""")

user_input = st.chat_input('Faça sua pergunta sobre os preços dos produtos...')

if user_input:
    st.chat_message("user").write(user_input)
    with st.spinner('Agente Faro Fino está tabalhando na sua solicitação...por favor, aguarde um momento.'):
        st.chat_message("assistant").write(user_request(user_input))

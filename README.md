The Price App - Gestor Inteligente de Precificação
O The Price App é uma aplicação web completa, desenvolvida em Python com Flask, desenhada para ajudar pequenos produtores, artesãos e empreendedores a calcular o preço de venda dos seus produtos de forma precisa e profissional.

A aplicação vai além de uma simples calculadora, incorporando um sistema de gestão de ingredientes, análise de custos detalhada e um assistente IA para fornecer insights de negócio valiosos.

✨ Funcionalidades Principais
Sistema de Autenticação: Registo e login de usuários para garantir a privacidade e segurança dos dados de cada negócio.

Gestão de Receitas: Crie, edite, visualize e exclua receitas completas.

Cálculo de Custos Detalhado:

Adicione ingredientes a partir de um banco centralizado.

Registe múltiplos gastos fixos (gás, eletricidade, embalagens, etc.) de forma individual.

Precificação Inteligente: A aplicação calcula o custo total, o faturamento, o lucro e sugere o preço de venda unitário com base na margem de lucro desejada.

Banco de Ingredientes Centralizado: Cadastre os seus ingredientes e os seus custos uma única vez. Ao atualizar o preço de um ingrediente, todas as receitas que o utilizam são recalculadas automaticamente.

Dashboard de Métricas: Visualize rapidamente o número total de receitas, o seu produto mais lucrativo e a sua margem de lucro média.

Assistente IA (Simulado):

Previsão de Custos: Analisa o histórico de preços para alertar sobre possíveis aumentos.

Otimização de Preço: Sugere o "preço ótimo" para maximizar a sua margem de lucro.

🛠️ Tecnologias Utilizadas
Backend: Python 3, Flask

Base de Dados: SQLAlchemy com SQLite

Autenticação: Flask-JWT-Extended

Frontend: HTML5, Tailwind CSS, JavaScript

Servidor de Produção: Gunicorn

🚀 Como Executar o Projeto Localmente
Siga os passos abaixo para ter a aplicação a funcionar na sua máquina.

Clone o Repositório:

git clone [(https://github.com/JpGomes1898/The-Price-App)](https://github.com/JpGomes1898/The-Price-App)

Crie e Ative um Ambiente Virtual:

# Para Windows
python -m venv venv
.\venv\Scripts\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate

Instale as Dependências:
Certifique-se de que tem o ficheiro requirements.txt na pasta principal.

pip install -r requirements.txt

Execute a Aplicação:

python main.py

Aceda no Navegador:
Abra o seu navegador e vá para http://127.0.0.1:5000.

☁️ Deploy

Esta aplicação está pronta para ser colocada em produção. Para um guia passo a passo detalhado sobre como fazer o deploy na plataforma Render, por favor, consulte o ficheiro DEPLOY_GUIDE.md.

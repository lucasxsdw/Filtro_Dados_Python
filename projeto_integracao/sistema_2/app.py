from flask import Flask, request, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Dados armazenados do Sistema 1
dados_filtrados = []

@app.route('/api/receber_dados', methods=['POST'])
def receber_dados():
    global dados_filtrados
    dados_filtrados = request.json  # Recebe os dados filtrados do Sistema 1
    return jsonify({'message': 'Dados recebidos com sucesso'}), 200

@app.route('/filtragem', methods=['GET'])
def filtragem():
    global dados_filtrados
    
    if not dados_filtrados:
        return "Nenhum dado disponível para exibição!", 400

    # Converter para DataFrame
    df = pd.DataFrame(dados_filtrados)
    
    # Criar um filtro opcional por data
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if data_inicio and data_fim:
        df['data_ocorrencia'] = pd.to_datetime(df['data_ocorrencia'])  # Converter para datetime
        df = df[(df['data_ocorrencia'] >= data_inicio) & (df['data_ocorrencia'] <= data_fim)]

    # Converter os dados filtrados para uma tabela HTML
    tabela_html = df.to_html(classes='table table-bordered', index=False)

    return render_template('filtragem.html', tabela=tabela_html)

@app.route('/grafico')
def gerar_grafico():
    global dados_filtrados
    
    if not dados_filtrados:
        return "Nenhum dado disponível para gerar gráfico!", 400

    # Converter os dados filtrados para DataFrame
    df = pd.DataFrame(dados_filtrados)

    if 'Tipo Violência' not in df.columns:
        return "A coluna 'Tipo Violência' não foi encontrada nos dados.", 400
    
    # Exemplo: Gerar um gráfico de barras com base no tipo de violência
    grafico = df['Tipo Violência'].value_counts().plot(kind='bar', title='Distribuição de Tipos de Violência')
    
    # Salvar o gráfico em um buffer de memória
    buf = io.BytesIO()
    grafico.figure.savefig(buf, format='png')
    buf.seek(0)
    
    # Converter o gráfico para base64 para exibir na página HTML
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return render_template('grafico.html', img_b64=img_b64)

@app.route('/')
def index():
    return render_template('index.html')  # Página principal

if __name__ == '__main__':
    app.run(debug=True, port=5001)

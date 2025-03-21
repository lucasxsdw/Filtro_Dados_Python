from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests

app = Flask(__name__)

# Regras de filtragem predefinidas
def filtrar_dados(x):
    # Verificar se a coluna 'data_ocorrencia' existe
    if 'data_ocorrencia' not in x.columns:
        return pd.DataFrame()  # Retornar dataframe vazio se a coluna não existir
    # Filtra as datas que são superiores a 2025
    return x[x['data_ocorrencia'] > '2025-01-01']

@app.route('/')
def index():
    return render_template('uploads.html')  # Página HTML com o formulário de upload
@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    # Receber o arquivo Excel enviado pelo usuário
    file = request.files['file']
    
    # Ler o arquivo Excel
    x = pd.read_excel(file, engine='openpyxl')
    
    # Aplicar as regras de filtragem
    dados_filtrados = filtrar_dados(x)
    
    # Converter as colunas de datas para string para garantir que o JSON possa serializar
    for col in dados_filtrados.select_dtypes(include=['datetime']).columns:
        dados_filtrados[col] = dados_filtrados[col].dt.strftime('%Y-%m-%d')  # ou o formato de data que você preferir
    
    # Enviar os dados filtrados para o Sistema 2 (via API ou outro método)
    url_sistema_2 = 'http://127.0.0.1:5001/api/receber_dados'
    
    response = requests.post(url_sistema_2, json=dados_filtrados.to_dict(orient='records'))
    
    if response.status_code == 200:
        return jsonify({'message': 'Dados enviados com sucesso para o Sistema 2!'}), 200
    else:
        return jsonify({'message': 'Erro ao enviar dados para o Sistema 2'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

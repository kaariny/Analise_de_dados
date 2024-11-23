from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Carregar dados
df = pd.read_excel('paises.xlsx')

# Função para limpar e converter colunas numéricas
def limpar_dados(df):
    def converter_pib(pib):
        if isinstance(pib, str):
            pib = pib.replace(' bilhões', 'e9').replace(' trilhões', 'e12').replace(',', '')
            try:
                return float(pib)
            except ValueError:
                return None
        return pib

    # Limpeza das colunas numéricas
    df['PIB Total (em dollar)'] = df['PIB Total (em dollar)'].apply(converter_pib)
    df['População'] = pd.to_numeric(df['População'], errors='coerce')
    df['PIB Per Capta (em dollar)'] = pd.to_numeric(df['PIB Per Capta (em dollar)'], errors='coerce')
    df['IDH'] = pd.to_numeric(df['IDH'], errors='coerce')
    
    return df

# Limpar os dados ao carregar
df = limpar_dados(df)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analise', methods=['POST'])
def analise():
    col_num = request.form.get('col_num')
    col_cat = request.form.get('col_cat')

    # Verificar se a coluna numérica é realmente numérica
    if col_num not in df.columns:
        return jsonify({'error': 'Coluna numérica inválida'})

    # Verificar se a coluna de categoria existe
    if col_cat not in df.columns:
        return jsonify({'error': 'Coluna de categoria inválida'})

    # Limpar valores ausentes para as colunas numéricas
    df_cleaned = df.dropna(subset=[col_num])

    # Agrupar os dados e calcular a média
    df_grouped = df_cleaned.groupby(col_cat)[col_num].mean().reset_index()

    # Criar gráfico interativo
    fig = px.bar(df_grouped, x=col_cat, y=col_num, title=f'Média de {col_num} por {col_cat}')
    graph_html = fig.to_html(full_html=False)

    return jsonify({'graph_html': graph_html})

if __name__ == '__main__':
    app.run(debug=True)

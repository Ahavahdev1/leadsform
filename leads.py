from flask import Flask, jsonify, request, render_template
import json
import os
import pandas as pd
from io import StringIO
import csv

app = Flask(__name__)
data_file = 'leads.json'

def read_leads():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def write_leads(leads):
    with open(data_file, 'w') as file:
        json.dump(leads, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/leads', methods=['GET'])
def get_leads():
    leads = read_leads()
    return jsonify(leads)

@app.route('/leads', methods=['POST'])
def add_lead():
    new_lead = request.get_json()
    leads = read_leads()
    new_lead['id'] = len(leads) + 1 if leads else 1
    leads.append(new_lead)
    write_leads(leads)
    return jsonify({'mensagem': 'Lead adicionado com sucesso!'})

@app.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    leads = read_leads()
    for lead in leads:
        if lead['id'] == lead_id:
            return jsonify(lead)
    return jsonify({'erro': 'Lead não encontrado!'}), 404

@app.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    updated_lead = request.get_json()
    leads = read_leads()
    for lead in leads:
        if lead['id'] == lead_id:
            lead['nome'] = updated_lead.get('nome', lead['nome'])
            lead['celular'] = updated_lead.get('celular', lead['celular'])
            lead['data'] = updated_lead.get('data', lead['data'])
            write_leads(leads)
            return jsonify({'mensagem': 'Lead atualizado com sucesso!'})
    return jsonify({'erro': 'Lead não encontrado!'}), 404

@app.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    leads = read_leads()
    leads = [lead for lead in leads if lead.get('id') != lead_id]
    write_leads(leads)
    return jsonify({'mensagem': 'Lead removido com sucesso!'})

@app.route('/export/csv')
def export_csv():
    leads = read_leads()
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'nome', 'celular', 'data'])
    writer.writeheader()
    writer.writerows(leads)
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=leads.csv'
    }

@app.route('/export/excel')
def export_excel():
    leads = read_leads()
    df = pd.DataFrame(leads)
    output = StringIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': 'attachment; filename=leads.xlsx'
    }

if __name__ == '__main__':
    app.run(debug=True)

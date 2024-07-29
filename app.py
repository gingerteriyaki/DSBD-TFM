from flask import Flask, jsonify
import boto3
import os

app = Flask(__name__)

session = boto3.session.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://climaplatano.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['SPACES_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['SPACES_SECRET_ACCESS_KEY'])

    space_name = 'climaplatano'  # Cambia esto por el nombre de tu Space en DigitalOcean

def get_file_from_spaces(file_name):
    try:
        response = client.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error al obtener el archivo: {e}")
        return None

@app.route('/data/<file_name>', methods=['GET'])
def get_data(file_name):
    data = get_file_from_spaces(file_name)
    if data:
        return jsonify({"data": data})
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

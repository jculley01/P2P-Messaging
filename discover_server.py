from flask import Flask, request, jsonify

app = Flask(__name__)
clients = {}


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    address = request.json.get('address')
    clients[username] = address
    return jsonify({'message': f'{username} registered successfully'})


@app.route('/clients', methods=['GET'])
def list_clients():
    return jsonify(clients)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

from flask import Flask, render_template, jsonify, request
import modules.system as system
import modules.cpu as cpu
import modules.memory as memory
import modules.disk as disk
import modules.network as network

app = Flask(__name__)

@app.route("/api/matrix")
def api_matrix():
    return jsonify(
        system=system.get_system(),
        cpu=cpu.get_cpu(),
        memory=memory.get_memory(),
        disk=disk.get_disk(),
        network=network.get_network()
    )

@app.route("/api/matrix/net-check", methods=["POST"])
def api_network_check():
    network.force_network_check()
    return jsonify(network=network.get_network())

@app.route("/api/matrix/set-dns", methods=["POST"])
def api_set_dns():
    data = request.get_json() or {}
    current_address = network.get_network()["dns"]
    resolver = data.get("resolver", current_address)
    network.set_dns_resolver(resolver)
    return jsonify(success=True)

@app.route("/api/matrix/ip-check", methods=["POST"])
def api_set_ip_api():
    data = request.get_json() or {}
    current_api = network.get_network()["ipapi"]
    checker = data.get("checker", current_api)
    network.set_ip_checker(checker)
    return jsonify(success=True)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

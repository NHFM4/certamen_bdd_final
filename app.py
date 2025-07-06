from flask import Flask, request, render_template
import connect

app = Flask(__name__)

colecciones = {"clientes", "pedidos"}

diccionario_de_busquedas = {
    "ciudad": connect.busqueda_cliente_ciudad,
    "fecha": connect.busqueda_por_fecha,
    "producto": connect.consultar_datos_del_producto,
    "total_pedidos_cliente": connect.consultar_pedidos_clientes,
    "todos_clientes": connect.todos_clientes,
    "todos_pedidos": connect.todos_pedidos
}

@app.route("/", methods=["GET"])
def main_():
    return render_template("index.html")

@app.route("/api/dinamic_api", methods=["GET", "POST"])
def dinamic_():
    
    parametros: dict = request.get_json()

    if any(connect.es_peligroso(x) for x in parametros.keys()) or any(connect.es_peligroso(x) for x in parametros.values()):
        return {"status": 400, "data": "Estas utilizando caracteres no autorizados."}
    
    if "consulta" not in parametros or "data" not in parametros:
        return {"status": 400, "data": "No estas enviando uno de los dos parametros con su respectivo valor."}
    
    if parametros["consulta"] not in diccionario_de_busquedas:
        return {"status": 500, "data": "El valor del parametro 'consulta' no existe como consulta."}

    respuesta_de_la_base_de_datos = diccionario_de_busquedas[parametros["consulta"]](parametros["data"])
    
    return respuesta_de_la_base_de_datos

if __name__ == "__main__":

    app.run(debug=True, use_reloader=False)
    

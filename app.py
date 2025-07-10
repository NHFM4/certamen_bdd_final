from flask import Flask, request, render_template
import connect

app = Flask(__name__)

colecciones = {"clientes", "pedidos"}

diccionario_de_busquedas = {
    "ciudad": connect.busqueda_cliente_ciudad,
    "fecha": connect.busqueda_por_fecha,
    "producto": connect.consultar_datos_del_producto,
    "total_pedidos_cliente": connect.consultar_pedidos_clientes,
    
    # Zona de todos
    "todos_clientes": connect.todos_clientes,
    "todos_pedidos": connect.todos_pedidos,
    "todos_productos": connect.todos_productos,

    "cliente_borrar": connect.eliminar_cliente_por_id,
    "producto_borrar": connect.eliminar_producto_por_id,
    "pedido_borrar": connect.eliminar_pedido_por_id
}

modify_bdd = {
    "agregar_cliente": connect.agregar_cliente,
    "agregar_producto": connect.agregar_producto,
    "agregar_pedido": connect.agregar_pedido,
    
    "modificar_cliente": connect.modificar_cliente,
    "modificar_producto": connect.modificar_producto,
    "modificar_pedido": connect.modificar_pedido 
}

@app.route("/", methods=["GET"])
def main_():
    return render_template("index.html")

@app.route("/api/modify_bdd", methods=["POST"])
def modify_():
    parametros: dict = request.get_json()

    if "consulta" not in parametros or "data" not in parametros:
        return {"status": 400, "data": "No estas enviando uno de los dos parametros con su respectivo valor."}

    if any(connect.es_peligroso(x) for x in parametros.keys()) or any(connect.es_peligroso(x) for x in parametros["data"].values()):
        return {"status": 400, "data": "Estas utilizando caracteres no autorizados."}
    
    if parametros["consulta"] not in modify_bdd:
        return {"status": 500, "data": "El valor del parametro 'consulta' no existe como consulta."}
    
    resp_ = modify_bdd[parametros["consulta"]](parametros["data"])

    return resp_

@app.route("/api/dinamic_api", methods=["GET", "POST"])
def dinamic_():
    
    parametros: dict = request.get_json()

    if any(connect.es_peligroso(x) for x in parametros.keys()) or any(connect.es_peligroso(x) for x in parametros.values()):
        return {"status": 400, "data": "Estas utilizando caracteres no autorizados."}
    
    if "consulta" not in parametros or "data" not in parametros:
        return {"status": 400, "data": "No estas enviando uno de los dos parametros con su respectivo valor."}
    
    if parametros["consulta"] not in diccionario_de_busquedas:
        return {"status": 500, "data": "El valor del parametro 'consulta' no existe como consulta."}
    
    if any(parametros["consulta"] == x for x in ["todos_clientes", "todos_pedidos", "todos_productos"]):
        respuesta_de_la_base_de_datos = diccionario_de_busquedas[parametros["consulta"]]()

    else:
        respuesta_de_la_base_de_datos = diccionario_de_busquedas[parametros["consulta"]](parametros["data"])
    
    return respuesta_de_la_base_de_datos

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    

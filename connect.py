from pymongo import MongoClient

connect = MongoClient("mongodb+srv://admin:admin@certamen.n0laby6.mongodb.net/?retryWrites=true&w=majority&appName=certamen")
bdd = connect["empresa"]

clientes = bdd["clientes"]
pedidos = bdd["pedidos"]

no_permitido = r"'\"\\/<>(){}[];%*=$+|&`~#"

########################################### Limpieza de campos

def es_peligroso(campo: str) -> bool:

    for x in campo:

        if x in no_permitido:
            print(x, True)
            return True
    
    return False

########################################### Requerimientos basicos

def busqueda_cliente_ciudad(ciudad: str) -> dict:
    try:
        resp_ = list(clientes.find({"direccion": {"$regex": ciudad}}, {"_id": 0}))

    except:
        print("ERROR: en busqueda de cliente por ciudad")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    if not resp_:
        return {"status": 000, "data": f"No se lograron encontrar resultados para la busqueda: {ciudad}"}
    
    return {"status": 200, "data": resp_}

def busqueda_por_fecha(fecha: str) -> dict:

    try:
        resp_ = clientes.find({"fecha_registro": fecha}, {"_id": 0, "nombre": 1})
    
    except:
        print("ERROR: en busqueda por fecha")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    if not resp_:
        return {"status": 000, "data": f"No se lograron encontrar resultados de busqueda por la fecha: {fecha}"}
    
    return {"status": 200, "data": list(resp_)}

def consultar_datos_del_producto(id_producto: str) -> dict:

    try:
        resp_ = pedidos.find({"_id": id_producto}, {"_id": 0})

    except:
        print("ERROR: en busqueda por id de producto")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}

    if not resp_:
        return {"status": 000, "data": f"No se logro encontrar ningun producto por le id: {id_producto}"}
    
    return {"status": 200, "data": list(resp_)}

def consultar_pedidos_clientes(id_cliente: str):
    
    try:
        resp_ = clientes.aggregate([
            {"$lookup": {"from": "pedidos", "localField": "_id", "foreignField": "cliente_id", "as": "pedidos_del_cliente"}},
            {"$project": {"_id": 0, "pedidos_del_cliente.cliente_id": 0}}
        ])
    except:
        print("ERROR: en busqueda por id cliente en consultar pedidos cliente")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    if not resp_:
        return {"status": 000, "data": f"No se logro encontrar ningun pedido asociado al id: {id_cliente}"}
    
    return {"status": 200, "data": list(resp_)}

def todos_clientes(arg_: str) -> dict:

    try:
        resp_ = list(clientes.find({}))
    except:
        print("ERROR: en busqueda por todos los clientes")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    return {"status": 200, "data": resp_}

# Alta paja modificar y agregar except, mejor un parametro invisible que no se ocupa
def todos_pedidos(arg_: str) -> dict:

    try:
        resp_ = list(pedidos.find({}))
    except:
        print("ERROR: en busqueda por todos los pedidos")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    return {"status": 200, "data": resp_ }
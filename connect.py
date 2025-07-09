from pymongo import MongoClient

connect = MongoClient("mongodb+srv://admin:admin@certamen.n0laby6.mongodb.net/?retryWrites=true&w=majority&appName=certamen")
bdd = connect["empresa"]

clientes = bdd["clientes"]
pedidos = bdd["pedidos"]
productos = bdd["productos"]

no_permitido = r"'\"\\/<>(){}[];%*=$+|&`~#"

######################################################## Limpieza de campos

def es_peligroso(campo: str) -> bool:

    for x in campo:

        if x in no_permitido:
            print(x, True)
            return True
    
    return False

######################################################## Requerimientos basicos

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
        resp_ = list(clientes.find({"fecha_registro": {"$regex": fecha}}, {"_id": 0, "nombre": 1}))
    
    except:
        print("ERROR: en busqueda por fecha")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    if not resp_:
        return {"status": 000, "data": f"No se lograron encontrar resultados de busqueda por la fecha: {fecha}"}
    
    return {"status": 200, "data": resp_}

def consultar_datos_del_producto(id_producto: str) -> dict:

    try:
        resp_ = list(productos.find({"_id": id_producto}, {"_id": 0}))

    except:
        print("ERROR: en busqueda por id de producto")
        return {"status": 500, "data": f"No se logro encontrar el producto con id: {id_producto}"}

    if not resp_:
        return {"status": 000, "data": f"No se logro encontrar ningun producto por le id: {id_producto}"}
    
    return {"status": 200, "data": resp_}

def consultar_pedidos_clientes(id_cliente: str) -> dict:
    
    try:
        resp_ = list(clientes.aggregate([
            {"$match": {"_id": id_cliente}},
            {"$lookup": {"from": "pedidos", "localField": "_id", "foreignField": "codigo_cliente", "as": "pedidos_del_cliente"}},
            {"$project": {"_id": 0, "pedidos_del_cliente.cliente_id": 0}}
        ]))
    except:
        print("ERROR: en busqueda por id cliente en consultar pedidos cliente")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    if not resp_:
        return {"status": 000, "data": f"No se logro encontrar ningun pedido asociado al id: {id_cliente}"}
    
    return {"status": 200, "data": resp_}

######################################################## Consultas generales

def todos_clientes() -> dict:

    try:
        resp_ = list(clientes.find({}))
    except:
        print("ERROR: en busqueda por todos los clientes")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    return {"status": 200, "data": resp_}

def todos_pedidos() -> dict:

    try:
        resp_ = list(pedidos.find({}))
    except:
        print("ERROR: en busqueda por todos los pedidos")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    return {"status": 200, "data": resp_ }

def todos_productos() -> dict:

    try:
        resp_ = list(productos.find({}))
    except:
        print("ERROR: en busqueda por todos los pedidos")
        return {"status": 500, "data": "INTERNAL ERROR SERVER"}
    
    return {"status": 200, "data": resp_ }

######################################################## Seccion de modificacion de bdd

# Seccion de agregar

def agregar_cliente(json_data: dict) -> dict:

    telefono = json_data["telefono"]
    direccion = json_data["direccion"]
    email = json_data["email"]
    fecha_registro = json_data["fecha"]
    nombre = json_data["nombre"]

    resp_ = todos_clientes()
    id_cliente = "C00" + str(len(resp_["data"]) + 1)

    try:
        clientes.insert_one({
            "_id": id_cliente, 
            "Telefono": telefono, 
            "direccion": direccion, 
            "email": email, 
            "fecha_registro": fecha_registro,
            "nombre": nombre
        })
    
    except:
        print(f"ERROR: No se logro insertar al usuario: {nombre} correctamente")
        return {"status": 500, "data": f"No se pudo agregar al nuevo usuario con nombre {nombre}."}

    return {"status": 200, "data": f"Usuario {nombre} ingresado correctamente."}

def agregar_producto(json_data: dict) -> dict:
    
    nombre = json_data["nombre"]
    precio = json_data["precio"]
    stock = json_data["stock"]
    estado = json_data["estado"]

    resp_ = todos_productos()
    id_producto = "PD00" + str(len(resp_["data"]) + 1)

    try: 
        productos.insert_one({
            "_id": id_producto,
            "nombre": nombre,
            "precio": int(precio),
            "stock": int(stock),
            "estado": estado
        })

    except:
        print(f"ERROR: No se logro insertar al producto: {nombre} correctamente")
        return {"status": 500, "data": f"No se pudo agregar al nuevo producto con nombre {nombre}."}

    return {"status": 200, "data": f"Producto {nombre} ingresado correctamente."}

def agregar_pedido(json_data: dict) -> dict:

    codigo_cliente = json_data["codigo_cliente"]
    metodo_pago = json_data["metodo_pago"]
    fecha_pedido = json_data["fecha_pedido"]

    resp_ = todos_pedidos()
    id_pedido = "PE00" + str(len(resp_["data"]) + 1)

    try: 
        pedidos.insert_one({
            "_id": id_pedido,
            "codigo_cliente": codigo_cliente,
            "metodo_pago": metodo_pago,
            "fecha_pedido": fecha_pedido
        })

    except:
        print(f"ERROR: No se logro ingresar el pedido asociado al cliente: {codigo_cliente} correctamente")
        return {"status": 500, "data": f"No se pudo agregar al nuevo pedido asociado al cliente {codigo_cliente}."}

    return {"status": 200, "data": f"Pedido asociado al cliente {codigo_cliente} ingresado correctamente."}

# Seccion de modificacion

def modificar_cliente(json_data: dict) -> dict:

    id_cliente = json_data["id"]
    telefono = json_data["telefono"]
    direccion = json_data["direccion"]
    email = json_data["email"]
    fecha_registro = json_data["fecha"]
    nombre = json_data["nombre"]

    try:

        clientes.update_one({"_id": id_cliente}, {"$set": {
            "nombre": nombre,
            "email": email,
            "fecha_registro": fecha_registro,
            "direccion": direccion,
            "Telefono": int(telefono)
        }})

    except:
        print(f"ERROR: No se logro modificar el cliente: {nombre} correctamente")
        return {"status": 500, "data": f"No se pudo modificar el cliente con nombre {nombre}."}

    return {"status": 200, "data": f"Cliente {nombre} modificado correctamente."}

def modificar_producto(json_data: dict) -> dict:

    id_producto = json_data["id"]
    nombre = json_data["nombre"]
    precio = json_data["precio"]
    stock = json_data["stock"]
    estado = json_data["estado"]

    try:

        productos.update_one({"_id": id_producto}, {"$set": {
            "nombre": nombre,
            "precio": int(precio),
            "stock": int(stock),
            "estado": estado
        }})

    except:
        print(f"ERROR: No se logro modificar el producto: {nombre} correctamente")
        return {"status": 500, "data": f"No se pudo modificar el producto con nombre {nombre}."}

    return {"status": 200, "data": f"Producto {nombre} modificado correctamente."}

def modificar_pedido(json_data: dict) -> dict:

    id_pedido = json_data["id"]
    codigo_cliente = json_data["codigo_cliente"]
    metodo_pago = json_data["metodo_pago"]
    fecha_pedido = json_data["fecha_pedido"]

    try: 
        pedidos.update_one({"_id": id_pedido}, {"$set": {
            "codigo_cliente": codigo_cliente,
            "metodo_pago": metodo_pago,
            "fecha_pedido": fecha_pedido
        }})

    except:
        print(f"ERROR: No se logro modificar el pedido asociado al cliente: {codigo_cliente} correctamente")
        return {"status": 500, "data": f"No se pudo modificar el pedido asociado al cliente {codigo_cliente}."}

    return {"status": 200, "data": f"Pedido asociado al cliente {codigo_cliente} modificado correctamente."}

    pass

# Seccion de eliminacion

def eliminar_cliente_por_id(id: str) -> dict:
    
    try:
        clientes.delete_one({"_id": id})
    
    except:
        print(f"ERROR: No se logro eliminar al usuario: {id} correctamente")
        return {"status": 500, "data": f"Usuario con id {id} no eliminado."}

    return {"status": 200, "data": f"Usuario con id {id} eliminado correctamente."}

def eliminar_pedido_por_id(id: str) -> dict:

    try:
        pedidos.delete_one({"_id": id})
    
    except:
        print(f"ERROR: No se logro eliminar el pedido: {id} correctamente")
        return {"status": 500, "data": f"Pedido con id {id} no eliminado."}

    return {"status": 200, "data": f"Pedido con id {id} eliminado correctamente."}

def eliminar_producto_por_id(id: str) -> dict:
    
    try:
        productos.delete_one({"_id": id})
    
    except:
        print(f"ERROR: No se logro eliminar al producto: {id} correctamente")
        return {"status": 500, "data": f"Producto con id {id} no eliminado."}

    return {"status": 200, "data": f"Producto con id {id} eliminado correctamente."}
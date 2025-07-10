from pymongo import MongoClient
from hashlib import md5
from datetime import datetime
import random


connect = MongoClient("mongodb+srv://admin:admin@certamen.n0laby6.mongodb.net/?retryWrites=true&w=majority&appName=certamen")
bdd = connect["empresa"]

clientes = bdd["clientes"]
pedidos = bdd["pedidos"]
productos = bdd["productos"]

no_permitido = r"'\"\\/<>(){}[];%*=$|&`~#"

######################################################## Limpieza de campos y utilidades

def es_peligroso(campo: str) -> bool:

    for x in campo:

        if x in no_permitido:
            return True
    
    return False

def es_peligroso_json(diccionario: dict) -> bool:

    keys_ = diccionario.keys()

    for x in keys_:

        if x in no_permitido:
            return True
    
    for key in keys_:
        
        for x in str(diccionario[key]):

            if type(diccionario[key]) == list:
                continue

            try:
                if x in no_permitido:
                    return True
            except:
                continue
    
    return False

def gen_id(lista: list) -> str:

    try:
        str_buffer = str(len(lista) + 1 + random.randint(1, 1000)) + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        return md5(str_buffer.encode("utf-8")).hexdigest()
    
    except:
        return str(random.randint(len(lista), 1000))


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
    id_cliente = "C00" + gen_id(resp_)

    try:
        clientes.insert_one({
            "_id": id_cliente, 
            "Telefono": int(telefono), 
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
    id_producto = "PD00" + gen_id(resp_)

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
    
    all_product = todos_productos()
    cliente_existe = consultar_pedidos_clientes(json_data["codigo_cliente"])

    if cliente_existe["status"] != 200:
        return {"status": 400, "data": "No se puede asociar el pedido a un usario que no existe."}

    codigo_cliente = json_data["codigo_cliente"]
    metodo_pago = json_data["metodo_pago"]
    fecha_pedido = json_data["fecha_pedido"]


    resp_ = todos_pedidos()
    id_pedido = "PE00" + gen_id(resp_)

    data_ = {
            "_id": id_pedido,
            "codigo_cliente": codigo_cliente,
            "metodo_pago": metodo_pago,
            "fecha_pedido": fecha_pedido
        }
    
    try:
        if "productos" in json_data:

            for producto in all_product["data"]:
                for producto_comprado in json_data["productos"]:
                    if producto_comprado["codigo_producto"] == producto["_id"]:

                        if producto_comprado["cantidad"] > producto["stock"]:
                            return {"status": 400, "data": f"No hay suficente stock para comprar {producto_comprado['cantidad']} de {producto_comprado['nombre']}. Estado: {producto['estado']}"}
                        
                        if not modificar_stock(producto_comprado["codigo_producto"], producto_comprado["cantidad"]):
                            return {"status": 500, "data": "Error, no se logro descontar el stock de la base de datos."}
            

            data_.setdefault("productos", json_data["productos"])
            data_.setdefault("total_compra", 
                sum([x["total_comprado"] for x in json_data["productos"]]))
    
    except:
        print(f"ERROR: No se logro ingresar el pedido asociado al cliente: {codigo_cliente} correctamente. Esto es en zona de IF PRODUCTS")
        return {"status": 500, "data": f"No se pudo agregar al nuevo pedido asociado al cliente {codigo_cliente} error interno."}
        
    try: 
        pedidos.insert_one(data_)

    except:
        print(f"ERROR: No se logro ingresar el pedido asociado al cliente: {codigo_cliente} correctamente")
        return {"status": 500, "data": f"No se pudo agregar al nuevo pedido asociado al cliente {codigo_cliente}."}

    return {"status": 200, "data": f"Pedido asociado al cliente {codigo_cliente} ingresado correctamente."}

# Seccion de modificacion

def modificar_stock(id: str, cantidad: int) -> bool:

    estado = "disponible"
    try:
        resp_ = productos.find_one({"_id": id})
        stock = resp_["stock"] - cantidad

        if stock == 0:
            estado = "agotado"
        
        productos.update_one({"_id": id}, {"$set": {"stock": stock, "estado": estado}})
    
    except:
        return False
    
    return True

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

    cliente_existe = consultar_pedidos_clientes(codigo_cliente)

    if cliente_existe["status"] != 200:
        return {"status": 400, "data": "No se puede asociar el pedido a un usario que no existe."}

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
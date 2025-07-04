# Manual para usar el endpoint `/api/dinamic_api`

Este endpoint te permite hacer consultas a una base de datos según el tipo de información que quieras buscar. Para que funcione, hay que mandarle un JSON con dos datos: qué tipo de consulta querés hacer, y la información necesaria para esa consulta.

## Dónde está

Si estás corriendo el servidor localmente, lo encontrás en:

```
http://localhost:5000/api/dinamic_api
```
pero actualmente lo tienes en el servidor de render

## Cómo se usa

Tenés que mandarle una petición `POST` (no GET) con un JSON en el cuerpo.

### Qué tiene que tener el JSON:

Dos claves:

* `"consulta"`: el tipo de búsqueda que querés hacer.
* `"data"`: lo que necesitás buscar.

### Tipos de búsqueda que se aceptan:

| consulta                  | Significado                           |
| ------------------------- | ------------------------------------- |
| `"ciudad"`                | Buscar clientes por ciudad            |
| `"fecha"`                 | Buscar pedidos por fecha              |
| `"producto"`              | Consultar info sobre un producto      |
| `"total_pedidos_cliente"` | Saber cuántos pedidos hizo un cliente |

## Ejemplos correctos

### 1. Buscar clientes por ciudad

```json
{
  "consulta": "ciudad",
  "data": "Madrid"
}
```

### 2. Buscar pedidos por fecha

```json
{
  "consulta": "fecha",
  "data": "2025-07-01"
}
```

### 3. Buscar información de un producto

```json
{
  "consulta": "producto",
  "data": "A123"
}
```

### 4. Ver cuántos pedidos hizo un cliente

```json
{
  "consulta": "total_pedidos_cliente",
  "data": "cliente_001"
}
```

## Ejemplos de errores (casos incorrectos)

### Caso 1: Faltan datos

```json
{
  "consulta": "ciudad"
}
```

**Respuesta esperada:**

```json
{
  "status": 400,
  "data": "No estas enviando uno de los dos parametros con su respectivo valor."
}
```

---

### Caso 2: Usás una consulta que no existe

```json
{
  "consulta": "edad",
  "data": "30"
}
```

**Respuesta esperada:**

```json
{
  "status": 500,
  "data": "El valor del parametro 'consulta' no existe como consulta."
}
```

---

### Caso 3: Usás caracteres peligrosos

```json
{
  "consulta": "ciudad",
  "data": "Madrid; DROP TABLE clientes;"
}
```

**Respuesta esperada:**

```json
{
  "status": 400,
  "data": "Estas utilizando caracteres no autorizados."
}
```

---

## Algunas cosas a tener en cuenta

* Solo se aceptan los nombres de consulta que están en la lista. No se puede inventar otro.
* Todo se valida: tanto el tipo de búsqueda como los datos que mandás.
* Si se detecta algo raro, el sistema corta la operación y responde con un error.
* No uses símbolos como `;`, `<`, `>` o cosas similares. El sistema los va a bloquear.

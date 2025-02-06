from fastapi import FastAPI, Request
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from starlette.middleware.wsgi import WSGIMiddleware

app = FastAPI()

class UserService(ServiceBase):
    users = []  # Lista en memoria (se reinicia con cada despliegue)

    @rpc(Unicode, Unicode, _returns=Unicode)
    def add_user(ctx, nombre, email):
        """Agrega un usuario a la lista."""
        for user in UserService.users:
            if user["email"] == email:
                return "Error: El email ya está registrado"
        
        new_user = {"nombre": nombre, "email": email}
        UserService.users.append(new_user)
        return f"Usuario agregado: {nombre} ({email})"

    @rpc(_returns=Unicode)
    def get_users(ctx):
        """Retorna la lista de usuarios en formato SOAP."""
        return str(UserService.users)

soap_app = Application([UserService], "soap.api",
                       in_protocol=Soap11(validator="lxml"),
                       out_protocol=Soap11())

wsgi_app = WsgiApplication(soap_app)
app.mount("/soap", WSGIMiddleware(wsgi_app))  # Montamos SOAP en /soap

@app.get("/")
def home():
    return {"message": "API SOAP con FastAPI"}


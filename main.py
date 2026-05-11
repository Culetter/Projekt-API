from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
import models
from database import engine
import routers.auth as auth, routers.products as products, routers.users as users, routers.orders as orders, routers.roles as roles

app = FastAPI()
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(roles.router)

models.Base.metadata.create_all(bind=engine)
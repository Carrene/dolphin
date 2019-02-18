from auditor import MiddleWare

from dolphin import dolphin as app
from dolphin.middleware_callback import callback


app.configure()
app.initialize_orm()
app = MiddleWare(app, callback)


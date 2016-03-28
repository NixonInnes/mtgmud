from app.mud import Mud
from app.models.db import Session
import app.presenters.textPres as TextPresenter
import app.presenters.jsonPres as JSONPresenter


mud = Mud()
presenter = {
    'text': TextPresenter,
    'json': JSONPresenter
}
session = Session()
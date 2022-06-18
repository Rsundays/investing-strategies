from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired


class SelectStock(FlaskForm):
    stock = RadioField("Selecciona el ETF", choices=[("^GSPC", "S&P 500"), ("NQ=F", "NASDAQ")])


class User(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = RadioField("User´s role", choices=[("Admin", "Admin"), ("User", "User")])


class ImageUploadForm(FlaskForm):
    trade_name = StringField("Image Name", validators=[DataRequired()])
    trade_tags = StringField("Tags separados por ; sin espacios", validators=[DataRequired()])
    trade_url = StringField("Google Drive URL", validators=[DataRequired()])
    submit = SubmitField("Upload")


class ImageUpdateForm(FlaskForm):
    trade_name = StringField("Image Name", validators=[DataRequired()])
    trade_tags = StringField("Tags separados por ; sin espacios", validators=[DataRequired()])
    trade_url = StringField("Google Drive URL", validators=[DataRequired()])
    submit = SubmitField("Save")

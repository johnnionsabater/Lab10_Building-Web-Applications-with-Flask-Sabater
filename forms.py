from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length, Optional


ROLE_CHOICES = [("viewer", "Viewer"), ("admin", "Admin")]


class RegisterForm(FlaskForm):
    display_name = StringField(
        "Display Name", validators=[InputRequired(), Length(min=2, max=120)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    role = SelectField("Role", choices=ROLE_CHOICES, validators=[InputRequired()])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=4, max=64)]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    display_name = StringField(
        "Display Name", validators=[InputRequired(), Length(min=2, max=120)]
    )
    profile_image = FileField(
        "Profile Picture",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png"],
                "Only JPG, JPEG, and PNG files are allowed.",
            ),
        ],
    )
    submit = SubmitField("Update Profile")

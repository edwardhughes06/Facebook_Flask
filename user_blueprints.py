class LoginForm(FlaskForm):
	first_name = StringField('first_name', validators=[InputRequired(), Length(min=4,max=16)])
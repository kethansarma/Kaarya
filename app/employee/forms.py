from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, FieldList, FormField, Form
from wtforms.validators import DataRequired



class SheetForm(Form):
    """
    Form to  add a day for Weekly Timesheet Creation
    """
    workhours = IntegerField('Workhours', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])


class SheetFormdb(Form):
    """
    Form to  collect a day from database for Weekly Timesheet Edit
    """
    date = StringField('Date', validators=[DataRequired()], render_kw={'readonly': True})
    workhours = IntegerField('Workhours', validators=[DataRequired(message="Please input Integer")])
    description = StringField('Description', validators=[DataRequired()])


class WeekSheetFillForm(FlaskForm):
    """
    Form for Weekly Timesheet Creation
    """
    sheets = FieldList(FormField(SheetFormdb))
    submit = SubmitField('Submit')


class WeekSheetFormdb(FlaskForm):
    """
    Form to collect Weekly Timesheet from database, edit and save
    """
    period = StringField('From-to', validators=[DataRequired()])
    sheets = FieldList(FormField(SheetFormdb))
    submit = SubmitField('Submit')

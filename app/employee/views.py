from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from . import employee
from .forms import WeekSheetFormdb, SheetFormdb, WeekSheetFillForm
from .. import db
from ..models import Sheet, WeekSheet
from ..util.errors_util import flash_errors


def getdates():
    from datetime import date, timedelta
    # dd/mm/YY
    testdate = date.today()
    # testdate = datetime.date(2014, 12, 31)
    testdateweekday = testdate.weekday()
    # lower bound
    sw = testdate - timedelta(days=testdateweekday)
    # upper bound
    ew = testdate + timedelta(days=(6 - testdateweekday))
    weekstring = str(sw.strftime("%d/%m/%Y") + '-' + ew.strftime("%d/%m/%Y"))
    week_dates = []
    for i in range(0, 5):
        week_dates.append((sw + timedelta(days=i)).strftime("%d/%m/%Y"))
    week_data = {"week": weekstring, "dates": week_dates, }
    return week_data


data = getdates()
dates = data["dates"]
period = data["week"]


def populate_form_fields(timesheet_db=None):
    if timesheet_db is None:
        form = WeekSheetFillForm()
        for i in range(0, 5):
            sheetformdb = SheetFormdb()
            sheetformdb.date = dates[i]
            sheetformdb.workhours = None
            sheetformdb.description = None
            form.sheets.append_entry(sheetformdb)
        return form
    else:
        form = WeekSheetFormdb()
        form.period.data = timesheet_db.period
        for sheet in timesheet_db.sheets:  # some database function to get a list of team members

            sheetformdb = SheetFormdb()
            sheetformdb.date = sheet.date  # These fields don't use 'data'
            sheetformdb.workhours = sheet.workhours
            sheetformdb.description = sheet.description
            form.sheets.append_entry(sheetformdb)

        return form


@employee.route('/timesheets', methods=['GET', 'POST'])
@login_required
def list_timesheets():
    """
    List all Timesheets
    """
    timesheets = WeekSheet.query.filter(WeekSheet.employee_id == current_user.get_id()).limit(52).all()
    return render_template('employee/timesheets.html',
                           timesheets=timesheets, title="Timesheets")


@employee.route('/timesheets/add', methods=['GET', 'POST'])
@login_required
def add_timesheet():
    """
    Add a timesheet to the database
    """
    exists = db.session.query(WeekSheet).filter_by(period=period, employee_id=current_user.get_id()).scalar()
    if exists:
        if exists.status == "Submitted":
            flash("You have already filled and submitted current weeek timesheet")
            return redirect(url_for('employee.view_timesheet', id=exists.id))

        else:
            flash('You have a saved timesheet. Please edit and Submit')
            return redirect(url_for('employee.edit_timesheet', id=exists.id))

    else:
        form = WeekSheetFillForm()
        if request.method == "GET":
            form = populate_form_fields()

        if form.validate_on_submit():
            weeksheet_db = WeekSheet()
            weeksheet_db.period = period
            weeksheet_db.employee_id = current_user.get_id()
            for entry in form.sheets.entries:
            # for i in range(0, 5):
                sheetdb = Sheet()
                sheetdb.date = entry.data['date']
                sheetdb.workhours = entry.data['workhours']
                sheetdb.description = entry.data['description']
                weeksheet_db.sheets.append(sheetdb)

            if "submit" in request.form:
                for entry in weeksheet_db.sheets:
                    entry.status = "Submitted"
                weeksheet_db.status = "Submitted"
            try:
                db.session.add(weeksheet_db)
                db.session.commit()
                flash('You have successfully added a new timesheet.')
            except:
                # in case department name already exists
                flash('Unable to Save Timesheet')

            # redirect to departments page
            return redirect(url_for('employee.list_timesheets'))
        else:
            flash_errors(form)

        # load department template
        return render_template('employee/timesheet.html', action="Add", dates=dates,
                               form=form, title="Add Timesheet", period=period)


@employee.route('/timesheets/view/<int:id>', methods=['GET'])
@login_required
def view_timesheet(id):
    """
    View a Timesheet
    """
    timesheet = WeekSheet.query.get_or_404(id)
    if current_user.get_id() != timesheet.employee_id:
        return abort(403)
    return render_template('employee/view_timesheet.html', action="View",
                           timesheet=timesheet, title="View Timesheet")


@employee.route('/timesheets/view/<int:id>/submit', methods=['GET', 'PUT'])
@login_required
def submit_timesheet(id):
    """
    Submit a Timesheet
    """

    timesheet = WeekSheet.query.get_or_404(id)
    if current_user.get_id() != timesheet.employee_id:
        return abort(403)
    timesheet.status = "Submitted"
    for item in timesheet.sheets:
        item.status = "Submitted"

    db.session.commit()
    flash('Timesheet is Submitted from View')
    return redirect(url_for('employee.list_timesheets'))


@employee.route('/timesheets/edit/<int:id>', methods=['GET', 'PUT'])
@login_required
def edit_timesheet(id):
    """
    Edit a Timesheet if saved
    """
    print("edit called")
    timesheet_db = WeekSheet.query.get_or_404(id)

    if current_user.get_id() != timesheet_db.employee_id:
        return abort(403)

    form = WeekSheetFormdb()
    if request.method == "GET":
        form = populate_form_fields(timesheet_db)

    else:
        form.period.data = timesheet_db.period
        if form.validate_on_submit():
            print(len(form.data))
            print(form.sheets)

            for i in range(0, len(timesheet_db.sheets)):
                print(i)

                if form.sheets.data[i]['workhours'] == timesheet_db.sheets[i].workhours:
                    pass
                else:
                    timesheet_db.sheets[i].workhours = form.sheets.data[i]['workhours']

                if form.sheets.data[i]['description'] == timesheet_db.sheets[i].description:
                    pass
                else:
                    timesheet_db.sheets[i].description = form.sheets.data[i]['description']

                if 'submit' in request.form:
                    timesheet_db.status = "Submitted"
                    timesheet_db.sheets[i].status = "Submitted"

            db.session.commit()
            flash('You have successfully edited the timesheet.')

            # redirect to the departments page
            return redirect(url_for('employee.list_timesheets'))

    return render_template('employee/edit_timesheet.html', action="Edit",
                           form=form, title="Edit Timesheet")


@employee.route('/timesheets/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_timesheet(id):
    """
    Delete a timesheet from the database if not submitted
    """
    timesheet = WeekSheet.query.get_or_404(id)
    if timesheet.status == "Not Submitted":
        db.session.delete(timesheet)
        db.session.commit()
        flash('You have successfully deleted the department.')
    else:
        flash('Submitted timesheet cannot be deleted')

    # redirect to the departments page
    return redirect(url_for('employee.list_timesheets'))

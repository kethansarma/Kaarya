from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from . import admin
from .forms import DepartmentForm, EmployeeAssignForm, RoleForm, RegistrationForm
from .. import db
from ..models import Department, Employee, Role, WeekSheet, Sheet


def check_admin():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)


# Department Views
@admin.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
        Register Users
        """
    check_admin()
    form = RegistrationForm()
    if form.validate_on_submit():
        employee = Employee(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data)

        # add employee to the database
        db.session.add(employee)
        db.session.commit()
        flash(f"Employee userId: {employee.username} registered")
        # redirect to the login page
        return redirect(url_for('admin.list_employees'))

    # load registration template
    return render_template('admin/register.html', form=form, title='Register')


@admin.route('/timesheets', methods=['GET'])
@login_required
def list_timesheets():
    """
    List all departments
    """
    check_admin()
    timesheets = WeekSheet.query.filter(WeekSheet.status != "Not Submitted").all()
    return render_template('admin/timesheets/timesheets.html',
                           timesheets=timesheets, title="Timesheets")


@admin.route('/timesheets/view/<int:id>', methods=['GET'])
@login_required
def view_timesheet(id):
    """
    View a Timesheet
    """
    check_admin()
    timesheet = WeekSheet.query.get_or_404(id)

    return render_template('admin/timesheets/view_timesheet.html', action="View",
                           timesheet=timesheet, title="View Timesheet")


@admin.route('/timesheets/approval/<int:id>/<decision>', methods=['GET', 'PUT'])
@login_required
def approve_timesheet(id, decision):
    """
    View a Timesheet
    """
    check_admin()
    decisions = {"approve": "Approved", "reject": "Rejected"}
    timesheet = WeekSheet.query.get_or_404(id)
    for sheet in timesheet.sheets:
        sheet.status = decisions[decision]
    timesheet.status = decisions[decision]
    db.session.commit()
    flash("Your approval is Successful")

    return redirect(url_for('admin.list_timesheets'))


@admin.route('/timesheets/approval/sheet/<int:id>/<decision>', methods=['GET', 'PUT'])
@login_required
def approve_sheet(id, decision):
    """
    View a Timesheet
    """
    check_admin()
    sheet = Sheet.query.get_or_404(id)
    decisions = {"approve": "Approved", "reject": "Rejected"}
    sheet.status = decisions[decision]

    flash(f'You have successfully Approve the {sheet.date} Sheet.')
    weeksheet = WeekSheet.query.filter(WeekSheet.id == sheet.weeksheet_id).one()
    if all(day.status == 'Approved' for day in weeksheet.sheets):
        weeksheet.status = "Approved"
    db.session.commit()
    return redirect(url_for('admin.list_timesheets'))


@admin.route('/timesheets/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_timesheet(id):
    """
    Delete a department from the database
    """
    check_admin()

    timesheet = WeekSheet.query.get_or_404(id)
    db.session.delete(timesheet)
    db.session.commit()
    flash('You have successfully deleted the timesheet')

    # redirect to the departments page
    return redirect(url_for('admin.list_timesheets'))


@admin.route('/departments', methods=['GET'])
@login_required
def list_departments():
    """
    List all departments
    """
    check_admin()
    departments = Department.query.all()
    return render_template('admin/departments/departments.html',
                           departments=departments, title="Departments")


@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """
    Add a department to the database
    """
    check_admin()
    add_department_boolean = True
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            flash('You have successfully added a new department.')
        except:
            # in case department name already exists
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_departments'))

    # load department template
    return render_template('admin/departments/department.html', action="Add",
                           add_department=add_department_boolean, form=form,
                           title="Add Department")


@admin.route('/departments/edit/<int:id>', methods=['GET', 'PUT'])
@login_required
def edit_department(id):
    """
    Edit a department
    """
    check_admin()

    add_department_boolean = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the department.')

        # redirect to the departments page
        return redirect(url_for('admin.list_departments'))

    form.description.data = department.description
    form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           add_department=add_department_boolean, form=form,
                           department=department, title="Edit Department")


@admin.route('/departments/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_department(id):
    """
    Delete a department from the database
    """
    check_admin()

    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('You have successfully deleted the department.')

    # redirect to the departments page
    return redirect(url_for('admin.list_departments'))


# Role Views
@admin.route('/roles', methods=['GET'])
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """
    roles = Role.query.all()
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')


@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role_boolean = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    # load role template
    return render_template('admin/roles/role.html', add_role=add_role_boolean,
                           form=form, title='Add Role')


@admin.route('/roles/edit/<int:id>', methods=['GET', 'PUT'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role_boolean = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role_boolean,
                           form=form, title="Edit Role")


@admin.route('/roles/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('admin.list_roles'))


# Employee Views
@admin.route('/employee')
@login_required
def list_employees():
    """
    List all employee
    """
    check_admin()
    employees = Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')


@admin.route('/employee/assign/<int:id>', methods=['GET', 'PUT'])
@login_required
def assign_employee(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    employee = Employee.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)
    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department_id = db.session.query(Department.id).filter_by(name=form['department'].data.name).scalar()
        employee.role_id = db.session.query(Role.id).filter_by(name=form['role'].data.name).scalar()

        db.session.commit()
        flash('You have successfully assigned a department and role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

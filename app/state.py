from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, State, Municipality, AppSettings

bp = Blueprint('state', __name__, url_prefix='/admin')

@bp.route('/states')
@login_required
def list_states():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    states = State.query.all()
    settings = AppSettings.query.get(1)  # Get settings
    return render_template('state/list.html', states=states, settings=settings)

@bp.route('/state/create', methods=['GET', 'POST'])
@login_required
def create_state():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)  # Add this line to get settings
    
    if request.method == 'POST':
        try:
            state = State(
                name=request.form['name'],
                name_ar=request.form['name_ar']
            )
            db.session.add(state)
            db.session.commit()
            flash('State created successfully', 'success')
            return redirect(url_for('state.list_states'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating state: {str(e)}', 'danger')
    
    return render_template('state/create.html', settings=settings)  # Pass settings here

@bp.route('/state/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_state(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    state = State.query.get_or_404(id)
    settings = AppSettings.query.get(1)  # Add this line
    
    if request.method == 'POST':
        try:
            state.name = request.form['name']
            state.name_ar = request.form['name_ar']
            db.session.commit()
            flash('State updated successfully', 'success')
            return redirect(url_for('state.list_states'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating state: {str(e)}', 'danger')
    
    return render_template('state/edit.html', state=state, settings=settings)  # Pass settings here

@bp.route('/state/<int:id>/delete', methods=['POST'])
@login_required
def delete_state(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    state = State.query.get_or_404(id)
    try:
        db.session.delete(state)
        db.session.commit()
        flash('State deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting state: {str(e)}', 'danger')
    
    return redirect(url_for('state.list_states'))

@bp.route('/state/<int:state_id>/municipalities')
@login_required
def list_municipalities(state_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    state = State.query.get_or_404(state_id)
    settings = AppSettings.query.get(1)  # Add this line to get settings
    return render_template('state/municipalities.html', state=state, settings=settings)  # Pass settings here

@bp.route('/state/<int:state_id>/municipality/create', methods=['GET', 'POST'])
@login_required
def create_municipality(state_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    state = State.query.get_or_404(state_id)
    settings = AppSettings.query.get(1)  # Add this line
    
    if request.method == 'POST':
        try:
            municipality = Municipality(
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                state_id=state_id
            )
            db.session.add(municipality)
            db.session.commit()
            flash('Municipality created successfully', 'success')
            return redirect(url_for('state.list_municipalities', state_id=state_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating municipality: {str(e)}', 'danger')
    
    return render_template('state/create_municipality.html', state=state, settings=settings)

@bp.route('/municipality/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_municipality(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    municipality = Municipality.query.get_or_404(id)
    settings = AppSettings.query.get(1)  # Add this line
    
    if request.method == 'POST':
        try:
            municipality.name = request.form['name']
            municipality.name_ar = request.form['name_ar']
            db.session.commit()
            flash('Municipality updated successfully', 'success')
            return redirect(url_for('state.list_municipalities', state_id=municipality.state_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating municipality: {str(e)}', 'danger')
    
    return render_template('state/edit_municipality.html', municipality=municipality, settings=settings)

@bp.route('/municipality/<int:id>/delete', methods=['POST'])
@login_required
def delete_municipality(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    municipality = Municipality.query.get_or_404(id)
    state_id = municipality.state_id
    try:
        db.session.delete(municipality)
        db.session.commit()
        flash('Municipality deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting municipality: {str(e)}', 'danger')
    
    return redirect(url_for('state.list_municipalities', state_id=state_id))
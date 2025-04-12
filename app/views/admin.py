current_session_id = request.form.get('current_session_id') or None
settings.current_session_id = current_session_id if current_session_id else None
import dash_bootstrap_components as dbc

def alert_msg(message):
    alert_message = dbc.Alert(
        message,
        color='danger',
        dismissable=True,
        duration=None,  
        id='error-alert'
    )
    return alert_message

def info_msg(message):
    info_message = dbc.Alert(
        message,
        color='success',
        dismissable=True,
        duration=None,  
        id='info-alert'
    )
    return info_message
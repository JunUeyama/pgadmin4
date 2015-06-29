##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2015, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

"""A blueprint module implementing the core pgAdmin browser."""
MODULE_NAME = 'browser'

from flask import Blueprint, Response, current_app, render_template, url_for
from flaskext.gravatar import Gravatar
from flask.ext.security import login_required
from flask.ext.login import current_user
from inspect import getmoduleinfo, getmembers

from . import sub_nodes
from pgadmin.browser import all_nodes
from pgadmin import modules
from pgadmin.settings import get_setting
from pgadmin.utils.ajax import make_json_response


import config

# Initialise the module
blueprint = Blueprint(MODULE_NAME, __name__, static_folder='static', template_folder='templates', url_prefix='/' + MODULE_NAME)

@blueprint.route("/")
@login_required
def index():
    """Render and process the main browser window."""
    # Get the Gravatar
    gravatar = Gravatar(current_app,
                        size=100,
                        rating='g',
                        default='retro',
                        force_default=False,
                        use_ssl=False,
                        base_url=None)

    # Get the plugin elements from the module
    file_items = [ ]
    edit_items = [ ]
    tools_items = [ ]
    management_items = [ ]
    help_items = [ ]
    stylesheets = [ ]
    scripts = [ ]

    modules_and_nodes = modules + all_nodes

    # Add browser stylesheets
    stylesheets.append(url_for('static', filename='css/codemirror/codemirror.css'))

    if config.DEBUG:
        stylesheets.append(url_for('static', filename='css/wcDocker/wcDockerSkeleton.css'))
    else:
        stylesheets.append(url_for('static', filename='css/wcDocker/wcDockerSkeleton.min.css'))

    stylesheets.append(url_for('static', filename='css/wcDocker/theme.css'))
    stylesheets.append(url_for('static', filename='css/jQuery-contextMenu/jquery.contextMenu.css'))
    stylesheets.append(url_for('browser.static', filename='css/browser.css'))
    stylesheets.append(url_for('browser.static', filename='css/aciTree/css/aciTree.css'))
    stylesheets.append(url_for('browser.browser_css'))

    # Add browser scripts
    scripts.append(url_for('static', filename='js/codemirror/codemirror.js'))
    scripts.append(url_for('static', filename='js/codemirror/mode/sql.js'))

    if config.DEBUG:
        scripts.append(url_for('static', filename='js/wcDocker/wcDocker.js'))
    else:
        scripts.append(url_for('static', filename='js/wcDocker/wcDocker.min.js'))

    scripts.append(url_for('static', filename='js/jQuery-contextMenu/jquery.ui.position.js'))
    scripts.append(url_for('static', filename='js/jQuery-contextMenu/jquery.contextMenu.js'))
    scripts.append(url_for('browser.static', filename='js/aciTree/jquery.aciPlugin.min.js'))
    scripts.append(url_for('browser.static', filename='js/aciTree/jquery.aciTree.dom.js'))
    scripts.append(url_for('browser.static', filename='js/aciTree/jquery.aciTree.min.js'))
    scripts.append(url_for('browser.browser_js'))

    for module in modules_and_nodes:
        # Get the edit menu items
        if 'hooks' in dir(module) and 'get_file_menu_items' in dir(module.hooks):
            file_items.extend(module.hooks.get_file_menu_items())

        # Get the edit menu items
        if 'hooks' in dir(module) and 'get_edit_menu_items' in dir(module.hooks):
            edit_items.extend(module.hooks.get_edit_menu_items())

        # Get the tools menu items
        if 'hooks' in dir(module) and 'get_tools_menu_items' in dir(module.hooks):
            tools_items.extend(module.hooks.get_tools_menu_items())

        # Get the management menu items
        if 'hooks' in dir(module) and 'get_management_menu_items' in dir(module.hooks):
            management_items.extend(module.hooks.get_management_menu_items())

        # Get the help menu items
        if 'hooks' in dir(module) and 'get_help_menu_items' in dir(module.hooks):
            help_items.extend(module.hooks.get_help_menu_items())

        # Get any stylesheets
        if 'hooks' in dir(module) and 'get_stylesheets' in dir(module.hooks):
            stylesheets += module.hooks.get_stylesheets()

        # Get any scripts
        if 'hooks' in dir(module) and 'get_scripts' in dir(module.hooks):
            scripts += module.hooks.get_scripts()

    file_items = sorted(file_items, key=lambda k: k['priority'])
    edit_items = sorted(edit_items, key=lambda k: k['priority'])
    tools_items = sorted(tools_items, key=lambda k: k['priority'])
    management_items = sorted(management_items, key=lambda k: k['priority'])
    help_items = sorted(help_items, key=lambda k: k['priority'])

    return render_template(MODULE_NAME + '/index.html',
                           username=current_user.email,
                           file_items=file_items,
                           edit_items=edit_items,
                           tools_items=tools_items,
                           management_items=management_items,
                           help_items=help_items,
                           stylesheets = stylesheets,
                           scripts = scripts)

@blueprint.route("/browser.js")
@login_required
def browser_js():
    """Render and return JS snippets from the nodes and modules."""
    snippets = ''
    modules_and_nodes = modules + all_nodes

    # Load the core browser code first

    # Get the context menu items
    standard_items = [ ]
    create_items = [ ]
    context_items = [ ]
    panel_items = [ ]

    for module in modules_and_nodes:
        # Get any standard menu items
        if 'hooks' in dir(module) and 'get_standard_menu_items' in dir(module.hooks):
            standard_items.extend(module.hooks.get_standard_menu_items())

        # Get any create menu items
        if 'hooks' in dir(module) and 'get_create_menu_items' in dir(module.hooks):
            create_items.extend(module.hooks.get_create_menu_items())

        # Get any context menu items
        if 'hooks' in dir(module) and 'get_context_menu_items' in dir(module.hooks):
            context_items.extend(module.hooks.get_context_menu_items())

        # Get any panels
        if 'hooks' in dir(module) and 'get_panels' in dir(module.hooks):
            panel_items += module.hooks.get_panels()

    standard_items = sorted(standard_items, key=lambda k: k['priority'])
    create_items = sorted(create_items, key=lambda k: k['priority'])
    context_items = sorted(context_items, key=lambda k: k['priority'])
    panel_items = sorted(panel_items, key=lambda k: k['priority'])

    layout = get_setting('Browser/Layout', default='')

    snippets += render_template('browser/js/browser.js',
                                layout = layout,
                                standard_items = standard_items,
                                create_items = create_items,
                                context_items = context_items,
                                panel_items = panel_items)

    # Add module and node specific code
    for module in modules_and_nodes:
        if 'hooks' in dir(module) and 'get_script_snippets' in dir(module.hooks):
            snippets += module.hooks.get_script_snippets()

    resp = Response(response=snippets,
                status=200,
                mimetype="application/javascript")

    return resp

@blueprint.route("/browser.css")
@login_required
def browser_css():
    """Render and return CSS snippets from the nodes and modules."""
    snippets = ''
    modules_and_nodes = modules + all_nodes

    for module in modules_and_nodes:
        if 'hooks' in dir(module) and 'get_css_snippets' in dir(module.hooks):
            snippets += module.hooks.get_css_snippets()

    resp = Response(response=snippets,
                status=200,
                mimetype="text/css")

    return resp


@blueprint.route("/nodes/")
@login_required
def get_nodes():
    """Build a list of treeview nodes from the child nodes."""
    value = '['
    nodes = []
    for node in sub_nodes:
        if hasattr(node, 'hooks') and hasattr(node.hooks, 'get_nodes'):
            nodes.extend(node.hooks.get_nodes())
    return make_json_response(data=nodes)

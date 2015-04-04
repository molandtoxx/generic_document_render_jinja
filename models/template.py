from datetime import datetime, date

from jinja2.environment import Environment as JinjaEnvironment
from jinja2.loaders import BaseLoader
from openerp import models, api


__author__ = 'deimos'

#TODO: integrate jinja2 translations into odoo translation mechanism


class JinjaOdooTemplateLoader(BaseLoader):
    def __init__(self, model):
        self.model = model

    def get_source(self, environment, template):
        t = self.model.search([('name', '=', template), ('type', '=', self.model.type)])
        return t.content, template, False

    def list_templates(self):
        templates = self.model.search([('type', '=', self.model.type)])
        return [template.filename for template in templates]


class DocumentTemplate(models.Model):
    _inherit = 'document.template'

    @api.multi
    def _render_jinja(self, data, **params):
        function_obj = self.env['document.template.function']
        self_obj = self.env['document.template']

        jenv = JinjaEnvironment(
            extensions=['jinja2.ext.i18n'],
            loader=JinjaOdooTemplateLoader(self)
        )

        all_functions = function_obj.jinja_get_all()

        jenv.filters.update(all_functions['filters'])
        jenv.tests.update(all_functions['tests'])
        jenv.globals.update(all_functions['functions'])

        if 'globals' in params:
            jenv.globals.update(params['globals'])

        if 'filters' in params:
            jenv.filters.update(params['filters'])

        if 'tests' in params:
            jenv.tests.update(params['tests'])

        if 'functions' in params:
            jenv.globals.update(params['functions'])

        data.update(now=datetime.now(), today=date.today(), context=self.env.context, env=self.env)

        jenv.globals.update({
            'model': lambda x: self.env[x],
            'root_model': lambda x: self.env[x].sudo(),
            'partial': lambda _template, _params=None: self_obj.render_template(_template, _params),
        })

        template = jenv.get_template(self.name)

        return template.render(**data)


import types
from openerp import models, fields, api, _


class DocumentTemplateFunctionJinja(models.Model):
    _inherit = 'document.template.function'

    is_filter = fields.Boolean('Is Filter')
    is_test = fields.Boolean('Is Test')
    is_function = fields.Boolean('Is Function')

    @api.one
    @api.constrains('code')
    def _check_code(self):
        try:
            l = eval(self.code)
            if not isinstance(l, types.LambdaType):
                raise ValueError(_("The python code must be a lambda."))
        except (SyntaxError, NameError, ):
            raise ValueError(_("The python code must be a lambda."))

    _sql_constraints = [
        ('name', 'unique(name)', 'The name must be unique')
    ]

    @api.multi
    def jinja_get_all(self):
        functions = {
            f.name: {
                'function': eval(f.code),
                'record': f
            } for f in self.search([])
        }

        return {
            'filters': {
                key: functions[key]['function'] for key in functions if functions[key]['record'].is_filter
            },
            'tests': {
                key: functions[key]['function'] for key in functions if functions[key]['record'].is_test
            },
            'functions': {
                key: functions[key]['function'] for key in functions if functions[key]['record'].is_function
            },
        }


class DataGenerator:
    DEFAULT_USER_PASSWORD = '123'

    def __init__(self, env, default_user_password=DEFAULT_USER_PASSWORD):
        self.env = env
        self.default_user_password = default_user_password

    xml_ids = {
        'unit': 'uom.product_uom_unit',
        'main_company': 'base.main_company',
    }

    models = {
        'ConfigSettings': 'res.config.settings',
    }

    def account(self, company, code):
        return self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('code', '=', code),
        ]).ensure_one()

    def execute_settings(self, vals):
        self.env['res.config.settings'].create(vals).execute()

    def create_property(self, model_name, field_name, res_id, company, value):
        field_id = self.env['ir.model.fields']._get_id(model_name, field_name)
        field_type = self.env[model_name]._fields[field_name].type

        # TODO Make res_id is list of ids
        property_vals = {
            'fields_id': field_id,
            'company_id': company.id,
            'res_id': res_id,
        }

        prop = self.env['ir.property'].search(
            [(name, '=', value) for name, value in property_vals.items()]
        )

        if prop:
            prop.write({
                'value': value,
                'type': field_type,
            })
        else:
            self.env['ir.property'].create(
                dict(property_vals, **{
                    'name': field_name,
                    'value': value,
                    'type': field_type,
                })
            )

    def create_user(self, vals, groups=()):

        self.env['res.users'].create(vals)

        # vals.setdefault('name', vals['login'].replace('_', ' ').replace('-', ' ').title())

        vals.setdefault('email', vals['login'] + '@example.com')
        vals.setdefault('password', self.default_user_password)

        vals.setdefault('company_ids', [(4, vals['company_id'])])

        vals.setdefault('country_id', self.russia.id)
        vals.setdefault('lang', 'ru_RU')
        vals.setdefault('tz', 'Europe/Saratov')

        if not vals.get('groups_id'):
            vals['groups_id'] = [self.env.ref(xml_id).id for xml_id in groups]

        return self.env['res.users'].with_context(no_reset_password=True).create(vals)

    # Main
    def generate(self):
        records = self.populate()
        self.save_refs(records)
        self.commit()

    def populate(self):
        pass

    def save_refs(self, records):
        if not records:
            return

        ModelData = env['ir.model.data']

        for name, value in records.items():
            if not isinstance(value, models.Model):
                continue

            if len(value) == 1 and not ModelData.search_count([
                ('model', '=', value._name),
                ('res_id', '=', value.id),
            ]):
                ModelData.create({
                    'module': 'test',
                    'name': name,
                    'model': value._name,
                    'res_id': value.id,
                })

    def commit(self):
        self.env.cr.commit()

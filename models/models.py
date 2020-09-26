# -*- coding: utf-8 -*-

from odoo import models, fields, api


class test(models.Model):
    _name = "test.test"
    _description = "test.test"

    name = fields.Char()
    value = fields.Integer()
    testField = fields.Char()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends("value")
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

            if (
                record.name
                and record.value
                and record.testField
                and record.value2
                and record.description
                and record
            ):
                pass

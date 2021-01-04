# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

PARTNER_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class PartnerState(models.Model):
    _name = 'project.partner.state'
    _description = 'Partner state'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char('Name', required=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self:self.env['res.company']._company_default_get())
    project_ids = fields.Many2many('project.project', 'project_partner_state_rel', 'state_id', 'project_id',
                                   string='Projects', default=_get_default_project_ids)
    description = fields.Text(translate=True)


class ProjectPartner(models.Model):
    _name = 'project.partner'
    _description = 'Project partner'
    _rec_name = 'partner_id'

    def _default_stage_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.partner.state'].search([
                '|',
                ('project_ids', '=', False),
                ('project_ids', '=', self._context['default_project_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).id
        return False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        project_id = self._context.get('default_project_id')
        search_domain = [('project_ids', '=', False)]
        if project_id:
            search_domain = ['|', ('project_ids', '=', project_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    color = fields.Integer('Color Index', default=0)
    state_id = fields.Many2one('project.partner.state', 'State', ondelete='restrict', tracking=True,
                               domain="['|', ('project_ids', '=', False), ('project_ids', '=', project_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.uid)
    priority = fields.Selection(PARTNER_PRIORITIES, string='Priority', default='0')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self:self.env['res.company']._company_default_get())


class Project(models.Model):
    _inherit = 'project.project'

    project_partner_ids = fields.One2many("project.partner", "project_id", "Partners")
    partner_count = fields.Integer('Partners')
    state_ids = fields.Many2many('project.partner.state', 'project_partner_state_rel', 'project_id', 'state_id',
                                 string='State partner')
    partner_count = fields.Integer(compute='_compute_partner_count', string="Partner Count")

    def _compute_partner_count(self):
        partner_data = self.env['project.partner'].read_group([('project_id', 'in', self.ids), '|', ('state_id.fold', '=', False), ('state_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in partner_data)
        for project in self:
            project.partner_count = result.get(project.id, 0)

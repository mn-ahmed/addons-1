# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AddonsPathConfigInstaller(models.TransientModel):
    _name = 'odoo_sh_community.config.installer'
    _inherit = 'res.config.installer'

    addons_path = fields.Char(
        string=u'Parent Path',
        help=u'Path where repositories will be downloaded, repositories folders will be created. Write permissions are mandatory.',
        default='/mnt/extra-addons'
    )
    uploaded_modules_path = fields.Char(
        string=u'Upload Modules Path',
        help=u'Path where uploaded modules will be stored. Write permissions are mandatory',
        default='/mnt/extra-addons/my-uploaded-modules'
    )

    def modules_to_install(self):
        # modules = super(AddonsPathConfigInstaller, self).modules_to_install()
        return set([])

    # Crea las acciones para chequear permisos de escritura en el config y en el addons path seleccionado
    
    def execute(self):
        IrParamSudo = self.env['ir.config_parameter'].sudo()
        addons_path = self.addons_path
        uploaded_modules_path = self.uploaded_modules_path

        try:
            # intenta ver si tenes permisos de escritura en la carpeta mencionada
            # intenta ver si tenes permisos de escritura en el config
            # Si todo esta ok:
            # Edita el ir.config.parameter que corresponde al addons_path del modulo
            IrParamSudo.set_param('repositories.addons_path',addons_path)
            IrParamSudo.set_param('repositories.upload_modules_path',uploaded_modules_path)
        except:
            pass
        return super(AddonsPathConfigInstaller, self).execute()
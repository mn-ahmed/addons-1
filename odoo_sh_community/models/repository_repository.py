# -*- coding: utf-8 -*-

import re
import os
from os.path import isfile
from os import environ, path
from odoo import api, exceptions, fields, models, _, service, tools
import subprocess
import logging
from os.path import isdir as is_dir
import shutil
from datetime import datetime
from odoo import release
from odoo.tools import config
from os.path import join as path_join
import sys
import urllib.parse
_logger = logging.getLogger(__name__)
import time
import sys
import subprocess
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from .module import PARAM_ADDONS_PATH
try:
    from git import Repo, Git, cmd
    from git.exc import InvalidGitRepositoryError, GitCommandError, UnmergedEntriesError, CheckoutError
except Exception as ex:
    subprocess.check_call(["python3", "-m", "pip", "install", 'GitPython'])
    from git import Repo, Git, cmd
    from git.exc import InvalidGitRepositoryError, GitCommandError, UnmergedEntriesError, CheckoutError

nlist_path = []
list_of_addons_paths = tools.config['addons_path'].split(",")
for path in list_of_addons_paths:
    nlist_path.append((path, path))


class RepositoryRepository(models.Model):
    _name = 'repository.repository'
    _rec_name = 'source'
    _description = 'Repository'

    def _selection_addons_path(self):
        nlist_path = []
        list_of_addons_paths = tools.config['addons_path'].split(",")
        for path in list_of_addons_paths:
            nlist_path.append((path, path))
        return nlist_path

    # @api.depends('module_ids') # no api.depends so it's computed every tyme
    def _compute_modules(self):
        module = self.env['ir.module.module']
        for repo in self:
            if repo.state == 'enabled':
                module_names = find_modules(repo.path)
                repo.module_ids = module.search([('name', 'in', module_names)])
                repo.module_count = len(repo.module_ids)
            else:
                repo.module_ids = False
                repo.module_count = 0

    path = fields.Char('Path', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    # path = fields.Many2one('addons.path',string='Path', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    source = fields.Char('Source', readonly=True, states={'draft': [('readonly', False)]})
    branch = fields.Char('Branch', default=release.series, readonly=True, states={'draft': [('readonly', False)]})
    rev_id = fields.Char('Last Revision', readonly=True)
    rev_date = fields.Datetime('Last Rev. Date', readonly=True)
    dirty = fields.Boolean('Dirty', readonly=True)
    module_ids = fields.Many2many('ir.module.module', string='Modules', compute=_compute_modules)
    module_count = fields.Integer('Modules', compute=_compute_modules)
    state = fields.Selection(string="Estado",
                             selection=[('draft', 'Draft'), ('cloned', 'Cloned'), ('enabled', 'Enabled'),
                                        ('disabled', 'Disabled')], default='draft', readonly=True,)
    # addons_paths = fields.Selection(selection=_selection_addons_path,
    #                                 string="Add-ons Paths", help="Please choose one of these directories to put "
    #                                                              "your module in", )
    password = fields.Char(string='Password', required=False)
    user = fields.Char(string='User', required=False)
    log = fields.Text(string='Log', required=False)

    def log_(self, mensaje):
        now = datetime.now()
        self.write({'log': '\n%s %s %s' % (str(now.strftime("%m/%d/%Y, %H:%M:%S")), str(mensaje), str(self.log))})

    requirements = fields.Char(
        string='Requirements',
        required=False)

    @api.onchange('source')
    def _onchange_source(self):
        if self.source:
            self.path = self.get_path('-'.join([chunk.replace('.git','') for chunk in self.source.split('/')[-2:]]))

    def get_path(self, path=False):
        self.ensure_one()
        conf_parameter = self.env['ir.config_parameter']
        if not path:
            return os.path.join(conf_parameter.get_param(PARAM_ADDONS_PATH, '/mnt/extra-addons'), self.path)
        else:
            return os.path.join(conf_parameter.get_param(PARAM_ADDONS_PATH, '/mnt/extra-addons'), path)


    def copy(self, default=None):
        raise exceptions.Warning(_("The repository cannot be cloned."))

    def unlink(self):
        if self.env.context.get('remove_repository'):
            for rec in self:
                if rec.state == 'enabled':
                    raise exceptions.Warning(_('Unable to remove an enabled repository.'))
                # res = Git(self.get_path())
                res = Git(rec.path)
                res.load()
                res.remove()
        return super(RepositoryRepository, self).unlink()

    def action_open_modules(self):
        self.ensure_one()
        return {
            'name': self.source,
            'type': 'ir.actions.act_window',
            'res_model': 'ir.module.module',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'domain': [('id', 'in', self.module_ids.ids)]
        }

    def install_requirements(self):
        requirement_file = self.path + '/requirements.txt'
        try:
            if os.path.exists(requirement_file):
                subprocess.check_call(["pip3", "install", "-r", requirement_file])
        except Exception as e:
            self.log_("Exception exception occured: {}".format(e))
            try:
                if os.path.exists(requirement_file):
                    subprocess.check_call(["python3","-m","pip", "install", "-r", requirement_file])
            except Exception as e:
                self.log_("2do Exception exception occured: {}".format(e))

    def action_enabled(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied
        addons_path = config['addons_path'].split(',')
        if config._is_addons_path(self.path) and self.path not in addons_path:
            # addons_path.insert(0, self.path)
            addons_path.append(self.path)
            config['addons_path'] = ','.join(addons_path)
            config.save()
        self.state = 'enabled'
        requirement_file = self.path + '/requirements.txt'
        if os.path.exists(requirement_file):
            f = open(requirement_file, "r")
            self.requirements = f.read()
            self.install_requirements()

        # self._compute_apps()
        return self.env.ref(
            'base.action_view_base_module_update').read()[0]

    def action_remove(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied
        try:
            self.with_context(remove_repository=True).unlink()
        except Exception as e:
            raise exceptions.Warning(_(" '%s':\n%s") % (self.source, e))
        return {'type': 'ir.actions.act_window_close'}

    def restart(self):
        service.server.restart()

    @api.model
    def pull_all(self):
        flags = self.env['repository.repository'].search([]).update()
        if any(flags):
            service.server.restart()


    def action_update(self):
        self.ensure_one()
        flags = self.update()
        if any(flags):
            service.server.restart()

    def update(self):
        repos_updated_flags = []
        for repo in self:
            if not self.env.user.has_group('base.group_system'):
                raise exceptions.AccessDenied
            try:
                res = Git(repo.path, repo.user, repo.password)
                res.load()
                flags=res.update(repo.source)
                repos_updated_flags.append(flags)
                for l in res.log():
                    repo.log_(l)
                if flags:
                    repo.install_requirements()
                    repo._compute_modules()
                    self.env['ir.module.module'].upgrade_changed_checksum(repo)
            except Exception as e:
                raise exceptions.Warning(_("'%s':\n%s") % (repo.source, e))
        return repos_updated_flags

    def action_disable(self):
        self.ensure_one()
        self.state = 'disabled'
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied
        addons_path = config['addons_path'].split(',')
        if self.path in addons_path:
            if self.module_ids.filtered(lambda r: r.state not in (
                    'uninstalled', 'uninstallable')):
                raise exceptions.Warning(
                    _('Some modules of this repository are installed.'))
            addons_path.remove(self.path)
            config['addons_path'] = ','.join(addons_path)
            config.save()

    def clone(self):
        self.ensure_one()
        # This way you can force a manual path which doesn't exist in addons path yet
        # if not self.path or self.path == '':
        #     self.path = path_join(self.addons_paths and self.addons_paths or '', self.path and self.path or '',re.compile(r'[^0-9a-zA-Z]+').sub('_', self.source + self.branch))
        #     must_add_addons_path = False
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError as e:
            os.makedirs(self.path)
        try:
            res = Git(self.path)
            res.init(self.source, branch=self.branch, user=self.user, password=self.password)
            res.load()
            self.env.cr.commit()
            # If addons path wasn't selected, must create the config entry
            requirement_file = self.path + '/requirements.txt'
            if os.path.exists(requirement_file):
                f = open(requirement_file, "r")
                self.requirements = f.read()
                self.install_requirements()
            self.write({'state':'cloned'})
            # self._compute_apps()
            self.env.cr.commit()
            service.server.restart()
        except Exception as e:
            self.write({'state':'draft'})
            raise exceptions.Warning(_(
                "An error has occurred while Clone '%s':\n%s") % (self.source, e))
        # Only set state to 'cloned' after a successful clone

    def _default_repository_ids(self):
        res = self.env['repository.repository']
        for path in config['addons_path'].split(','):
            git = Git(path)
            if git.load():
                data = git.info()
                result = res.search([('path', '=', data['path'])])
                if not result:
                    data.update({'state': 'enabled'})
                    result = res.create(data)
                    # result._compute_apps()
                    self.env.cr.commit()

def find_modules(path):
    return [module for module in os.listdir(path) if any(map(
        lambda f: isfile(path_join(path, module, f)), (
            '__manifest__.py', '__openerp__.py')))]


class Git():
    _source_http = None
    _source_git = None
    _repo = None
    _user = None
    _pass = None
    _path = None
    _output_list = []

    def __init__(self, path=None, user=None, password=None):
        self._path = path
        self._user = user
        self._pass = password

    def remove(self):
        if self.is_initialized() and not self.is_clean():
            raise exceptions.Warning(_("Error, Repository no clean."))
        if self._path and is_dir(self._path):
            shutil.rmtree(self._path)

    def is_initialized(self):
        return not not self._repo

    def init(self, source, branch=None, user=None, password=None):
        self._user = user
        self._pass = password
        if not self.is_initialized():
            if not self._user:
                self._repo = Repo.clone_from(source, self._path, **{
                    'branch': branch, 'single-branch': True, 'depth': 1})
                self._source_http = source
            else:
                source = source.replace('https://', '')
                source_git = "https://" + self._user + ":" + self._pass + "@" + source
                self._source_git=source_git
                self._repo = Repo.clone_from(source_git, self._path, **{
                    'branch': branch, 'single-branch': True, 'depth': 1})
                self._source_http = source_git

    def is_clean(self):
        return self.is_initialized() and not self._repo.is_dirty(untracked_files=True)

    def load(self, **kwargs):
        if not self._repo:
            if self._path and is_dir(path_join(self._path, '.git')):
                self._repo = Repo(self._path)
                return True
            else:
                return False

    def info(self):
        branch = self._repo.active_branch.name
        curr_rev = self._repo.rev_parse(branch)
        git = self.info_base()
        source=''
        if self._repo.remotes:
            source = self._repo.remotes.origin.url.split('@')
            if len(source) > 1:
                source = "https://" + source[1]
            else:
                source = self._repo.remotes.origin.url
        return dict(git, **{
            'source': source,
            'branch': branch,
            'rev_id': curr_rev.hexsha,
            'path': self._path,
            'rev_date': datetime.fromtimestamp(curr_rev.committed_date),
        })

    def info_base(self):
        return {
            'path': self._path,
            'source': None,
            'branch': None,
            'rev_id': None,
            'rev_date': None,
            'dirty': False,
        }
    def log(self):
        return self._output_list

    def update(self,url):
        msg = ''
        old_env = {}
        ret_flag = True

        self._output_list.append(str(time.ctime()) + ": Checking for updates")

        if self.is_initialized():
            branch = self._repo.active_branch
            remote_origin = self._repo.remotes.origin
            if remote_origin.exists():
                try:
                    self._repo.remote()
                    git_cmd = cmd.Git(self._path)
                    if not self._source_git:
                        if self._user:
                            source_git = "https://" + self._user + ":" + self._pass + "@" + url.replace('https://', '')
                            self._source_git = source_git


                    # if self._user and self._pass:
                    #     project_dir = os.path.dirname(os.path.abspath(__file__))
                    #     # old_env = git_cmd.update_environment(SSH_ASKPASS=os.path.join(project_dir, 'askpass.py'),
                    #     #                                      REPO_USERNAME=self._user, GIT_PASSWORD=self._passwd)
                    #     old_env = git_cmd.update_environment(SSH_ASKPASS=os.path.join(project_dir, 'askpass.py'),
                    #                                          REPO_USERNAME=self._user, REPO_PASSWORD=self._pass)
                    # fetch_info = git_cmd.fetch(branch.name)
                    _logger.error('PULL ++++'+str(self._source_git))
                    git_cmd.reset('--hard')
                    msg = git_cmd.pull(self._source_git,force=True)
                    # branch.set_reference(fetch_info[0].ref.name)

                    # restore the environment back to its previous state after operation.
                    #if old_env:
                    #    git_cmd.update_environment(**old_env)

                    # msg is '' or 'Updating ...' or 'Already up-to-date.' if you pulled successfully
                    if msg:  # encoding = 'utf-8', msg1 = msg.decode(encoding) to see if use here instead of msg!
                        if 'Already' in msg:
                            ret_flag = False
                        else:
                            ret_flag = True
                        _logger.info(str(msg))
                        self._output_list.append(str(msg))
                    else:
                        ret_flag = True


                except GitCommandError as exc:
                    # after some tests we can cancel _logger.error of exc.stdout e exc.stdin because with
                    # GIT_PYTHON_TRACE set to "full" the same output is written to logger.
                    ret_flag = False
                    if exc.stderr:
                        self._output_list.append(exc.stderr.lstrip())
                        _logger.error('GitCommandError exception occured: {}'.format(exc.stderr.lstrip()))
                    elif exc.stdout:
                        self._output_list.append(exc.stdout.lstrip())
                        _logger.error('GitCommandError exception occured: {}'.format(exc.stdout.lstrip()))
                except InvalidGitRepositoryError as exc:
                    ret_flag = False
                    _logger.error('Invalid git repository: {}, {} '.format(self._repo_path, exc))
                    self._output_list.append(str('Invalid git repository: {}, {} '.format(self._repo_path, exc)))
                except CheckoutError as exc:
                    ret_flag = False
                    _logger.error("CheckoutError exception occured: {}".format(exc))
                    self._output_list.append("CheckoutError exception occured: {}".format(exc))
                except UnmergedEntriesError as exc:
                    ret_flag = False
                    _logger.error("CheckouUnmergedEntriesError exception occured: {}".format(exc))
                    self._output_list.append("CheckouUnmergedEntriesError exception occured: {}".format(exc))
                # except AssertionError as exc:
                #     ret_flag = False
                #     _logger.error("AssertionError exception occured: {}".format(exc))

            else:
                ret_flag = False
                _logger.info('Remote repository \'origin\' doesn\'t exsist!')
                self._output_list.append('Remote repository \'origin\' doesn\'t exsist!')

        return ret_flag

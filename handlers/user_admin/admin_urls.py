#coding=utf-8
from handlers.user_admin.admin_handler import AdminHandler
from handlers.user_admin.swissquote_handler import SwissquoteHandler
from handlers.user_admin.swissquote_proxy_handler import SwissquoteProxyHandler
from handlers.user_admin.swissquote_proxy_info_handler import SwissquoteProxyInfoHandler
from handlers.user_admin.sendmail_handler import SendmailHandler
from handlers.user_admin.strategy_handler import StrategyHandler
from handlers.user_admin.copy_handler import CopyHandler
from handlers.user_admin.parameter_handler import ParameterHandler
from handlers.user_admin.accounts_handler import AccountsHandler
from handlers.user_admin.info_handler import InfoHandler
from handlers.user_admin.proposal_handler import ProposalHandler
from handlers.user_admin.command_handler import CommandHandler
from handlers.user_admin.lang_handler import LangHandler
from handlers.user_admin.proxy_handler import ProxyHandler
from handlers.user_admin.proxy_info_handler import ProxyInfoHandler
from handlers.user_admin.history_handler import HistoryHandler

user_admin_urls = [
    (r'/index', AdminHandler),
    (r'/h', HistoryHandler),
    (r'/user/index', AdminHandler),
    (r'/user/sendmail', SendmailHandler),
    (r'/user/strategy', StrategyHandler),
    (r'/user/copy', CopyHandler),
    (r'/user/parameter', ParameterHandler),
    (r'/user/accounts', AccountsHandler),
    (r'/user/info', InfoHandler),
    (r'/user/proposal', ProposalHandler),
    (r'/user/command', CommandHandler),
    (r'/user/lang', LangHandler),
    (r'/user/proxy', ProxyHandler),
    (r'/user/proxy_info', ProxyInfoHandler),
    (r'/swissquote', SwissquoteHandler),
    (r'/swissquote/proxy', SwissquoteProxyHandler),
    (r'/swissquote/proxy_info', SwissquoteProxyInfoHandler),
]
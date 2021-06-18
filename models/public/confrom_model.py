#coding=utf-8
from wtforms_tornado import Form
from wtforms import StringField, validators, PasswordField, IntegerField, HiddenField, BooleanField, FloatField, FileField

class ErrorForm(Form):
    # 错误代码
    cla = StringField('cla', [
        validators.InputRequired(message=(u'操作类型不正确'))
    ])
    ukid = StringField('ukid', [
        validators.Regexp('[a-zA-Z\d]+$', message=(u'非法数据')),
        validators.Length(min=32, max=32, message=(u'密码应为32个字符'))
    ])
    f2 = IntegerField('f2', [
        validators.NumberRange(1, 999999999999, message=(u'只能是数字'))
    ])
    f5 = StringField('f5', [
        validators.Regexp('[a-zA-Z\d]+$', message=(u'非法数据')),
        validators.Length(min=32, max=32, message=(u'密码应为32个字符'))
    ])
    f10 = StringField('f10', [
        validators.Regexp('[a-zA-Z\d]+$', message=(u'非法数据')),
        validators.Length(min=32, max=32, message=(u'密码应为32个字符'))
    ])
    f8 = IntegerField('f8', [
        validators.NumberRange(0, 1000, message=(u'只能是数字'))
    ])
    f7 = IntegerField('f7', [
        validators.NumberRange(0, 10, message=(u'只能是数字'))
    ])
    f9 = StringField('f9', [
        validators.InputRequired(message=(u'字符不正确'))
    ])

class SendEmailForm(Form):
    # 管理员登陆
    umail = StringField('umail', [
        validators.InputRequired(message=(u'邮箱输入不正确，请重新输入')),
        validators.Length(min=5, max=32, message=(u'邮箱字符应为5-32个字符，请重新输入')),
        validators.Email(message=(u'邮箱格式不正确，请重新输入')),
        # validators.Regexp('^((?!\.de).)*$', message=(u'非法数据')),
        validators.Regexp('.*\.(com|cn|net|org|gov|edu|top)$', message=(u'非法数据')),
    ])

class LoginForm(Form):
    # 管理员登陆
    umail = StringField('umail', [
        validators.optional(),
        validators.InputRequired(message=(u'邮箱输入不正确，请重新输入')),
        validators.Length(min=5, max=32, message=(u'邮箱字符应为5-32个字符，请重新输入')),
        validators.Email(message=(u'邮箱格式不正确，请重新输入')),
        validators.Regexp('.*\.(com|cn|net|org|gov|edu|top)$', message=(u'非法数据')),
    ])
    pword = StringField('pword', [
        validators.optional(),
        validators.Length(min=6, max=6, message=(u'验证码应为6个字符，请重新输入'))
    ])
    password = StringField('password', [
        validators.optional(),
        validators.Length(min=8, max=30, message=(u'验证码应为8-30个字符，请重新输入'))
    ])
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=1, max=20, message=(u'类型应为20个字符以内'))
    ])

class StrategyForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=25, message=(u'类型应为10个字符以内'))
    ])
    fx_id = IntegerField('fx_id', [
        validators.optional(),
        validators.NumberRange(min=0, max=99999999999, message=(u'类型应为数字'))
    ], default=0)

class StrategySelectForm(Form):
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为10个字符以内'))
    ])
    form_uaid = IntegerField('form_uaid', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'id只能是数字'))
    ])
    backurl = StringField('backurl', [
        validators.optional(),
        validators.URL(message=(u'不规范的URL'))
    ], default="")

class CopySelectForm(Form):
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为10个字符以内'))
    ])
    fx_flag = IntegerField('fx_flag', [
        validators.optional(),
        validators.NumberRange(0, 9, message=(u'只能是数字'))
    ])
    form_id = IntegerField('form_id', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'只能是数字'))
    ])
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)
    # search_value = IntegerField('search[value]', [
    #     validators.optional(),
    #     validators.NumberRange(0, 99999999999, message=(u'搜索只能是数字'))
    # ], default=0)
    # search_regex = BooleanField('search_regex', [
    #     validators.optional(),
    #     validators.InputRequired(message=(u'类型不正确'))
    # ])
    time_type = StringField('time_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为10个字符以内'))
    ])

class ParameterForm(Form):
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为20个字符以内'))
    ])
    fx_id = IntegerField('fx_id', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'id超出数字范围'))
    ])
    maxtime = IntegerField('maxtime', [
        validators.optional(),
        validators.NumberRange(0, 100000, message=(u'最大延时超出数字范围'))
    ], default=0)
    maxloss = IntegerField('maxloss', [
        validators.optional(),
        validators.NumberRange(0, 1000, message=(u'最大滑点超出数字范围'))
    ], default=0)
    maxnum = IntegerField('maxnum', [
        validators.optional(),
        validators.NumberRange(0, 5000, message=(u'最大持仓量超出数字范围'))
    ], default=0)
    reflex = IntegerField('reflex', [
        validators.optional(),
        validators.NumberRange(0, 2, message=(u'反向跟单类型错误'))
    ], default=0)
    fixed = FloatField('fixed', [
        validators.optional(),
        validators.NumberRange(0, 10000, message=(u'固定手数超出数字范围'))
    ], default=0)
    percent = FloatField('percent', [
        validators.optional(),
        validators.NumberRange(0, 10000, message=(u'位数开仓超出数字范围'))
    ], default=0)
    rate_min = FloatField('rate_min', [
        validators.optional(),
        validators.NumberRange(0, 5000, message=(u'最小持仓超出数字范围'))
    ], default=0)
    rate_max = FloatField('rate_max', [
        validators.optional(),
        validators.NumberRange(0, 5000, message=(u'最大持仓超出数字范围'))
    ], default=0)
    rate = FloatField('rate', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'风控线超出数字范围'))
    ], default=0)

    tpsl_flag = IntegerField('tpsl_flag', [
        validators.optional(),
        validators.NumberRange(0, 10, message=(u'超出数字范围'))
    ], default=0)

class AccountsForm(Form):
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为20个字符以内'))
    ])
    fx_id = IntegerField('fx_id', [
        validators.optional(),
        validators.NumberRange(0, 9999999999, message=(u'fx_id超出数字范围'))
    ])
    fx_id2 = IntegerField('fx_id2', [
        validators.optional(),
        validators.NumberRange(0, 5, message=(u'fx_id2超出数字范围'))
    ])
    datetype = IntegerField('datetype', [
        validators.optional(),
        validators.NumberRange(0, 1, message=(u'新增与续费只能两选一'))
    ])
    daytype = IntegerField('daytype', [
        validators.optional(),
        validators.NumberRange(0, 5, message=(u'daytype超出数字范围'))
    ])
    fx_num = IntegerField('fx_num', [
        validators.optional(),
        validators.NumberRange(0, 999999999, message=(u'跟单账户数量超出数字范围'))
    ])
    cnh = FloatField('cnh', [
        validators.optional(),
        validators.NumberRange(0, 5000, message=(u'人民币价格超出数字范围'))
    ], default=0)
    fx_no = StringField('fx_no', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=30, message=(u'类型应为20个字符以内'))
    ])
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)

class InfoForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=30, message=(u'类型应为30个字符以内'))
    ])
    fx_name = StringField('fx_name', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=25, message=(u'类型应为25个字符以内'))
    ], default="")
    comment = StringField('comment', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'仅支持a-z A-Z 0-9 _这些字符组成')),
        validators.Length(min=1, max=21, message=(u'类型应为20个字符以内'))
    ], default="")
    urlpass = StringField('urlpass', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'仅支持a-z A-Z 0-9 _这些字符组成')),
        validators.Length(min=3, max=32, message=(u'类型应为32个字符以内'))
    ], default="")
    pu_status = IntegerField('pu_status', [
        validators.optional(),
        validators.NumberRange(0, 2, message=(u'只能是数字'))
    ], default=0)
    fx_id = IntegerField('fx_id', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'只能是数字'))
    ], default=0)

class ImgForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=25, message=(u'类型应为10个字符以内'))
    ])
    file_name = StringField('file_name', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=64, message=(u'类型应为64个字符以内'))
    ], default=0)

class ProposalForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=50, message=(u'类型应为50个字符以内'))
    ])
    fx_id = IntegerField('fx_id', [
        validators.optional(),
        validators.NumberRange(min=0, max=99999999999, message=(u'类型应为数字'))
    ], default=0)
    fx_name = StringField('fx_name', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=25, message=(u'类型应为25个字符以内'))
    ], default=0)
    fx_text = StringField('fx_text', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=1000, message=(u'类型应为1000个字符以内'))
    ], default=0)
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)

class HistoryForm(Form):
    fx_type = StringField('fx_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=50, message=(u'类型应为50个字符以内'))
    ], default="")
    k = StringField('k', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=64, message=(u'类型应为64个字符以内'))
    ], default="0")
    fx_pass = StringField('fx_pass', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=1000, message=(u'类型应为1000个字符以内'))
    ], default=0)
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    uaid = IntegerField('uaid', [
        validators.optional(),
        validators.NumberRange(0, 99999999999999, message=(u'只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)
    time_type = StringField('time_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为10个字符以内'))
    ])

class ProxyForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=50, message=(u'类型应为10个字符以内'))
    ])
    account = IntegerField('account', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'只能是数字'))
    ], default=0)
    uid = IntegerField('uid', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'只能是数字'))
    ], default=0)
    time_type = StringField('time_type', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=0, max=20, message=(u'类型应为10个字符以内'))
    ])
    a_code = IntegerField('a_code', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'页长只能是数字'))
    ], default=0)
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)
    amount = FloatField('amount', [
        validators.optional()
    ], default=0)
    in_uname = StringField('in_uname', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\s]+$', message=(u'只能包括英文字母')),
        validators.Length(min=0, max=20, message=(u'类型应为20个字符以内'))
    ])
    in_iban = StringField('in_iban', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d]+$', message=(u'非法数据')),
        validators.Length(min=0, max=50, message=(u'类型应为50个字符以内'))
    ])
    out_iban = StringField('out_iban', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d]+$', message=(u'非法数据')),
        validators.Length(min=0, max=50, message=(u'类型应为50个字符以内'))
    ])
    remarks = StringField('remarks', [
        validators.optional(),
        validators.Length(min=0, max=200, message=(u'类型应为200个字符以内'))
    ])

class ProxyInfoForm(Form):
    fx_type = StringField('fx_type', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=2, max=25, message=(u'类型应为10个字符以内'))
    ])
    uname = StringField('uname', [
        validators.optional(),
        validators.Regexp('[a-zA-Z ]+$', message=(u'只能包括英文字母')),
        validators.Length(min=0, max=25, message=(u'类型应为25个字符以内'))
    ])
    iban = StringField('iban', [
        validators.optional(),
        validators.Regexp('[a-zA-Z0-9]+$', message=(u'非法数据')),
        validators.Length(min=0, max=50, message=(u'类型应为50个字符以内'))
    ])
    uid = IntegerField('uid', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'只能是数字'))
    ], default=0)
    grade_id = IntegerField('grade_id', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'只能是数字'))
    ], default=0)
    account = IntegerField('account', [
        validators.optional(),
        # validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.NumberRange(0, 999999999999, message=(u'只能是数字'))
    ], default=0)
    a_code = StringField('a_code', [
        validators.optional(),
        validators.Regexp('[a-zA-Z\d\s]+$', message=(u'非法数据')),
        validators.Length(min=0, max=50, message=(u'类型应为50个字符以内'))
    ])
    start = IntegerField('start', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'开始页只能是数字'))
    ], default=0)
    length = IntegerField('length', [
        validators.optional(),
        validators.NumberRange(0, 99999999999, message=(u'页长只能是数字'))
    ], default=0)


class LangForm(Form):
    lang = StringField('lang', [
        validators.Regexp('[a-zA-Z\d_]+$', message=(u'非法数据')),
        validators.Length(min=1, max=3, message=(u'类型应为50个字符以内'))
    ])
#--------
class AdminPassEditForm(Form):
    # 管理员登陆
    old_password = PasswordField('old_password', [
        validators.InputRequired(message=(u'旧密码不符合规范，请重新输入')),
        validators.Length(min=5, max=20, message=(u'旧密码应为6-20个字符，请重新输入'))
    ])
    password = PasswordField('password', [
        validators.Length(min=6, max=20, message=(u'新密码应为6-20个字符，请重新输入'))
    ])
    password2 = PasswordField('password2', [
        validators.Length(min=6, max=20, message=(u'确认密码应为6-20个字符，请重新输入')),
        validators.EqualTo('password', message=(u'新密码与确认密码不一致，请重新输入'))
    ])

class AdminPostEditForm(Form):
    # 博文修改
    post_title = StringField('post_title', [
        validators.InputRequired(message=(u'标题不符合规范，请重新输入')),
        validators.Length(min=5, max=60, message=(u'旧密码应为5-60个字符，请重新输入'))
    ])
    id = HiddenField('id', [
        validators.NumberRange(message=(u'文章ID不正确'))
    ])
    posts_type_id = IntegerField('posts_type_id', [
        validators.InputRequired(message=(u'分类不正确'))
    ])
    post_status = IntegerField('post_status', [
        validators.NumberRange(0, 6, message=(u'操作类型不正确'))
    ])
    post_content = StringField('post_content', [
        validators.InputRequired(message=(u'内容不符合规范，请重新输入')),
    ])
    post_excerpt = StringField('post_excerpt', [
        validators.InputRequired(message=(u'引言不符合规范，请重新输入')),
        validators.Length(min=5, max=160, message=(u'引言应为5-160个字符，请重新输入'))
    ])
    tags = StringField('tags', [
        validators.InputRequired(message=(u'标签不符合规范，请重新输入')),
    ])
    # comment_flag = BooleanField('comment_flag', default=0)

class AdminClassRoomEditForm(Form):
    #
    post_title = StringField('post_title', [
        validators.InputRequired(message=(u'标题不符合规范，请重新输入')),
        validators.Length(min=3, max=60, message=(u'标题应为5-60个字符，请重新输入'))
    ])
    posts_url = StringField('posts_url', [
        validators.InputRequired(message=(u'缩略图，请重新输入')),
    ])
    id = HiddenField('id', [
        validators.NumberRange(message=(u'文章ID不正确'))
    ])
    post_type_id = IntegerField('post_type_id', [
        validators.InputRequired(message=(u'分类不正确'))
    ])
    status_v = IntegerField('status_v', [
        validators.NumberRange(0, 6, message=(u'操作类型不正确'))
    ])
    post_text = StringField('post_text', [
        validators.InputRequired(message=(u'内容不符合规范，请重新输入')),
    ])
    description = StringField('description', [
        validators.InputRequired(message=(u'引言不符合规范，请重新输入')),
        validators.Length(min=5, max=160, message=(u'引言应为5-160个字符，请重新输入'))
    ])
    tags = StringField('tags', [
        validators.InputRequired(message=(u'标签不符合规范，请重新输入')),
    ])
    comment_flag = BooleanField('comment_flag', default=0)


class GoodForm(Form):
    # 点赞
    classid = IntegerField('classid', [
        validators.InputRequired(message=(u'编号不正确')),
    ])
    type = StringField('type', [
        validators.InputRequired(message=(u'类型不正确')),
    ])

class AdvisoryForm(Form):
    # 预约
    ugender = IntegerField('ugender', [
        # validators.NumberRange(0, 1, message=(u'性别不正确'))
    ])
    uname = StringField('uname', [
        validators.InputRequired(message=(u'非法字符'))
    ])
    umobile = StringField('umobile', [
        validators.DataRequired(message=(u'手机号码格式不正确')),
        validators.Length(11, 11, message=(u'手机号码位数不正确')),
        # validators.Regexp('^1[35789]\d{9}$', 0, message=(u'手机号码不合法'))
    ])

def get_ErrorForm(my_form):
    # 获得所有错误信息
    errors_list = ""
    if my_form.errors:
        for field_errors in my_form.errors:
            for errors in my_form[field_errors].errors:
                errors_list = errors_list + errors + "<BR>"
        return errors_list
    else:
        return None
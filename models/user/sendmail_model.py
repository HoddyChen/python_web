#coding=utf-8
from libs.db.dbsession import pool
from tornado import gen
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

logger = logging.getLogger('Main')
class SendmailModel():
    from_mail = "cs@fxcns.com"#'cs@fxcns.com'
    from_title = "跟单交易多账户管理系统邮件"
    mail_password = 'o~yA@C@fi&JiUt&jZHVfMOQT2IHyJtuvvjnljOVK~$Zjha6z~lWwS~9g70bqVcgGFUk8j~wouSv`4rfXp@IKhdlTkL9kX&rx$za'
    # mail_password = 'gtW2zyF5WhAgxMPi'

    @gen.coroutine
    def email_err_send(self):
        tomail = ['99051131@qq.com']
        echotext = "Fxncs-发生错误停止运行"
        mailtitle = "Fxncs-发生错误停止运行"
        send_flag = yield self.email_send(tomail, echotext, mailtitle)
        logger.info("send_flag: %s" % send_flag)
        if send_flag == True:
            logger.info("%s,邮件发送成功!" % mailtitle)
        return

    @gen.coroutine
    def email_send(self, to_mail, mail_msg, mailtitle):
        #to_mail必须是列表['']
        message = MIMEText(mail_msg, 'html', 'utf-8')
        message['From'] = formataddr([self.from_title, self.from_mail])
        # message['To'] = ';'.join(to_mail)  # formataddr(["亲", ""])
        message['To'] = formataddr(["dear", to_mail[0]])
        message['Subject'] = mailtitle

        try:
            # smtpObj = smtplib.SMTP('smtp.office365.com', 587)
            # 65.49.208.148:587
            smtpObj = smtplib.SMTP('65.49.208.148', 587)
            # smtpObj.connect('smtp.office365.com', 587)  # 25 为 SMTP 端口号
            smtpObj.starttls()
            # smtpObj.set_debuglevel(1)# 调试时开启
            smtpObj.login(self.from_mail, self.mail_password)
            smtpObj.sendmail(self.from_mail, to_mail, message.as_string())
            # print("邮件发送成功")

            return True
        except smtplib.SMTPException:
            logger.error("Error: 无法发送邮件")
            return False
        finally:
            smtpObj.quit()

    @gen.coroutine
    def email_send_proxy(self, to_mail, mail_msg, mailtitle, from_title2):
        #to_mail必须是列表['']
        message = MIMEText(mail_msg, 'html', 'utf-8')
        message['From'] = formataddr([from_title2, self.from_mail])
        # message['To'] = ';'.join(to_mail)  # formataddr(["亲", ""])
        message['To'] = formataddr(["dear", to_mail[0]])
        message['Subject'] = mailtitle

        try:
            # smtpObj = smtplib.SMTP('smtp.office365.com', 587)
            smtpObj = smtplib.SMTP('65.49.208.148', 587)
            # smtpObj.connect('smtp.office365.com', 587)  # 25 为 SMTP 端口号
            smtpObj.starttls()
            # smtpObj.set_debuglevel(1)# 调试时开启
            smtpObj.login(self.from_mail, self.mail_password)
            smtpObj.sendmail(self.from_mail, to_mail, message.as_string())
            # print("邮件发送成功")

            return True
        except smtplib.SMTPException:
            logger.error("Error: 无法发送邮件")
            return False
        finally:
            smtpObj.quit()
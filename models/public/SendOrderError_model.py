#coding=utf-8

class OrderError():

   def getErrorText(self, ErrorNum, Language):
       ErrorDist = {
           "0_0": "没有错误返回,0",
           "0_1": "ERR_NO_ERROR,0",
           "1_0": "没有返回错误，但结果未知,1",
           "1_1": "ERR_NO_RESULT,1",
           "2_0": "常见错误,2",
           "2_1": "ERR_COMMON_ERROR,2",
           "3_0": "无效的交易参数,3",
           "3_1": "ERR_INVALID_TRADE_PARAMETERS,3",
           "4_0": "交易服务器正忙,4",
           "4_1": "ERR_SERVER_BUSY,4",
           "5_0": "客户端终端版本太旧,5",
           "5_1": "ERR_OLD_VERSION,5",
           "6_0": "与交易服务器无连接,6",
           "6_1": "ERR_NO_CONNECTION,6",
           "7_0": "权限不足,7",
           "7_1": "ERR_NOT_ENOUGH_RIGHTS,7",
           "8_0": "请求太频繁,8",
           "8_1": "ERR_TOO_FREQUENT_REQUESTS,8",
           "9_0": "交易运作失灵,9",
           "9_1": "ERR_MALFUNCTIONAL_TRADE,9",
           "64_0": "帐户已禁用,64",
           "64_1": "ERR_ACCOUNT_DISABLED,64",
           "65_0": "无效账户,65",
           "65_1": "ERR_INVALID_ACCOUNT,65",
           "128_0": "交易超时,128",
           "128_1": "ERR_TRADE_TIMEOUT,128",
           "129_0": "价格无效,129",
           "129_1": "ERR_INVALID_PRICE,129",
           "130_0": "无效的止损,130",
           "130_1": "ERR_INVALID_STOPS,130",
           "131_0": "无效的交易量,131",
           "131_1": "ERR_INVALID_TRADE_VOLUME,131",
           "132_0": "市场关闭,132",
           "132_1": "ERR_MARKET_CLOSED,132",
           "133_0": "交易被禁用,133",
           "133_1": "ERR_INVALID_STOPS,133",
           "134_0": "没有足够的钱,134",
           "134_1": "ERR_NOT_ENOUGH_MONEY,134",
           "135_0": "价格变更,135",
           "135_1": "ERR_PRICE_CHANGED,135",
           "136_0": "报价超出,136",
           "136_1": "ERR_OFF_QUOTES,136",
           "137_0": "经纪商很忙,137",
           "137_1": "ERR_BROKER_BUSY,137",
           "138_0": "重新报价,138",
           "138_1": "ERR_REQUOTE,138",
           "139_0": "订单已锁定,139",
           "139_1": "ERR_ORDER_LOCKED,139",
           "140_0": "只允许购买订单,140",
           "140_1": "ERR_LONG_POSITIONS_ONLY_ALLOWED,140",
           "141_0": "请求太多,141",
           "141_1": "ERR_TOO_MANY_REQUESTS,141",
           "145_0": "由于订单距离市场太近，修改被拒绝,145",
           "145_1": "ERR_TRADE_MODIFY_DENIED,145",
           "146_0": "贸易环境很忙,146",
           "146_1": "ERR_TRADE_CONTEXT_BUSY,146",
           "147_0": "经纪人拒绝到期,147",
           "147_1": "ERR_TRADE_EXPIRATION_DENIED,147",
           "148_0": "未结订单和挂单数量已达到经纪商设定的限额,148",
           "148_1": "ERR_TRADE_TOO_MANY_ORDERS,148",
           "149_0": "禁用对冲时尝试打开与现有订单相反的订单,149",
           "149_1": "ERR_TRADE_HEDGE_PROHIBITED,149",
           "150_0": "尝试关闭违反FIFO规则的订单,150",
           "150_1": "ERR_TRADE_PROHIBITED_BY_FIFO,150",
           "200_0": "风控预警,200",
           "200_1": "Wind control warning,200",
           "201_0": "净资产小于风控，不再开新仓位,201",
           "201_1": "Net assets less than risk control, no longer open positions,201",
           "202_0": "订单开仓失败,请手动进入后台寻找合适的时机进行一键补单,202",
           "202_1": "Order opening failed, please manually enter the background to find a suitable time to make a one-click replenishment,202",
       }
       try:
           if ErrorDist.get(str(ErrorNum) + "_" + str(Language)) != None:
               return ErrorDist.get(str(ErrorNum) + "_" + str(Language))
           else:
               if Language == 0:
                   return "未知错误," + str(ErrorNum)
               else:
                   return "unknown mistake," + str(ErrorNum)
       except:
           if Language == 0:
               return "未知错误," + str(ErrorNum)
           else:
               return "unknown mistake," + str(ErrorNum)

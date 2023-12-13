// 创建<audio>标签(参数:音频文件路径)
// const audio = new Audio('/static/034writer.mp3');
// const mp3 = new Audio('/static/apple.wav', muted="muted");
// mp3.loop = false;
// mp3.play();

// <audio autoPlay="autoplay" src="http://127.0.0.1:8000/static/apple.wav"></audio>
function audio_play(){
    $('#audioDIV').html('<audio autoPlay="autoplay"><source src="/static/next.wav"'
		+ ' type="audio/wav"/><source src="/static/next.wav" type="audio/mpeg"/></audio>');
}

function master_load() {
    //n
        updata_count();
        updata_strategy_symbol();
        updata_strategy_copy_status();
        updata_strategy_loging();
        updata_strategy_net_ratio();
    }

function Strategy_tag() {
    // 策略列表
    $.ajax({
        type: 'get',
        url: '/user/strategy?fx_type=list',
        data: $("form").serialize(),
        cache: false,
        dataType: "JSON",
        success:  function(re) {
            if (re.reponse_status == 5) {
                var echo_str = "<ul class=\"list-unstyled\">";
                for(i = 0; i < re.s_data.length; i++)
                {
                    echo_str = echo_str + "<li class=\"text-truncate";
                    if(re.s_data[i].uaid.toString() == re.strategy){
                        echo_str = echo_str + " bg-blue";
                    }
                    echo_str = echo_str + "\">\n" +
                        "                                <div><a href=\index?fx_type=strategy_select&form_uaid=";
                    echo_str = echo_str + re.s_data[i].uaid.toString() + " \"><i class=\"zmdi zmdi-account\"></i>&nbsp;&nbsp;";
                    // alert(re.s_data[i].uaid);
                    if (re.s_data[i].ma_name == null) {
                        echo_str = echo_str + re.s_data[i].account;
                    }else {
                        echo_str = echo_str + re.s_data[i].ma_name;
                    }
                    echo_str = echo_str + "</a></div>\n" +
                        "                            </li>";
                }
                echo_str = echo_str + "</ul>";
                // $("#StrategyList").innerHTML(echo_str);
                document.getElementById("StrategyList").innerHTML = echo_str;
                document.getElementById("master_count_all").innerHTML = re.master_count_all.toString();
                document.getElementById("master_count_ok").innerHTML = re.master_count_ok.toString();
                document.getElementById("master_max_num").innerHTML = re.master_max_num.toString();
            }else if (re.reponse_status == -1){
                login_time_out();
            }
            else {
                $("#StrategyList").text("暂无策略账号");
                $("#StrategyList").addClass("text-center");
            }
        },
        error:function(re) {
            showNotification("bg-red","策略列表获取异常，稍后重试","bottom","center",null,null);//错误警示
            login_time_out();
        }
    });
}

function sign_out(){
    // 退出登陆
    $.ajax({
        type: 'POST',
        url: '/index?type=sign_out',
        data: {},
        cache: false,
        dataType: "JSON",
        success:  function(re) {
            if (re.reponse_status == 5) {
                showNotification("bg-blue","成功退出","bottom","center",null,null);//正常提示
                window.location.reload();
                scrollTo(0,0);
            }else {
                showNotification("bg-red","退出异常，稍后重试","bottom","center",null,null);//错误警示
            }
        },
        error:function(re) {
                showNotification("bg-red","退出异常，稍后重试","bottom","center",null,null);//错误警示
            }
    });
}

function updata_count(){
    // 资金统计
    if(fxcns_window_flag == true && fxcns_window_hidden_flag == true) {
        $.ajax({
            type: 'get',
            url: '/user/strategy?fx_type=count',
            data: {},
            cache: false,
            dataType: "JSON",
            success:  function(re) {
                if (re.reponse_status == 5) {
                    document.getElementById("h2_1").innerHTML = number_format(re.echo.out_balance, 2, ".", ",", "floor");
                    document.getElementById("h2_2").innerHTML = number_format(re.echo.out_quity, 2, ".", ",", "floor");
                    document.getElementById("h2_3").innerHTML = number_format(re.echo.out_profit, 2, ".", ",", "floor");
                    document.getElementById("h2_31").innerHTML = number_format(re.echo.out_profit / re.echo.out_balance *100, 2, ".", ",", "floor");
                    document.getElementById("h2_4").innerHTML = number_format(re.echo.out_position_num, 2, ".", ",", "floor");
                    document.getElementById("h2_5").innerHTML = re.echo.out_position_order_num;
                    document.getElementById("h4_1").innerHTML = number_format(re.echo.out_today, 2, ".", ",", "floor");
                    document.getElementById("h4_2").innerHTML = number_format(re.echo.out_week, 2, ".", ",", "floor");
                    document.getElementById("h4_3").innerHTML = number_format(re.echo.out_month, 2, ".", ",", "floor");
                    document.getElementById("h4_31").innerHTML = number_format(re.echo.out_month/re.echo.out_balance*100, 2, ".", ",", "floor");
                    document.getElementById("h4_4").innerHTML = number_format(re.echo.out_year, 2, ".", ",", "floor");
                    document.getElementById("h4_5").innerHTML = number_format(re.echo.out_all, 2, ".", ",", "floor");
                    if ($("#position_order_num").val() != re.echo.out_position_order_num){
                        // alert($("#position_num").val());
                        $("#position_order_num").val(re.echo.out_position_order_num);
                        audio_play();
                    }
                }else if (re.reponse_status == -1){
                    login_time_out();
                }
            },
            error:function(re) {
                    showNotification("bg-red","资金统计,获得数据异常,稍后重试","bottom","center",null,null);//错误警示
                }
        });
        setTimeout(function() {
            updata_count()
        },5*10*1000);
    }else {
        setTimeout(function() {
            updata_count()
        },1300);
    }


}

function updata_strategy_symbol(){
    // 品种分布
    if(fxcns_window_flag == true && fxcns_window_hidden_flag == true) {
        $.ajax({
            type: 'get',
            url: '/user/strategy?fx_type=symbol_count',
            data: {},
            cache: false,
            dataType: "JSON",
            success: function (re) {
                if (re.reponse_status == 5) {
                    pieChart_check("#pie_chart2", re.symbol_list, re.num_list);
                } else if (re.reponse_status == -1) {
                    login_time_out();
                } else {
                    $("#pie_chart2").text("暂无数据");
                    $("#pie_chart2").addClass("text-center");
                }
            },
            error: function (re) {
                showNotification("bg-red", "策略持仓分布,获得数据异常,稍后重试", "bottom", "center", null, null);//错误警示
            }
        });
        setTimeout(function() {
            updata_strategy_symbol()
        },2.1*10*1000);
    }else {
        setTimeout(function() {
            updata_strategy_symbol()
        },1000);
    }

}

function updata_strategy_net_ratio(){
    // 已用/净值
    if(fxcns_window_flag == true && fxcns_window_hidden_flag == true) {
        $.ajax({
            type: 'get',
            url: '/user/strategy?fx_type=net_ratio_list',
            data: {},
            cache: false,
            dataType: "JSON",
            success:  function(re) {
                if (re.reponse_status == 5) {
                    if (re.m_echo.quity <= 0){
                        re.m_echo.quity = 0.01;
                    }
                    // re.m_echo.ma_margin = 900000;
                    var ma_var = re.m_echo.ma_margin/re.m_echo.quity*100;
                    var ma_margin = parseFloat(number_format((re.m_echo.ma_margin), 2));
                    var quity = parseFloat(number_format((re.m_echo.quity-re.m_echo.ma_margin), 2));
                    if (quity < 0){
                        quity = 0;
                    }

                    new Chart(document.getElementById("pie_chart").getContext("2d"), getChartJsStrategy('pie', [ma_margin,quity], ['已用预付款','可用预付款']));
                    for (i=0;i< re.echo.length;i++){
                        // alert("progress_account_" +i.toString());
                        document.getElementById("progress_account_" + (i+1).toString()).innerHTML = re.echo[i].account;
                        editStyle_net_ratio("progress_" + (i+1).toString(), number_format(re.echo[i].position_ratio, 2));
                    }

                    // 警告
                    if (ma_var > 80){
                        // document.getElementById("Warninglabel_3").style.cssText = "background: #fb483a";
                        set_warning("#Warninglabel_3", 1, "_red");
                        audio_play();
                    }else if (ma_var > 50){
                        // document.getElementById("Warninglabel_3").style.cssText = "background: #ff9600";
                        set_warning("#Warninglabel_3", 1, "_gold");
                        audio_play();
                    }else if (ma_var > 30){
                        // document.getElementById("Warninglabel_3").style.cssText = "background: #ff9600";
                        set_warning("#Warninglabel_3", 1, "_gold");
                        audio_play();
                    }else {
                        // document.getElementById("Warninglabel_3").style.cssText = "background: none";
                        set_warning("#Warninglabel_3",0);
                    }
                }else if (re.reponse_status == -1){
                    login_time_out();
                }else{
                    $("#pie_chart").text("暂无数据");
                }
            },
            error:function(re) {
                showNotification("bg-red","已用预付款 : 可用预付款,获得数据异常,请重试","bottom","center",null,null);//错误警示
            }
        });
        setTimeout(function() {
            updata_strategy_net_ratio()
        },3.5*10*1000);
    }else {
        setTimeout(function() {
            updata_strategy_net_ratio()
        },1500);
    }

}

function editStyle_net_ratio(name, num) {
    // 修改比例条的样式
    var styleElement = document.getElementById(name);
    // alert('width: ' + num + '%');
    if (Number(num) >= 80) {
        styleElement.style.cssText = 'width: ' + num + '%;color: #000000';
        styleElement.className = 'progress-bar progress-bar-danger progress-bar-striped';
    } else if (Number(num) >= 50) {
        styleElement.style.cssText = 'width: ' + num + '%;color: #000000';
        styleElement.className = 'progress-bar progress-bar-warning';
    }else {
        styleElement.style.cssText = 'width: ' + num + '%;color: #000000';
        styleElement.className = 'progress-bar';
    }
    styleElement.innerHTML = num + '%';
}

function updata_strategy_loging(){
    // 在线情况
    if(fxcns_window_flag == true && fxcns_window_hidden_flag == true) {
        $.ajax({
            type: 'get',
            url: '/user/strategy?fx_type=loging_count',
            data: {},
            cache: false,
            dataType: "JSON",
            success:  function(re) {
                if (re.reponse_status == 5) {
                    new Chart(document.getElementById("bar_chart_20").getContext("2d"), getChartJsStrategy('bar', re.loging_data, ['在线','授权']));
                    // getMorrisBarChart("m_bar_chart", [{y: '在线数量', a:re.loging_data.actual, b:re.loging_data.expected}], ['a','b'], ['在线','授权']);
                    if (re.loging_data.actual != re.loging_data.expected){
                        set_warning2("#bar_chart_21", 1, "_red");
                        audio_play();
                    }else {
                        set_warning2("#bar_chart_21", 0, "_red");
                    }
                }else if (re.reponse_status == -1){
                    login_time_out();
                }else{
                    $("#bar_chart").text("暂无数据");
                }
            },
            error:function(re) {
                showNotification("bg-red","在线状态,获得数据异常,请重试","bottom","center",null,null);//错误警示
            }
        });
        setTimeout(function() {
            updata_strategy_loging()
        },7*10*1000);
    }
    else {
        setTimeout(function() {
            updata_strategy_loging()
        },2000);
    }

}


function updata_strategy_copy_status(){
    // 跟单完整情况
    if(fxcns_window_flag == true && fxcns_window_hidden_flag == true) {
        $.ajax({
            type: 'get',
            url: '/user/strategy?fx_type=position_count',
            data: {},
            cache: false,
            dataType: "JSON",
            success:  function(re) {
                if (re.reponse_status == 5) {
                    new Chart(document.getElementById("bar_chart_10").getContext("2d"), getChartJsStrategy('bar', re.position_count_data, ['现有持仓','预期持仓']));
                    // getMorrisBarChart("m_bar_chart", [{y: '在线数量', a:re.loging_data.actual, b:re.loging_data.expected}], ['a','b'], ['在线','授权']);
                    if (re.position_count_data.expected != re.position_count_data.actual){
                        set_warning3("#bar_chart_11", 1, "_red");
                    }else{
                        set_warning3("#bar_chart_11", 0, "_red");
                    }
                }else if (re.reponse_status == -1){
                    login_time_out();
                }else{
                    $("#bar_chart").text("暂无数据");
                }
            },
            error:function(re) {
                showNotification("bg-red","跟单完整情况,获得数据异常,请重试","bottom","center",null,null);//错误警示
            }
        });
        setTimeout(function() {
            updata_strategy_copy_status()
        },2*10*1000);
    }
    else {
        setTimeout(function() {
            updata_strategy_copy_status()
        },2000);
    }

}

function set_natural_scheme() {
    // 已经取消
    // document.body.backgroundColor = "#000000";
    // document.body.style.backgroundColor = "#000000";
    document.body.style.color = "#ffffff";
    var  dim_card = document.getElementsByClassName("card");
    for(var i = 0; i < dim_card.length; i++){
            dim_card[i].style.background = "#1c2a3aed";
            // dim_card[i].style = "color: #ffffff";
        }
    var  dim_boby = document.getElementsByClassName("body");
    for(var i = 0; i < dim_boby.length; i++){
            dim_boby[i].style.color = "#ffffff";
        }
    var  dim_navbar = document.getElementsByClassName("navbar");
    for(var i = 0; i < dim_navbar.length; i++){
        dim_navbar[i].style.background = "#000000";
    }
    var  dim_content = document.getElementsByClassName("content");
    for(var i = 0; i < dim_content.length; i++){
        dim_content[i].style.background = "#000000";
    }
    document.getElementById("leftsidebar").style = "background: #1c2a3aed";
    var  dim_sidebar = document.querySelectorAll("#leftsidebar a")
    for(var i = 0; i < dim_sidebar.length; i++){
            dim_sidebar[i].style.color = "#78909c";
        }

        // $('.content').removeClass().addClass('theme-purple section.content red');
}

var time_v = 120;
function set_warning(name, flag, warn_type) {
    // 警告提示
    if (flag == 1){
        if (time_v < 0) {
            time_v = 120;
            return;
        }
        if (time_v % 2 == 0){
            $(name).addClass("warning_border" + warn_type);
        }else {
            $(name).removeClass("warning_border" + warn_type);
        }
        time_v = time_v - 1;
        setTimeout(function() {
                set_warning(name, flag, warn_type)
            },1000);
    }else {
        $(name).removeClass("warning_border_gold");
        $(name).removeClass("warning_border_red");
    }
}

var time_v2 = 120;
function set_warning2(name, flag, warn_type) {
    // 警告提示
    if (flag == 1){
        if (time_v2 < 0) {
            time_v2 = 120;
            return;
        }
        if (time_v2 % 2 == 0){
            $(name).addClass("warning_border" + warn_type);
        }else {
            $(name).removeClass("warning_border" + warn_type);
        }
        time_v2 = time_v2 - 1;
        setTimeout(function() {
                set_warning2(name, flag, warn_type)
            },1000);
    }else {
        $(name).removeClass("warning_border_gold");
        $(name).removeClass("warning_border_red")
    }
}

var time_v3 = 120;
function set_warning3(name, flag, warn_type) {
    // 警告提示
    if (flag == 1){
        if (time_v3 < 0) {
            time_v3 = 120;
            return;
        }
        if (time_v3 % 2 == 0){
            $(name).addClass("warning_border" + warn_type);
        }else {
            $(name).removeClass("warning_border" + warn_type);
        }
        time_v3 = time_v3 - 1;
        setTimeout(function() {
                set_warning3(name, flag, warn_type)
            },1000);
    }else {
        $(name).removeClass("warning_border_gold");
        $(name).removeClass("warning_border_red");
    }
}

function number_format(number, decimals, dec_point, thousands_sep,roundtag) {
  /*
  * 参数说明：
  * number：要格式化的数字
  * decimals：保留几位小数
  * dec_point：小数点符号
  * thousands_sep：千分位符号
  * roundtag:舍入参数，默认 "ceil" 向上取,"floor"向下取,"round" 四舍五入
  * */
    number = (number + '').replace(/[^0-9+-Ee.]/g, '');
    roundtag = roundtag || "floor"; //"ceil","floor","round"
    var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? '' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
        var k = Math.pow(10, prec);
        console.log();
        return '' + parseFloat(Math[roundtag](parseFloat((n * k).toFixed(prec*2))).toFixed(prec*2)) / k;
    };
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (sep != "") {
        var re = /(-?\d+)(\d{3})/;
        while (re.test(s[0])) {
            s[0] = s[0].replace(re, "$1" + sep + "$2");
        }
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

function login_time_out() {
    // 超时退出
    showNotification("bg-red","超时，退出，请重新登陆","bottom","center",null,null);//错误警示
    window.location.href="/index?backurl="+window.location.href;
}

function login_url_time_out(k) {
    // 超时退出
    showNotification("bg-red","超时，退出，请重新登陆","bottom","center",null,null);//错误警示
    window.location.href="/h?k=" + urlkey + "&backurl="+window.location.href;
}



function yyyyy() {
    alert("1");
}


// 进入全屏
function fullScreen() {
    var el = document.documentElement;
    var rfs = el.requestFullScreen || el.webkitRequestFullScreen ||
      el.mozRequestFullScreen || el.msRequestFullScreen;
    if(typeof rfs != "undefined" && rfs) {
        rfs.call(el);
    }
    else if(typeof window.ActiveXObject != "undefined") {
    //for IE，这里其实就是模拟了按下键盘的F11，使浏览器全屏
        var wscript = new ActiveXObject("WScript.Shell");
        if(wscript != null) {
            wscript.SendKeys("{F11}");
        }
    }
    document.getElementById("navClick").href="javascript:exitFullScreen();";
    $("#nav_i").removeClass("zmdi-fullscreen");
    $("#nav_i").addClass("zmdi-window-restore");
}
// 退出全屏
function exitFullScreen() {
    var el = document;
    var cfs = el.cancelFullScreen || el.webkitCancelFullScreen ||
        el.mozCancelFullScreen || el.exitFullScreen;
    if(typeof cfs != "undefined" && cfs) {
        cfs.call(el);
    }
    else if(typeof window.ActiveXObject != "undefined") {
    //for IE，这里和fullScreen相同，模拟按下F11键退出全屏
        var wscript = new ActiveXObject("WScript.Shell");
        if(wscript != null) {
            wscript.SendKeys("{F11}");
        }
    }
    document.getElementById("navClick").href="javascript:fullScreen();";
    $("#nav_i").removeClass("zmdi-window-restore");
    $("#nav_i").addClass("zmdi-fullscreen");
}

// 设置语言的cookie
function set_lang(lang) {
    $.ajax({
        type: 'get',
        url: '/user/lang?lang=' + lang,
        data: {},
        cache: false,
        dataType: "JSON",
        success:  function(re) {
            if (re.reponse_status == 5) {
                window.location.reload();
                scrollTo(0,0);
            }else{
                $("#bar_chart").text("切换失败，稍候重试！");
            }
        },
        error:function(re) {
            showNotification("bg-red","切换失败,请重试","bottom","center",null,null);//错误警示
        }
    });
}
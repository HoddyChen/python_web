function theme_load() {
    // 主题导入
    $.ajaxSetup({
        cache: false
    });
    checkCookie();
    skinChanger_setCookie();
}

function skinChanger_setCookie() {
    // 修改主题时，设置cookie
    $(".right-sidebar .choose-skin li").on("click", function () {
        var a = $("body"), b = $(this), c = $(".right-sidebar .choose-skin li.active").data("theme");
        //  a = $("body"),    c = $(".right-sidebar .choose-skin li.active").data("theme");
        $(".right-sidebar .choose-skin li").removeClass("active"), a.removeClass("theme-" + c), b.addClass("active"), a.addClass("theme-" + b.data("theme"))
        setCookie("choose-skin", $(this).data("theme"), 100000);
    })
    // 修改主题背景色时，设置cookie
    $(".theme-light-dark .t-light").on("click", function () {
        // $("body").removeClass("menu_dark");
        setCookie("light-dark", "t-light", 100000);
    }), $(".theme-light-dark .t-dark").on("click", function () {
        // $("body").addClass("menu_dark");
        setCookie("light-dark", "t-dark", 100000);
    })
}

function skinChanger_edit(choose_skin) {
    // 更换主题色
    var a = $("body"), b = $(".right-sidebar .choose-skin li"),
        c = $(".right-sidebar .choose-skin li.active").data("theme");
    a.removeClass("theme-" + c);
    $(".right-sidebar .choose-skin li.active").removeClass("active");
    a.addClass("theme-" + choose_skin);
    $("#id_" + choose_skin).addClass("active");
}

function getCookie(cname) {
    // 获取cookie
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

function setCookie(cname, cvalue, exdays) {
    // 设置cookie
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    // var expires = "expires="+d.toGMTString();
    var expires = "path=/;expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
    // alert(cname + ",ok, " + cvalue);
}

function checkCookie() {
    // 查主题cookie
    var light_dark = getCookie("light-dark");
    if (light_dark == "t-dark") {
        $("body").addClass("menu_dark");
    } else {
        $("body").removeClass("menu_dark");
    }
    var choose_skin = getCookie("choose-skin");
    // alert(light_dark+","+ choose_skin);
    if (choose_skin != "") {
        skinChanger_edit(choose_skin);
    }

}

//复制按钮
function chick_copy() {
    //使用函数
    var val = $("#key_val").val();
    Clipboard.copy(val);
}

//定义函数。//复制按钮
window.Clipboard = (function (window, document, navigator) {
    var textArea,
        copy;

    // 判断是不是ios端
    function isOS() {
        return navigator.userAgent.match(/ipad|iphone/i);
    }

    //创建文本元素
    function createTextArea(text) {
        textArea = document.createElement('textArea');
        textArea.value = text;
        document.body.appendChild(textArea);
    }

    //选择内容
    function selectText() {
        var range,
            selection;

        if (isOS()) {
            range = document.createRange();
            range.selectNodeContents(textArea);
            selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            textArea.setSelectionRange(0, 999999);
        } else {
            textArea.select();
        }
    }

//复制到剪贴板
    function copyToClipboard() {
        try {
            if (document.execCommand("Copy")) {
                showNotification("bg-blue", "复制成功！", "bottom", "center", null, null);
            } else {
                showNotification("bg-red", "复制失败！请手动复制", "bottom", "center", null, null);
            }
        } catch (err) {
            showNotification("bg-red", "复制错误！请手动复制", "bottom", "center", null, null);
        }
        document.body.removeChild(textArea);
    }

    copy = function (text) {
        createTextArea(text);
        selectText();
        copyToClipboard();
    };

    return {
        copy: copy
    };
})(window, document, navigator);


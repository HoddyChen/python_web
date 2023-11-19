function getChartJsStrategy(type, datas, tags) {
    var config = null;
    if (type === 'line') {
        config = {
            type: 'line',
            data: {
                labels: ["January", "February", "March", "April", "May", "June", "July"],
                datasets: [{
                    label: "My First dataset",
                    data: [28, 58, 39, 45, 30, 55, 68],
                    borderColor: 'rgba(241,95,121, 0.2)',
                    backgroundColor: 'rgba(241,95,121, 0.5)',
                    pointBorderColor: 'rgba(241,95,121, 0.3)',
                    pointBackgroundColor: 'rgba(241,95,121, 0.2)',
                    pointBorderWidth: 1
                }, {
                    label: "My Second dataset",
                    data: [40, 28, 50, 48, 63, 39, 41],
                    borderColor: 'rgba(140,147,154, 0.2)',
                    backgroundColor: 'rgba(140,147,154, 0.2)',
                    pointBorderColor: 'rgba(140,147,154, 0)',
                    pointBackgroundColor: 'rgba(140,147,154, 0.9)',
                    pointBorderWidth: 1
                }]
            },
            options: {
                responsive: true,
                legend: false,

            }
        }
    }
    else if (type === 'bar') {
        //柱图
        config = {
            type: 'bar',
            data: {
                labels: [' '],
                datasets: [{
                    label: tags[0],
                    data: [datas['actual'],0],
                    backgroundColor: '#26c6da',
                    strokeColor: "rgba(255,118,118,0.1)",
                }, {
                        label: tags[1],
                        data: [datas['expected'],0],
                        backgroundColor: '#8a8a8b',
                        strokeColor: "rgba(255,118,118,0.1)",
                    }]
            },
            options: {
                responsive: true,
                legend: true
            }
        }
    }
    else if (type === 'radar') {
        config = {
            type: 'radar',
            data: {
                labels: ["January", "February", "March", "April", "May", "June", "July"],
                datasets: [{
                    label: "My First dataset",
                    data: [65, 25, 90, 81, 56, 55, 40],
                    borderColor: 'rgba(241,95,121, 0.8)',
                    backgroundColor: 'rgba(241,95,121, 0.5)',
                    pointBorderColor: 'rgba(241,95,121, 0)',
                    pointBackgroundColor: 'rgba(241,95,121, 0.8)',
                    pointBorderWidth: 1
                }, {
                        label: "My Second dataset",
                        data: [72, 48, 40, 19, 96, 27, 100],
                        borderColor: 'rgba(140,147,154, 0.8)',
                        backgroundColor: 'rgba(140,147,154, 0.5)',
                        pointBorderColor: 'rgba(140,147,154, 0)',
                        pointBackgroundColor: 'rgba(140,147,154, 0.8)',
                        pointBorderWidth: 1
                    }]
            },
            options: {
                responsive: true,
                legend: false
            }
        }
    }
    else if (type === 'pie') {
        config = {
            type: 'pie',
            data: {
                datasets: [{
                    data: datas,
                    backgroundColor: [
                        "#cce6eb",
                        "#65a0eb",
                    ],
                }],
                labels: tags
            },
            options: {
                responsive: true,
                legend: true
            }
        }
    }
    return config;
}
// 圆饼图
function pieChart_check(pieChart_name, label_name, pieChartDatas) {
    var pieChartData = [],
        pieChartSeries = pieChartDatas.length;
    // var pieChartColors = ['#EBDCBF', '#CCE6EB', '#65A0EB', '#EF929A', '#9ec38b', "#607D8B","#9e9499"];
    var pieChartColors = ['#7299BF','#BF66A7','#72BFB0','#9E72BF','#6ABF8C','#BF6474','#BFBD6A','#BF8A5D'];
    // var pieChartDatas = [45, 17, 28, 10];

    for (var i = 0; i < pieChartSeries; i++) {
        pieChartData[i] = {
            label: label_name[i] + " " + pieChartDatas[i],
            data: pieChartDatas[i],
            color: pieChartColors[i]
        }
    }
    $.plot(pieChart_name, pieChartData, {
        series: {
            pie: {
                show: true,
                radius: 1,
                label: {
                    show: true,
                    radius: 3 / 4,
                    formatter: labelFormatter,
                    background: {
                        opacity: 0.5
                    }
                }
            }
        },
        legend: {
            show: false
        }
    });

}
function labelFormatter(label, series) {
    // alert(series);
    return '<div style="font-size:8pt; text-align:center; padding:2px; color:white;">' + label + '<br/>' + Math.round(series.percent) + '%</div>';
}
var randomScalingFactor = function() {
    return Math.round(Math.random() * 100);
};

var chartColors = window.chartColors;
var color = Chart.helpers.color;
var config = {
    data: {
        datasets: [{
            data: [
                70,
                1,
            ],
            backgroundColor: [
                color(chartColors.yellow).alpha(0.5).rgbString(),
                color(chartColors.blue).alpha(0.5).rgbString(),
            ],
            label: 'My dataset' // for legend
        }],
        labels: [
            "实际持仓数",
            "应有持仓数"
        ]
    },
    options: {
        responsive: true,
        legend: {
            position: 'right',
        },
        title: {
            display: true,
            text: 'Chart.js Polar Area Chart'
        },
        scale: {
            ticks: {
                beginAtZero: true
            },
            reverse: false
        },
        animation: {
            animateRotate: false,
            animateScale: true
        }
    }
};

// 圆图及引用方法
//         $("#knob_1").attr("value",90);
//         knob_check("#knob_1");
function knob_check(knob_name) {
  // $('.knob').knob({
  $(knob_name).knob({
        draw: function () {
            // "tron" case
            if (this.$.data('skin') == 'tron') {

                var a = this.angle(this.cv)  // Angle
                    , sa = this.startAngle          // Previous start angle
                    , sat = this.startAngle         // Start angle
                    , ea                            // Previous end angle
                    , eat = sat + a                 // End angle
                    , r = true;

                this.g.lineWidth = this.lineWidth;

                this.o.cursor
                    && (sat = eat - 0.3)
                    && (eat = eat + 0.3);

                if (this.o.displayPrevious) {
                    ea = this.startAngle + this.angle(this.value);
                    this.o.cursor
                        && (sa = ea - 0.3)
                        && (ea = ea + 0.3);
                    this.g.beginPath();
                    this.g.strokeStyle = this.previousColor;
                    this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sa, ea, false);
                    this.g.stroke();
                }

                this.g.beginPath();
                this.g.strokeStyle = r ? this.o.fgColor : this.fgColor;
                this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sat, eat, false);
                this.g.stroke();

                this.g.lineWidth = 2;
                this.g.beginPath();
                this.g.strokeStyle = this.o.fgColor;
                this.g.arc(this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
                this.g.stroke();

                return false;
            }
        }
    });
}

//柱图
function getMorrisBarChart(name, datas, xkey, ykeys, tags) {
    Morris.Bar({
        element: name,//'m_bar_chart',
        data: datas, //[{y: '2011',a: 80,b: 56,c: 89}, {y: '2017',a: 87,b: 88,c: 36}],
        xkey: xkey,
        ykeys: ykeys,//['a', 'b', 'c'],
        labels: tags,//['A', 'B', 'C'],
        barColors: ['#26c6da'],
        hideHover: 'auto',
        gridLineColor: '#eef0f2',
        resize: false
    });
}

// 曲线图 CHART
function getMorrisLineChart(name, datas, xkey, ykeys, tags) {
    var line = new Morris.Line({
        element: name,
        resize: true,
        data: datas,
        xkey: xkey,
        ykeys: ykeys,
        labels: tags,
        lineColors: ['#034aff','#6C6C6C','#AE0000','#00AEAE','#D200D2','#8600FF','#00AEAE','#F00078'],
        lineWidth: 3,
        //pointStrokeColors:"#034aff",
        pointSize: 1,
        hideHover: 'auto',
        parseTime: false
    });
}

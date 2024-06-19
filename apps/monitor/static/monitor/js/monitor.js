// 判断一个数字的奇偶性
function isEvenOrOdd(number) {
    if (number % 2 === 0) {
        return "even";
    } else {
        return "odd";
    }
}

function get_servers(csrf, api) {
    $.ajaxSetup({
        data: {
            csrfmiddlewaretoken: csrf
        }
    });
    $.ajax({
        type: 'get',
        url: api,
        dataType: 'json',
        success: function (ret) {
            if (ret.code === 0) {
                let table_body = '';
                for (let i = 0; i < ret.data['list'].length; i++) {
                    const item = ret.data['list'][i];
                    const {
                        status,
                        name,
                        uptime,
                        system,
                        cpu_cores,
                        cpu_model,
                        cpu,
                        load_1,
                        load_5,
                        load_15,
                        memory_total,
                        memory_used,
                        swap_total,
                        swap_used,
                        hdd_total,
                        hdd_used,
                        network_in,
                        network_out,
                        process,
                        thread,
                        tcp,
                        udp,
                        memory,
                        hdd,
                        version,
                        date,
                        interval,
                        client_version,
                        alarm
                    } = item;
                    let sys_icon;
                    const static_path = '/static/monitor/img';
                    switch (true) {
                        case system.toLowerCase().includes("darwin"):
                            sys_icon = `<img alt="darwin" src="${static_path}/mac-os.svg">macOS`
                            break
                        case system.toLowerCase().includes("windows"):
                            sys_icon = `<img alt="windows" src="${static_path}/windows.svg">Windows`
                            break
                        case system.toLowerCase().includes("ubuntu"):
                            sys_icon = `<img alt="ubuntu" src="${static_path}/ubuntu.svg">Ubuntu`
                            break
                        case system.toLowerCase().includes("centos"):
                            sys_icon = `<img alt="centos" src="${static_path}/centos.svg">CentOS`
                            break
                        case system.toLowerCase().includes("debian"):
                            sys_icon = `<img alt="debian" src="${static_path}/debian.svg">Debian`
                            break
                        case system.toLowerCase().includes("redhat"):
                            sys_icon = `<img alt="redhat" src="${static_path}/redhat.svg">Redhat`
                            break
                        case system.toLowerCase().includes("dsm"):
                            sys_icon = `<img alt="DSM" src="${static_path}/DSM.svg">DSM`
                            break
                        case system.toLowerCase().includes("linux"):
                            sys_icon = `<img alt="linux" src="${static_path}/linux.svg">Linux`
                            break
                        default:
                            sys_icon = 'Unknown'

                    }
                    let status_bg = 'bg-success';
                    let is_show = '';
                    let cpu_bg = 'bg-success', memory_bg = 'bg-success', hdd_bg = 'bg-success';
                    // 根据状态使用不同的颜色的点
                    if (status !== "online") {
                        status_bg = 'bg-danger'
                    }
                    // 保留原来的展开状态
                    if ($('#more-info-' + i).hasClass('show')) {
                        is_show = 'show'
                    }
                    // 判断进度条颜色
                    if (70 < cpu && cpu < 90) {
                        cpu_bg = 'bg-warning'
                    } else if (cpu >= 90) {
                        cpu_bg = 'bg-danger'
                    }
                    if (70 < memory && memory < 90) {
                        memory_bg = 'bg-warning'
                    } else if (memory >= 90) {
                        memory_bg = 'bg-danger'
                    }
                    if (70 < hdd && hdd < 90) {
                        hdd_bg = 'bg-warning'
                    } else if (hdd >= 90) {
                        hdd_bg = 'bg-danger'
                    }
                    const item_html = `<tr data-toggle="collapse" data-target="#more-info-${i}" class="accordion-toggle ${isEvenOrOdd(i)}" aria-expanded="true">` +
                        `<td><div class="status-container"><div class="status-icon ${status_bg}"></div></div></td>` +
                        `<td>${name}</td>` +
                        `<td class="monitor-none">${sys_icon}</td>` +
                        `<td>${uptime}</td>` +
                        `<td class="monitor-none">${load_1} | ${load_5} | ${load_15}</td>` +
                        `<td class="monitor-none">${network_out} | ${network_in}</td>` +
                        `<td><div class="progress"><div class="progress-bar ${cpu_bg}" role="progressbar" style="width: ${cpu}%;" aria-valuenow="${cpu}" aria-valuemin="0" aria-valuemax="100">${cpu}%</div></div></td>` +
                        `<td><div class="progress"><div class="progress-bar ${memory_bg}" role="progressbar" style="width: ${memory}%;" aria-valuenow="${memory}" aria-valuemin="0" aria-valuemax="100">${memory}%</div></div></td>` +
                        `<td><div class="progress"><div class="progress-bar ${hdd_bg}" role="progressbar" style="width: ${hdd}%;" aria-valuenow="${hdd}" aria-valuemin="0" aria-valuemax="100">${hdd}%</div></div></td>` +
                        `<td class="monitor-none">${version}</td>` +
                        '</tr>';
                    const item_even_html = `<tr class="expandRow ${isEvenOrOdd(i)}"><td colspan="16"><div class="accordian-body collapse ${is_show}" id="more-info-${i}" aria-expanded="true">` +
                        `<div>系统版本: ${system}</div>` +
                        `<div>CPU型号: ${cpu_model}</div>` +
                        `<div>CPU核心数: ${cpu_cores}</div>` +
                        `<div>内存: ${memory_used} / ${memory_total}</div>` +
                        `<div>Swap: ${swap_used} / ${swap_total}</div>` +
                        `<div>硬盘: ${hdd_used} / ${hdd_total}</div>` +
                        `<div>TCP|UDP: ${tcp} | ${udp}</div>` +
                        `<div>进程数|线程数: ${process} | ${thread}</div>` +
                        `<div class="monitor-big-none">负载: ${load_1} | ${load_5} | ${load_15}</div>` +
                        `<div class="monitor-big-none">网络↑|↓: ${network_out} | ${network_in}</div>` +
                        `<div class="monitor-big-none">服务版本: ${version}</div>` +
                        `<div>离线告警: ${alarm}</div>` +
                        `<div>上报频率: ${interval} 秒</div>` +
                        `<div>上报时间: ${date}</div>` +
                        `<div>客户端版本: ${client_version}</div>` +
                        '</div></td></tr>'
                    table_body += item_html + item_even_html;
                }
                $('#servers').html(table_body);
            }
        },
    })
}
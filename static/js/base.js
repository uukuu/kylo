function aside_left_profile() {
    document.getElementById("aside-btn-profile").style.borderBottom = "1px solid #ebf0fa";
    document.getElementById("aside-btn-tool").style.borderBottom = "none";
    document.getElementById("aside-profile").style.display = "block";
    document.getElementById("aside-tool").style.display = "none";
}
function aside_left_tool() {
    document.getElementById("aside-btn-tool").style.borderBottom = "1px solid #ebf0fa";
    document.getElementById("aside-btn-profile").style.borderBottom = "none";
    document.getElementById("aside-profile").style.display = "none";
    document.getElementById("aside-tool").style.display = "block";
}


function aside_left_profile2() {
    document.getElementById("aside-btn-profile2").style.borderBottom = "1px solid #ebf0fa";
    document.getElementById("aside-profile2").style.display = "block";
    document.getElementById("aside-btn-tool2").style.borderBottom = "none";
    document.getElementById("aside-tool2").style.display = "none";
    document.getElementById("aside-btn-menu2").style.borderBottom = "none";
    document.getElementById("aside-menu2").style.display = "none";
    document.getElementById("aside-menu2").style.overflowY = "hidden";
}
function aside_left_tool2() {
    document.getElementById("aside-btn-tool2").style.borderBottom = "1px solid #ebf0fa";
    document.getElementById("aside-tool2").style.display = "block";
    document.getElementById("aside-btn-profile2").style.borderBottom = "none";
    document.getElementById("aside-profile2").style.display = "none";
    document.getElementById("aside-btn-menu2").style.borderBottom = "none";
    document.getElementById("aside-menu2").style.display = "none";
    document.getElementById("aside-menu2").style.overflowY = "hidden";
}
function aside_left_menu2() {
    document.getElementById("aside-btn-menu2").style.borderBottom = "1px solid #ebf0fa";
    document.getElementById("aside-menu2").style.display = "block";
    document.getElementById("aside-menu2").style.overflowY = "auto";
    document.getElementById("aside-btn-profile2").style.borderBottom = "none";
    document.getElementById("aside-profile2").style.display = "none";
    document.getElementById("aside-btn-tool2").style.borderBottom = "none";
    document.getElementById("aside-tool2").style.display = "none";

}



// function get_background()
// {
//     var H=window.innerHeight;
//     console.log(H)
//     H+="px";
//     var back_img=document.getElementById("background-image");
//     if(back_img.style.height<=H)
//     {
//         back_img.style.height=H;
//     }
// }

window.onload = function () {
    var h1 = document.getElementById("post-article").clientHeight;
    var h3 = document.getElementsByClassName("content")[0].clientHeight;
    var h2 = document.getElementById("sidebar").clientHeight;
    var mx = Math.max(h1, h2, h3);
    document.getElementById("mainuuku").style.height = mx + "px";
    document.getElementById("sidebar").style.height = mx + "px";

}

// 确保在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.highlight').forEach(block => {
        // 创建切换按钮
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'code-toggle';
        toggleBtn.textContent = '展开代码';
        block.appendChild(toggleBtn);

        // 添加点击事件
        toggleBtn.addEventListener('click', () => {
            block.classList.toggle('expanded');
            toggleBtn.textContent = block.classList.contains('expanded') ? '收起代码' : '展开代码';
        });
    });

    // 处理目录点击事件
    document.querySelectorAll('.toc-item').forEach(item => {
        // 为有子项的目录项添加箭头图标
        var nextItem = item.nextElementSibling;
        if (nextItem && nextItem.classList.contains('toc-item') &&
            parseInt(nextItem.classList[1].split('-')[2]) >
            parseInt(item.classList[1].split('-')[2])) {
            item.classList.add('has-children');
            const arrow = document.createElement('span');
            arrow.className = 'toc-arrow';
            arrow.innerHTML = '▸';
            item.insertBefore(arrow, item.firstChild);
        }
        var preItem = item.previousElementSibling;
        var min_level = parseInt(item.classList[1].split('-')[2]);
        while (preItem) {
            if (parseInt(preItem.classList[1].split('-')[2]) < min_level) {
                min_level = parseInt(preItem.classList[1].split('-')[2]);
            }
            preItem = preItem.previousElementSibling;
        }
        if (parseInt(item.classList[1].split('-')[2]) > min_level) {
            item.style.display = 'none';
        }
        // 添加点击事件

        item.addEventListener('click', function (e) {
            // 防止点击链接时触发折叠
            if (e.target.tagName === 'A') return;

            var nextItem = this.nextElementSibling;
            if (nextItem && nextItem.classList.contains('toc-item') &&
                parseInt(nextItem.classList[1].split('-')[2]) >
                parseInt(this.classList[1].split('-')[2])) {

                // 切换展开/收起状态
                if (this.classList.contains('expanded')) {
                    this.classList.remove('expanded');
                    this.querySelector('.toc-arrow').innerHTML = '▸';
                    while (nextItem &&
                        parseInt(nextItem.classList[1].split('-')[2]) >
                        parseInt(this.classList[1].split('-')[2])) {

                        nextItem.style.display = 'none';
                        nextItem.classList.remove('expanded');
                        nextItem = nextItem.nextElementSibling;
                    }
                } else {
                    this.classList.add('expanded');
                    this.querySelector('.toc-arrow').innerHTML = '▾';
                    var min_level = parseInt(nextItem.classList[1].split('-')[2]);
                    while (nextItem &&
                        parseInt(nextItem.classList[1].split('-')[2]) >
                        parseInt(this.classList[1].split('-')[2])) {
                        if (parseInt(nextItem.classList[1].split('-')[2]) <= min_level) {
                            nextItem.style.display = 'block';
                            min_level = parseInt(nextItem.classList[1].split('-')[2]);
                        }
                        nextItem = nextItem.nextElementSibling;
                    }
                }
            }
        });
    });

    // 默认展开一级目录
    // document.querySelectorAll('.toc-level-1').forEach(item => {
    //     item.classList.add('expanded');
    //     const arrow = item.querySelector('.toc-arrow');
    //     if (arrow) arrow.innerHTML = '▾';
    // });

    // 添加主题切换按钮功能
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });

    // PDF目录跳转
    document.querySelectorAll('.pdf-toc a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const pageNumber = this.getAttribute('href').replace('#page', '');
            const iframe = document.querySelector('.pdf-viewer iframe');
            if (iframe) {
                iframe.contentWindow.PDFViewerApplication.page = parseInt(pageNumber);
            }
        });
    });
});

// 获取主题设置
function getTheme() {
    // 检查localStorage
    if (localStorage.getItem('theme')) {
        return localStorage.getItem('theme');
    }
    // 检查系统偏好
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function sendMessage(message) {
    const iframe = document.querySelector("iframe.giscus-frame");
    if (!iframe || !iframe.contentWindow) return;
    iframe.contentWindow.postMessage({ giscus: message }, "https://giscus.app");
  }

// 设置主题
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    sendMessage({
        setConfig: { theme: theme == "dark" ? "dark_dimmed" : "light" },
    });
}
// 初始化主题

function initTheme() {
    // const currentTheme = getTheme();
    setTheme('dark');

    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }

    });
}


// 在DOM加载完成后初始化主题
document.addEventListener('DOMContentLoaded', initTheme);


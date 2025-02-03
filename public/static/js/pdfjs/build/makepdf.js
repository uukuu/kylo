pdfjsLib.GlobalWorkerOptions.workerSrc = "../../../../js/pdfjs/build/pdf.worker.js";
//创建canvas元素
function createPdfContainer(id, className) {
    var pdfContainer = document.getElementById('canvas');
    var canvasNew = document.createElement('canvas');
    canvasNew.id = id;
    canvasNew.className = className;
    pdfContainer.appendChild(canvasNew);
};

//建议给定pdf宽度
function renderPDF(pdf, i, id) {
    pdf.getPage(i).then(function (page) {
        var scale = 2; //scale的值是canvas的渲染尺寸，影响清晰度
        var viewport = page.getViewport({
            scale: scale
        });
        //
        //  准备用于渲染的 canvas 元素
        //
        var canvas = document.getElementById(id);
        var context = canvas.getContext('2d');
        CSS_UNITS = 1;
        canvas.height = Math.floor(viewport.height * CSS_UNITS);
        canvas.width = Math.floor(viewport.width * CSS_UNITS);
        //
        // 将 PDF 页面渲染到 canvas 上下文中
        //
        var renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        page.render(renderContext);
    });
};

//创建和pdf页数等同的canvas数
function createSeriesCanvas(num, template) {
    var id = '';
    for (var j = 1; j <= num; j++) {
        id = template + j;
        createPdfContainer(id, 'pdfClass');
    }
}

//读取pdf文件，并加载到页面中
async function loadPDF(fileURL) {
    await pdfjsLib.getDocument(fileURL).promise.then(function (pdf) {
        //用 promise 获取页面
        var id = '';
        var idTemplate = 'cw-pdf-';
        var pageNum = pdf.numPages; //pdf文件总页数
        //根据页码创建画布
        createSeriesCanvas(pageNum, idTemplate);
        $("#canvas canvas").css("width", "100%"); //canvas展示宽度
        //将pdf渲染到画布上去
        for (var i = 1; i <= pageNum; i++) {
            id = idTemplate + i;
            renderPDF(pdf, i, id);
        }
    });
    await get_height()
}


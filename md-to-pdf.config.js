module.exports = {
    stylesheet: ["pdf-style.css"],
    pdf_options: {
        format: "A4",
        margin: {
            top: "24mm",
            bottom: "22mm",
            left: "18mm",
            right: "18mm"
        },
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: `
            <div style="font-size:8pt;color:#888;width:100%;padding:0 18mm;display:flex;justify-content:space-between;">
                <span>FastAPI 한국어 가이드</span>
                <span>2026-04</span>
            </div>
        `,
        footerTemplate: `
            <div style="font-size:8pt;color:#888;width:100%;text-align:center;">
                <span class="pageNumber"></span> / <span class="totalPages"></span>
            </div>
        `
    },
    launch_options: {
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
    },
    document_title: "FastAPI 한국어 가이드"
};

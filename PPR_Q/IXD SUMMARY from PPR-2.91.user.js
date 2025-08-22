// ==UserScript==
// @name         IXD SUMMARY from PPR
// @namespace    http://tampermonkey.net/
// @version      2.91
// @description  Get main data from PPR in a summary table
// @author       @gerpaes
// @icon         https://drive-render.corp.amazon.com/view/gerpaes@/ECFT_logo.png
// @match        https://fclm-portal.amazon.com/reports/processPathRollup?*
// @updateURL    https://axzile.corp.amazon.com/-/carthamus/download_script/ixd-summary-from-ppr.user.js
// @downloadURL  https://axzile.corp.amazon.com/-/carthamus/download_script/ixd-summary-from-ppr.user.js
// @require     https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js
// @grant        GM_setValue
// @grant        GM_setClipboard
// @grant        GM_getValue
// @grant        GM_xmlhttpRequest
// @grant        GM_addElement
// @grant        unsafeWindow
// @grant        window.focus
// @grant        window.close
// @grant        GM_openInTab
// @connect fclm-portal.amazon.com
// @connect axzile.corp.amazon.com
// @connect drive-render.corp.amazon.com
// @connect console.harmony.a2z.com
// @connect cdnjs.cloudflare.com
// ==/UserScript==

// @run-at       document-start

async function updatecheck(forceCheck = false) {
console.log('checking for new version');
const lastchecktime = GM_getValue('lastupdatecheckvret', 0);
const tnow = Date.now();
const fiveh = 5 * 60 * 60 * 1000; // 5 ore in millisecondi

if (forceCheck || tnow - lastchecktime >= fiveh) {
    return new Promise((resolve, reject) => {
        GM_xmlhttpRequest({
            method: 'GET',
            url: 'https://axzile.corp.amazon.com/-/carthamus/download_script/ixd-summary-from-ppr.user.js',
            onload: function (response) {
                const versionMatch = response.responseText.match(/@version\s+([\d.]+)/);
                const newversion = versionMatch ? versionMatch[1] : '0';
                const currentversion = GM_info.script.version;

                // Converti le versioni in numeri per confronto preciso
                const newVersionNum = Number(newversion.replace('.', ''));
                const currentVersionNum = Number(currentversion.replace('.', ''));

                if (newVersionNum > currentVersionNum) {
                    GM_openInTab('https://axzile.corp.amazon.com/-/carthamus/download_script/ixd-summary-from-ppr.user.js');
                    reject(new Error('New version available'));
                } else {
                    console.log('No new version available');
                    resolve();
                }

                GM_setValue('lastupdatecheckvret', tnow);
            }
        });
    });
}
return Promise.resolve();

}

(function () {
// Función para obtener los parámetros de la página principal

const fontAwesome = document.createElement('link');
fontAwesome.rel = 'stylesheet';
fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
document.head.appendChild(fontAwesome);

// Añadir estilos para tooltips de link
const tooltipStyles = document.createElement('style');
tooltipStyles.textContent = `

.tooltip-trigger {
position: relative;
}

.tooltip-trigger:hover::after {
content: 'Click to check details';
position: absolute;
background-color: rgba(0, 0, 0, 0.8);
color: white;
padding: 4px 8px;
border-radius: 4px;
font-size: 11px;
white-space: nowrap;
z-index: 1000;
top: 50%;
left: calc(100% + 10px);  /* 100% del ancho del elemento + 10px de espacio /
transform: translateY(-50%);  / Centra verticalmente */
animation: fadeInOut 2s forwards;
}

@keyframes fadeInOut {
0% { opacity: 0; }
10% { opacity: 1; }
90% { opacity: 1; }
100% { opacity: 0; }
}
`;
document.head.appendChild(tooltipStyles);

function getCurrentPageParameters() {
const params = new URLSearchParams(window.location.search);
const spanType = params.get("spanType") || "Intraday";

let startDate = "";
let endDate = "";
let startHour = params.get("startHourIntraday") || "0";
let startMinute = params.get("startMinuteIntraday") || "0";
let endHour = params.get("endHourIntraday") || "0";
let endMinute = params.get("endMinuteIntraday") || "0";

switch (spanType) {
    case "Day":
        startDate = params.get("startDateDay") || "";
        endDate = startDate;
        startHour = "0";
        startMinute = "0";
        endHour = "0";
        endMinute = "0";
        break;
    case "Week":
        startDate = params.get("startDateWeek") || "";
        endDate = "";
        startHour = "0";
        startMinute = "0";
        endHour = "0";
        endMinute = "0";
        break;
    case "Month":
        startDate = params.get("startDateMonth") || "";
        endDate = "";
        startHour = "0";
        startMinute = "0";
        endHour = "0";
        endMinute = "0";
        break;
    case "Intraday":
    default:
        startDate = params.get("startDateIntraday") || "";
        endDate = params.get("endDateIntraday") || "";
        break;
}

return {
    warehouseId: params.get("warehouseId") || "",
    startDate: startDate,
    endDate: endDate,
    startHour: startHour,
    startMinute: startMinute,
    endHour: endHour,
    endMinute: endMinute,
    spanType: spanType
};

}

// Función para extraer y formatear los valores numéricos de un selector dado
function extractNumericValue(selector) {
const element = document.querySelector(selector);
if (!element) return null;

const text = element.textContent.trim();

// Detecta si el separador de miles es una coma, un punto o un espacio
const hasDot = /\d+\.\d{3}/.test(text);
const hasComma = /\d+,\d{3}/.test(text);
const hasSpace = /\d+\s\d{3}/.test(text);

let cleanedText = text;

if (hasDot) {
    // Si hay puntos como separadores de miles, elimínalos y usa la coma como decimal
    cleanedText = text.replace(/\./g, '').replace(',', '.');
} else if (hasComma) {
    // Si hay comas como separadores de miles, simplemente elimínalas
    cleanedText = text.replace(/,/g, '');
} else if (hasSpace) {
    // Si hay espacios como separadores de miles, elimínalos
    cleanedText = text.replace(/\s/g, '');
}

// Intenta convertir a número
const number = parseFloat(cleanedText);

// Verifica si el resultado es un número válido
return isNaN(number) ? null : number;

}

// Función para obtener el valor o "N/A" si el valor es nulo o undefined
function getValueOrNA(element) {
return element ? element.textContent.trim() : "N/A";
}

// Función para crear y mostrar la tabla con los resultados
function createResultTable(
LPupc, ibTotal, inbound, inboundhours, inboundrate, transin, transinhours, transinrate, ERvol, ERSvol, ERMvol, ERLvol, ERhours, ERrate, prepvol, prepSvol, prepMvol, prepLvol, prephours, preprate, daTotal, totalHours, ibHours, daHours, palletReceive, eachTotal, caseTotal, eachColor, sortVolume, sortVolumesmall, sortShare, pidUpc, prEditorUpc, arosUpc, pidcases, preditorcases, aroscases, pidvol, preditorvol, arosvol, preditorhours, preditorrate, autore, autorepallet, ibRate, daRate,
palletTIunits, palletTIvol, palletTIhours, palletTIrate, palletTIcases, palletunits, palletvol, pallethours, palletrate, palletcases, LPpallet, RDpalletunits, RDpalletvol, RDpalletcases, IBpalletunits, IBpalletvol, IBpalletcases,
FLThours, FLvol, FLrate, flcasecase, fltotecase, FLCycleTime, MPvol, MPcase, MPhours, MPrate, TPvol, TPtote, TPhours, TPrate, RPvol, RPtote, TPhours2, TSOvol, TSOhours, TSOrate, TSOpallets, sortHours, FLshare, DAupt, DAupc,FLupc, FLupt, MPupc, TPupt, toteshare, caseshare, totalTotes,
msvolume, mshours, msrate, msSvolume, msMvolume, msLvolume, uis5volume, uis5hours, uis5rate, uis5Svolume, uis5Mvolume, uis5Lvolume, uis5upt, uis20volume, uis20hours, uis20rate, uis20Svolume, uis20Mvolume, uis20Lvolume, uis20upt,
QAPShours, buildingHshare, buildingHIBPS, buildingHTSOPS, buildingHICQA, ms2volume, ms2hours, ms2rate, ms2Svolume, ms2Mvolume, ms2Lvolume, decantvol, decantSvol, decantMvol, decantLvol, decanthours, decantrate, decantcase, decant2vol, decant2Svol, decant2Mvol, decant2Lvol, decant2hours, decant2rate, decant2case, sevhours, IBPSvol, IBPShours, IBPSrate, TSOPSvol, TSOPShours, TSOPSrate, ICQAvol, ICQAhours, ICQArate, rshours, Transferouthours, TSOdockhours, prepStick, prepWrap, prepOverbox, prepResearch, prepOther, prepAssort,presortCases, presortCasesVolume, presortCasesHours, presortCasesRate,
misctotalHours, tomHours, tomTrainingHours, teamConnectHours, trainingHours, jambustersHours, fiveShours
) {

     console.log('Valores recibidos en createResultTable:', {
        misctotalHours,
        tomHours,
        tomTrainingHours,
        teamConnectHours,
        trainingHours,
        jambustersHours,
        fiveShours
    });

const newTable = document.createElement('table');
newTable.className = 'summary-table';
Object.assign(newTable.style, {
borderCollapse: "separate",
borderSpacing: 0,
marginTop: "auto",
marginLeft: "auto",
maxWidth: "700px", // Añade un ancho máximo
marginRight: "auto",
width: "35%", // ajusta para hacer más ancha la tabla
textAlign: "left",
boxShadow: "0 0 10px rgba(0,0,0,0.1), 0 5px 15px rgba(0,0,0,0.05)",
borderRadius: "10px",
overflow: "hidden"
});

// Función para Copiar tabla en fomrato imagen
async function copyTableAsImage() {
    try {
        const table = document.querySelector('.summary-table');
        if (!table) throw new Error('Table not found');
        if (typeof html2canvas !== 'function') throw new Error('html2canvas library is not loaded');
        if (!navigator.clipboard || !navigator.clipboard.write) throw new Error('Clipboard API not supported');

        const originalScroll = window.scrollY;
        table.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showTemporaryMessage?.('Processing image...', 4000);

        await new Promise(resolve => requestAnimationFrame(resolve));

        // Obtener el ancho real de la tabla
        const computedStyle = window.getComputedStyle(table);
        const actualWidth = table.offsetWidth;
        const actualHeight = table.scrollHeight;

        const canvas = await html2canvas(table, {
            scale: 2,
            backgroundColor: 'white',
            useCORS: true,
            logging: false,
            height: actualHeight,
            width: actualWidth,
            windowHeight: actualHeight,
            windowWidth: actualWidth,
            scrollY: -window.scrollY,
            onclone: clonedDoc => {
                const clonedTable = clonedDoc.querySelector('.summary-table');
                if (clonedTable) {
                    // Forzar el ancho exacto y eliminar márgenes
                    clonedTable.style.cssText = `
                width: ${actualWidth}px !important;
                max-width: ${actualWidth}px !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                border-radius: 10px !important;
                box-shadow: 0 0 10px rgba(0,0,0,0.1), 0 5px 15px rgba(0,0,0,0.05) !important;
            `;
                }

                // Ajustar el contenedor
                clonedDoc.body.style.cssText = `
            margin: 0 !important;
            padding: 0 !important;
            width: ${actualWidth}px !important;
            max-width: ${actualWidth}px !important;
            overflow: hidden !important;
        `;
            }
        });

        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png', 1.0));
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);

        window.scrollTo({ top: originalScroll, behavior: 'smooth' });
        showTemporaryMessage?.('Image copied to clipboard!', 3000);
    } catch (err) {
        console.error(err.message);
        showTemporaryMessage?.('Failed to copy image, please try again', 5000);
    }
}

// Actualizar la función showTemporaryMessage para manejar múltiples mensajes
function showTemporaryMessage(message, duration = 3000) {
    // Eliminar mensajes anteriores
    const existingMessages = document.querySelectorAll('.temporary-message');
    existingMessages.forEach(msg => msg.remove());

    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.className = 'temporary-message';
    Object.assign(messageElement.style, {
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: '#4CAF50',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        zIndex: '9999',
        fontSize: '12px',
        transition: 'opacity 0.3s ease'
    });
    document.body.appendChild(messageElement);

    setTimeout(() => {
        messageElement.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(messageElement)) {
                document.body.removeChild(messageElement);
            }
        }, 300);
    }, duration);
}

// Función para Copiar tabla
function copyTableToClipboard() {
    const table = document.querySelector('.summary-table');
    if (!table) {
        console.error('Table not found');
        return;
    }

    // Obtener el último chequeo
    const lastCheckedElement = document.querySelector('div.resourceDrilldownLink strong');
    let lastCheckedTime = null;
    if (lastCheckedElement) {
        const lastCheckedText = lastCheckedElement.textContent;
        lastCheckedTime = new Date(lastCheckedText.replace(/ (CET|GMT)/, ''));
    }

    // Obtener parámetros de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const spanType = urlParams.get('spanType') || 'Intraday';

    // Función para formatear tiempo
    const formatTime = (hour, minute) => `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;

    // Función para formatear fecha
    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}/${month}/${day}`;
    }

    // Determinar el período del reporte
    let reportPeriod = '';
    switch (spanType) {
        case 'Day':
            reportPeriod = `Day: ${formatDate(urlParams.get('startDateDay'))}`;
            break;
        case 'Week': {
            const startDate = new Date(urlParams.get('startDateWeek'));
            const weekNumber = getWeekNumber(startDate);
            reportPeriod = `Week ${weekNumber}: ${formatDate(urlParams.get('startDateWeek'))}`;
            break;
        }
        case 'Month':
            reportPeriod = `Month: ${formatDate(urlParams.get('startDateMonth'))}`;
            break;
        case 'Intraday':
        default: {
            const startDate = formatDate(urlParams.get('startDateIntraday'));
            const endDate = formatDate(urlParams.get('endDateIntraday'));
            const startHour = urlParams.get('startHourIntraday');
            const startMinute = urlParams.get('startMinuteIntraday');
            const endHour = urlParams.get('endHourIntraday');
            const endMinute = urlParams.get('endMinuteIntraday');

            const endDateTime = new Date(`${endDate.replace(/\//g, '-')} ${endHour}:${endMinute}`);
            const formattedStartTime = formatTime(startHour, startMinute);
            let formattedEndTime;
            let actualEndDate = endDate;

            if (lastCheckedTime && endDateTime > lastCheckedTime) {
                formattedEndTime = lastCheckedTime.toTimeString().substring(0, 5);
                const year = lastCheckedTime.getFullYear();
                const month = String(lastCheckedTime.getMonth() + 1).padStart(2, '0');
                const day = String(lastCheckedTime.getDate()).padStart(2, '0');
                actualEndDate = `${year}/${month}/${day}`;
            } else {
                formattedEndTime = formatTime(endHour, endMinute);
            }

            reportPeriod = `Intraday: ${startDate} ${formattedStartTime} - ${actualEndDate} ${formattedEndTime}`;
            break;
        }
    }

    // Clonar la tabla para no modificar la original
    const clonedTable = table.cloneNode(true);

    // Función para limpiar enlaces y otros elementos no deseados
    function cleanTable(element) {
        // Reemplazar todos los enlaces con su texto
        element.querySelectorAll('a').forEach(link => {
            const span = document.createElement('span');
            span.textContent = link.textContent;
            span.style.cssText = link.style.cssText;
            link.parentNode.replaceChild(span, link);
        });

        // Ajustar alineación para Time Off Task y SEV rows al copiar
        element.querySelectorAll('td[colspan="3"]').forEach(td => {
            if (td.textContent.includes('Time Off Task') || td.textContent.includes('SEV 1/2')) {
                td.style.textAlign = 'center';
                // También ajustar el div interno si existe
                const div = td.querySelector('div');
                if (div) {
                    div.style.justifyContent = 'center';
                }
            }
        });
        // Eliminar botones de show/hide details y otros elementos no deseados
        element.querySelectorAll('.prep-dropdown-toggle, .dropdown-toggle, #copyTableButton, #versionCheck').forEach(el => {
            el.remove();
        });

        // Verificar el estado de expansión de Prep Recorder y eliminar detalles si está contraído
        const prepDetails = element.querySelector('.prep-details');
        if (prepDetails && prepDetails.style.display === 'none') {
            prepDetails.remove();
        }

        // Verificar el estado de expansión de QAPS y eliminar detalles si está contraído
        const qapsDetails = Array.from(element.querySelectorAll('.qaps-detail'));
        if (qapsDetails.length > 0 && qapsDetails[0].style.display === 'none') {
            qapsDetails.forEach(detail => detail.remove());

            // Ajustar el rowspan del td de QAPS
            const qapsCell = element.querySelector('td[rowspan]');
            if (qapsCell && qapsCell.textContent.includes('QAPS')) {
                qapsCell.setAttribute('rowspan', '1');
            }
        }

        // Remover cualquier atributo href o onclick que pueda quedar
        element.querySelectorAll('*').forEach(el => {
            el.removeAttribute('href');
            el.removeAttribute('onclick');
        });
    }

    // Aplicar la limpieza a la tabla clonada
    cleanTable(clonedTable);

    // Actualizar el título con la información del período
    const warehouseId = urlParams.get('warehouseId') || '';
    const titleRow = clonedTable.querySelector('tr');
    if (titleRow) {
        titleRow.innerHTML = `
    <th colspan="8" style="background-color: #4F5A66; text-align: center; color: white; font-size: 20px; padding: 2px;">
        <span style="color: #ADD8E6;">${warehouseId}</span> IXD SUMMARY
    </th>`;
        const reportInfoRow = document.createElement('tr');
        reportInfoRow.innerHTML = `
    <th colspan="8" style="background-color: #4F5A66; color: white; text-align: center; font-size: 12px; padding: 2px;">
        Report ${reportPeriod}
    </th>`;
        titleRow.parentNode.insertBefore(reportInfoRow, titleRow.nextSibling);
    }

    // Envolver la tabla en un div con estilos para preservar el diseño
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'font-family: Arial, sans-serif; font-size: 10px;';
    wrapper.appendChild(clonedTable);

    const html = `

<html>
<head>
<style>
table {
border-collapse: collapse;
width: 100%;
}
td, th {
border: 1px solid black !important;
padding: 1px 2px !important;
line-height: 1.1 !important;
height: auto !important;
text-align: left;
vertical-align: middle !important;
}
tr:last-child td {
border: 1px solid black !important;
}
tr:last-child td[colspan] {
border: 1px solid black !important;
}
.summary-table td,
.summary-table th {
border: 1px solid black !important;
}
.cell-content {
display: block;
margin: 0;
padding: 0;
}
.summary-table {
border: 1px solid black !important;
border-collapse: collapse !important;
border-spacing: 0;
margin-top: auto;
margin-left: auto;
max-width: 700px;
margin-right: auto;
width: 36%;
text-align: left;
}
td[colspan], th[colspan] {
border: 1px solid black !important;
}
</style>
</head>
<body>
${wrapper.outerHTML}
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const item = new ClipboardItem({ "text/html": blob });

    navigator.clipboard.write([item]).then(() => {
        showTemporaryMessage('Table copied to clipboard');
    }).catch(err => {
        console.error('Error copying table: ', err);

        // Método alternativo
        const tempElem = document.createElement('div');
        tempElem.innerHTML = html;
        document.body.appendChild(tempElem);

        const range = document.createRange();
        range.selectNode(tempElem);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);

        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showTemporaryMessage('Table copied to clipboard');
            } else {
                showTemporaryMessage('Copying failed. Please try again.', 5000);
            }
        } catch (err) {
            console.error('Fallback copying failed:', err);
            showTemporaryMessage('Copying failed. Please see console for details.', 5000);
        }

        document.body.removeChild(tempElem);
    });
}


// Agregar estilos CSS para bordes
const styles = document.createElement('style');
styles.textContent = `

.fpp-tooltip {
position: absolute;
background-color: rgba(0, 0, 0, 0.8);
color: white;
padding: 4px 8px;
border-radius: 4px;
font-size: 11px;
pointer-events: none;
z-index: 1000;
display: none;
}

.summary-table {
border: none;
border-collapse: separate;
border-spacing: 0;
}
.summary-table th, .summary-table td {
border: none;
border-bottom: 1px solid black;
}
.summary-table tr:last-child td {
border-bottom: none;
}
.summary-table td + td,
.summary-table th + th {
border-left: 1px solid black;
}
.summary-table tr:nth-child(2) th {
border-bottom: 1px solid black;
}
.summary-table td:first-child,
.summary-table th:first-child {
border-left: none;
}
.summary-table td:last-child,
.summary-table th:last-child {
border-right: none;
}
.process-cell {
border-right: 1px solid black !important;
}
.no-left-border {
border-left: none !important;
}
.summary-table td:nth-child(4),
.summary-table th:nth-child(4) {
padding-left: 5px !important;
padding-right: 5px !important;
margin-left: 5px !important;
margin-right: 5px !important;
}
.summary-table td:nth-child(6),
.summary-table th:nth-child(6) {
padding-left: 5px !important;
padding-right: 5px !important;
margin-left: 5px !important;
margin-right: 5px !important;
}
.summary-table td:nth-child(7),
.summary-table th:nth-child(7) {
padding-left: 5px !important;
padding-right: 5px !important;
margin-left: 5px !important;
margin-right: 5px !important;
}
`;
document.head.appendChild(styles);

// Variables globales al inicio del script
let globalReportPeriod = '';
let globalWarehouseId = '';

// Función para formatear la fecha en AAAA-MM-DD
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
}

// Función para calcular el report period
function calculateReportPeriod() {
    const urlParams = new URLSearchParams(window.location.search);
    const spanType = urlParams.get('spanType') || 'Intraday';
    const formatTime = (hour, minute) => `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;

    // Obtener el último chequeo
    const lastCheckedElement = document.querySelector('div.resourceDrilldownLink strong');
    let lastCheckedTime = null;
    if (lastCheckedElement) {
        const lastCheckedText = lastCheckedElement.textContent;
        lastCheckedTime = new Date(lastCheckedText.replace(/ (CET|GMT)/, ''));
    }

    switch (spanType) {
        case 'Day':
            return `Day: ${formatDate(urlParams.get('startDateDay'))}`;
        case 'Week': {
            const startDate = new Date(urlParams.get('startDateWeek'));
            const weekNumber = getWeekNumber(startDate);
            return `Week ${weekNumber}: ${formatDate(urlParams.get('startDateWeek'))}`;
        }
        case 'Month':
            return `Month: ${formatDate(urlParams.get('startDateMonth'))}`;
        case 'Intraday':
        default: {
            const startDate = formatDate(urlParams.get('startDateIntraday'));
            const endDate = formatDate(urlParams.get('endDateIntraday'));
            const startHour = urlParams.get('startHourIntraday');
            const startMinute = urlParams.get('startMinuteIntraday');
            const endHour = urlParams.get('endHourIntraday');
            const endMinute = urlParams.get('endMinuteIntraday');

            const endDateTime = new Date(`${endDate.replace(/\//g, '-')} ${endHour}:${endMinute}`);

            const formattedStartTime = formatTime(startHour, startMinute);
            let formattedEndTime;
            let actualEndDate = endDate;

            if (lastCheckedTime && endDateTime > lastCheckedTime) {
                formattedEndTime = lastCheckedTime.toTimeString().substring(0, 5);
                const year = lastCheckedTime.getFullYear();
                const month = String(lastCheckedTime.getMonth() + 1).padStart(2, '0');
                const day = String(lastCheckedTime.getDate()).padStart(2, '0');
                actualEndDate = `${year}/${month}/${day}`;
            } else {
                formattedEndTime = formatTime(endHour, endMinute);
            }

            return `Intraday: ${startDate} ${formattedStartTime} - ${actualEndDate} ${formattedEndTime}`;
        }
    }
}

// Función auxiliar para obtener el número de semana
function getWeekNumber(date) {
    const target = new Date(date.valueOf());

    // Verificar si la fecha está en la última semana de diciembre
    // y si esa semana contiene el 1 de enero del siguiente año
    const nextYear = new Date(target.getFullYear() + 1, 0, 1);
    const daysUntilNextYear = Math.floor((nextYear - target) / (24 * 60 * 60 * 1000));

    if (target.getMonth() === 11 && daysUntilNextYear <= 7) {
        // Verificar si la semana contiene el 1 de enero del siguiente año
        const dayOfWeek = target.getDay();
        const daysToNextYear = daysUntilNextYear;

        if (daysToNextYear <= (7 - dayOfWeek)) {
            return 1; // Es la semana 1 del siguiente año
        }
    }

    // Para otras fechas, calcular la semana normalmente
    const firstDayOfYear = new Date(target.getFullYear(), 0, 1);
    const pastDaysOfYear = (target - firstDayOfYear) / 86400000;

    // Ajustar para que la semana comience en domingo
    const firstDayOfYearDay = firstDayOfYear.getDay();
    const weekNumber = Math.ceil((pastDaysOfYear + firstDayOfYearDay + 1) / 7);

    return weekNumber;
}

// Inicializar las variables globales
function initializeGlobalVariables() {
    const urlParams = new URLSearchParams(window.location.search);
    globalWarehouseId = urlParams.get('warehouseId') || '';
    globalReportPeriod = calculateReportPeriod();
}

// Llamar a la función de inicialización al inicio
initializeGlobalVariables();


// Fila de título con flecha e imagen más grande
const headerRow = document.createElement('tr');
const header = document.createElement('th');
const scriptVersion = GM_info.script.version;

// Función para forzar la comprobación de actualización
async function forceUpdateCheck() {
    try {
        await updatecheck(true);
        alert("You have already the latest version 🙌 ");
    } catch (error) {
        console.error("Error checking for updates:", error);
    }
}

header.innerHTML = `

<div style="position: relative; display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; flex-direction: column; align-items: flex-start; margin-right: 10px;">
<a href="javascript:void(0);" onclick="return false;" style="text-decoration: none;">
<span style="font-size: 10px; color: white; cursor: pointer;" id="versionCheck">Version: v${scriptVersion}</span>
</a>
<a href="https://w.amazon.com/bin/view/EUFC_Central_Flow/ECFT_Operation_Model/IXD/Tools/IXD_Summary_Script/" target="_blank" style="font-size: 10px; color: #ADD8E6; text-decoration: underline; margin-bottom: 3px;">Check what's new</a>

<div class="copy-dropdown" style="position: relative; display: inline-block;">
<button id="copyTableButton" style="font-size: 9px; color: #3c4856; background-color: #ADD8E6; border: none; padding: 2px 13px; margin-top: 3px; cursor: pointer; border-radius: 5px; display: flex; align-items: center; justify-content: center; gap: 3px; font-weight: bold; transition: background-color 0.3s ease; text-align: center; min-width: 60px;">
Copy table
</button>

<div id="copyDropdownContent" style="display: none; position: absolute; background-color: #ffffff; min-width: 100px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); z-index: 1; border-radius: 4px; top: calc(100% + 5px); left: 0; border: 1px solid #e0e0e0;">
<div id="copyAsText" style="padding: 6px 12px; cursor: pointer; font-size: 9px; color: #3c4856; transition: background-color 0.2s ease;">Copy as Text</div>
<div style="border-top: 1px solid #e0e0e0;"></div>
<div id="copyAsImage" style="padding: 6px 12px; cursor: pointer; font-size: 9px; color: #3c4856; transition: background-color 0.2s ease;">Copy as Image</div>
</div>

</div>
</div>
<div class="toggle-area" style="display: flex; align-items: center; cursor: pointer; flex-grow: 1; justify-content: center;">
<img src="https://drive-render.corp.amazon.com/view/gerpaes@/ECFT_logo.png" alt="ECFT" style="height: 40px; vertical-align: middle; margin-right: 8px;"
onerror="this.style.display='none'; const text = document.createElement('span'); text.textContent='ECFT'; text.style.cssText='font-size:8px; color:inherit; margin-left: 15px; display: inline-block; vertical-align: middle;'; this.parentNode.querySelector('.toggle-arrow').after(text);">
<div style="display: flex; flex-direction: column; align-items: center;">
<span style="font-weight: bold; margin-bottom: -2px;font-size: 25px;">
<span style="color: #ADD8E6; font-weight: bold;font-size: 25px; justify-content: center">${globalWarehouseId}</span> IXD SUMMARY
</span>
<span style="font-size: 10px; color: white; margin-top: 4px; font-weight: bold;">Report ${globalReportPeriod}</span>
</div>
<span class="toggle-arrow" style="vertical-align: middle; margin-left: 5px;">▼</span>
</div>
<a href="https://form.asana.com/?k=kYTqJjA65kUjn0Dg1VWI4A&d=8442528107068" target="_blank" style="text-decoration: none; margin-right: 4px;" title="Report a bug">
<i class="fa-solid fa-bug" style="color: white; font-size: 21px;"></i>
</a>
</div>
`;

// Añadir el event listener para el botón de copiar
setTimeout(() => {
    const copyDropdown = document.querySelector('.copy-dropdown');
    const copyButton = document.getElementById('copyTableButton');
    Object.assign(copyButton.style, {
        fontSize: '9px',
        color: '#3c4856',
        backgroundColor: '#ADD8E6',
        border: 'none',
        padding: '2px 8px',
        marginTop: '3px',
        cursor: 'pointer',
        borderRadius: '5px',
        display: 'flex',
        alignItems: 'center',
        gap: '3px',
        fontWeight: 'bold',
        transition: 'background-color 0.3s ease'
    });

    const dropdownContent = document.getElementById('copyDropdownContent');
    Object.assign(dropdownContent.style, {
        display: 'none',
        position: 'absolute',
        backgroundColor: '#ffffff',
        minWidth: '100px',
        boxShadow: '0px 4px 8px rgba(0,0,0,0.1)',
        zIndex: '1',
        borderRadius: '4px',
        top: 'calc(100% + 5px)',
        left: '0',
        border: '1px solid #e0e0e0'
    });

    const copyAsText = document.getElementById('copyAsText');
    const copyAsImage = document.getElementById('copyAsImage');

    // Estilos para las opciones del menú
    [copyAsText, copyAsImage].forEach(element => {
        Object.assign(element.style, {
            padding: '6px 12px',
            cursor: 'pointer',
            fontSize: '9px',
            color: '#3c4856',
            transition: 'background-color 0.2s ease'
        });
    });

    if (copyDropdown && dropdownContent) {
        // Mostrar menú y cambiar color del botón al hover
        copyButton.addEventListener('mouseenter', () => {
            copyButton.style.backgroundColor = '#d4ebf2';
            dropdownContent.style.display = 'block';
        });

        // Cerrar el menú cuando el ratón sale del área completa
        copyDropdown.addEventListener('mouseleave', () => {
            setTimeout(() => {
                if (!copyDropdown.matches(':hover')) {
                    dropdownContent.style.display = 'none';
                    copyButton.style.backgroundColor = '#ADD8E6';
                }
            }, 100);
        });

        // Efectos hover en las opciones
        [copyAsText, copyAsImage].forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.backgroundColor = '#ADD8E6';
            });
            element.addEventListener('mouseleave', () => {
                element.style.backgroundColor = 'transparent';
            });
        });

        // Funcionalidad de copiado
        copyAsText.addEventListener('click', () => {
            copyTableToClipboard();
            dropdownContent.style.display = 'none';
        });

        copyAsImage.addEventListener('click', async function (e) {
            e.stopPropagation();
            copyTableAsImage().catch(err => {
                console.error('Error copying image:', err);
                showTemporaryMessage('Failed to copy image, please try again or refresh the website.', 4000);
            });
            dropdownContent.style.display = 'none';
        });
    } else {
        console.error('Copy button elements not found');
    }
}, 0);

// Añadir el evento de clic después de que el elemento se haya agregado al DOM
setTimeout(() => {
    const versionElement = document.getElementById('versionCheck');
    if (versionElement) {
        versionElement.addEventListener('click', forceUpdateCheck);
    }
}, 0);

Object.assign(header.style, {
    backgroundColor: "#3c4856",
    color: "#FFFFFF",
    textAlign: "center",
    fontSize: "20px",
    fontWeight: "bold",
    padding: "10px",
    cursor: "pointer"
});

header.colSpan = 8;
headerRow.appendChild(header);
newTable.appendChild(headerRow);

// Contenedor para las filas restantes
const contentRows = document.createElement('tbody');
contentRows.id = 'content-rows';

// Fila de subtítulos
const subHeaderRow = document.createElement('tr');
subHeaderRow.innerHTML = `

<th class="process-cell" style="background-color: #6c7886; color: rgb(255, 255, 255); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;">Process</th>
<th class="no-left-border" style="background-color: #6c7886; color: #fff; font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; white-space: nowrap; min-width: 230px;" colspan="3">Metric</th>
<th style="background-color: #6c7886; color: #fff; font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; white-space: nowrap; min-width: 25px;">FPP %</th>
<th style="background-color: #6c7886; color: rgb(255, 255, 255); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;">Volume</th>
<th class="hidden-column" style="background-color: #6c7886; color: rgb(255, 255, 255); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;">Jobs</th>
<th style="background-color: #6c7886; color: rgb(255, 255, 255); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;">Hours</th>
<th style="background-color: #6c7886; color: rgb(255, 255, 255); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;">Rate</th>
`;
contentRows.appendChild(subHeaderRow);

// Agregar estilos para ocultar la columna de JOBS
const style = document.createElement('style');
style.textContent = `

.hidden-column {
display:none;
}

`;
document.head.appendChild(style);

// Fila para IB
const ibRow = document.createElement('tr');
const ibRowspan = arosvol === 0 ?
    (transin === 0 ?
        (palletTIvol > 0 ? 10 : 9) : // si transin es 0
        (palletTIvol > 0 ? 12 : 11) // si transin no es 0
    ) :
    (transin === 0 ?
        (palletTIvol > 0 ? 11 : 10) : // si transin es 0
        (palletTIvol > 0 ? 13 : 12) // si transin no es 0
    );

const rsindirect = ibHours ? (((rshours-decanthours)/ibHours) * 100).toFixed(1) + '%' : '0%';
        const dockindirect = ibHours ? (((ibHours-(decanthours+decant2hours+ERhours+prephours+preditorhours+pallethours))/ibHours) * 100).toFixed(1) + '%' : '0%';

ibRow.innerHTML = `<td class="process-cell" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; position: relative;" rowspan="${ibRowspan}">     <div style="height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: center;">         <span style="font-weight: bold; font-size: 12px;">IB</span>         <div style="margin-top: 15px;">             <a href="https://eu.relat.aces.amazon.dev/countify/history/${params.warehouseId}"                style="color: #515151; font-size: 9px; font-weight: normal; text-decoration: underline;"                target="_blank">                 Countify             </a>         </div>     </div>     <div style="position: absolute; bottom: 10px; left: 0; right: 0; text-align: center;">             <div style="color: #000; font-size: 9px; font-weight: bold;">% Indirect</div>     <div style="color: #515151; font-size: 8px; font-weight: normal;">${dockindirect} <b>Dock </b></div>     <div style="color: #515151; font-size: 8px; font-weight: normal;">${rsindirect} <b>RCV Supp. </b></div> </div> </td> <td class="no-left-border" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;" colspan="3">IB - Total (Vendor Rec. + Transfer-In)</td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;"></td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ibTotal !== null ? ibTotal.toLocaleString() : 'N/A'}</td> <td class="hidden-column" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ibHours !== null ? ibHours.toLocaleString() : 'N/A'}</td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ibRate !== null ? Math.round(ibRate).toLocaleString() : 'N/A'}</td>`;

contentRows.appendChild(ibRow);

if (transin !== 0) {
    // Fila para Inbound (subdivisión de IB total)
    const inboundRow = document.createElement('tr');
    inboundRow.innerHTML = `

<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">Inbound (Vendor Receipts)</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;"></td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${inbound !== null ? inbound.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${inboundhours !== null ? inboundhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${inboundrate !== null ? Math.round(inboundrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(inboundRow);

    // Fila para Transfer-In
    const transinRow = document.createElement('tr');
    transinRow.innerHTML = `

<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">Transfer-In</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;"></td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${transin !== null ? transin.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${transinhours !== null ? transinhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${transinrate !== null ? Math.round(transinrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(transinRow);
}

// Fila para Each Receive (subdivisión de IB total)
const eachreceiveRow = document.createElement('tr');
const ERfpp = inbound ? ((ERvol / inbound) * 100).toFixed(1) + '%' : '0%';
const ERsmall = ERSvol ? ((ERSvol / (ERvol)) * 100).toFixed(1) + '%' : '0%';
const ERmedium = ERMvol ? ((ERMvol / (ERvol)) * 100).toFixed(1) + '%' : '0%';
const ERlarge = ERLvol ? ((ERLvol / (ERvol)) * 100).toFixed(1) + '%' : '0%';
eachreceiveRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px;padding: 5px 10px; padding-left: 15px;" colspan="3">
Each Receive - Total
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
${ERsmall} <b>S</b> | ${ERmedium} <b>M</b> | ${ERlarge} <b>L</b>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ERfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ERvol !== null ? ERvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ERhours !== null ? ERhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ERrate !== null ? Math.round(ERrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(eachreceiveRow);

// Fila para Prep (subdivisión de IB total)
const prepRow = document.createElement('tr');
const prepfpp = inbound ? ((prepvol / inbound) * 100).toFixed(1) + '%' : '0%';
const prepsmall = prepSvol ? ((prepSvol / (prepvol)) * 100).toFixed(1) + '%' : '0%';
const prepmedium = prepMvol ? ((prepMvol / (prepvol)) * 100).toFixed(1) + '%' : '0%';
const preplarge = prepLvol ? ((prepLvol / (prepvol)) * 100).toFixed(1) + '%' : '0%';

// Calcular el total de todos los tipos de prep
const totalPrepTypes = (prepStick || 0) + (prepWrap || 0) + (prepOverbox || 0) +
    (prepResearch || 0) + (prepOther || 0) + (prepAssort || 0);

// Crear array de tipos y ordenarlos por valor
const prepTypes = [
    { name: 'Stickering', value: prepStick },
    { name: 'Shrinkwrap', value: prepWrap },
    { name: 'Overbox', value: prepOverbox },
    { name: 'Research', value: prepResearch },
    { name: 'Other', value: prepOther },
    { name: 'Assortment', value: prepAssort }
].sort((a, b) => b.value - a.value);

// Obtener el estado guardado
const isPrepExpanded = localStorage.getItem('isPrepExpanded') === 'true';

// Crear los detalles ordenados
const prepTypeDetails = prepTypes
    .map(type => {
        const percentage = totalPrepTypes > 0 ? ((type.value / totalPrepTypes) * 100).toFixed(1) : '0';
        if (type.value > 0) {
            return `<div style="font-weight: normal; margin-left: 20px; font-size: 10px; color: #4f5a66; margin-bottom: 2px;">
        ${percentage}% <b>${type.name}</b> - ${type.value.toLocaleString()}
    </div>`;
        }
        return '';
    })
    .filter(detail => detail !== '')
    .join('');

prepRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 15px;" colspan="3">
<div>
<div style="display: flex; align-items: center; margin-bottom: 5px;">
<span style="flex-grow: 1;">Prep Recorder - Total</span>
<button class="prep-dropdown-toggle" style="background: none; border: none; color: #2E3944; cursor: pointer; padding: 0; display: flex; align-items: center; font-size: 10px;">
${isPrepExpanded ? 'Hide details' : 'Show details'}
<i class="fas fa-chevron-${isPrepExpanded ? 'up' : 'down'}" style="margin-left: 5px; font-size: 13px;"></i>
</button>
</div>
<div class="prep-details" style="display: ${isPrepExpanded ? 'block' : 'none'}; margin-top: 3px;">
${prepTypeDetails}
</div>
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
${prepsmall} <b>S</b> | ${prepmedium} <b>M</b> | ${preplarge} <b>L</b>
</div>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${prepfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${prepvol !== null ? prepvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${prephours !== null ? prephours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${preprate !== null ? Math.round(preprate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(prepRow);

// En el evento click, actualizar el HTML del botón así:
setTimeout(() => {
    const dropdownToggle = prepRow.querySelector('.prep-dropdown-toggle');
    const detailsDiv = prepRow.querySelector('.prep-details');

    if (dropdownToggle && detailsDiv) {
        dropdownToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const scrollPos = window.scrollY;
            const isCurrentlyExpanded = detailsDiv.style.display === 'block';
            detailsDiv.style.display = isCurrentlyExpanded ? 'none' : 'block';

            // Actualizar el botón con el texto primero y luego la flecha
            this.innerHTML = `
        ${isCurrentlyExpanded ? 'Show details' : 'Hide details'}
        <i class="fas fa-chevron-${isCurrentlyExpanded ? 'down' : 'up'}" style="margin-left: 5px; font-size: 12px;"></i>
    `;

            localStorage.setItem('isPrepExpanded', (!isCurrentlyExpanded).toString());
            window.scrollTo(0, scrollPos);
        });
    }
}, 0);



// Fila para Pallet Receive (subdivisión de IB total)
const palletRow = document.createElement('tr');
const palletTvol = (palletvol || 0) + (RDpalletvol || 0) + (IBpalletvol || 0);
const palletTcases = (palletcases || 0) + (RDpalletcases || 0) + (IBpalletcases || 0);
const PAXupc = ((palletTvol / (palletTcases || 1)) || 0).toFixed(1);
const PAXupp = ((palletTvol || 0) / (palletReceive || 1)).toFixed(1);
const PAXcpp = ((palletTcases || 0) / (palletReceive || 1)).toFixed(1);
const palletfpp = inbound && inbound !== 0 ? ((palletTvol / inbound) * 100).toFixed(1) + '%' : '0%';

palletRow.innerHTML = `

<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;padding-left: 15px;">
Pallet Receive - <span style="color: #4f5a66;font-size: 11px;font-weight: bold;">${palletReceive != null ? palletReceive.toLocaleString() : '0'} Pallets</span>
<div style="font-weight: normal; font-size: 11px; margin-top: 3px; color: #4f5a66;">
<div style="margin-left: 10px;"><span style="font-style: italic;">Pallet Autoreceive</span>: ${autorepallet !== null && autorepallet !== undefined ? autorepallet : '0%'}</div>
</div>
</td>
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column;">
<span style="white-space: nowrap; display: inline-block; min-width: 20px;">
UPC: <span style="font-weight: bold;">${PAXupc != null && !isNaN(PAXupc) ? PAXupc : '0'}</span>
</span>
<span style="white-space: nowrap; display: inline-block; min-width: 20px;">
CPP: <span style="font-weight: bold;">${PAXcpp != null && !isNaN(PAXcpp) ? PAXcpp : '0'}</span>
</span>
<span style="white-space: nowrap; display: inline-block; min-width: 20px;">
UPP: <span style="font-weight: bold;">${PAXupp != null && !isNaN(PAXupp) ? PAXupp : '0'}</span>
</span>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${palletfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${palletTvol != null ? palletTvol.toLocaleString() : '0'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${palletReceive != null ? palletReceive.toLocaleString() : '0'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${pallethours != null ? pallethours.toLocaleString() : '0'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${palletrate != null ? Math.round(palletrate).toLocaleString() : '0'}</td>
`;
contentRows.appendChild(palletRow);

// Fila para TransferIn Pallet receive
if (palletTIvol > 0) {
    const palletTIRow = document.createElement('tr');
    palletTIRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;padding-left: 15px;" colspan="3">Transfer-In Pallet - <span style="color: #4f5a66;font-size: 11px;font-weight: bold;">${palletTIunits !== null ? palletTIunits.toLocaleString() : 'N/A'} Pallets</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${palletTIvol !== null ? palletTIvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${palletTIcases !== null ? palletTIcases.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${palletTIhours !== null ? palletTIhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${palletTIrate !== null ? Math.round(palletTIrate).toLocaleString() : 'N/A'}</td>

`;
contentRows.appendChild(palletTIRow);
}

// Fila para LP Receive
const LPreceiveRow = document.createElement('tr');
const LPfpp = inbound ? ((eachTotal / inbound) * 100).toFixed(1) + '%' : '0%';
LPreceiveRow.innerHTML = `

<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;padding-left: 15px;">
LP Receive - <span style="color: #4f5a66;font-size: 11px;">${caseTotal !== null ? caseTotal.toLocaleString() : 'N/A'} Cases</span>
<div style="font-weight: normal; font-size: 11px; margin-top: 3px; color: #4f5a66;">
<div style="margin-left: 10px;"><span style="font-style: italic;">LP Autoreceive</span>: ${autore !== null && autore !== undefined ? autore : '0%'}</div>
</div>
</td>
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 10px;">
UPC: <span style="font-weight: bold;">${LPupc.toFixed(1)}</span>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${LPfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${eachTotal !== null ? eachTotal.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${caseTotal !== null ? caseTotal.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(LPreceiveRow);

// Fila para PID UPC
const pidUpcRow = document.createElement('tr');
const pidfpp = inbound ? ((pidvol / inbound) * 100).toFixed(1) + '%' : '0%';
pidUpcRow.innerHTML = `

<td colspan="2" style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 20px;">PID - <span style="color: #4f5a66;font-size: 11px;">${pidcases !== null ? pidcases.toLocaleString() : 'N/A'} Cases</span></td>
<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 10px;">
UPC: ${pidUpc !== null && pidUpc !== undefined ? pidUpc.toFixed(1) : 'N/A'}
</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${pidfpp}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${pidvol !== null ? pidvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${pidcases !== null ? pidcases.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(pidUpcRow);

// Fila para PrEditor UPC
const prEditorUpcRow = document.createElement('tr');
const preditorfpp = inbound ? ((preditorvol / inbound) * 100).toFixed(1) + '%' : '0%';
prEditorUpcRow.innerHTML = `

<td colspan="2" style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 20px;">PrEditor - <span style="color: #4f5a66;font-size: 11px;">${preditorcases !== null ? preditorcases.toLocaleString() : 'N/A'} Cases</span></td>
<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 10px;">
UPC: ${prEditorUpc !== null && prEditorUpc !== undefined ? prEditorUpc.toFixed(1) : 'N/A'}
</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${preditorfpp}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${preditorvol !== null ? preditorvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${preditorcases !== null ? preditorcases.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${preditorhours !== null ? preditorhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${preditorrate !== null ? Math.round(preditorrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(prEditorUpcRow);

// Fila para Aros
if (arosvol !== 0) {
    const arosUpcRow = document.createElement('tr');
    const arosfpp = inbound ? ((arosvol / inbound) * 100).toFixed(1) + '%' : '0%';
    arosUpcRow.innerHTML = `

<td colspan="2" style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 20px;">AROS - <span style="color: #4f5a66;font-size: 11px;">${aroscases !== null ? aroscases.toLocaleString() : 'N/A'} Cases</span></td>
<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 10px;">
UPC: ${arosUpc !== null && arosUpc !== undefined ? arosUpc.toFixed(1) : 'N/A'}
</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${arosfpp}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${arosvol !== null ? arosvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${aroscases !== null ? aroscases.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(arosUpcRow);
}

// Fila para Decant (subdivisión de IB total)
const decantTvol = (decantvol || 0) + (decant2vol || 0);
const decantTcase = (decantcase || 0) + (decant2case || 0);
const decantUPC = (decantTcase || 0) !== 0 ? (decantTvol || 0) / (decantTcase || 0) : 0;
const decantTvolsmall = (decantSvol || 0) + (decant2Svol || 0);
const decantsmall = decantTvolsmall ? ((decantTvolsmall / (decantTvol)) * 100).toFixed(1) + '%' : '0%';

const decantTvolmedium = (decantMvol || 0) + (decant2Mvol || 0);
const decantmedium = decantTvolmedium ? ((decantTvolmedium / (decantTvol)) * 100).toFixed(1) + '%' : '0%';

const decantTvollarge = (decantLvol || 0) + (decant2Lvol || 0);
const decantlarge = decantTvollarge ? ((decantTvollarge / (decantTvol)) * 100).toFixed(1) + '%' : '0%';

const decantThours = (decanthours || 0) + (decant2hours || 0);
const decantUPH = (decantThours || 0) !== 0 ? (decantTcase || 0) / (decantThours || 0) : 0;
const decantTrate = decantThours > 0 ? decantTvol / decantThours : 0;
sessionStorage.setItem('decantTrate', decantTrate);
const decantRow = document.createElement('tr');
const decantfpp = decantTvol ? ((decantTvol / inbound) * 100).toFixed(1) + '%' : '0%';

decantRow.innerHTML = `

<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;padding-left: 15px;">
Decant - <span style="color: #4f5a66; font-size: 11px;"> ${decantUPH !== null ? decantUPH.toFixed(1) : 'N/A'} Case/h</span>
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
${decantsmall} <b>S</b> | ${decantmedium} <b>M</b> | ${decantlarge} <b>L</b>
</div>
</td>
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 10px;">
UPC: <span style="font-weight: bold;">${decantUPC !== null && decantUPC !== undefined ? decantUPC.toFixed(1) : 'N/A'}</span>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${decantfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${decantTvol !== null ? decantTvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${decantThours !== null ? decantThours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${decantTrate !== null ? Math.round(decantTrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(decantRow);

    // PRESORT CASES

const presortCasesRow = document.createElement('tr');
const presortVolume = (mainPageValues.presortCases * PAXupc) || 0;
const presortCasesfpp = ibTotal ? ((presortVolume / ibTotal) * 100).toFixed(1) + '%' : '0%';

presortCasesRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 15px;" colspan="3">
    Presort Cases
    <span style="font-weight: normal; font-size: 10px; color: #4f5a66;">
        [RC Presort Cases x Pallet Receive UPC]
    </span>
    <span style="color: #4f5a66; font-size: 11px;">
        - ${mainPageValues.presortCases !== null ? mainPageValues.presortCases.toLocaleString() : 'N/A'} Cases
    </span>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${presortCasesfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${presortVolume !== null ? Math.round(presortVolume).toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${mainPageValues.presortCases !== null ? mainPageValues.presortCases.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;

    contentRows.appendChild(presortCasesRow);

// Fila para Sort - Total
const sortTotalRow = document.createElement('tr');
const sortsmall = sortVolumesmall ? ((sortVolumesmall / (sortVolume)) * 100).toFixed(1) + '%' : '0%';
            const msThours = (mshours || 0) + (ms2hours || 0);
const sortindirect = sortHours ? (((sortHours-(msThours+uis5hours+uis20hours)) / (sortHours)) * 100).toFixed(1) + '%' : '0%';

sortTotalRow.innerHTML = `<td class="process-cell" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; position: relative;" rowspan="5"> <div style="height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: center;"> <span style="font-weight: bold; font-size: 12px;">Sort</span>         <div style="margin-top: 15px;">             <a href="https://console.harmony.a2z.com/crossdock-manager/#/dice/eu/case-break?context=Prod&relativeDays=7&query=${params.warehouseId}"                style="color: #515151; font-size: 9px; white-space: nowrap; font-weight: normal; text-decoration: underline;"                target="_blank">                 Case Break Limit             </a>         </div>         <div style="margin-top: 5px;">         <div style="margin-top: 5px;">             <a href="https://cw-dashboards.aka.amazon.com/cloudwatch/dashboardInternal?accountId=989351316793#dashboards/dashboard/Dice-EU-Business-Metrics-Case-Break-Prod"                style="color: #515151; font-size: 9px; font-weight: normal; white-space: nowrap; text-decoration: underline;"                target="_blank">                 DICE Metrics             </a>         </div>         <div style="position: absolute; bottom: 10px; left: 0; right: 0; text-align: center;">             <div style="color: #000; font-size: 9px; font-weight: normal;"><b>% Indirect</b></div>             <div style="color: #515151; font-size: 8px; font-weight: normal;">${sortindirect} <b>Sort</b></div>         </div>     </div> </td> <td class="no-left-border" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;" colspan="3">Sort - Total </td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;"></td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${sortVolume !== null ? sortVolume.toLocaleString() : 'N/A'}</td> <td class="hidden-column" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${sortHours !== null ? sortHours.toLocaleString() : 'N/A'}</td> <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;"> ${sortVolume !== null && sortHours !== null && sortHours !== 0 ? (Math.round(sortVolume / sortHours) || 0).toLocaleString() : '0' } </td>`;
contentRows.appendChild(sortTotalRow);

// Fila para Manual Sort
const msTvolume = (msvolume || 0) + (ms2volume || 0);
const msTSvolume = (msSvolume || 0) + (ms2Svolume || 0);
const msTMvolume = (msMvolume || 0) + (ms2Mvolume || 0);
const msTLvolume = (msLvolume || 0) + (ms2Lvolume || 0);
const msTrate = msThours > 0 ? msTvolume / msThours : 0;

// Calcular porcentajes por tamaño
const msTSmall = msTSvolume ? ((msTSvolume / msTvolume) * 100).toFixed(1) + '%' : '0%';
const msTMedium = msTMvolume ? ((msTMvolume / msTvolume) * 100).toFixed(1) + '%' : '0%';
const msTLarge = msTLvolume ? ((msTLvolume / msTvolume) * 100).toFixed(1) + '%' : '0%';

sessionStorage.setItem('msTrate', msTrate);
const manualSortRow = document.createElement('tr');
const msfpp = sortVolume ? ((msTvolume / daTotal) * 100).toFixed(1) + '%' : '0%';
manualSortRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 15px;" colspan="3">
Manual Sort
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
${msTSmall} <b>S</b> | ${msTMedium} <b>M</b> | ${msTLarge} <b>L</b>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${msfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${msTvolume.toLocaleString()}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${msThours.toLocaleString()}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${Math.round(msTrate).toLocaleString()}</td>
`;
contentRows.appendChild(manualSortRow);

// Fila para UIS 5lbs
const uis5Row = document.createElement('tr');
const uis5fpp = sortVolume ? ((uis5volume / daTotal) * 100).toFixed(1) + '%' : '0%';
const uis5Small = uis5Svolume ? ((uis5Svolume / uis5volume) * 100).toFixed(1) + '%' : '0%';
const uis5Medium = uis5Mvolume ? ((uis5Mvolume / uis5volume) * 100).toFixed(1) + '%' : '0%';
const uis5Large = uis5Lvolume ? ((uis5Lvolume / uis5volume) * 100).toFixed(1) + '%' : '0%';

uis5Row.innerHTML = `<td colspan="0" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;">     UIS 5lbs     <div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">         ${uis5Small} <b>S</b> | ${uis5Medium} <b>M</b> | ${uis5Large} <b>L</b>     </div> </td> <td colspan="1" style="background-color: #e9f3f5; text-align: center; padding: 5px 10px; font-size: 12px;" rowspan="2">     UIS UPT: <b>${((uis5volume + uis20volume) / (uis5upt + uis20upt)).toFixed(2)}</b> </td> <td colspan="1" style="background-color: #e9f3f5; text-align: center; padding: 5px 10px; font-size: 12px;">     5lb UPT: <b>${(uis5volume / uis5upt).toFixed(2)}</b> </td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis5fpp}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis5volume !== null ? uis5volume.toLocaleString() : 'N/A'}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis5hours !== null ? uis5hours.toLocaleString() : 'N/A'}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis5rate !== null ? Math.round(uis5rate).toLocaleString() : 'N/A'}</td>`;

    contentRows.appendChild(uis5Row);

// Fila para UIS 20lbs
const uis20Row = document.createElement('tr');
const uis20fpp = sortVolume ? ((uis20volume / daTotal) * 100).toFixed(1) + '%' : '0%';
const uis20Small = uis20Svolume ? ((uis20Svolume / uis20volume) * 100).toFixed(1) + '%' : '0%';
const uis20Medium = uis20Mvolume ? ((uis20Mvolume / uis20volume) * 100).toFixed(1) + '%' : '0%';
const uis20Large = uis20Lvolume ? ((uis20Lvolume / uis20volume) * 100).toFixed(1) + '%' : '0%';

uis20Row.innerHTML = `<td colspan="0" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;">     UIS 20lbs     <div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">         ${uis20Small} <b>S</b> | ${uis20Medium} <b>M</b> | ${uis20Large} <b>L</b>     </div> </td> <td colspan="1" style="background-color: #e9f3f5; text-align: center; padding: 5px 10px; font-size: 12px;">     20lb UPT: <b>${(uis20volume / uis20upt).toFixed(2)}</b> </td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis20fpp}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis20volume !== null ? uis20volume.toLocaleString() : 'N/A'}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis20hours !== null ? uis20hours.toLocaleString() : 'N/A'}</td> <td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${uis20rate !== null ? Math.round(uis20rate).toLocaleString() : 'N/A'}</td>`;

    contentRows.appendChild(uis20Row);

// Fila para Sort Share
const sortShareRow = document.createElement('tr');

sortShareRow.innerHTML = `<td colspan="2" style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; padding: 5px 10px;">Sort Share (%)</td> <td colspan="5" style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${sortShare !== null ? sortShare.toFixed(2) + '%' : 'N/A'}</td>`;

    contentRows.appendChild(sortShareRow);

// Fila para DA Total
// Primero, determinar cuántas filas serán visibles
let visibleRows = 5; // Comenzamos con 5 filas básicas (DA Total, Fluid Load, Manual Palletize, TOTE Palletize, TSO)

// Verificar si tanto RPvol como (TPvol - RPvol) son mayores que 0
if (RPvol > 0 && (TPvol - RPvol) > 0) {
    visibleRows += 2; // Añadir 2 filas más para Robot Palletize y Manual Tote Palletize
}

// Fila para DA Total
const daRow = document.createElement('tr');
const datotes = (fltotecase || 0) + (TPtote || 0);
const dacases = (flcasecase || 0) + (MPcase || 0);
const dajobs = (flcasecase || 0) + (MPcase || 0) + (fltotecase || 0) + (TPtote || 0);
    const TSOtotalhours = ((Transferouthours|| 0) + (TSOdockhours|| 0)) ;
    const daindirect = TSOtotalhours ? (((TSOtotalhours-(FLThours+MPhours+TPhours)) / (TSOtotalhours)) * 100).toFixed(1) + '%' : '0%';


daRow.innerHTML = `

<td class="process-cell" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; position: relative;" rowspan="${visibleRows}">
<div style="height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: center;">
<span style="font-weight: bold; font-size: 12px;">DA</span>
</div>
<div style="position: absolute; bottom: 10px; left: 0; right: 0; text-align: center;">
<div style="color: #000; font-size: 9px; font-weight: normal;"><b>% Indirect</b></div>
<div style="color: #515151; font-size: 8px; font-weight: normal;">${daindirect} <b>TSO/Dock</b></div>
</div>
</td>
<td colspan="2" class="no-left-border" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column; width: 100%;">
<div>DA - Total - <span style="color: #4f5a66; font-size: 11px;">${dajobs !== null ? dajobs.toLocaleString() : 'N/A'} Containers</span></div>
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66; white-space: nowrap;">${dacases !== null ? dacases.toLocaleString() : 'N/A'} - ${caseshare} <b>Cases</b> | ${datotes !== null ? datotes.toLocaleString() : 'N/A'} - ${toteshare} <b>Totes</b></div>
</div>
</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: normal; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column; gap: 2px;">
<span style="white-space: nowrap;">UPT: <span style="font-weight: bold;">${DAupt !== null ? DAupt.toLocaleString() : 'N/A'}</span></span>
<span style="white-space: nowrap;">UPC: <span style="font-weight: bold;">${DAupc !== null ? DAupc.toLocaleString() : 'N/A'}</span></span>
</div>
</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;"></td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${daTotal !== null ? daTotal.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${dajobs !== null ? dajobs.toLocaleString() : 'N/A'}</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${daHours !== null ? daHours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${daRate !== null ? Math.round(daRate).toLocaleString() : 'N/A'}</td>`;
contentRows.appendChild(daRow);

// Función auxiliar para formatear en K (miles)
function formatToK(number) {
    if (number === null || isNaN(number)) return 'N/A';
    if (number < 1000) return number.toString();
    return (number / 1000).toFixed(1) + 'K';
}

// Fila para Fluid load - Total
const fluidLoadRow = document.createElement('tr');
const FLfpp = daTotal ? ((FLvol / daTotal) * 100).toFixed(1) + '%' : '0%';
const flcontainers = (flcasecase + fltotecase);
const FLfpp2 = flcontainers ? ((flcontainers / dajobs) * 100).toFixed(1) + '%' : '0%';
const flcaseshare = flcasecase ? ((flcasecase / (flcasecase + fltotecase)) * 100).toFixed(1) + '%' : '0%';
const fltoteshare = fltotecase ? ((fltotecase / (flcasecase + fltotecase)) * 100).toFixed(1) + '%' : '0%';
sessionStorage.setItem('FLrate', FLrate);
fluidLoadRow.innerHTML = `
<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; white-space: nowrap; padding-left: 15px;">
    Fluid Load - Total - <span style="color: #4f5a66;font-size: 11px;">${flcontainers !== null ? flcontainers.toLocaleString() : 'N/A'} Containers - ${FLfpp2}</span>
    <div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
        <div style="margin-left: 0px;">${flcasecase !== null ? flcasecase.toLocaleString() : 'N/A'} C (${(FLupc !== null && flcasecase !== null) ? formatToK(FLupc * flcasecase) : 'N/A'}) - ${fltotecase !== null ? fltotecase.toLocaleString() : 'N/A'} T (${(FLupt !== null && fltotecase !== null) ? formatToK(FLupt * fltotecase) : 'N/A'})</div>
        FL Cycle Time: <b>${FLCycleTime}</b>
    </div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column; gap: 2px;">
<span style="white-space: nowrap;">UPT: <span style="font-weight: bold;">${FLupt !== null ? FLupt.toLocaleString() : 'N/A'}</span></span>
<span style="white-space: nowrap;">UPC: <span style="font-weight: bold;">${FLupc !== null ? FLupc.toLocaleString() : 'N/A'}</span></span>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${FLfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${FLvol !== null ? FLvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${flcontainers !== null ? flcontainers.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${FLThours !== null ? FLThours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${FLrate !== null ? Math.round(FLrate).toLocaleString() : 'N/A'}</td>
`;

contentRows.appendChild(fluidLoadRow);


// Fila para Manual Palletize
const manualPalletizeRow = document.createElement('tr');
const MPfpp = daTotal ? ((MPvol / daTotal) * 100).toFixed(1) + '%' : '0%';
const MPfpp2 = MPcase ? ((MPcase / dajobs) * 100).toFixed(1) + '%' : '0%';
sessionStorage.setItem('MPrate', MPrate);
manualPalletizeRow.innerHTML = `

<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; white-space: nowrap; padding-left: 15px;" colspan="1">Manual Palletize Case - <span style="color: #4f5a66 ;font-size: 11px;">${MPcase !== null ? MPcase.toLocaleString() : 'N/A'} Cases - ${MPfpp2}</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column; gap: 2px;">
<span style="white-space: nowrap;">UPC: <span style="font-weight: bold;">${MPupc !== null ? MPupc.toLocaleString() : 'N/A'}</span></span>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${MPfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${MPvol !== null ? MPvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${MPcase !== null ? MPcase.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${MPhours !== null ? MPhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${MPrate !== null ? Math.round(MPrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(manualPalletizeRow);

// Fila para TOTE Palletize
const totePalletizeRow = document.createElement('tr');
sessionStorage.setItem('TPrate', TPrate);
const TPfpp = daTotal ? ((TPvol / daTotal) * 100).toFixed(1) + '%' : '0%';
const TPfpp2 = TPtote ? ((TPtote / dajobs) * 100).toFixed(1) + '%' : '0%';
totePalletizeRow.innerHTML = `

<td colspan="2" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; white-space: nowrap; padding-left: 15px;" colspan="1">Palletize Tote - Total - <span style="color: #4f5a66 ;font-size: 11px;">${TPtote !== null ? TPtote.toLocaleString() : 'N/A'} Totes - ${TPfpp2}</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: normal; font-size: 12px; padding: 5px 10px;">
<div style="display: flex; flex-direction: column; gap: 2px;">
<span style="white-space: nowrap;">UPT: <span style="font-weight: bold;">${TPupt !== null ? TPupt.toLocaleString() : 'N/A'}</span></span>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TPfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TPvol !== null ? TPvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TPtote !== null ? TPtote.toLocaleString() : 'N/A'} </td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TPhours !== null ? TPhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TPrate !== null ? Math.round(TPrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(totePalletizeRow);

// Solo mostrar las filas de Robot y Manual si ambos tienen volumen
if (RPvol > 0 && (TPvol - RPvol) > 0) {
    // Robot Palletize Row
    const robotPalletizeRow = document.createElement('tr');
    const robotfpp = daTotal ? ((RPvol / daTotal) * 100).toFixed(1) + '%' : '0%';
    const robotfpp2 = dajobs ? ((RPtote / dajobs) * 100).toFixed(1) + '%' : '0%';
    robotPalletizeRow.innerHTML = `

<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 30px; padding-left: 20px;" colspan="3">Robot Palletize - <span style="color: #4f5a66 ;font-size: 11px;">${RPtote !== null ? RPtote.toLocaleString() : 'N/A'} Totes - ${robotfpp2}</span></td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${robotfpp}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${RPvol !== null ? RPvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${RPtote !== null ? RPtote.toLocaleString() : 'N/A'} </td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(robotPalletizeRow);

    // Manual Tote Palletize Row
    const manualtotePalletizeRow = document.createElement('tr');
    const manualtotevol = TPvol - RPvol;
    const manualtotetote = TPtote - RPtote;
    const TPrate2 = TPhours2 && TPhours2 > 0 ? manualtotetote / TPhours2 : 'N/A';
    const manualtotefpp = daTotal ? ((manualtotevol / daTotal) * 100).toFixed(1) + '%' : '0%';
    const manualtotefpp2 = dajobs ? ((manualtotetote / dajobs) * 100).toFixed(1) + '%' : '0%';
    sessionStorage.setItem('TPrate2', TPrate2);
    manualtotePalletizeRow.innerHTML = `

<td style="background-color: #ffffff; color: rgb(0, 0, 0); font-weight: normal; font-size: 12px; padding: 5px 5px 5px 30px; padding-left: 20px;" colspan="3">Manual Palletize Tote -  <span style="color: #4f5a66 ;font-size: 11px;">${manualtotetote !== null ? manualtotetote.toLocaleString() : 'N/A'} Totes - ${manualtotefpp2}</span></td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${manualtotefpp}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${manualtotevol !== null ? manualtotevol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${manualtotetote !== null ? manualtotetote.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${TPhours2 !== null ? TPhours2.toLocaleString() : 'N/A'}</td>
<td style="background-color: #ffffff; color: #000; font-weight: normal; font-size: 12px; text-align: center;">${TPrate2 !== 'N/A' ? Math.round(TPrate2).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(manualtotePalletizeRow);
}

// Fila para TSO (PAX DA)
const TSORow = document.createElement('tr');
const TSOfpp = daTotal ? ((TSOvol / daTotal) * 100).toFixed(1) + '%' : '0%';
const paxgap = palletReceive - TSOpallets;

TSORow.innerHTML = `

<td colspan="3" style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 15px;">
PAX DA - <span style="color: #4f5a66;font-size: 11px; ">${TSOpallets !== null ? TSOpallets.toLocaleString() : 'N/A'} Pallets</span>
<div style="font-weight: normal; font-size: 11px; margin-top: 3px; color: #4f5a66;">
<div style="margin-left: 10px;"><span style="font-style: italic;">PAX GAP (IB-DA)</span>: ${paxgap !== null ? paxgap.toLocaleString() : 'N/A'} Pallets</div>
</div>
</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOfpp}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOvol !== null ? TSOvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOpallets !== null ? TSOpallets.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOhours !== null ? TSOhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOrate !== null ? Math.round(TSOrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(TSORow);

// QAPS row con dropdown
const qapsRow = document.createElement('tr');
const isQAPSExpanded = localStorage.getItem('isQAPSExpanded') === 'true';
qapsRow.innerHTML = `

<td class="process-cell" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;" rowspan="${isQAPSExpanded ? '4' : '1'}">QAPS</td>
<td class="no-left-border" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;" colspan="3">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span>QAPS - Total</span>
<button class="dropdown-toggle" style="background: none; border: none; color: #2E3944; cursor: pointer;font-size: 10px;">
${isQAPSExpanded ? 'Hide details' : 'Show details'}
<i class="fas fa-chevron-${isQAPSExpanded ? 'up' : 'down'}" style="margin-left: 5px; font-size: 13px;"></i>
</button>
</td>
<td class="fpp-cell" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${buildingHshare} <span style="font-weight: normal">h</span></td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${QAPShours !== null ? QAPShours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(qapsRow);

// IBPS row
const ibpsRow = document.createElement('tr');
ibpsRow.className = 'qaps-detail';
ibpsRow.style.display = isQAPSExpanded ? 'table-row' : 'none';
ibpsRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">IB Problem Solve <span style="color: #4f5a66 ;"></td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${buildingHIBPS} <span style="font-weight: normal">h</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${IBPSvol !== null ? IBPSvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${IBPShours !== null ? IBPShours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${IBPSrate !== null ? Math.round(IBPSrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(ibpsRow);

// TSOPS row
const tsopsRow = document.createElement('tr');
tsopsRow.className = 'qaps-detail';
tsopsRow.style.display = isQAPSExpanded ? 'table-row' : 'none';
tsopsRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">TSO Problem Solve <span style="color: #4f5a66 ;"></td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${buildingHTSOPS} <span style="font-weight: normal">h</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOPSvol !== null ? TSOPSvol.toLocaleString() : 'N/A'}</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOPShours !== null ? TSOPShours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${TSOPSrate !== null ? Math.round(TSOPSrate).toLocaleString() : 'N/A'}</td>
`;
contentRows.appendChild(tsopsRow);

// ICQA row
const icqaRow = document.createElement('tr');
icqaRow.className = 'qaps-detail';
icqaRow.style.display = isQAPSExpanded ? 'table-row' : 'none';
icqaRow.innerHTML = `

<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3"> IC/QA/CS <span style="color: #4f5a66 ;"></td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${buildingHICQA} <span style="font-weight: normal">h</span></td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${ICQAhours !== null ? ICQAhours.toLocaleString() : 'N/A'}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(icqaRow);

// Agregar el evento click para mostrar/ocultar detalles
const dropdownToggle = qapsRow.querySelector('.dropdown-toggle');
dropdownToggle.addEventListener('click', function () {
    const icon = this.querySelector('i');
    const detailRows = document.querySelectorAll('.qaps-detail');
    const isExpanded = icon.classList.contains('fa-chevron-up');
    const processCell = qapsRow.querySelector('.process-cell');

    detailRows.forEach(row => {
        row.style.display = isExpanded ? 'none' : 'table-row';
    });

    // Ajustar el rowspan basado en si está expandido o contraído
    processCell.setAttribute('rowspan', isExpanded ? '1' : '4');

    // Actualizar el texto del botón
    this.innerHTML = `
${isExpanded ? 'Show details' : 'Hide details'}
<i class="fas fa-chevron-${isExpanded ? 'down' : 'up'}" style="margin-left: 5px; font-size: 13px;"></i>

`;

    // Guardar el estado en localStorage
    localStorage.setItem('isQAPSExpanded', !isExpanded);
});


// Después de crear todas las filas QAPS, añade estas líneas:
setTimeout(() => {
    // Crear el tooltip solo si no existe
    if (!document.querySelector('.fpp-tooltip')) {
        const tooltip = document.createElement('div');
        tooltip.className = 'fpp-tooltip';
        tooltip.textContent = 'Building hour share';
        Object.assign(tooltip.style, {
            position: 'fixed', // Cambiado de 'absolute' a 'fixed'
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            pointerEvents: 'none',
            zIndex: '1000',
            display: 'none'
        });
        document.body.appendChild(tooltip);
    }

    // Agregar los event listeners a las celdas FPP
    const tooltip = document.querySelector('.fpp-tooltip');
    const fppCells = document.querySelectorAll('.fpp-cell');

    fppCells.forEach(cell => {
        cell.addEventListener('mousemove', (e) => {
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX + 10) + 'px';
            tooltip.style.top = (e.clientY + 10) + 'px';
        });

        cell.addEventListener('mouseout', () => {
            tooltip.style.display = 'none';
        });

        // Eliminar la línea que añadía el cursor help
        // cell.style.cursor = 'help';
    });
}, 100); // Pequeño delay para asegurar que los elementos existen

// Misc Hours row con dropdown
const miscRow = document.createElement('tr');
const isMiscExpanded = localStorage.getItem('isMiscExpanded') === 'true';

// Logs de valores recibidos de extractMiscData
console.log('%c➜ Valores recibidos de extractMiscData:', 'color: #2196F3; font-weight: bold;', misctotalHours);

miscRow.innerHTML = `
    <td class="process-cell" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center;" rowspan="${isMiscExpanded ? '7' : '1'}">Misc</td>
    <td class="no-left-border" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px;" colspan="3">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>Misc Hours - Total</span>
            <button class="misc-dropdown-toggle" style="background: none; border: none; color: #2E3944; cursor: pointer;font-size: 10px;">
                ${isMiscExpanded ? 'Hide details' : 'Show details'}
                <i class="fas fa-chevron-${isMiscExpanded ? 'up' : 'down'}" style="margin-left: 5px; font-size: 13px;"></i>
            </button>
        </div>
    </td>
    <td class="fpp-cell" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
    <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
    <td class="hidden-column" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
    <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof misctotalHours === 'number' ? misctotalHours.toFixed(2) : misctotalHours}</td>
    <td style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;

// Log después de crear la fila
console.log('%c➜ Fila de Misc Hours creada:', 'color: #9C27B0; font-weight: bold;', {
    totalMostrado: typeof misctotalHours === 'number' ? misctotalHours.toFixed(2) : misctotalHours,
    valoresIndividuales: {
        tomHours,
        tomTrainingHours,
        teamConnectHours,
        trainingHours,
        jambustersHours,
        fiveShours
    }
});

contentRows.appendChild(miscRow);

// TOM Hours row
const tomRow = document.createElement('tr');
tomRow.className = 'misc-detail';
tomRow.style.display = isMiscExpanded ? 'table-row' : 'none';
tomRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">TOM Hours
    <div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
        (TOM_ADMIN + TOM_YARD_CHECKIN/OUT + TOM_YARD_SPECIALISTS)
    </div>
</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof tomHours === 'number' ? tomHours.toFixed(2) : tomHours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(tomRow);

// TOM Training row
const tomTrainingRow = document.createElement('tr');
tomTrainingRow.className = 'misc-detail';
tomTrainingRow.style.display = isMiscExpanded ? 'table-row' : 'none';
tomTrainingRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: g: 5px 10px; padding-left: 20px;" colspan="3">TOM Trainings</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof tomTrainingHours === 'number' ? tomTrainingHours.toFixed(2) : tomTrainingHours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
console.log('%c➜ Fila TOM Training creada con valor:', 'color: #2196F3; font-weight: bold;', tomTrainingHours);
contentRows.appendChild(tomTrainingRow);

// Team Connects row
const teamConnectRow = document.createElement('tr');
teamConnectRow.className = 'misc-detail';
teamConnectRow.style.display = isMiscExpanded ? 'table-row' : 'none';
teamConnectRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">Team Connects</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof teamConnectHours === 'number' ? teamConnectHours.toFixed(2) : teamConnectHours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
    console.log('%c➜ Fila Team Connects creada con valor:', 'color: #2196F3; font-weight: bold;', teamConnectHours);
contentRows.appendChild(teamConnectRow);

// Training Hours row
const trainingRow = document.createElement('tr');
trainingRow.className = 'misc-detail';
trainingRow.style.display = isMiscExpanded ? 'table-row' : 'none';
trainingRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">Training Hours
<div style="font-weight: normal; font-size: 10px; margin-top: 3px; color: #4f5a66;">
        (LN_AMB_CLASSRM_TRAIN + LN_FC_TRAING_EVENTS + LN_TDRCLASSRM_TRAING)
    </div>
</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof trainingHours === 'number' ? trainingHours.toFixed(2) : trainingHours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(trainingRow);

// Jambusters row
const jambustersRow = document.createElement('tr');
jambustersRow.className = 'misc-detail';
jambustersRow.style.display = isMiscExpanded ? 'table-row' : 'none';
jambustersRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">Jambusters</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof jambustersHours === 'number' ? jambustersHours.toFixed(2) : jambustersHours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(jambustersRow);

// 5S row
const fiveSRow = document.createElement('tr');
fiveSRow.className = 'misc-detail';
fiveSRow.style.display = isMiscExpanded ? 'table-row' : 'none';
fiveSRow.innerHTML = `
<td style="background-color: #e9f3f5; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; padding-left: 20px;" colspan="3">5S</td>
<td class="fpp-cell" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td class="hidden-column" style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">${typeof fiveShours === 'number' ? fiveShours.toFixed(2) : fiveShours}</td>
<td style="background-color: #e9f3f5; color: #000; font-weight: bold; font-size: 12px; text-align: center;">-</td>
`;
contentRows.appendChild(fiveSRow);

// Agregar el evento click para mostrar/ocultar detalles de Misc
const miscDropdownToggle = miscRow.querySelector('.misc-dropdown-toggle');
miscDropdownToggle.addEventListener('click', function () {
    const icon = this.querySelector('i');
    const detailRows = document.querySelectorAll('.misc-detail');
    const isExpanded = icon.classList.contains('fa-chevron-up');
    const processCell = miscRow.querySelector('.process-cell');

    detailRows.forEach(row => {
        row.style.display = isExpanded ? 'none' : 'table-row';
    });

    // Ajustar el rowspan basado en si está expandido o contraído
    processCell.setAttribute('rowspan', isExpanded ? '1' : '7');

    // Actualizar el texto del botón
    this.innerHTML = `
        ${isExpanded ? 'Show details' : 'Hide details'}
        <i class="fas fa-chevron-${isExpanded ? 'down' : 'up'}" style="margin-left: 5px; font-size: 13px;"></i>
    `;

    // Guardar el estado en localStorage
    localStorage.setItem('isMiscExpanded', !isExpanded);
});

// Fila para Crossdock con el texto centrado visualmente hacia la primera columna
const crossdockRow = document.createElement('tr');
const crossdock = (ibTotal || 0) - (daTotal || 0);
crossdockRow.innerHTML = `

<td colspan="3" style="background-color: #b3c8d8; color: rgb(0, 0, 0); font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: left; border-bottom: none;">
<div style="display: flex; justify-content: center;">Crossdock volume</div>
</td>
<td colspan="5" style="background-color: #b3c8d8; color: #000; font-weight: bold; font-size: 12px; text-align: center; border-bottom: none;">
${crossdock !== null ? crossdock.toLocaleString() : 'N/A'}
</td>
`;
crossdockRow.id = 'crossdock-row';
crossdockRow.id = 'crossdock-row';
contentRows.appendChild(crossdockRow);

// Fila para Sev hours (solo si es mayor que 0)
if (sevhours > 0) {
    const sevHoursRow = document.createElement('tr');
    const sevReportURL = buildReportURL('1003047');
    sevHoursRow.innerHTML = `

<td colspan="3" style="background-color: #ffe6e8; font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: left; border-top: 1px solid black;">
<div style="display: flex; justify-content: center; align-items: center;">
<a href="${sevReportURL}" target="_blank" style="text-decoration: none; cursor: pointer; display: flex; align-items: center;" class="tooltip-trigger">
<span style="color: #8B0000; margin-right: 5px;">🚨 SEV 1/2 Event or Overstaffing hours 🚨</span>
</a>
</div>
</td>
<td colspan="5" style="background-color: #ffe6e8; color: #000; font-weight: bold; font-size: 12px; text-align: center;  border-top: 1px solid black; white-space: nowrap;">
${sevhours.toLocaleString()}
</td>
`;
contentRows.appendChild(sevHoursRow);
}

newTable.appendChild(contentRows);





function removeOuterBorders(table) {
    const rows = table.rows;
    const lastRowIndex = rows.length - 1;
    const lastColumnIndex = rows[0].cells.length - 1;

    for (let i = 0; i <= lastRowIndex; i++) {
        for (let j = 0; j <= lastColumnIndex; j++) {
            const cell = rows[i].cells[j];

            // Eliminar bordes superiores de la primera fila
            if (i === 0) {
                cell.style.borderTop = 'none';
            }

            // Eliminar bordes inferiores de la última fila visible
            if (i === lastRowIndex || (cell.rowSpan && i + cell.rowSpan - 1 === lastRowIndex)) {
                cell.style.borderBottom = 'none';
            }

            // Eliminar bordes izquierdos de la primera columna
            if (j === 0) {
                cell.style.borderLeft = 'none';
            }

            // Eliminar bordes derechos de la última columna
            if (j === lastColumnIndex || (cell.colSpan && j + cell.colSpan - 1 === lastColumnIndex)) {
                cell.style.borderRight = 'none';
            }
        }
    }

    // Ajuste específico para la fila de encabezado con FPP%, Volume, Hours, Rate
    const headerRow = table.querySelector('tr:nth-child(2)');
    if (headerRow) {
        const headerCells = headerRow.cells;
        for (let cell of headerCells) {
            cell.style.borderBottom = '1px solid black'; // o el color que prefieras
        }
    }
}



// Elimina los bordes exteriores
removeOuterBorders(newTable);


// Crea un contenedor para la tabla con margen inferior
const tableContainer = document.createElement('div');
tableContainer.style.marginBottom = '20px';

// Añade la tabla al contenedor
tableContainer.appendChild(newTable);

// Crea el div para el texto del desarrollador
const developerText = document.createElement('div');
Object.assign(developerText.style, {
    fontSize: '10px',
    color: '#666',
    textAlign: 'center',
    marginTop: '5px',
    width: '100%'
});

// Crear el texto inicial
developerText.appendChild(document.createTextNode('Developed by '));

// Crear el enlace a Phonetool
const authorLink = document.createElement('a');
authorLink.textContent = '@Gerpaes';
authorLink.href = 'https://phonetool.amazon.com/users/gerpaes';
authorLink.target = '_blank'; // Abrir en nueva pestaña
Object.assign(authorLink.style, {
    color: '#666',
    textDecoration: 'none',
    cursor: 'pointer'
});
developerText.appendChild(authorLink);

// Crear el texto separador
developerText.appendChild(document.createTextNode(' - '));

// Crear el enlace de descarga
const downloadLink = document.createElement('a');
downloadLink.textContent = 'Script download link';
downloadLink.href = 'https://axzile.corp.amazon.com/-/carthamus/script/ixd-summary-from-ppr';
Object.assign(downloadLink.style, {
    color: '#666',
    textDecoration: 'underline',
    cursor: 'pointer'
});

// Añadir evento de clic al enlace de descarga
downloadLink.addEventListener('click', function (e) {
    e.preventDefault();

    // Copiar al portapapeles
    navigator.clipboard.writeText(this.href)
        .then(() => {
            // Mostrar mensaje de copiado exitoso
            const message = document.createElement('div');
            message.textContent = 'Link copied to clipboard!';
            Object.assign(message.style, {
                position: 'fixed',
                top: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: '#4CAF50',
                color: 'white',
                padding: '10px',
                borderRadius: '5px',
                zIndex: '9999',
                fontSize: '12px'
            });
            document.body.appendChild(message);

            // Eliminar el mensaje después de 2 segundos
            setTimeout(() => {
                document.body.removeChild(message);
            }, 2000);
        })
        .catch(err => console.error('Error copying to clipboard:', err));

    // Abrir el enlace en una nueva pestaña
    window.open(this.href, '_blank');
});

// Añadir el enlace de descarga al div
developerText.appendChild(downloadLink);



// Añade el texto del desarrollador al contenedor
tableContainer.appendChild(developerText);



// Inserta el contenedor después del timestamp y antes del div con clase "disclaimer"
const timestampDiv = document.getElementById("timestamps");
const disclaimerDiv = document.querySelector('.disclaimer');

if (timestampDiv) {
    if (timestampDiv.nextSibling) {
        timestampDiv.parentNode.insertBefore(tableContainer, timestampDiv.nextSibling);
    } else {
        timestampDiv.parentNode.appendChild(tableContainer);
    }
} else if (disclaimerDiv) {
    disclaimerDiv.parentNode.insertBefore(tableContainer, disclaimerDiv);
} else {
    document.body.appendChild(tableContainer);
}



// Agregar evento de clic para contraer/expandir solo en el área toggle
const toggleArea = header.querySelector('.toggle-area');
toggleArea.addEventListener('click', function (event) {
    const arrow = this.querySelector('.toggle-arrow');
    const content = document.getElementById('content-rows');
    if (content.style.display === 'none') {
        content.style.display = '';
        arrow.innerHTML = '&#9660;';
        localStorage.setItem('ixdSummaryExpanded', 'true');
    } else {
        content.style.display = 'none';
        arrow.innerHTML = '&#9654;';
        localStorage.setItem('ixdSummaryExpanded', 'false');
    }
});

// Función para establecer el estado inicial de expandido/contraido
function setInitialState() {
    const content = document.getElementById('content-rows');
    const arrow = toggleArea.querySelector('.toggle-arrow');
    const isExpanded = localStorage.getItem('ixdSummaryExpanded');

    if (isExpanded === 'false') {
        content.style.display = 'none';
        arrow.innerHTML = '&#9654;';
    } else {
        content.style.display = '';
        arrow.innerHTML = '&#9660;';
    }
}

setInitialState();
if (localStorage.getItem('ixdSummaryExpanded') === null) {
    contentRows.style.display = '';
    localStorage.setItem('ixdSummaryExpanded', 'true');
}

}

// Función para aclarar un color RGB
function lightenColor(color, percent) {
const rgb = color.match(/\d+/g);
let r = parseInt(rgb[0], 10);
let g = parseInt(rgb[1], 10);
let b = parseInt(rgb[2], 10);

r = Math.min(255, Math.floor(r + (255 - r) * percent));
g = Math.min(255, Math.floor(g + (255 - g) * percent));
b = Math.min(255, Math.floor(b + (255 - b) * percent));

return `rgb(${r}, ${g}, ${b})`;

}

// Obtener parámetros de la página principal
const params = getCurrentPageParameters();

// Obtener los valores de la página principal

const mainPageValues = {
ibTotal: extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.actualVolume.numeric div.original') || 0,
inbound: extractNumericValue('tr[id="ppr.fcSummary.vendorRec"] td.actualVolume.numeric div.original') || 0,
inboundhours: extractNumericValue('tr[id="ppr.fcSummary.vendorRec"] td.numeric.actualTimeSeconds div.original') || 0,
inboundrate: extractNumericValue('tr[id="ppr.fcSummary.vendorRec"] td.numeric.actualProductivity.rate div.original') || 0,
transin: extractNumericValue('tr[id="ppr.fcSummary.transferIn"] td.actualVolume.numeric div.original') || 0,
transinhours: extractNumericValue('tr[id="ppr.fcSummary.transferIn"] td.numeric.actualTimeSeconds div.original') || 0,
transinrate: extractNumericValue('tr[id="ppr.fcSummary.transferIn"] td.numeric.actualProductivity.rate div.original') || 0,
ERvol: extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.actualVolume.numeric div.original') || 0,
ERSvol: extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.small"] td.actualVolume.numeric div.original') || 0,
ERMvol: extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.medium"] td.actualVolume.numeric div.original') || 0,
ERLvol: extractNumericValue('tr[id="ppr.detail.inbonbound.receive.eachReceive.large"] td.actualVolume.numeric div.original') || 0,
ERhours: extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.numeric.actualTimeSeconds div.original') || 0,
ERrate: extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.numeric.actualProductivity.rate div.original') || 0,
prepvol: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.actualVolume.numeric div.original') || 0,
prepSvol: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.small"] td.actualVolume.numeric div.original') || 0,
prepMvol: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.medium"] td.actualVolume.numeric div.original') || 0,
prepLvol: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.large"] td.actualVolume.numeric div.original') || 0,
prephours: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.numeric.actualTimeSeconds div.original') || 0,
preprate: extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.numeric.actualProductivity.rate div.original') || 0,
daTotal: extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.actualVolume.numeric div.original') || 0,
ibHours: extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.numeric.actualTimeSeconds div.original') || 0,
daHours: extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.numeric.actualTimeSeconds div.original') || 0,
ibRate: extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.numeric.actualProductivity.rate div.original') || 0,
daRate: extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.numeric.actualProductivity.rate div.original') || 0,
LPreceive: extractNumericValue('tr[id="ppr.detail.inbound.receive.lpReceive"] td.actualVolume.numeric div.original') || 0,
palletReceive: extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.actualVolume.numeric div.original') || 0,
palletTIrate: extractNumericValue('tr[id="ppr.detail.inbound.transferInAndStow.palletTransferIn"] td.numeric.actualProductivity.rate div.original') || 0,
palletrate: extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.numeric.actualProductivity.rate div.original') || 0,
sortVolume: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.actualVolume.numeric div.original') || 0,
sortVolumesmall: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.small"] td.actualVolume.numeric div.original') || 0,
sortHours: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.numeric.actualTimeSeconds div.original') || 0,
tphH: extractNumericValue('tr[id="ppr.rcSummary.throughput"] td.numeric.actualTimeSeconds div.original') || 0,
sevhours: extractNumericValue('tr[id="ppr.detail.support.support.nonFCControllable"] td.numeric.actualTimeSeconds div.original') || 0,
IBPSvol: extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.actualVolume.numeric div.original') || 0,
IBPShours: extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.numeric.actualTimeSeconds div.original') || 0,
IBPSrate: extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.numeric.actualProductivity.rate div.original') || 0,
TSOPSvol: extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.actualVolume.numeric div.original') || 0,
TSOPShours: extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.numeric.actualTimeSeconds div.original') || 0,
TSOPSrate: extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.numeric.actualProductivity.rate div.original') || 0,
ICQAvol: extractNumericValue('tr[id="ppr.detail.support.support.ICQACS"] td.actualVolume.numeric div.original') || 0,
ICQAhours: extractNumericValue('tr[id="ppr.detail.support.support.ICQACS"] td.numeric.actualTimeSeconds div.original') || 0,
ICQArate: extractNumericValue('tr[id="ppr.detail.support.support.ICQACS"] td.numeric.actualProductivity.rate div.original') || 0,
RShours: extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveSupport"] td.numeric.actualTimeSeconds div.original') || 0,
Transferouthours: extractNumericValue('tr[id="ppr.detail.da.transferOut.transferOut"] td.numeric.actualTimeSeconds div.original') || 0,
TSOdockhours: extractNumericValue('tr[id="ppr.detail.da.transferOutDock.transferOutDock"] td.numeric.actualTimeSeconds div.original') || 0,
presortCases: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.actualVolume.numeric div.original') || 0,
presortCasesVolume: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.actualVolume.numeric div.original') || 0,
presortCasesHours: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.numeric.actualTimeSeconds div.original') || 0,
presortCasesRate: extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.numeric.actualProductivity.rate div.original') || 0

};

// Calcular valores derivados
const totalHours = (mainPageValues.ibHours || 0) + (mainPageValues.daHours || 0);
const sortShare = (mainPageValues.daTotal && mainPageValues.sortVolume) ? (mainPageValues.sortVolume / mainPageValues.daTotal) * 100 : 0;
const QAPShours = (mainPageValues.IBPShours || 0) + (mainPageValues.TSOPShours || 0) + (mainPageValues.ICQAhours || 0);
const QAPSvol = (mainPageValues.IBPSvol || 0) + (mainPageValues.TSOPSvol || 0) + (mainPageValues.ICQAvol || 0);
const buildingHshare = mainPageValues.tphH ? ((QAPShours / mainPageValues.tphH) * 100).toFixed(2) + '%' : '0%';
const buildingHIBPS = mainPageValues.tphH ? ((mainPageValues.IBPShours / mainPageValues.tphH) * 100).toFixed(2) + '%' : '0%';
const buildingHTSOPS = mainPageValues.tphH ? ((mainPageValues.TSOPShours / mainPageValues.tphH) * 100).toFixed(2) + '%' : '0%';
const buildingHICQA = mainPageValues.tphH ? ((mainPageValues.ICQAhours / mainPageValues.tphH) * 100).toFixed(2) + '%' : '0%';

// Función para construir URLs de reportes
function buildReportURL(processId) {
    const baseUrl = 'https://fclm-portal.amazon.com/reports/functionRollup';
    return `${baseUrl}?reportFormat=HTML&warehouseId=${params.warehouseId}&processId=${processId}&maxIntradayDays=1&spanType=${params.spanType}&startDate${params.spanType}=${params.startDate}&startHourIntraday=${params.startHour}&startMinuteIntraday=${params.startMinute}&endDate${params.spanType}=${params.endDate}&endHourIntraday=${params.endHour}&endMinuteIntraday=${params.endMinute}`;
}

    // Funcion para construir URLs de Misc hours
function buildReportURLMisc() {
    const baseUrl = 'https://fclm-portal.amazon.com/reports/functionRollup';
    const url = `${baseUrl}?reportFormat=HTML&warehouseId=${params.warehouseId}&processId=1002960&maxIntradayDays=1&spanType=${params.spanType}&startDate${params.spanType}=${params.startDate}&startHourIntraday=${params.startHour}&startMinuteIntraday=${params.startMinute}&endDate${params.spanType}=${params.endDate}&endHourIntraday=${params.endHour}&endMinuteIntraday=${params.endMinute}`;

    console.log('\n');
    console.log('%c╔════════════════════════════════════════════════════════════════════════════════╗', 'color: #4CAF50; font-weight: bold;');
    console.log('%c║                              MISC HOURS URL                                    ║', 'color: #4CAF50; font-weight: bold;');
    console.log('%c╠════════════════════════════════════════════════════════════════════════════════╣', 'color: #4CAF50; font-weight: bold;');
    console.log('%c║ ' + url, 'color: #2196F3; font-weight: bold; background-color: #f0f0f0; padding: 5px;');
    console.log('%c╚════════════════════════════════════════════════════════════════════════════════╝', 'color: #4CAF50; font-weight: bold;');
    console.log('\n');

    return url;
}

    // Funcion para construir URLs de Jambusters hours
function buildReportURLJambusters() {
    const baseUrl = 'https://fclm-portal.amazon.com/reports/functionRollup';
    const url = `${baseUrl}?reportFormat=HTML&warehouseId=${params.warehouseId}&processId=1003028&maxIntradayDays=1&spanType=${params.spanType}&startDate${params.spanType}=${params.startDate}&startHourIntraday=${params.startHour}&startMinuteIntraday=${params.startMinute}&endDate${params.spanType}=${params.endDate}&endHourIntraday=${params.endHour}&endMinuteIntraday=${params.endMinute}`;

    console.log('\n');
    console.log('%c╔════════════════════════════════════════════════════════════════════════════════╗', 'color: #4CAF50; font-weight: bold;');
    console.log('%c║                            JAMBUSTERS HOURS URL                                ║', 'color: #4CAF50; font-weight: bold;');
    console.log('%c╠════════════════════════════════════════════════════════════════════════════════╣', 'color: #4CAF50; font-weight: bold;');
    console.log('%c║ ' + url, 'color: #2196F3; font-weight: bold; background-color: #f0f0f0; padding: 5px;');
    console.log('%c╚════════════════════════════════════════════════════════════════════════════════╝', 'color: #4CAF50; font-weight: bold;');
    console.log('\n');

    return url;
}

// Función para hacer fetch y parsear el HTML
async function fetchAndParse(url) {
const response = await fetch(url);
const text = await response.text();
return new DOMParser().parseFromString(text, 'text/html');
}

// Función para extraer datos de UPC
function extractUPCData(doc) {
const targetRow = doc.querySelector('tr.total.empl-all');
if (!targetRow) return {};

const cells = targetRow.querySelectorAll('td.numeric');
const eachTotal = parseFloat(cells[3]?.textContent.replace(/[\s,]/g, '') || '0');
const caseTotal = parseFloat(cells[7]?.textContent.replace(/[\s,]/g, '') || '0');
const LPupc = (eachTotal && caseTotal) ? parseFloat((eachTotal / caseTotal).toFixed(2)) : 0;
const eachColor = cells[3] ? window.getComputedStyle(cells[3]).backgroundColor : '';

const extractUPC = (tableSelector, eachSelector, caseSelector) => {
    const table = doc.querySelector(tableSelector);
    if (!table) return 0;
    const eachCell = table.querySelector(eachSelector);
    const caseCell = table.querySelector(caseSelector);
    if (!eachCell || !caseCell) return 0;
    const eachValue = parseFloat(getValueOrNA(eachCell)) || 0;
    const caseValue = parseFloat(getValueOrNA(caseCell)) || 0;
    return (eachValue && caseValue) ? parseFloat((eachValue / caseValue).toFixed(2)) : 0;
};

const pidUpc = extractUPC('table#function-4300018908', 'tfoot tr.total.empl-amzn td.numeric.size-total.highlighted', 'tfoot tr td:nth-of-type(18)');
const prEditorUpc = extractUPC('table#function-4300034939', 'tfoot tr td:nth-of-type(16)', 'tfoot tr td:nth-of-type(18)');
const arosUpc = extractUPC('table#function-1598050091281', 'tfoot tr td:nth-of-type(16)', 'tfoot tr td:nth-of-type(18)');

// Extraction for cases
const pidcases = parseFloat(getValueOrNA(doc.querySelector('table#function-4300018908 tfoot tr td:nth-of-type(18)'))) || 0;
const preditorcases = parseFloat(getValueOrNA(doc.querySelector('table#function-4300034939 tfoot tr td:nth-of-type(18)'))) || 0;
const aroscases = parseFloat(getValueOrNA(doc.querySelector('table#function-1598050091281 tfoot tr td:nth-of-type(18)'))) || 0;

// Extraction for volumes
const pidvol = parseFloat(getValueOrNA(doc.querySelector('table#function-4300018908 tfoot tr td:nth-of-type(16)'))) || 0;
const preditorvol = parseFloat(getValueOrNA(doc.querySelector('table#function-4300034939 tfoot tr td:nth-of-type(16)'))) || 0;
const arosvol = parseFloat(getValueOrNA(doc.querySelector('table#function-1598050091281 tfoot tr td:nth-of-type(16)'))) || 0;

// Extraction for preditor hours and rate
const preditorhours = parseFloat(getValueOrNA(doc.querySelector('table#function-4300034939 tfoot tr td:nth-of-type(5)'))) || 0;
const preditorrate = parseFloat(getValueOrNA(doc.querySelector('table#function-4300034939 tfoot tr td:nth-of-type(17)'))) || 0;
sessionStorage.setItem('preditorrate', preditorrate);
return { LPupc, eachTotal, caseTotal, eachColor, pidUpc, prEditorUpc, arosUpc, pidcases, preditorcases, aroscases, pidvol, preditorvol, arosvol, preditorhours, preditorrate };

}

// Definición global de extractNumericValueForReports
function extractNumericValueForReports(element, isHours = false) {
if (!element) return null;

const text = element.textContent.trim();

const hasCommaAsDecimal = /\d+,\d+$/.test(text);
const hasDotAsDecimal = /\d+\.\d+$/.test(text);
const hasCommaAsThousands = /\d{1,3}(,\d{3})+/.test(text);
const hasDotAsThousands = /\d{1,3}(\.\d{3})+/.test(text);

let value;
if (hasCommaAsThousands && hasDotAsDecimal) {
    value = parseFloat(text.replace(/,/g, ''));
} else if (hasDotAsThousands && hasCommaAsDecimal) {
    value = parseFloat(text.replace(/\./g, '').replace(',', '.'));
} else if (hasCommaAsDecimal) {
    value = parseFloat(text.replace(',', '.'));
} else {
    value = parseFloat(text);
}

if (isNaN(value)) return null;

if (isHours || hasCommaAsDecimal || hasDotAsDecimal) {
    return Number(value.toFixed(2));
}

return value;

}

// Función para extraer datos de Sort
function extractSortData(doc) {
const extractTableData = (tableId) => {
const table = doc.querySelector(`table#${tableId}`);
if (!table) return {
volume: 0,
hours: 0,
rate: 0,
Svolume: 0,
Mvolume: 0,
Lvolume: 0
};

    const cells = Array.from(table.querySelectorAll('tfoot tr td'));
    const getValue = (index, isHours = false) => extractNumericValueForReports(cells[index], isHours) || 0;

    return {
        volume: getValue(15),
        hours: getValue(4, true),
        Svolume: getValue(7),
        Mvolume: getValue(9),
        Lvolume: getValue(11)
    };
};

const extractUPTData = (tableId) => {
    const table = doc.querySelector(`table#${tableId}`);
    if (!table) return 0;
    const cells = Array.from(table.querySelectorAll('tfoot tr td'));
    return extractNumericValueForReports(cells[7]) || 0;
};

const uis5Data1 = extractTableData('function-1588886488518');
const uis5Data2 = extractTableData('function-1748942467646');
const uis20Data1 = extractTableData('function-1588886757628');
const uis20Data2 = extractTableData('function-1748942479650');

const uis5 = {
    volume: uis5Data1.volume + uis5Data2.volume,
    hours: uis5Data1.hours + uis5Data2.hours,
    Svolume: uis5Data1.Svolume + uis5Data2.Svolume,
    Mvolume: uis5Data1.Mvolume + uis5Data2.Mvolume,
    Lvolume: uis5Data1.Lvolume + uis5Data2.Lvolume,
};
uis5.rate = uis5.hours > 0 ? uis5.volume / uis5.hours : 0;

const uis20 = {
    volume: uis20Data1.volume + uis20Data2.volume,
    hours: uis20Data1.hours + uis20Data2.hours,
    Svolume: uis20Data1.Svolume + uis20Data2.Svolume,
    Mvolume: uis20Data1.Mvolume + uis20Data2.Mvolume,
    Lvolume: uis20Data1.Lvolume + uis20Data2.Lvolume,
};
uis20.rate = uis20.hours > 0 ? uis20.volume / uis20.hours : 0;

const tableIds = ['function-4300006775', 'function-4300006777'];
const data = Object.fromEntries(tableIds.map(id => [id, extractTableData(id)]));

// Save rates to sessionStorage
sessionStorage.setItem('uis5rate', uis5.rate.toString());
sessionStorage.setItem('uis20rate', uis20.rate.toString());

return {
    ms: data['function-4300006775'],
    ms2: data['function-4300006777'],
    uis5: uis5,
    uis20: uis20,
    uis5upt: extractUPTData('function-1588886632019'),
    uis20upt: extractUPTData('function-1588886928371')
};

}

// Función para extraer datos de DA
function extractDAData(doc) {
const extractCellData = (tableId, tfootIndex = 3, trIndex = 0) => {
const getCellValue = (selector, isHours = false) => {
const element = doc.querySelector(selector);
return extractNumericValueForReports(element, isHours) || 0;
};

    return {
        each: getCellValue(`#${tableId} tfoot tr:nth-child(${trIndex + 1}) td:nth-child(17)`),
        case: getCellValue(`#${tableId} tfoot tr:nth-child(${trIndex + 1}) td:nth-child(19)`),
        hours: getCellValue(`#${tableId} tfoot tr:nth-child(${trIndex + 1}) td:nth-child(6)`, true),
        rate: getCellValue(`#${tableId} tfoot tr:nth-child(${trIndex + 1}) td:nth-child(20)`),
        pallets: getCellValue(`#${tableId} tfoot tr:nth-child(${trIndex + 1}) td:nth-child(21)`),
    };
};

const FL = {
    case: extractCellData('function-4300032947'),
    tote: extractCellData('function-4300032948'),
    wallhours: (() => {
        const element = doc.querySelector('#function-1540335693954 tfoot tr td:nth-child(6)');
        return extractNumericValueForReports(element, true) || 0;
    })(),
    casehours: (() => {
        const element = doc.querySelector('#function-4300032947 tfoot tr td:nth-child(6)');
        return extractNumericValueForReports(element, true) || 0;
    })(),
    totehours: (() => {
        const element = doc.querySelector('#function-4300032948 tfoot tr td:nth-child(6)');
        return extractNumericValueForReports(element, true) || 0;
    })()
};

const flcasecase = FL.case.case;
const fltotecase = FL.tote.case;

const MP = extractCellData('function-4300032950');
const TP = extractCellData('function-4300032949');
const TSO = extractCellData('function-4300006839');

// Extracción de RPvol, RPtote y TPhours2
let RPvol = 0;
let RPtote = 0;
let TPhours2 = 0;

const rows = doc.querySelectorAll('table#function-4300032949 tbody tr');
for (const row of rows) {
    const nameCell = row.querySelector('td:nth-child(3)');

    if (nameCell) {
        const name = nameCell.textContent.trim().toLowerCase();

        // Para usuarios anonymous
        if (name === 'anonymous') {
            const eachTotalCell = row.querySelector('td.numeric.size-total.highlighted:nth-of-type(20)');
            const toteTotalCell = row.querySelector('td.numeric.size-total.highlighted:nth-of-type(22)');
            if (eachTotalCell) {
                RPvol = extractNumericValueForReports(eachTotalCell) || 0;
            }
            if (toteTotalCell) {
                RPtote = extractNumericValueForReports(toteTotalCell) || 0;
            }
        }
        // Para usuarios NO anonymous
        else {
            // Buscar el valor de jobs en la primera columna de jobs (columna 10)
            const jobsCell = row.querySelector('td:nth-child(10)');
            if (jobsCell && jobsCell.textContent.trim() !== '') {
                // Si hay jobs, obtener las horas de la columna 5 (paid hours)
                const hoursCell = row.querySelector('td:nth-child(5)');
                if (hoursCell) {
                    const hours = extractNumericValueForReports(hoursCell) || 0;
                    TPhours2 += hours;
                }
            }
        }
    }
}

const headerRow = doc.querySelector('thead tr:nth-child(2)');

let toteIndices = [];
let columnCount = 0;

if (headerRow) {
    const cells = headerRow.querySelectorAll('th');
    cells.forEach((cell) => {
        if (cell.hasAttribute('rowspan') && cell.classList.contains('jph')) {
            columnCount += 1;
        } else if (cell.hasAttribute('colspan')) {
            const colspan = parseInt(cell.getAttribute('colspan'), 10);
            const cellText = cell.textContent.trim();
            if (cellText === 'Tote') {
                toteIndices.push(columnCount + 1);
            }
            columnCount += colspan;
        }
    });
}

let totalTotes = 0;
const totalRow = doc.querySelector('tfoot tr.total.empl-all');
if (totalRow) {
    const numericCells = totalRow.querySelectorAll('td.numeric');
    toteIndices.forEach(index => {
        if (index < numericCells.length) {
            const toteValue = extractNumericValueForReports(numericCells[index]) || 0;
            totalTotes += toteValue;
        }
    });
}
const FLThours = FL.wallhours + FL.totehours + FL.casehours ;
const FLvol = FL.case.each + FL.tote.each;
const FLrate = FLThours ? ((FL.case.case + FL.tote.case) / FLThours).toFixed(2) : '0';
const FLCycleTime = FLThours && FLvol ? (60 / (((FL.case.case + FL.tote.case) / FLThours) / 60)).toFixed(2) : '0';
const FLshare = FLvol && mainPageValues.daTotal ? `${((FLvol / mainPageValues.daTotal) * 100).toFixed(2)}%` : '0%';
const DAupc = ((FL.case.each + MP.each) / (FL.case.case + MP.case || 1)).toFixed(2);
const DAupt = ((FL.tote.each + TP.each) / (FL.tote.case + TP.case || 1)).toFixed(2);
const FLupc = ((FL.case.each) / (FL.case.case || 1)).toFixed(2);
const FLupt = ((FL.tote.each) / (FL.tote.case || 1)).toFixed(2);
const MPupc = ((MP.each) / (MP.case || 1)).toFixed(2);
const TPupt = ((TP.each) / (TP.case || 1)).toFixed(2);

const toteshare = `${(((FL.tote.case + TP.case) / (FL.tote.case + TP.case + FL.case.case + MP.case || 1)) * 100).toFixed(2)}%`;
const caseshare = `${(((FL.case.case + MP.case) / (FL.tote.case + TP.case + FL.case.case + MP.case || 1)) * 100).toFixed(2)}%`;

return { FLThours, FLvol, FLrate, FL, MP, TP, TSO, FLshare, DAupc, DAupt, FLupc, FLupt, MPupc, TPupt, toteshare, caseshare, totalTotes, RPvol, flcasecase, fltotecase, RPtote, TPhours2 ,FLCycleTime };

}

// Función para extraer datos de Transfer-In Pallet (United states)
function extractPalletTIData(doc) {
const targetRow = doc.querySelector('tr.total.empl-all');
if (!targetRow) {
return {
palletunits: 0,
palletvol: 0,
pallethours: 0,
palletcases: 0,
};
}

const cells = targetRow.querySelectorAll('td.numeric');

const safeExtractNumericValue = (cell, isHours = false) => {
    return extractNumericValueForReports(cell, isHours) || 0;
};

return {
    palletunits: safeExtractNumericValue(cells[7]),
    palletvol: safeExtractNumericValue(cells[3]),
    pallethours: safeExtractNumericValue(cells[0], true),
    palletcases: safeExtractNumericValue(cells[5]),
};

}

// Función para extraer datos de Pallet
function extractPalletData(doc) {
const targetRow = doc.querySelector('tr.total.empl-all');
if (!targetRow) {
return {
palletunits: 0,
palletvol: 0,
pallethours: 0,
palletcases: 0,
LPpallet: 0
};
}

const cells = targetRow.querySelectorAll('td.numeric');

const safeExtractNumericValue = (cell, isHours = false) => {
    return extractNumericValueForReports(cell, isHours) || 0;
};

const LPpallet = (() => {
    const element = doc.querySelector('#function-1630434747379 tfoot tr td:nth-child(7)');
    return safeExtractNumericValue(element);
})();

return {
    palletunits: safeExtractNumericValue(cells[7]),
    palletvol: safeExtractNumericValue(cells[3]),
    pallethours: safeExtractNumericValue(cells[0], true),
    palletcases: safeExtractNumericValue(cells[5]),
    LPpallet
};

}

// Función para extraer datos de Pallets de Receive Dock
function extractreceivedockData(doc) {
console.log('Iniciando extracción de datos de Receive Dock...');

const functionHeaderRow = doc.querySelector('thead tr:first-child');
if (!functionHeaderRow) {
    console.error('No se encontró la fila de encabezado de función');
    return { RDpalletvol: 0, RDpalletcases: 0 };
}

const headers = Array.from(functionHeaderRow.querySelectorAll('th'));
let receiveDockIndex = -1;
let colspanSum = 0;

for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent.trim() === 'PalletReceived') {
        receiveDockIndex = i;
        break;
    }
    colspanSum += parseInt(headers[i].getAttribute('colspan') || '1', 10);
}

if (receiveDockIndex === -1) {
    console.error('No se encontró la columna PalletReceived');
    return { RDpalletvol: 0, RDpalletcases: 0 };
}

console.log('Índice de PalletReceived:', receiveDockIndex);
console.log('Suma de colspan antes de PalletReceived:', colspanSum);

const totalRow = doc.querySelector('tr.total.empl-all');
if (!totalRow) {
    console.error('No se encontró la fila de totales');
    return { RDpalletvol: 0, RDpalletcases: 0 };
}

const cells = Array.from(totalRow.querySelectorAll('td.numeric'));

const RDpalletvolIndex = colspanSum;
const RDpalletcasesIndex = colspanSum + 2;

const RDpalletvol = extractNumericValueForReports(cells[RDpalletvolIndex]) || 0;
const RDpalletcases = extractNumericValueForReports(cells[RDpalletcasesIndex]) || 0;

console.log('Índice de RDpalletvol:', RDpalletvolIndex);
console.log('Índice de RDpalletcases:', RDpalletcasesIndex);
console.log('RDpalletvol:', RDpalletvol);
console.log('RDpalletcases:', RDpalletcases);

return { RDpalletvol, RDpalletcases };

}

// Función para extraer datos de Pallets de IB Problem Solve
function extractIBpsData(doc) {
console.log('Iniciando extracción de datos...');

const functionHeaderRow = doc.querySelector('thead tr:first-child');
if (!functionHeaderRow) {
    console.error('No se encontró la fila de encabezado de función');
    return { IBpalletvol: 0, IBpalletcases: 0 };
}

const headers = Array.from(functionHeaderRow.querySelectorAll('th'));
let palletReceivedIndex = -1;
let colspanSum = 0;

for (let i = 0; i < headers.length; i++) {
    if (headers[i].textContent.trim() === 'PalletReceived') {
        palletReceivedIndex = i;
        break;
    }
    colspanSum += parseInt(headers[i].getAttribute('colspan') || '1', 10);
}

if (palletReceivedIndex === -1) {
    console.error('No se encontró la columna PalletReceived');
    return { IBpalletvol: 0, IBpalletcases: 0 };
}

console.log('Índice de PalletReceived:', palletReceivedIndex);
console.log('Suma de colspan antes de PalletReceived:', colspanSum);

const totalRow = doc.querySelector('tr.total.empl-all');
if (!totalRow) {
    console.error('No se encontró la fila de totales');
    return { IBpalletvol: 0, IBpalletcases: 0 };
}

const cells = Array.from(totalRow.querySelectorAll('td.numeric'));

const IBpalletvolIndex = colspanSum;
const IBpalletcasesIndex = colspanSum + 2;

const IBpalletvol = extractNumericValueForReports(cells[IBpalletvolIndex]) || 0;
const IBpalletcases = extractNumericValueForReports(cells[IBpalletcasesIndex]) || 0;

console.log('Índice de IBpalletvol:', IBpalletvolIndex);
console.log('Índice de IBpalletcases:', IBpalletcasesIndex);
console.log('IBpalletvol:', IBpalletvol);
console.log('IBpalletcases:', IBpalletcases);

return { IBpalletvol, IBpalletcases };

}

// Función para extraer datos de Decant
function extractdecantData(doc) {
const table = doc.querySelector('table#function-4300014829');
if (!table) return { volume: 0, hours: 0, rate: 0 };

const cells = table.querySelectorAll('tfoot tr td');
return {
    volume: extractNumericValueForReports(cells[15]) || 0,
    Svol: extractNumericValueForReports(cells[7]) || 0,
    Mvol: extractNumericValueForReports(cells[9]) || 0,
    Lvol: extractNumericValueForReports(cells[11]) || 0,
    hours: extractNumericValueForReports(cells[4], true) || 0,
    rate: extractNumericValueForReports(cells[16]) || 0,
    case: extractNumericValueForReports(cells[17]) || 0,
};

}

// Función para extraer datos de Decant2 de RSR
function extractdecant2Data(doc) {
const table = doc.querySelector('table#function-4300016857');
if (!table) return { volume: 0, hours: 0, rate: 0 };

const cells = table.querySelectorAll('tfoot tr td');
return {
    volume: extractNumericValueForReports(cells[15]) || 0,
    Svol: extractNumericValueForReports(cells[7]) || 0,
    Mvol: extractNumericValueForReports(cells[9]) || 0,
    Lvol: extractNumericValueForReports(cells[11]) || 0,
    hours: extractNumericValueForReports(cells[4], true) || 0,
    rate: extractNumericValueForReports(cells[16]) || 0,
    case: extractNumericValueForReports(cells[17]) || 0,
};

}

    // Funcion para extraer datos de Misc hour
async function extractMiscData(doc) {
    console.log('\n');
    console.log('%c╔════════════════════════════════════════════╗', 'color: #9C27B0; font-weight: bold;');
    console.log('%c║        INICIANDO EXTRACCIÓN MISC DATA      ║', 'color: #9C27B0; font-weight: bold;');
    console.log('%c╚════════════════════════════════════════════╝', 'color: #9C27B0; font-weight: bold;');

    // Función auxiliar para extraer valores de una tabla
    const extractTableValue = (table, index = 4) => {
        if (!table) {
            console.warn('%c⚠️ Tabla no encontrada', 'color: #FFA500; font-weight: bold;');
            return 0;
        }
        const cells = table.querySelectorAll('tfoot tr td');
        return cells[index] ? extractNumericValueForReports(cells[index], true) || 0 : 0;
    };

    // Obtener referencias a todas las tablas
    const table = doc.querySelector('table#function-4300035077');
    const teamConnectTable = doc.querySelector('table#function-4300035091');
    const tomTable = doc.querySelector('table#function-1588624038482');
    const tomTable2 = doc.querySelector('table#function-4300035026');
    const tomTable3 = doc.querySelector('table#function-4300035028');
    const trainingTable1 = doc.querySelector('table#function-4300035014');
    const trainingTable2 = doc.querySelector('table#function-4300035018');
    const trainingTable3 = doc.querySelector('table#function-4300035017');

    const tomTrainingHours = extractTableValue(table);
    const teamConnectHours = extractTableValue(teamConnectTable);

    const tomHours1 = extractTableValue(tomTable);
    const tomHours2 = extractTableValue(tomTable2);
    const tomHours3 = extractTableValue(tomTable3);
    const tomHours = tomHours1 + tomHours2 + tomHours3;

    const trainingHours1 = extractTableValue(trainingTable1);
    const trainingHours2 = extractTableValue(trainingTable2);
    const trainingHours3 = extractTableValue(trainingTable3);
    const trainingHours = trainingHours1 + trainingHours2 + trainingHours3;

    const jambustersUrl = buildReportURLJambusters();
const miscDoc = await fetchAndParse(jambustersUrl);
const jambustersTable = miscDoc.querySelector('table#function-4300004574');
const fiveSTable = miscDoc.querySelector('table#function-4300006665');
const jambustersHours = extractTableValue(jambustersTable);
const fiveShours = extractTableValue(fiveSTable);

    const miscData = {
        tomHours: tomHours,
        tomTrainingHours: tomTrainingHours,
        teamConnectHours: teamConnectHours,
        trainingHours: trainingHours,
        jambustersHours: jambustersHours,
        fiveShours: fiveShours,
    };

    // Calculamos la suma una sola vez
    miscData.misctotalHours = miscData.tomHours +
                           miscData.tomTrainingHours +
                           miscData.teamConnectHours +
                           miscData.trainingHours +
                           miscData.jambustersHours +
                           miscData.fiveShours;

    console.log('\n=== RESUMEN DE DATOS EXTRAÍDOS ===');
    console.log(JSON.stringify(miscData, null, 2));
    console.log('\n=== FIN EXTRACCIÓN DE DATOS MISC ===\n');

    return miscData;
}

// Función para extraer datos de Prep
function extractprepData(doc) {
// Objeto para mapear los tipos de prep que buscamos
const prepTypes = {
'PrepStickering': 'prepStick',
'PrepShrinkwrap': 'prepWrap',
'PrepOverbox': 'prepOverbox',
'PrepResearch': 'prepResearch',
'PrepOther': 'prepOther',
'PrepAssortment': 'prepAssort'
};

// Inicializar resultado con valores por defecto
const result = {
    prepStick: 0,
    prepWrap: 0,
    prepOverbox: 0,
    prepResearch: 0,
    prepOther: 0,
    prepAssort: 0
};

// Encontrar la fila de encabezados con los tipos de prep
const headerRow = doc.querySelector('thead tr:first-child');
if (!headerRow) return result;

// Encontrar la fila de totales (específicamente la que tiene class="total empl-all")
const totalRow = doc.querySelector('tr.total.empl-all');
if (!totalRow) return result;

// Para cada tipo de prep que buscamos
Object.entries(prepTypes).forEach(([prepHeader, resultKey]) => {
    // Encontrar la columna correspondiente
    const headers = headerRow.querySelectorAll('th.job-action');
    let columnStartIndex = 0;
    let found = false;

    for (let header of headers) {
        if (header.textContent.trim() === prepHeader) {
            found = true;
            break;
        }
        // Sumar el colspan de las columnas anteriores
        columnStartIndex += parseInt(header.getAttribute('colspan')) || 1;
    }

    if (found) {
        // En la fila de totales, necesitamos encontrar la celda correcta
        // Las celdas numéricas empiezan después de las dos primeras columnas de totales
        const cells = totalRow.querySelectorAll('td.numeric');
        // El valor EACH está en la tercera columna de cada grupo de 6 columnas
        const eachIndex = columnStartIndex + 3; // +2 para llegar al valor EACH

        if (cells[eachIndex]) {
            const value = parseFloat(cells[eachIndex].textContent.trim()) || 0;
            result[resultKey] = value;
        }
    }
});

return result;

}

// Funciones para Time Off Task
function extractNumber(str) {
if (!str) return 0;
const match = str.match(/\d+(.\d+)?/);
return match ? parseFloat(match[0]) : 0;
}

function parseTimeOnTaskData(htmlContent) {
const parser = new DOMParser();
const doc = parser.parseFromString(htmlContent, 'text/html');
const resultTable = doc.querySelector('table.sortable.result-table');

if (!resultTable) {
    return { totalTime: 0, timeOnTask: 0, hasData: false };
}

// Usar querySelectorAll una sola vez y convertir a Array para mejor rendimiento
const rows = Array.from(resultTable.querySelectorAll('tr.tot-row'));

// Usar reduce en lugar de forEach para mejor rendimiento
const totals = rows.reduce((acc, row) => {
    const timeCell = row.querySelector('td.time');
    const onTaskCell = row.querySelector('td.on-task');

    if (timeCell && onTaskCell) {
        acc.totalTime += extractNumber(timeCell.textContent);
        acc.timeOnTask += extractNumber(onTaskCell.textContent);
    }
    return acc;
}, { totalTime: 0, timeOnTask: 0 });

return {
    ...totals,
    hasData: rows.length > 0
};

}

// Timeoff task
async function fetchTimeOffTaskData(url) {
// Si no es Intraday ni Day, retornar objeto vacío inmediatamente
const params = getCurrentPageParameters();
if (!['Intraday', 'Day'].includes(params.spanType)) {
return {
totalTime: 0,
timeOnTask: 0,
hasData: false
};
}

try {
    const response = await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(() => {
            resolve({
                responseText: '',
                status: 'timeout'
            });
        }, 6000); // timeout de 3 segundo

        GM_xmlhttpRequest({
            method: 'POST',
            url: url.split('?')[0],
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': document.cookie
            },
            data: new URLSearchParams(new URL(url).search).toString(),
            withCredentials: true,
            onload: function (response) {
                clearTimeout(timeoutId);
                resolve(response);
            },
            onerror: function () {
                clearTimeout(timeoutId);
                resolve({
                    responseText: '',
                    status: 'error'
                });
            }
        });
    });

    // Si la respuesta contiene la tabla y los datos son válidos, procesar
    if (response.responseText && response.responseText.includes('class="sortable result-table"')) {
        const result = parseTimeOnTaskData(response.responseText);
        if (result.hasData) {
            return result;
        }
    }

    // En cualquier otro caso, retornar objeto vacío
    return {
        totalTime: 0,
        timeOnTask: 0,
        hasData: false
    };

} catch (error) {
    console.warn('Error fetching Time Off Task data:', error);
    return {
        totalTime: 0,
        timeOnTask: 0,
        hasData: false
    };
}

}

// Funcion para timeoff
function addTimeOffTaskRow(timeOffTask, timeOffTaskPercentage, params) {
// Buscar la tabla
const table = document.querySelector('.summary-table tbody');
if (!table) {
console.error('Table body not found');
return;
}

// Crear la fila de Time Off Task
const timeOffTaskRow = document.createElement('tr');
const totUrl = `https://fclm-portal.amazon.com/reports/timeOnTask?reportFormat=HTML&warehouseId=${params.warehouseId}&startDate${params.spanType}=${params.startDate}&maxIntradayDays=1&spanType=${params.spanType}&startHourIntraday=${params.startHour}&startMinuteIntraday=${params.startMinute}&endDate${params.spanType}=${params.endDate}&endHourIntraday=${params.endHour}&endMinuteIntraday=${params.endMinute}&_adjustPlanHours=on&hideEmptyLineItems=true&_hideEmptyLineItems=on&employmentType=AllEmployees&processPath=All`;

timeOffTaskRow.innerHTML = `

<td colspan="3" style="background-color: #ffe6e8; font-weight: bold; font-size: 12px; padding: 5px 10px; text-align: center; border-top: 1px solid black; border-bottom: none;">
<div style="display: flex; justify-content: center; align-items: center;">
<a href="${totUrl}" target="_blank" style="text-decoration: none; cursor: pointer; display: flex; align-items: center;" class="tooltip-trigger">
<span style="color: rgb(0, 0, 0); margin-right: 5px;">⚠️ Time Off Task hours</span>
<span style="color: #515151; font-size: 12px;"> (${timeOffTaskPercentage.toFixed(2)}%)</span>
</a>
</div>
</td>
<td colspan="5" style="background-color: #ffe6e8; color: #000; font-weight: bold; font-size: 12px; text-align: center; border-top: 1px solid black; border-bottom: none;">
${timeOffTask.toFixed(2)}
</td>
`;

// Buscar el punto de inserción correcto
const rows = Array.from(table.querySelectorAll('tr'));
const crossdockIndex = rows.findIndex(row =>
    row.textContent.toLowerCase().includes('crossdock volume')
);

if (crossdockIndex !== -1) {
    // Insertar después de la fila de Crossdock
    if (crossdockIndex + 1 < rows.length) {
        // Si hay una fila después de Crossdock, insertar antes de esa
        table.insertBefore(timeOffTaskRow, rows[crossdockIndex + 1]);
    } else {
        // Si Crossdock es la última fila, añadir al final
        table.appendChild(timeOffTaskRow);
    }
} else {
    // Si no encontramos la fila de Crossdock, insertar al final
    table.appendChild(timeOffTaskRow);
}

}

async function main() {
await updatecheck();
try {
const params = getCurrentPageParameters();

    // Configurar todas las URLs
    const processIds = [
        '1003031', '1003009', '1003021', '1003041', '1003032',
        '1003033', '1003012', '1003010', '1002980', '1003002'
    ];
    const urls = processIds.map(id => buildReportURL(id));
    const miscURL = buildReportURLMisc();
urls.push(miscURL);


    // Ejecutar todas las peticiones en paralelo primero
    const [
        upcDoc,
        sortDoc,
        daDoc,
        palletTIDoc,
        palletDoc,
        decantDoc,
        decant2Doc,
        receivedockDoc,
        IBpsDoc,
        prepDoc,
        miscDoc
    ] = await Promise.all(urls.map(url => fetchAndParse(url)));

    console.log('%c➜ Docs fetcheados exitosamente, incluyendo miscDoc', 'color: #4CAF50; font-weight: bold;');

    // Extraer todos los datos en paralelo usando Promise.all
    const [
        upcData,
        sortData,
        daData,
        palletTIData,
        palletData,
        decantData,
        decant2Data,
        receivedockData,
        IBpsData,
        prepData,
        miscData
    ] = await Promise.all([
        Promise.resolve(extractUPCData(upcDoc)),
        Promise.resolve(extractSortData(sortDoc)),
        Promise.resolve(extractDAData(daDoc)),
        Promise.resolve(extractPalletTIData(palletTIDoc)),
        Promise.resolve(extractPalletData(palletDoc)),
        Promise.resolve(extractdecantData(decantDoc)),
        Promise.resolve(extractdecant2Data(decant2Doc)),
        Promise.resolve(extractreceivedockData(receivedockDoc)),
        Promise.resolve(extractIBpsData(IBpsDoc)),
        Promise.resolve(extractprepData(prepDoc)),
        Promise.resolve(extractMiscData(miscDoc))
    ]);

    console.log('Datos MISC extraídos en main:', miscData);

    // Calcular el total de horas Misc

        console.log('\n');
        console.log('%c╔════════════════════════════════════════════╗', 'color: #FF4081; font-weight: bold;');
        console.log('%c║         DATOS MISC EXTRAÍDOS              ║', 'color: #FF4081; font-weight: bold;');
        console.log('%c╠════════════════════════════════════════════╣', 'color: #FF4081; font-weight: bold;');
        console.log('%c║ Total Misc Hours:', 'color: #FF4081; font-weight: bold;', miscData.misctotalHours);
        console.log('%c╚════════════════════════════════════════════╝', 'color: #FF4081; font-weight: bold;');


    // Calcular autoreceive ve y pallet autoreceive en paralelo
    const [autore, autorepallet] = await Promise.all([
        Promise.resolve((() => {
            const denominator = mainPageValues.inbound - palletData.palletvol;
            if (denominator !== 0) {
                const result = ((upcData.eachTotal / denominator) * 100) || 0;
                return `${result.toFixed(2)}%`;
            }
            return '0%';
        })()),
        Promise.resolve((() => {
            const ratio = (palletData.LPpallet / (mainPageValues.palletReceive || 1)) || 0;
            return `${(ratio * 100).toFixed(1)}%`;
        })())
    ]);

    // Agregar logs específicos para los valores de misc
console.log('Valores Misc antes de crear tabla:', {
    misctotalHours: miscData.misctotalHours,
    tomHours: miscData.tomHours,
    tomTrainingHours: miscData.tomTrainingHours,
    teamConnectHours: miscData.teamConnectHours,
    trainingHours: miscData.trainingHours,
    jambustersHours: miscData.jambustersHours,
    fiveShours: miscData.fiveShours
});

console.log('Valores antes de crear tabla:', {
    misctotalHours: miscData.misctotalHours,
    tomHours: miscData.tomHours,
    tomTrainingHours: miscData.tomTrainingHours,
    teamConnectHours: miscData.teamConnectHours,
    trainingHours: miscData.trainingHours,
    jambustersHours: miscData.jambustersHours,
    fiveShours: miscData.fiveShours
});

    // Crear la tabla sin Time Off Task
    createResultTable(
        upcData.LPupc, mainPageValues.ibTotal, mainPageValues.inbound, mainPageValues.inboundhours, mainPageValues.inboundrate,
        mainPageValues.transin, mainPageValues.transinhours, mainPageValues.transinrate,
        mainPageValues.ERvol, mainPageValues.ERSvol, mainPageValues.ERMvol, mainPageValues.ERLvol, mainPageValues.ERhours,
        mainPageValues.ERrate, mainPageValues.prepvol, mainPageValues.prepSvol, mainPageValues.prepMvol, mainPageValues.prepLvol,
        mainPageValues.prephours, mainPageValues.preprate, mainPageValues.daTotal, totalHours, mainPageValues.ibHours,
        mainPageValues.daHours, mainPageValues.palletReceive, upcData.eachTotal, upcData.caseTotal, upcData.eachColor,
        mainPageValues.sortVolume, mainPageValues.sortVolumesmall, sortShare, upcData.pidUpc, upcData.prEditorUpc,
        upcData.arosUpc, upcData.pidcases, upcData.preditorcases, upcData.aroscases, upcData.pidvol, upcData.preditorvol,
        upcData.arosvol, upcData.preditorhours, upcData.preditorrate, autore, autorepallet, mainPageValues.ibRate,
        mainPageValues.daRate, palletTIData.palletunits, palletTIData.palletvol, palletTIData.pallethours,
        mainPageValues.palletTIrate, palletTIData.palletcases, palletData.palletunits, palletData.palletvol,
        palletData.pallethours, mainPageValues.palletrate, palletData.palletcases, palletData.LPpallet,
        receivedockData.RDpalletunits, receivedockData.RDpalletvol, receivedockData.RDpalletcases,
        IBpsData.IBpalletunits, IBpsData.IBpalletvol, IBpsData.IBpalletcases, daData.FLThours, daData.FLvol, daData.FLrate,
        daData.flcasecase, daData.fltotecase, daData.FLCycleTime, daData.MP.each, daData.MP.case, daData.MP.hours,
        daData.MP.rate, daData.TP.each, daData.TP.case, daData.TP.hours, daData.TP.rate, daData.RPvol,
        daData.RPtote, daData.TPhours2, daData.TSO.each, daData.TSO.hours, daData.TSO.rate, daData.TSO.pallets,
        mainPageValues.sortHours, daData.FLshare, daData.DAupt, daData.DAupc, daData.FLupc, daData.FLupt, daData.MPupc, daData.TPupt, daData.toteshare, daData.caseshare,
        daData.totalTotes, sortData.ms.volume, sortData.ms.hours, sortData.ms.rate, sortData.ms.Svolume,
        sortData.ms.Mvolume, sortData.ms.Lvolume, sortData.uis5.volume, sortData.uis5.hours, sortData.uis5.rate,
        sortData.uis5.Svolume, sortData.uis5.Mvolume, sortData.uis5.Lvolume, sortData.uis5upt, sortData.uis20.volume,
        sortData.uis20.hours, sortData.uis20.rate, sortData.uis20.Svolume, sortData.uis20.Mvolume,
        sortData.uis20.Lvolume, sortData.uis20upt, QAPShours, buildingHshare, buildingHIBPS, buildingHTSOPS, buildingHICQA, sortData.ms2.volume, sortData.ms2.hours,
        sortData.ms2.rate, sortData.ms2.Svolume, sortData.ms2.Mvolume, sortData.ms2.Lvolume, decantData.volume,
        decantData.Svol, decantData.Mvol, decantData.Lvol, decantData.hours, decantData.rate, decantData.case,
        decant2Data.volume, decant2Data.Svol, decant2Data.Mvol, decant2Data.Lvol, decant2Data.hours,
        decant2Data.rate, decant2Data.case, mainPageValues.sevhours,
        mainPageValues.IBPSvol, mainPageValues.IBPShours, mainPageValues.IBPSrate, mainPageValues.TSOPSvol, mainPageValues.TSOPShours, mainPageValues.TSOPSrate, mainPageValues.ICQAvol, mainPageValues.ICQAhours, mainPageValues.ICQArate, mainPageValues.RShours,mainPageValues.Transferouthours,mainPageValues.TSOdockhours,
        prepData.prepStick, prepData.prepWrap, prepData.prepOverbox, prepData.prepResearch, prepData.prepOther, prepData.prepAssort, mainPageValues.presortCases,mainPageValues.presortCasesVolume, mainPageValues.presortCasesHours, mainPageValues.presortCasesRate,
        miscData.misctotalHours,
    miscData.tomHours,
    miscData.tomTrainingHours,
    miscData.teamConnectHours,
    miscData.trainingHours,
    miscData.jambustersHours,
    miscData.fiveShours
);

    // Cargar Time Off Task de forma asíncrona
    if (['Intraday', 'Day'].includes(params.spanType)) {
        const totParams = new URLSearchParams({
            reportFormat: 'HTML',
            warehouseId: params.warehouseId,
            startDateDay: params.startDate,
            maxIntradayDays: '1',
            spanType: params.spanType,
            startDateIntraday: params.startDate,
            startHourIntraday: params.startHour,
            startMinuteIntraday: params.startMinute,
            endDateIntraday: params.endDate,
            endHourIntraday: params.endHour,
            endMinuteIntraday: params.endMinute,
            _adjustPlanHours: 'on',
            hideEmptyLineItems: 'true',
            _hideEmptyLineItems: 'on',
            employmentType: 'AllEmployees',
            processPath: 'All'
        });

        const timeOnTaskUrl = `https://fclm-portal.amazon.com/reports/timeOnTask?${totParams.toString()}`;
        fetchTimeOffTaskData(timeOnTaskUrl).then(totResult => {
            if (totResult.hasData) {
                const timeOffTaskValue = Math.max(totResult.totalTime - totResult.timeOnTask, 0);
                const timeOffTaskPercentage = totResult.totalTime > 0 ?
                    ((totResult.totalTime - totResult.timeOnTask) / totResult.totalTime) * 100 : 0;

                if (timeOffTaskValue > 0) {
                    addTimeOffTaskRow(timeOffTaskValue, timeOffTaskPercentage, params);
                }
            }
        }).catch(error => {
            console.warn('Error loading Time Off Task data:', error);
        });
    }

} catch (error) {
    console.error("Error en la ejecución del script:", error);
}

}

// ==UserScript==     RATES SUMMARY
// @run-at       document-end

(function () {
'use strict';

console.log('RATES SUMMARY script is starting');

function extractNumericValue(selector) {
    const element = document.querySelector(selector);
    if (!element) return '0';

    const text = element.textContent.trim();

    const hasDot = /\d+\.\d{3}/.test(text);
    const hasComma = /\d+,\d{3}/.test(text);
    const hasSpace = /\d+\s\d{3}/.test(text);

    let cleanedText = text;

    if (hasDot) {
        cleanedText = text.replace(/\./g, '').replace(',', '.');
    } else if (hasComma) {
        cleanedText = text.replace(/,/g, '');
    } else if (hasSpace) {
        cleanedText = text.replace(/\s/g, '');
    }

    const value = parseFloat(cleanedText);

    if (isNaN(value) || value === 0) return '0';

    const roundedValue = Math.round(value);

    return roundedValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function createRatesSummaryTable(ibData, sortData, daData) {
    console.log('Creating rates summary table');

    const floatingContainer = document.createElement('div');
    floatingContainer.id = 'floatingRatesSummary';

    // Obtener y validar la posición guardada
    // En createRatesSummaryTable, actualiza la parte de la posición inicial:
    let savedPosition;
    try {
        savedPosition = JSON.parse(localStorage.getItem('floatingContainerPosition'));
        if (!savedPosition) {
            savedPosition = { top: '75px', left: '20px' };
        }


        const viewportWidth = window.innerWidth;
        const margin = 20;

        // Convertir posiciones a números
        let leftPos = parseInt(savedPosition.left);

        // Ajustar si está fuera de los límites horizontales
        if (leftPos < margin) {
            leftPos = margin;
        }
        if (leftPos > viewportWidth - 100 - margin) {
            leftPos = viewportWidth - 100 - margin;
        }

        savedPosition = {
            top: savedPosition.top,
            left: leftPos + 'px'
        };
    } catch {
        savedPosition = { top: '75px', left: '20px' };
    }


    Object.assign(floatingContainer.style, {
        position: 'absolute', // Corregido de 'absolut' a 'absolute'
        top: savedPosition.top,
        left: savedPosition.left,
        zIndex: '9999',
        backgroundColor: '#3c4856',
        boxShadow: '0 0 10px rgba(0,0,0,0.5)',
        padding: '5px',
        cursor: 'move',
        width: '60px',
        height: '30px',
        borderRadius: '5px'
    });



    const minimizeButton = document.createElement('button');
    minimizeButton.textContent = '+';
    Object.assign(minimizeButton.style, {
        position: 'absolute',
        top: '2px',
        right: '2px',
        border: 'none',
        background: 'transparent',
        color: 'white',
        fontSize: '12px',
        cursor: 'pointer',
        width: '16px',
        height: '16px',
        lineHeight: '16px',
        textAlign: 'center',
        borderRadius: '3px'
    });
    floatingContainer.appendChild(minimizeButton);

    const table = document.createElement('table');
    Object.assign(table.style, {
        borderCollapse: 'separate',
        borderSpacing: '0',
        fontSize: '12px',
        display: 'none',
        backgroundColor: 'white',
        borderRadius: '5px',
        overflow: 'hidden',
        width: 'auto',
        maxWidth: '600px'
    });

    const header = table.createTHead();
    const headerRow = header.insertRow();
    const headerCell = headerRow.insertCell();
    headerCell.colSpan = 5;
    headerCell.textContent = 'RATES SUMMARY';
    Object.assign(headerCell.style, {
        backgroundColor: '#3c4856',
        color: 'white',
        fontWeight: 'bold',
        padding: '10px 10px 5px 10px', // Reducido el padding inferior a 5px
        fontSize: '15px',
        textAlign: 'center'
    });

    const toggleRow = header.insertRow();
    const toggleCell = toggleRow.insertCell();
    toggleCell.colSpan = 5;
    Object.assign(toggleCell.style, {
        padding: '0',
        backgroundColor: '#3c4856',
    });

    const toggleButton = document.createElement('button');
    toggleButton.textContent = GM_getValue('showPlanColumns', false) ? 'Hide % to plan' : 'Show % to plan';
    Object.assign(toggleButton.style, {
        width: '100%',
        padding: '5px',
        backgroundColor: '#3c4856',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
        fontSize: '11px',
        fontWeight: 'normal',
        outline: 'none',
    });
    toggleCell.appendChild(toggleButton);

    // Agregar evento hover para mejorar la interactividad
    toggleButton.addEventListener('mouseover', function () {
        this.style.backgroundColor = '#4e5d6c';
    });
    toggleButton.addEventListener('mouseout', function () {
        this.style.backgroundColor = '#3c4856';
    });



    const columnHeadersRow = header.insertRow();
    const processHeader = columnHeadersRow.insertCell();
    processHeader.textContent = 'Process';
    const actualRateHeader = columnHeadersRow.insertCell();
    actualRateHeader.textContent = 'Actual Rate';
    const planRateHeader = columnHeadersRow.insertCell();
    planRateHeader.textContent = 'Plan Rate';
    const gainLossHeader = columnHeadersRow.insertCell(); // Nueva columna
    gainLossHeader.textContent = 'Gain/Loss Hours';
    const ratioHeader = columnHeadersRow.insertCell();
    ratioHeader.textContent = '% to Plan (OP2)';

    [processHeader, actualRateHeader, planRateHeader, gainLossHeader, ratioHeader].forEach(cell => {
        Object.assign(cell.style, {
            backgroundColor: '#6c7886',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '12px',
            padding: '5px',
            textAlign: 'center',
            whiteSpace: 'nowrap',
            minWidth: '60px',
            maxWidth: '150px'
        });
    });

    // Alinear el encabezado "Process" a la izquierda
    processHeader.style.textAlign = 'left';

    const body = table.createTBody();

    function addSection(title, data, isLastSection) {

const sectionRow = body.insertRow();
const sectionCell = sectionRow.insertCell();
const sectionActualCell = sectionRow.insertCell();
const sectionPlanCell = sectionRow.insertCell();
const sectionGainLossCell = sectionRow.insertCell();
const sectionRatioCell = sectionRow.insertCell();

sectionCell.textContent = title;
sectionActualCell.textContent = data['Overall'];
sectionPlanCell.textContent = data['Overall_plan'];

// Cálculo de Gain/Loss Hours usando volumen para la sección Overall
let gainLoss = '-';
if (data['Overall_plan'] && data['Overall_plan'] !== '-') {
const volume = parseFloat(data['Overall_volume']?.replace(/,/g, '')) || 0;
const actualRate = parseFloat(data['Overall']?.replace(/,/g, '')) || 0;
const planRate = parseFloat(data['Overall_plan']?.replace(/,/g, '')) || 0;

if (planRate > 0 && actualRate > 0) {
    const actualHours = volume / actualRate;
    const planHours = volume / planRate;
    gainLoss = Math.round(planHours - actualHours).toLocaleString();
}

}

sectionGainLossCell.textContent = gainLoss;
sectionRatioCell.textContent = data['Overall_ratio'] + '%';

[sectionCell, sectionActualCell, sectionPlanCell, sectionGainLossCell, sectionRatioCell].forEach(cell => {
Object.assign(cell.style, {
backgroundColor: '#b3c8d8',
fontWeight: 'bold',
padding: '5px'
});
});

sectionGainLossCell.style.color = gainLoss === '-' ? 'black' :
(parseFloat(gainLoss.replace(/,/g, '')) >= 0 ? 'green' : '#8B0000');

sectionCell.style.textAlign = 'left';
sectionActualCell.style.textAlign = 'right';
sectionPlanCell.style.textAlign = 'right';
sectionGainLossCell.style.textAlign = 'right';
sectionRatioCell.style.textAlign = 'right';

sectionRatioCell.style.color = parseFloat(data['Overall_ratio']) >= 100 ? 'green' : '#8B0000';

const entries = Object.entries(data).filter(([key]) =>
key !== 'Overall' &&
!key.includes('_plan') &&
!key.includes('_ratio') &&
!key.includes('_volume')
);

entries.forEach(([key, value], index) => {
const row = body.insertRow();
const keyCell = row.insertCell();
const valueCell = row.insertCell();
const planCell = row.insertCell();
const gainLossCell = row.insertCell();
const ratioCell = row.insertCell();

keyCell.textContent = key;
valueCell.textContent = value;
planCell.textContent = data[`${key}_plan`] || '-';

// Cálculo de Gain/Loss Hours para cada proceso
let processGainLoss = '-';
if (data[`${key}_plan`] && data[`${key}_plan`] !== '-' && value !== '-') {
    const processVolume = parseFloat(data[`${key}_volume`]?.replace(/,/g, '')) || 0;
    const processActual = parseFloat(value.replace(/,/g, '')) || 0;
    const processPlan = parseFloat(data[`${key}_plan`]?.replace(/,/g, '')) || 0;

    if (processPlan > 0 && processActual > 0) {
        const processActualHours = processVolume / processActual;
        const processPlanHours = processVolume / processPlan;
        processGainLoss = Math.round(processPlanHours - processActualHours).toLocaleString();
    }
}

gainLossCell.textContent = processGainLoss;
ratioCell.textContent = (data[`${key}_ratio`] || '-') + (data[`${key}_ratio`] ? '%' : '');

if (data[`${key}_ratio`]) {
    const ratio = parseFloat(data[`${key}_ratio`]);
    ratioCell.style.color = ratio >= 100 ? 'green' : '#8B0000';
}

Object.assign(keyCell.style, {
    padding: '5px',
    borderBottom: '1px solid #ddd'
});
Object.assign(valueCell.style, {
    padding: '5px',
    borderBottom: '1px solid #ddd',
    textAlign: 'right'
});
Object.assign(planCell.style, {
    padding: '5px',
    borderBottom: '1px solid #ddd',
    textAlign: 'right',
    backgroundColor: '#f0f0f0'
});
Object.assign(gainLossCell.style, {
    padding: '5px',
    borderBottom: '1px solid #ddd',
    textAlign: 'right',
    backgroundColor: '#f0f0f0',
    color: processGainLoss === '-' ? 'black' :
          (parseFloat(processGainLoss.replace(/,/g, '')) >= 0 ? 'green' : '#8B0000')
});
Object.assign(ratioCell.style, {
    padding: '5px',
    borderBottom: '1px solid #ddd',
    textAlign: 'right',
    backgroundColor: '#f0f0f0'
});

if (isLastSection && index === entries.length - 1) {
    keyCell.style.borderBottom = 'none';
    valueCell.style.borderBottom = 'none';
    planCell.style.borderBottom = 'none';
    gainLossCell.style.borderBottom = 'none';
    ratioCell.style.borderBottom = 'none';
}

});

}

    addSection('IB', ibData, false);
    addSection('RC Sort - Total', sortData, false);
    addSection('DA', daData, true);


    floatingContainer.appendChild(table);
    document.body.appendChild(floatingContainer);

    makeDraggable(floatingContainer);

    let isMinimized = GM_getValue('isMinimized', true);
    const ratesText = document.createElement('span');
    ratesText.textContent = 'RATES';
    Object.assign(ratesText.style, {
        fontSize: '12px',
        position: 'absolute',
        left: '11px',
        right: '7px',
        top: '13px',
        color: 'white',
        fontWeight: 'bold'
    });
    floatingContainer.appendChild(ratesText);

    function setMinimizedState(minimized) {
        if (minimized) {
            table.style.display = 'none';
            ratesText.style.display = 'block';
            Object.assign(floatingContainer.style, {
                width: '60px',
                height: '30px',
                padding: '5px',
                backgroundColor: '#3c4856',
                borderRadius: '5px'
            });
            Object.assign(minimizeButton.style, {
                fontSize: '12px',
                top: '2px',
                right: '2px',
                width: '16px',
                height: '16px',
                color: 'white',
                backgroundColor: 'transparent',
                border: 'none',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            });
            minimizeButton.textContent = '+';
        } else {
            table.style.display = 'table';
            ratesText.style.display = 'none';
            Object.assign(floatingContainer.style, {
                width: 'auto',
                height: 'auto',
                padding: '0',
                backgroundColor: 'transparent',
                borderRadius: '5px'
            });
            Object.assign(minimizeButton.style, {
                fontSize: '14px',
                top: '5px',
                right: '5px',
                width: '16px',
                height: '16px',
                color: 'white',
                backgroundColor: 'transparent',
                border: 'none',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                borderRadius: '3px'
            });
            minimizeButton.innerHTML = '&#8211;';
        }
        isMinimized = minimized;
        GM_setValue('isMinimized', isMinimized);
    }

    function toggleMinimize() {
        setMinimizedState(!isMinimized);
    }

    minimizeButton.addEventListener('click', toggleMinimize);
    ratesText.addEventListener('click', toggleMinimize);

    setMinimizedState(isMinimized);

    function togglePlanColumns() {
        const showPlanColumns = !GM_getValue('showPlanColumns', false);
        GM_setValue('showPlanColumns', showPlanColumns);
        toggleButton.textContent = showPlanColumns ? 'Hide % to plan' : 'Show % to plan';

        const planCells = table.querySelectorAll('td:nth-child(3), td:nth-child(4), td:nth-child(5), th:nth-child(3), th:nth-child(4), th:nth-child(5)');
        planCells.forEach(cell => {
            cell.style.display = showPlanColumns ? 'table-cell' : 'none';
        });
    }

    toggleButton.addEventListener('click', togglePlanColumns);

    // Set initial state of plan columns
    const showPlanColumns = GM_getValue('showPlanColumns', false);
    const planCells = table.querySelectorAll('td:nth-child(3), td:nth-child(4), th:nth-child(3), th:nth-child(4)');
    planCells.forEach(cell => {
        cell.style.display = showPlanColumns ? 'table-cell' : 'none';
    });
}

function makeDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    const header = element.querySelector('th') || element;

    header.style.cursor = 'move';
    header.onmousedown = dragMouseDown;

    function checkAndAdjustPosition() {
        const viewportWidth = window.innerWidth;
        const box = element.getBoundingClientRect();
        const margin = 20;

        // Ajustar posición horizontal si está fuera de los límites
        if (box.right > viewportWidth - margin) {
            element.style.left = (viewportWidth - box.width - margin) + 'px';
        }
        if (box.left < margin) {
            element.style.left = margin + 'px';
        }
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();

        // Calcular el cambio en la posición
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;

        // Calcular nueva posición
        let newTop = element.offsetTop - pos2;
        let newLeft = element.offsetLeft - pos1;

        // Obtener dimensiones actuales
        const viewportWidth = window.innerWidth;
        const box = element.getBoundingClientRect();
        const margin = 20;

        // Aplicar límites horizontales
        if (newLeft < margin) {
            newLeft = margin;
        }
        if (newLeft + box.width > viewportWidth - margin) {
            newLeft = viewportWidth - box.width - margin;
        }

        // Aplicar la nueva posición
        element.style.top = newTop + "px";
        element.style.left = newLeft + "px";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;

        // Guardar la posición final
        const position = {
            top: element.style.top,
            left: element.style.left
        };
        localStorage.setItem('floatingContainerPosition', JSON.stringify(position));
    }

    // Añadir listener para el evento de zoom/resize
    window.addEventListener('resize', checkAndAdjustPosition);

    // Comprobar posición inicial
    setTimeout(checkAndAdjustPosition, 0);
}




async function initScript() {
    await main();
    console.log('Initializing script');

    const ibData = {
        'Overall': extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.numeric.actualProductivity.rate div.original'),
        'Overall_plan': extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.numeric.planProductivity div.original'),
        'Overall_ratio': extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.numeric.ratioToPlan.ratio div.original'),
        'Overall_volume': extractNumericValue('tr[id="ppr.rcSummary.inbound"] td.actualVolume.numeric div.original'),

        'Receive dock': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveDock"] td.numeric.actualProductivity.rate div.original'),
        'Receive dock_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveDock"] td.numeric.planProductivity div.original'),
        'Receive dock_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveDock"] td.numeric.ratioToPlan.ratio div.original'),
        'Receive dock_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveDock"] td.actualVolume.numeric div.original'),

        'Each Receive - Total': extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.numeric.actualProductivity.rate div.original'),
        'Each Receive - Total_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.numeric.planProductivity div.original'),
        'Each Receive - Total_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.numeric.ratioToPlan.ratio div.original'),
        'Each Receive - Total_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.eachReceive.total"] td.actualVolume.numeric div.original'),

        'LP Receive': extractNumericValue('tr[id="ppr.detail.inbound.receive.lpReceive"] td.numeric.actualProductivity.rate div.original'),
        'LP Receive_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.lpReceive"] td.numeric.planProductivity div.original'),
        'LP Receive_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.lpReceive"] td.numeric.ratioToPlan.ratio div.original'),
        'LP Receive_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.lpReceive"] td.actualVolume.numeric div.original'),

        'LP Preditor': sessionStorage.getItem('preditorrate') ? Math.round(parseFloat(sessionStorage.getItem('preditorrate'))).toLocaleString() : '-',

        'Pallet Receive': extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.numeric.actualProductivity.rate div.original'),
        'Pallet Receive_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.numeric.planProductivity div.original'),
        'Pallet Receive_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.numeric.ratioToPlan.ratio div.original'),
        'Pallet Receive_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.palletReceive"] td.actualVolume.numeric div.original'),

        'Receive Support': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveSupport"] td.numeric.actualProductivity.rate div.original'),
        'Receive Support_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveSupport"] td.numeric.planProductivity div.original'),
        'Receive Support_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveSupport"] td.numeric.ratioToPlan.ratio div.original'),
        'Receive Support_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.receiveSupport"] td.actualVolume.numeric div.original'),

        'Decant': sessionStorage.getItem('decantTrate') ? Math.round(parseFloat(sessionStorage.getItem('decantTrate'))).toLocaleString() : '-',

        'Presort Cases': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.numeric.actualProductivity.rate div.original'),
        'Presort Cases_plan': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.numeric.planProductivity div.original'),
        'Presort Cases_ratio': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.numeric.ratioToPlan.ratio div.original'),
        'Presort Cases_volume': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSortCases"] td.actualVolume.numeric div.original'),

        'Case Receive': extractNumericValue('tr[id="ppr.detail.inbound.receive.caseReceive"] td.numeric.actualProductivity.rate div.original'),
        'Case Receive_plan': extractNumericValue('tr[id="ppr.detail.inbound.receive.caseReceive"] td.numeric.planProductivity div.original'),
        'Case Receive_ratio': extractNumericValue('tr[id="ppr.detail.inbound.receive.caseReceive"] td.numeric.ratioToPlan.ratio div.original'),
        'Case Receive_volume': extractNumericValue('tr[id="ppr.detail.inbound.receive.caseReceive"] td.actualVolume.numeric div.original'),

        'Cubicscan/Atac': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.cubiscan"] td.numeric.actualProductivity.rate div.original'),
        'Cubicscan/Atac_plan': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.cubiscan"] td.numeric.planProductivity div.original'),
        'Cubicscan/Atac_ratio': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.cubiscan"] td.numeric.ratioToPlan.ratio div.original'),
        'Cubicscan/Atac_volume': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.cubiscan"] td.actualVolume.numeric div.original'),

        'Prep Recorder - Total': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.numeric.actualProductivity.rate div.original'),
        'Prep Recorder - Total_plan': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.numeric.planProductivity div.original'),
        'Prep Recorder - Total_ratio': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.numeric.ratioToPlan.ratio div.original'),
        'Prep Recorder - Total_volume': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepRecorder.total"] td.actualVolume.numeric div.original'),

        'Prep Support': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepSupport"] td.numeric.actualProductivity.rate div.original'),
        'Prep Support_plan': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepSupport"] td.numeric.planProductivity div.original'),
        'Prep Support_ratio': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepSupport"] td.numeric.ratioToPlan.ratio div.original'),
        'Prep Support_volume': extractNumericValue('tr[id="ppr.detail.inbound.ibPrep.prepSupport"] td.actualVolume.numeric div.original'),

        'RSR Support': extractNumericValue('tr[id="ppr.detail.inbound.rsr.rsrSupport"] td.numeric.actualProductivity.rate div.original'),
        'RSR Support_plan': extractNumericValue('tr[id="ppr.detail.inbound.rsr.rsrSupport"] td.numeric.planProductivity div.original'),
        'RSR Support_ratio': extractNumericValue('tr[id="ppr.detail.inbound.rsr.rsrSupport"] td.numeric.ratioToPlan.ratio div.original'),
        'RSR Support_volume': extractNumericValue('tr[id="ppr.detail.inbound.rsr.rsrSupport"] td.actualVolume.numeric div.original'),

        'IB Lead': extractNumericValue('tr[id="ppr.detail.inbound.ibLeadPa.ibLeadPa"] td.numeric.actualProductivity.rate div.original'),
        'IB Lead_plan': extractNumericValue('tr[id="ppr.detail.inbound.ibLeadPa.ibLeadPa"] td.numeric.planProductivity div.original'),
        'IB Lead_ratio': extractNumericValue('tr[id="ppr.detail.inbound.ibLeadPa.ibLeadPa"] td.numeric.ratioToPlan.ratio div.original'),
        'IB Lead_volume': extractNumericValue('tr[id="ppr.detail.inbound.ibLeadPa.ibLeadPa"] td.actualVolume.numeric div.original'),

        'IB Problem Solve': extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.numeric.actualProductivity.rate div.original'),
        'IB Problem Solve_plan': extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.numeric.planProductivity div.original'),
        'IB Problem Solve_ratio': extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.numeric.ratioToPlan.ratio div.original'),
        'IB Problem Solve_volume': extractNumericValue('tr[id="ppr.detail.inbound.ibDefect.ibProblemSolve"] td.actualVolume.numeric div.original')
    };

    const sortData = {
        'Overall': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.numeric.actualProductivity.rate div.original'),
        'Overall_plan': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.numeric.planProductivity div.original'),
        'Overall_ratio': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.numeric.ratioToPlan.ratio div.original'),
        'Overall_volume': extractNumericValue('tr[id="ppr.detail.da.rcSort.rcSort.total"] td.actualVolume.numeric div.original'),

        'Manual Sort': sessionStorage.getItem('msTrate') ? Math.round(parseFloat(sessionStorage.getItem('msTrate'))).toLocaleString() : '-',
        'UIS 5lbs': sessionStorage.getItem('uis5rate') ? Math.round(parseFloat(sessionStorage.getItem('uis5rate'))).toLocaleString() : '-',
        'UIS 20lbs': sessionStorage.getItem('uis20rate') ? Math.round(parseFloat(sessionStorage.getItem('uis20rate'))).toLocaleString() : '-'
    };

    const daData = {
        'Overall': extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.numeric.actualProductivity.rate div.original'),
        'Overall_plan': extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.numeric.planProductivity div.original'),
        'Overall_ratio': extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.numeric.ratioToPlan.ratio div.original'),
        'Overall_volume': extractNumericValue('tr[id="ppr.rcSummary.delayedAllocation"] td.actualVolume.numeric div.original'),

        'Transfer Out': extractNumericValue('tr[id="ppr.detail.da.transferOut.transferOut"] td.numeric.actualProductivity.rate div.original'),
        'Transfer Out_plan': extractNumericValue('tr[id="ppr.detail.da.transferOut.transferOut"] td.numeric.planProductivity div.original'),
        'Transfer Out_ratio': extractNumericValue('tr[id="ppr.detail.da.transferOut.transferOut"] td.numeric.ratioToPlan.ratio div.original'),
        'Transfer Out_volume': extractNumericValue('tr[id="ppr.detail.da.transferOut.transferOut"] td.actualVolume.numeric div.original'),

        'Fluid load': sessionStorage.getItem('FLrate') ? Math.round(parseFloat(sessionStorage.getItem('FLrate'))).toLocaleString() : '-',
        'Manual Palletize Case': sessionStorage.getItem('MPrate') ? Math.round(parseFloat(sessionStorage.getItem('MPrate'))).toLocaleString() : '-',
        'Palletize Tote - Total ': sessionStorage.getItem('TPrate') ? Math.round(parseFloat(sessionStorage.getItem('TPrate'))).toLocaleString() : '-',
        'Manual Palletize Tote ': sessionStorage.getItem('TPrate2') ? Math.round(parseFloat(sessionStorage.getItem('TPrate2'))).toLocaleString() : '-',

        'Transfer Out Dock': extractNumericValue('tr[id="ppr.detail.da.transferOutDock.transferOutDock"] td.numeric.actualProductivity.rate div.original'),
        'Transfer Out Dock_plan': extractNumericValue('tr[id="ppr.detail.da.transferOutDock.transferOutDock"] td.numeric.planProductivity div.original'),
        'Transfer Out Dock_ratio': extractNumericValue('tr[id="ppr.detail.da.transferOutDock.transferOutDock"] td.numeric.ratioToPlan.ratio div.original'),
        'Transfer Out Dock_volume': extractNumericValue('tr[id="ppr.detail.da.transferOutDock.transferOutDock"] td.actualVolume.numeric div.original'),

        'TSO Lead': extractNumericValue('tr[id="ppr.detail.da.toLeadPa.toLeadPa"] td.numeric.actualProductivity.rate div.original'),
        'TSO Lead_plan': extractNumericValue('tr[id="ppr.detail.da.toLeadPa.toLeadPa"] td.numeric.planProductivity div.original'),
        'TSO Lead_ratio': extractNumericValue('tr[id="ppr.detail.da.toLeadPa.toLeadPa"] td.numeric.ratioToPlan.ratio div.original'),
        'TSO Lead_volume': extractNumericValue('tr[id="ppr.detail.da.toLeadPa.toLeadPa"] td.actualVolume.numeric div.original'),

        'TSO Problem Solve': extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.numeric.actualProductivity.rate div.original'),
        'TSO Problem Solve_plan': extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.numeric.planProductivity div.original'),
        'TSO Problem Solve_ratio': extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.numeric.ratioToPlan.ratio div.original'),
        'TSO Problem Solve_volume': extractNumericValue('tr[id="ppr.detail.da.toDefect.toProblemSolve"] td.actualVolume.numeric div.original')
    };

    createRatesSummaryTable(ibData, sortData, daData);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScript);
} else {
    initScript();
}

})();

})();
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('CellSense')
    .addItem('Open Sidebar', 'showSidebar')
    .addToUi();
}


function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('html/sidebar')
    .setTitle('CellSense')
    .setWidth(450);
  SpreadsheetApp.getUi().showSidebar(html);
}


function getActiveRangeA1Notation() {
  const sheet = SpreadsheetApp.getActiveSheet();
  if (!sheet) {
    return null;
  }
  Logger.log(`Active sheet: ${sheet.getName()}`);

  const activeRange = sheet.getActiveRange();
  if (!activeRange) {
    return null;
  }
  Logger.log(`Active range: ${activeRange.getA1Notation()}`);

  return {sheetName: sheet.getName(), activeRange: activeRange.getA1Notation()};
}

function getRangePayload(rangeLabel) {
  const match = rangeLabel.match(/^'(.*)'!(.+)$/);
  if (!match) {
    return null;
  }

  const sheetName = match[1].replace(/''/g, "'");
  const rangeNotation = match[2];

  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    return null;
  }

  try {
    const values = sheet.getRange(rangeNotation).getValues();
    return { range: rangeLabel, values };
  } catch (error) {
    Logger.log(`Failed to read range ${rangeLabel}: ${error}`);
    return null;
  }
}


function extractRangesFromMessage(message) {
  const pattern = /<cell-range>(.*?)<cell-range\/>/g;
  const ranges = [];
  const seen = new Set();
  let match;

  while ((match = pattern.exec(message)) !== null) {
    const rangeLabel = match[1];
    if (seen.has(rangeLabel)) {
      continue;
    }
    seen.add(rangeLabel);
    const payload = getRangePayload(rangeLabel);
    if (payload) {
      ranges.push(payload);
    }
  }

  return ranges;
}


function handleMessage(message) {
  const apiUrl = CONFIG.API_URL;
  const sheet = SpreadsheetApp.getActiveSheet();
  const sheetData = sheet.getDataRange().getValues();
  const selectedRanges = extractRangesFromMessage(message);

  const payload = {
    message,
    sheet: sheetData,
    sheet_name: sheet.getName(),
    selected_ranges: selectedRanges,
  };

  const response = callApi('POST', apiUrl + '/chat', payload);

  if (response.error) {
    return { reply: `Something went wrong: ${response.error}` };
  }

  sheet.getRange(1, 1).setValue('it worked');

  return { reply: response.reply || 'No reply from server.' };
}

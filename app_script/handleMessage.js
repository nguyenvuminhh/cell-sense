
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
    const cell_values = sheet.getRange(rangeNotation).getValues();
    return { sheet_name_and_range: rangeLabel, cell_values };
  } catch (error) {
    Logger.log(`Failed to read range ${rangeLabel}: ${error}`);
    return null;
  }
}


function extractRangesFromMessage(message) {
  const pattern = /<cells>(.*?)<\/cells>/g;
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
  const selectedRanges = extractRangesFromMessage(message);
  const apiUrl = CONFIG.API_URL;
  const payload = {
    message,
    selected_ranges: selectedRanges,
    // llm_provider: "google",
    // llm_model: "gemini-2.5-flash"
  };

  const response = callApi('POST', apiUrl + '/chat', payload);

  if (response.error) {
    return { reply: `Something went wrong: ${response.error}` };
  }
  try {
    const filled_ranges = response.filled_ranges;
    if (filled_ranges) {
      filled_ranges.forEach(filled_range => {
        const targetSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(filled_range.sheet_name);
        if (!targetSheet) {
          throw new Error(`Sheet not found: ${filled_range.sheet_name}`);
        }

        const range = targetSheet.getRange(filled_range.range);
        range.setFormulaR1C1(filled_range.r1c1_value);
      });
    }
  } catch (err) {
    Logger.log("Error filling cells: " + err);
    return { reply: "Error while filling cells: " + err.message };
  }

  return { reply: response.message || 'No reply from server.' };
}

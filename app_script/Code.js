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

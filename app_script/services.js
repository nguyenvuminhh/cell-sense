
function buildQuery(query = {}) {
  const keys = Object.keys(query);
  if (keys.length === 0) return '';
  const params = keys
    .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(query[key]))
    .join('&');
  return '?' + params;
}


function callApi(method, url, payload = {}, query = {}) {
  const fullUrl = url + buildQuery(query);
  const options = {
    method: method.toUpperCase(),
    contentType: 'application/json',
    muteHttpExceptions: true,
  };

  if (['POST', 'PUT', 'PATCH'].includes(options.method)) {
    options.payload = JSON.stringify(payload);
  }

  Logger.log('🔹 Request URL: ' + fullUrl);
  Logger.log('🔹 Method: ' + options.method);
  Logger.log('🔹 Payload: ' + JSON.stringify(payload));

  try {
    const response = UrlFetchApp.fetch(fullUrl, options);
    const code = response.getResponseCode();
    const text = response.getContentText();

    Logger.log('🔹 Response Code: ' + code);
    Logger.log('🔹 Response Body: ' + text);

    if (code >= 200 && code < 300) {
      return JSON.parse(text);
    } else {
      throw new Error(`HTTP ${code}: ${text}`);
    }
  } catch (e) {
    Logger.log('❌ Error: ' + e.message);
    return { error: e.message };
  }
}
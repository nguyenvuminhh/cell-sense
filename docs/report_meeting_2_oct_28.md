# Meeting Report - October 28, 2025

## Progress Since Last Meeting:
- Implemented custom prompt parsing, with 1 simple prompt template.
- Implemented API calls to Google Gemini LLMs, with 3 models: `gemini-2.5-flash`, `gemini-2.5-flash-lite`, and `gemini-2.5-pro`.
- Implemented some middleware for robustness and convenience (custom errors, removing trailing slashes).

## Some Comparison of LLM Models

I have tested three models with this example sheets:
![alt text](assets/2_example_sheets.png)

User message: This is a table of cost sharing between some friends: <cells>'Sheet1'!A1:N7</cells>. <cells>'Sheet1'!B4:M7</cells> contains the shares of each person per months. Please calculate the total cost for each person according to there montly shares. total personal cost = sum((monthly personal shares/ monthly total shares) for each month).

The selected range is the range covered by the image above, and the target range is highlighted in the image as well.

The results are as follows:
- **Gemini 2.5 Pro**: Best performance, most accurate and context-aware, but also the slowest and most expensive. It used a concise and efficient formula for the target cell:
```
=SUMPRODUCT(B4:M4/$B$3:$M$3,$B$2:$M$2)
```
- **Gemini 2.5 Flash**: Good performance, fairly accurate, faster and cheaper than Pro. It used a very lengthy formula for the target cell:
```
=SUM((B4/B$3)*B$2,(C4/C$3)*C$2,(D4/D$3)*D$2,(E4/E$3)*E$2,(F4/F$3)*F$2,(G4/G$3)*G$2,(H4/H$3)*H$2,(I4/I$3)*I$2,(J4/J$3)*J$2,(K4/K$3)*K$2,(L4/L$3)*L$2,(M4/M$3)*M$2)
```
- **Gemini 2.5 Flash Lite**: Very poor performance, inaccurate results, fastest and cheapest. It did not even provide the correct formula for R1C1 cell:
```
=SUMPRODUCT(RC[-11:RC[-1]]/R3C11:R3C[-1],R2C11:R2C[-1])
```

For analogy, if we were to compare these models to a coding task, where each model is asked to write a function that calculates the total cost for each person based on their monthly shares:
- Gemini 2.5 Pro would use a for loop to iterate through the months and calculate the total cost efficiently.
- Gemini 2.5 Flash would write out the calculation for each month separately, leading to a longer and more cumbersome function.
- Gemini 2.5 Flash Lite would struggle to write a correct function, resulting in errors and incorrect calculations.

## What failed:
- The implementation of the inline chat service failed due to underestimating the complexity.
- Inline chat requires a custom function, and a custom function does not have access to the Google Sheets API in the Apps Script environment. Therefore, the inline chat service cannot access the spreadsheet data to provide context-aware responses.
- Furthermore, the range passed into the inline chat is not exactly the range, but it is actually the data. See example below:
```
/**
 * @customfunction
 */
function CELLSENSE(range, message) {
  return `You asked: ${message} (range type: ${typeof range}, value of range: ${range})`;
}

// Calling CELLSENSE(A1, "Just copy the value of this")
// would return: "You asked: Just copy the value of this (range type: number, value of range: 42)"
```

- One work around is to pass the range as string, e.g., `CELLSENSE("A1", "Just copy the value of this")`, then send the message along with the range string to the backend, where the backend can then use the Sheets API to fetch the actual data. However, this approach is not very user-friendly (and developer-friendly):
  - User: Since the backend don't know what cell to fill, it must return the result string (in this case, `"=A1"`) instead of filling the cell directly. Then the user must copy-paste the result string into the target cell.
  - Developer: In order for the process to work, OAuth authentication must be implemented to allow the backend to access the user's spreadsheet data.

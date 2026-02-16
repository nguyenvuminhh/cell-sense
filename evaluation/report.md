# Evaluation Report on LLMs Performance in Google Sheets Formula Generation

## Settings
- Compared models:
    - Google:
        - Gemini 2.5 Pro
        - Gemini 2.5 Flash
        - Gemini 2.5 Flash Lite
    - OpenAI:
        - GPT-5
        - GPT-5 Mini
        - GPT-5 Nano
    - Anthropic:
        - Claude Haiku 4.5
        - Claude Sonnet 4.5
        - Claude Opus 4.5

- Test set: 3 levels of difficulty (Easy, Medium, Hard), 3 sheets per level, 1 task per sheet.

- Evaluation metrics:
    - Consistancy and Accuracy: Each model will attempt each task 3 times.
        - Grade Y (Yes): If all 3 attempts are the same (with the exception of extra spaces or parentheses) and they are all correct, it is considered consistent and accurate.
        - Grade D (Different ways same purpose): If the attempts differ but yield the same correct result when applied, it is considered different ways same purpose.
        - Grade C (Critical): If the attempts differ and yield the same correct result when applied, but they only yield the same result due to specific conditions (e.g., columns names), it is considered critical.
        - Grade N (No): If the attempts differ and yield different results when applied, it is considered inconsistent and inaccurate.
    - Style: Evaluating if the formula is written in a concise and efficient manner.
        - Grade Y (Yes): The formula is the most concise and efficient way to achieve the desired result.
        - Grade N (No): The formula is not the most concise and efficient way to achieve the desired result.

## Test Sheets and Prompts

---
### Task E1: Sales Revenue Totals
![alt text](./assets/sheet_e1.png)
**Sheet:** `E1_Sales_Revenue`

**Prompt:**
`This is a quarterly sales revenue table: <cells>'E1_Sales_Revenue'!A1:F6</cells>. Columns B-E contain quarterly revenue for each product. Please calculate the annual total revenue for each product by summing all four quarters. Write results here: <target>'E1_Sales_Revenue'!F2:F6</target>. Also calculate the grand total of all products and quarters here: <target>'E1_Sales_Revenue'!F7</target>.`

**Expected Formulas:**
- F2:F6: `=SUM(B2:E2)`
- F7: `=SUM(F2:F6)`


---
### Task E2: Student Grade Average and Pass/Fail
![alt text](./assets/sheet_e2.png)
**Sheet:** `E2_Student_Grades`

**Prompt:**
`This is a student test scores table: <cells>'E2_Student_Grades'!A1:G7</cells>. Columns B-E contain test scores for each student. Please calculate each student's average score across all 4 tests in column F. Then, determine the pass/fail status in column G: if average >= 70, show "Pass", otherwise show "Fail". Write average here: <target>'E2_Student_Grades'!F2:F7</target>. Write status here: <target>'E2_Student_Grades'!G2:G7</target>.`

**Expected Formulas:**
- F2:F7: `=AVERAGE(B2:E2)`
- G2:G7: `=IF(F2>=70, "Pass", "Fail")`



---
### Task E3: Inventory Stock Value and Reorder Alert
![alt text](./assets/sheet_e3.png)
**Sheet:** `E3_Inventory_Check`

**Prompt:**
`This is an inventory management table: <cells>'E3_Inventory_Check'!A1:F8</cells>. Column B has current stock, column C has reorder level, column D has unit cost. Please calculate the stock value (current stock × unit cost) for each item. Then check if reorder is needed: if current stock <= reorder level, show "Yes", otherwise "No". Write stock value here: <target>'E3_Inventory_Check'!E2:E8</target>. Write reorder status here: <target>'E3_Inventory_Check'!F2:F8</target>. Also calculate total stock value here: <target>'E3_Inventory_Check'!E9</target>.`

**Expected Formulas:**
- E2:E8: `=B2*D2`
- F2:F8: `=IF(B2<=C2, "Yes", "No")`
- E9: `=SUM(E2:E8)`


---
### Task M1: Employee Bonus Calculation with Lookup
![alt text](./assets/sheet_m1.png)
**Sheet:** `M1_Employee_Bonus`

**Prompt:**
`This is an employee data table: <cells>'M1_Employee_Bonus'!A1:F9</cells>. There is also a department bonus rate lookup table: <cells>'M1_Employee_Bonus'!H1:I5</cells>. Please look up the bonus rate for each employee based on their department (column B) using the lookup table. Then calculate the bonus amount (base salary × bonus rate). Write the bonus rate here: <target>'M1_Employee_Bonus'!E2:E9</target>. Write the bonus amount here: <target>'M1_Employee_Bonus'!F2:F9</target>.`

**Expected Formulas:**
- E2:E9: `=VLOOKUP(B2, $H$2:$I$5, 2, FALSE)`
- F2:F9: `=C2*E2`



---
### Task M2: Order Analysis with SUMIFS and COUNTIFS
![alt text](./assets/sheet_m2.png)
**Sheet:** `M2_Order_Analysis`

**Prompt:**
`This is an order transactions table: <cells>'M2_Order_Analysis'!A1:G11</cells>. Please calculate the following summary statistics: (1) Total revenue from orders where Customer is "Acme Corp" AND Product is "Product A" (revenue = quantity × unit price). (2) Count of orders where Region is "North" AND Status is "Completed". (3) Average quantity for all "Product B" orders. Write results here: <target>'M2_Order_Analysis'!K2</target> for revenue, <target>'M2_Order_Analysis'!K3</target> for count, <target>'M2_Order_Analysis'!K4</target> for average.`

**Expected Formulas:**
- K2: `=SUMPRODUCT((B2:B11="Acme Corp")*(C2:C11="Product A")*E2:E11*F2:F11)`
- K3: `=COUNTIFS(D2:D11, "North", G2:G11, "Completed")`
- K4: `=AVERAGEIF(C2:C11, "Product B", E2:E11)`



---
### Task M3: Project Duration and Budget Status
![alt text](./assets/sheet_m3.png)
**Sheet:** `M3_Date_Calculations`

**Prompt:**
`This is a project tracking table: <cells>'M3_Date_Calculations'!A1:H7</cells>. Column B has start date, column C has end date, column D has budget, column E has actual cost. Please calculate: (1) Project duration in days (end date - start date). (2) Cost per day (actual cost / duration). (3) Budget status: "Under Budget" if actual < budget, "Over Budget" if actual > budget, "On Budget" if equal. Write duration here: <target>'M3_Date_Calculations'!F2:F7</target>. Write cost per day here: <target>'M3_Date_Calculations'!G2:G7</target>. Write budget status here: <target>'M3_Date_Calculations'!H2:H7</target>.`

**Expected Formulas:**
- F2:F7: `=C2-B2`
- G2:G7: `=E2/F2`
- H2:H7: `=IF(E2<D2, "Under Budget", IF(E2>D2, "Over Budget", "On Budget"))`


---
### Task H1: Financial Metrics with Running Totals
![alt text](./assets/sheet_h1.png)
**Sheet:** `H1_Financial_Analysis`

**Prompt:**
`This is a monthly financial data table: <cells>'H1_Financial_Analysis'!A1:I13</cells>. Column B is Revenue, C is COGS (Cost of Goods Sold), D is Operating Expenses. Please calculate: (1) Gross Profit = Revenue - COGS. (2) Net Profit = Gross Profit - OpEx. (3) Gross Profit Margin % = (Gross Profit / Revenue) × 100. (4) Month-over-Month Revenue Growth % = ((Current Revenue - Previous Revenue) / Previous Revenue) × 100. For January, show "N/A" since there's no previous month. (5) Cumulative Revenue = running total of revenue from Jan to current month. Write Gross Profit here: <target>'H1_Financial_Analysis'!E2:E13</target>. Write Net Profit here: <target>'H1_Financial_Analysis'!F2:F13</target>. Write GP Margin here: <target>'H1_Financial_Analysis'!G2:G13</target>. Write MoM Growth here: <target>'H1_Financial_Analysis'!H2:H13</target>. Write Cumulative Revenue here: <target>'H1_Financial_Analysis'!I2:I13</target>.`

**Expected Formulas:**
- E2:E13: `=B2-C2`
- F2:F13: `=E2-D2`
- G2:G13: `=(E2/B2)*100`
- H2: `="N/A"`
- H3:H13: `=((B3-B2)/B2)*100`
- I2:I13: `=SUM($B$2:B2)`



---
### Task H2: Tiered Commission with Lookup
![alt text](./assets/sheet_h2.png)
**Sheet:** `H2_Commission_Tiers`

**Prompt:**
`This is a sales performance table: <cells>'H2_Commission_Tiers'!A1:I9</cells>. Columns C-F contain quarterly sales. There is also a commission tier table: <cells>'H2_Commission_Tiers'!K2:M6</cells> showing rate bands based on annual sales. Please calculate: (1) Annual Sales = sum of all 4 quarters. (2) Commission Rate by looking up the annual sales in the tier table (use the rate where annual sales falls between min and max). (3) Commission Earned = Annual Sales × Commission Rate. Write Annual Sales here: <target>'H2_Commission_Tiers'!G2:G9</target>. Write Commission Rate here: <target>'H2_Commission_Tiers'!H2:H9</target>. Write Commission Earned here: <target>'H2_Commission_Tiers'!I2:I9</target>.`

**Expected Formulas:**
- G2:G9: `=SUM(C2:F2)`
- H2:H9: `=VLOOKUP(G2, $K$3:$M$6, 3, TRUE)`
- I2:I9: `=G2*H2`



---
### Task H3: Weighted Scoring with Ranking
![alt text](./assets/sheet_h3.png)
**Sheet:** `H3_Weighted_Scoring`

**Prompt:**
`This is a candidate evaluation table: <cells>'H3_Weighted_Scoring'!A1:H9</cells>. Columns B-E contain scores in different categories with weights shown in the header (Technical 40%, Experience 25%, Culture Fit 20%, Communication 15%). Decision criteria is shown in <cells>'H3_Weighted_Scoring'!J1:J4</cells>. Please calculate: (1) Weighted Score = (Technical×0.4) + (Experience×0.25) + (Culture Fit×0.2) + (Communication×0.15). (2) Rank = rank of each candidate based on weighted score (1 = highest). (3) Decision based on weighted score: >= 85 show "Hire", 75-84 show "Second Interview", < 75 show "Reject". Write Weighted Score here: <target>'H3_Weighted_Scoring'!F2:F9</target>. Write Rank here: <target>'H3_Weighted_Scoring'!G2:G9</target>. Write Decision here: <target>'H3_Weighted_Scoring'!H2:H9</target>.`

**Expected Formulas:**
- F2:F9: `=(B2*0.4)+(C2*0.25)+(D2*0.2)+(E2*0.15)`
- G2:G9: `=RANK(F2, $F$2:$F$9, 0)`
- H2:H9: `=IF(F2>=85, "Hire", IF(F2>=75, "Second Interview", "Reject"))`

## Summary of Results
### Consistency
![alt text](./assets/consistency_result.png)

### Style
- Unless mentioned in the sections below, all models produced concise and efficient formulas.
- Extra error handling (e.g., `IFERROR`) is not considered unnecessary in this evaluation.
- Percentage variations (e.g., 0.05 vs 5 (%)) and rounding operations are not considered unnecessary.
#### Sheet E1
- GPT-5 Nano and Claude Sonnet returned formulas for multiple cells instead of a single formula for the entire range, leading to redundancy.
```
"claude-sonnet-4-5": {
    "first": {
      "F2": "=SUM(B2:E2)",
      "F3": "=SUM(B3:E3)",
      "F4": "=SUM(B4:E4)",
      "F5": "=SUM(B5:E5)",
      "F6": "=SUM(B6:E6)",
      "F7": "=SUM(B2:E6)"
    },
    "second": {
      "F2:F6": "=SUM(B2:E2)",
      "F7": "=SUM(F2:F6)"
    }
}
```

#### Sheet E2 and E3
- Do not consider GPT-5 Nano due to incorrect formulas.
- All other models produced concise formulas.

#### Sheet M1

- GPT-5 Nano used an extra row in the lookup table, which is wrong. In this case, it did not affect the result due to the specific data, but it might lead to errors in other cases.

```
"gpt-5-nano": {
    "first": {
      "E2:E9": "=VLOOKUP(B2, $H$2:$I$5, 2, FALSE)",
      "F2:F9": "=C2 * E2"
    },
    "second": {
      "E2:E9": "=VLOOKUP(B2, $H$1:$I$5, 2, FALSE)",
      "F2:F9": "=C2*E2"
    }
}
```

#### Sheet M2
- Do not consider Gemini 2.5 Flash Lite, GPT-5 Nano, Claude Sonnet 4.5, and Claude Haiku 4.5 due to incorrect formulas.
- Gemini 2.5 Pro used extra "--", which does not affect the result, hence unnecessary.
```
"gemini-2.5-pro": {
    "first": {
      "K2": "=SUMPRODUCT(--(B2:B11=\"Acme Corp\"),--(C2:C11=\"Product A\"),E2:E11,F2:F11)",
      "K3": "=COUNTIFS(D2:D11,\"North\",G2:G11,\"Completed\")",
      "K4": "=AVERAGEIF(C2:C11,\"Product B\",E2:E11)"
    }
}
```

#### Sheet M3
- Do not consider GPT-5 Mini due to incorrect formulas.
- GPT-5 Nano used range operations, which are unnecessary due to automatic range expansion in Google Sheets.
```
"gpt-5-nano": {
    "first": {
      "F2:F7": "=C2:C7-B2:B7",
      "G2:G7": "=IF((C2:C7-B2:B7)>0, E2:E7/(C2:C7-B2:B7), \"\")",
      "H2:H7": "=IF(E2:E7<D2:D7, \\\"Under Budget\\\", IF(E2:E7>D2:D7, \\\"Over Budget\\\", \\\"On Budget\\\"))"
    },
    "second": {
      "F2:F7": "=C2:C7 - B2:B7",
      "G2:G7": "=IF(F2:F7>0, E2:E7 / F2:F7, \"\")",
      "H2:H7": "=IF(E2:E7 < D2:D7, \"Under Budget\", IF(E2:E7 > D2:D7, \"Over Budget\", \"On Budget\"))"
    },
    "third": {
      "F2:F7": "=C2-B2",
      "G2:G7": "=E2/F2",
      "H2:H7": "=IF(E2<D2,\"Under Budget\",IF(E2>D2,\"Over Budget\",\"On Budget\"))"
    }
}
```

#### Sheet H1
- Do not consider GPT-5 and Claude Sonnet 4.5 due to incorrect formulas.
- GPT-5 Mini hardcoded the row numbers instead of using relative references.
```
"gpt-5-mini": {
    "first": {
      "E2:E13": "=B2-C2",
      "F2:F13": "=E2-D2",
      "G2:G13": "=IF(B2=0,\"\",E2/B2*100)",
      "H2:H13": "=IF(ROW()=2,\"N/A\",IF(NOT(ISNUMBER(B1)),\"N/A\",(B2-B1)/B1*100))",
      "I2:I13": "=SUM($B$2:B2)"
    },
    "second": {
      "E2:E13": "=B2-C2",
      "F2:F13": "=B2-C2-D2",
      "G2:G13": "=IF(B2=0,\"\",(E2/B2)*100)",
      "H2:H13": "=IF(ROW()=2,\"N/A\",(B2-B1)/B1*100)",
      "I2:I13": "=SUM($B$2:B2)"
    },
    "third": {
      "E2:E13": "=B2-C2",
      "F2:F13": "=E2-D2",
      "G2:G13": "=IF(B2=0,\"\",E2/B2*100)",
      "H2": "N/A",
      "H3:H13": "=(B3-B2)/B2*100",
      "I2:I13": "=SUM($B$2:B2)"
    }
}
```

- GPT-5 Nano used overly complex logic in one attempt. It also hardcoded the row numbers.
```
"gpt-5-nano": {
    "first": {
      "E2:E13": "=B2 - C2",
      "F2:F13": "=B2 - C2 - D2",
      "G2:G13": "=(E2 / B2) * 100",
      "H2:H13": "=IF(ROW()=2, \"N/A\", (B2 - B1)/B1 * 100)",
      "I2:I13": "=IF(ROW()=2, B2, I1 + B2)"
    },
    "second": {
      "E2:E13": "=B2:B13 - C2:C13",
      "F2:F13": "=(B2:B13 - C2:C13) - D2:D13",
      "G2:G13": "=(B2:B13 - C2:C13) / B2:B13 * 100",
      "H2:H13": "=IF(ROW(B2:B13)=ROW(B2), \"N/A\", (B2:B13 - OFFSET(B2:B13, -1, 0)) / OFFSET(B2:B13, -1, 0) * 100)",
      "I2:I13": "=SCAN(0, B2:B13, LAMBDA(acc, val, acc + val))"
    }
}
```
#### Sheet H2
- Do not consider Gemini 2.5 Flash Lite, GPT-5 Mini, Claude Opus 4.5, and Claude Sonnet 4.5 due to incorrect formulas.

- Gemini 2.5 Flash used an extra row in the lookup table, which is wrong. In this case, it did not affect the result due to the specific data, but it might lead to errors in other cases.
```
"gemini-2.5-flash": {
    "second": {
      "G2:G9": "=SUM(C2:F2)",
      "H2:H9": "=VLOOKUP(G2, $K$2:$M$6, 3, TRUE)",
      "I2:I9": "=G2*H2"
    },
    "third": {
      "G2:G9": "=SUM(C2:F2)",
      "H2:H9": "=VLOOKUP(G2,$K$3:$M$6,3,TRUE)",
      "I2:I9": "=G2*H2"
    }
},
```

- GPT-5 Nano used an extra row in the lookup table, which is wrong. In this case, it did not affect the result due to the specific data, but it might lead to errors in other cases. It also returned formulas for multiple cells instead of a single formula for the entire range, leading to redundancy.
```
"gpt-5-nano": {
    "first": {
      "G2:G9": "=SUM(C2:F2)",
      "H2:H9": "=LOOKUP(G2, $K$2:$K$6, $M$2:$M$6)",
      "I2:I9": "=G2*H2"
    },
    "third": {
      "G2": "=SUM(C2:F2)",
      "G3": "=SUM(C3:F3)",
      "G4": "=SUM(C4:F4)",
      "G5": "=SUM(C5:F5)",
      "G6": "=SUM(C6:F6)",
      "G7": "=SUM(C7:F7)",
      "G8": "=SUM(C8:F8)",
      "G9": "=SUM(C9:F9)",
      "H2": "=LOOKUP(G2, $K$3:$K$6, $M$3:$M$6)",
      "H3": "=LOOKUP(G3, $K$3:$K$6, $M$3:$M$6)",
      "H4": "=LOOKUP(G4, $K$3:$K$6, $M$3:$M$6)",
      "H5": "=LOOKUP(G5, $K$3:$K$6, $M$3:$M$6)",
      "H6": "=LOOKUP(G6, $K$3:$K$6, $M$3:$M$6)",
      "H7": "=LOOKUP(G7, $K$3:$K$6, $M$3:$M$6)",
      "H8": "=LOOKUP(G8, $K$3:$K$6, $M$3:$M$6)",
      "H9": "=LOOKUP(G9, $K$3:$K$6, $M$3:$M$6)",
      "I2": "=G2*H2",
      "I3": "=G3*H3",
      "I4": "=G4*H4",
      "I5": "=G5*H5",
      "I6": "=G6*H6",
      "I7": "=G7*H7",
      "I8": "=G8*H8",
      "I9": "=G9*H9"
    }
},
```

- Claude Haiku 4.5 did not use `VLOOKUP` as expected. Instead, it used nested `IF` statements with hardcoded values (instead of reference to cells) or complex `INDEX/MATCH` formulas.
```
"claude-haiku-4-5": {
    "first": {
      "H2:H9": "=IF(G2<=200000,0.05,IF(G2<=400000,0.08,IF(G2<=600000,0.12,0.15)))"
    },
    "third": {
      "H2:H9": "=IFERROR(INDEX($M$2:$M$6,MATCH(1,(G2>=$K$2:$K$6)*(G2<=$L$2:$L$6),0)),0.05)"
    }
}
```

#### Sheet H3
- Do not consider Claude Sonnet 4.5 due to incorrect formulas.
- GPT-5 Nano returned formulas for multiple cells instead of a single formula for the entire range, leading to redundancy.
```
"gpt-5-nano": {
    "first": {
      "F2:F9": "=0.4*B2+0.25*C2+0.2*D2+0.15*E2",
      "G2:G9": "=RANK(F2,$F$2:$F$9,0)",
      "H2:H9": "=IF(F2>=85,\"Hire\",IF(F2>=75,\"Second Interview\",\"Reject\"))"
    },
    "second": {
      "F2:F9": "=B2*0.4 + C2*0.25 + D2*0.2 + E2*0.15",
      "G2:G9": "=RANK.EQ(F2, $F$2:$F$9, 0)",
      "H2:H9": "=IF(F2>=85, \"Hire\", IF(F2>=75, \"Second Interview\", \"Reject\"))"
    },
    "third": {
      "F2": "=0.4*B2+0.25*C2+0.2*D2+0.15*E2",
      "F3": "=0.4*B3+0.25*C3+0.2*D3+0.15*E3",
      "F4": "=0.4*B4+0.25*C4+0.2*D4+0.15*E4",
      "F5": "=0.4*B5+0.25*C5+0.2*D5+0.15*E5",
      "F6": "=0.4*B6+0.25*C6+0.2*D6+0.15*E6",
      "F7": "=0.4*B7+0.25*C7+0.2*D7+0.15*E7",
      "F8": "=0.4*B8+0.25*C8+0.2*D8+0.15*E8",
      "F9": "=0.4*B9+0.25*C9+0.2*D9+0.15*E9",
      "G2": "=RANK.EQ(F2,$F$2:$F$9,0)",
      "G3": "=RANK.EQ(F3,$F$2:$F$9,0)",
      "G4": "=RANK.EQ(F4,$F$2:$F$9,0)",
      "G5": "=RANK.EQ(F5,$F$2:$F$9,0)",
      "G6": "=RANK.EQ(F6,$F$2:$F$9,0)",
      "G7": "=RANK.EQ(F7,$F$2:$F$9,0)",
      "G8": "=RANK.EQ(F8,$F$2:$F$9,0)",
      "G9": "=RANK.EQ(F9,$F$2:$F$9,0)",
      "H2": "=IF(F2>=85,\"Hire\",IF(F2>=75,\"Second Interview\",\"Reject\"))",
      "H3": "=IF(F3>=85,\"Hire\",IF(F3>=75,\"Second Interview\",\"Reject\"))",
      "H4": "=IF(F4>=85,\"Hire\",IF(F4>=75,\"Second Interview\",\"Reject\"))",
      "H5": "=IF(F5>=85,\"Hire\",IF(F5>=75,\"Second Interview\",\"Reject\"))",
      "H6": "=IF(F6>=85,\"Hire\",IF(F6>=75,\"Second Interview\",\"Reject\"))",
      "H7": "=IF(F7>=85,\"Hire\",IF(F7>=75,\"Second Interview\",\"Reject\"))",
      "H8": "=IF(F8>=85,\"Hire\",IF(F8>=75,\"Second Interview\",\"Reject\"))",
      "H9": "=IF(F9>=85,\"Hire\",IF(F9>=75,\"Second Interview\",\"Reject\"))"
    }
},
```

#### Final result of Style criteria
![alt text](./assets/style_result.png)

### Some common errors:
- Gemini 2.5 Pro: Extra double negatives (e.g., `--(condition)`).
- GPT-5 Nano: Extra escape characters (e.g., `\\\"` instead of `\"`).
- Claude Sonnet 4.5: JSON parsing errors.

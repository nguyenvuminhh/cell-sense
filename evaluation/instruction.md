# LLM Formula Generation Evaluation Tasks

## Overview
- **3 Difficulty Levels**: Easy, Medium, Hard
- **3 Sheets per Level**: 9 sheets total
- **1 Task per Sheet**: Each with clear data range and target cells

Yellow highlighted cells in the spreadsheet indicate target output cells.

---

# EASY LEVEL

## Task E1: Sales Revenue Totals
**Sheet:** `E1_Sales_Revenue`

**Prompt:**
```
This is a quarterly sales revenue table: <cells>'E1_Sales_Revenue'!A1:F6</cells>. Column B-E contains quarterly revenue for each product. Please calculate the annual total revenue for each product by summing all four quarters. Write results here: <target>'E1_Sales_Revenue'!F2:F6</target>. Also calculate the grand total of all products and quarters here: <target>'E1_Sales_Revenue'!F7</target>.
```

**Expected Formulas:**
- F2:F6: `=SUM(B2:E2)`
- F7: `=SUM(F2:F6)`

---

## Task E2: Student Grade Average and Pass/Fail
**Sheet:** `E2_Student_Grades`

**Prompt:**
```
This is a student test scores table: <cells>'E2_Student_Grades'!A1:G7</cells>. Columns B-E contain test scores for each student. Please calculate each student's average score across all 4 tests in column F. Then, determine the pass/fail status in column G: if average >= 70, show "Pass", otherwise show "Fail". Write average here: <target>'E2_Student_Grades'!F2:F7</target>. Write status here: <target>'E2_Student_Grades'!G2:G7</target>.
```

**Expected Formulas:**
- F2:F7: `=AVERAGE(B2:E2)`
- G2:G7: `=IF(F2>=70, "Pass", "Fail")`

---

## Task E3: Inventory Stock Value and Reorder Alert
**Sheet:** `E3_Inventory_Check`

**Prompt:**
```
This is an inventory management table: <cells>'E3_Inventory_Check'!A1:F8</cells>. Column B has current stock, column C has reorder level, column D has unit cost. Please calculate the stock value (current stock × unit cost) for each item. Then check if reorder is needed: if current stock <= reorder level, show "Yes", otherwise "No". Write stock value here: <target>'E3_Inventory_Check'!E2:E8</target>. Write reorder status here: <target>'E3_Inventory_Check'!F2:F8</target>. Also calculate total stock value here: <target>'E3_Inventory_Check'!E9</target>.
```

**Expected Formulas:**
- E2:E8: `=B2*D2`
- F2:F8: `=IF(B2<=C2, "Yes", "No")`
- E9: `=SUM(E2:E8)`

---

# MEDIUM LEVEL

## Task M1: Employee Bonus Calculation with Lookup
**Sheet:** `M1_Employee_Bonus`

**Prompt:**
```
This is an employee data table: <cells>'M1_Employee_Bonus'!A1:F9</cells>. There is also a department bonus rate lookup table: <cells>'M1_Employee_Bonus'!H1:I5</cells>. Please look up the bonus rate for each employee based on their department (column B) using the lookup table. Then calculate the bonus amount (base salary × bonus rate). Write the bonus rate here: <target>'M1_Employee_Bonus'!E2:E9</target>. Write the bonus amount here: <target>'M1_Employee_Bonus'!F2:F9</target>.
```

**Expected Formulas:**
- E2:E9: `=VLOOKUP(B2, $H$2:$I$5, 2, FALSE)`
- F2:F9: `=C2*E2`

---

## Task M2: Order Analysis with SUMIFS and COUNTIFS
**Sheet:** `M2_Order_Analysis`

**Prompt:**
```
This is an order transactions table: <cells>'M2_Order_Analysis'!A1:G11</cells>. Please calculate the following summary statistics: (1) Total revenue from orders where Customer is "Acme Corp" AND Product is "Product A" (revenue = quantity × unit price). (2) Count of orders where Region is "North" AND Status is "Completed". (3) Average quantity for all "Product B" orders. Write results here: <target>'M2_Order_Analysis'!K2</target> for revenue, <target>'M2_Order_Analysis'!K3</target> for count, <target>'M2_Order_Analysis'!K4</target> for average.
```

**Expected Formulas:**
- K2: `=SUMPRODUCT((B2:B11="Acme Corp")*(C2:C11="Product A")*E2:E11*F2:F11)`
- K3: `=COUNTIFS(D2:D11, "North", G2:G11, "Completed")`
- K4: `=AVERAGEIF(C2:C11, "Product B", E2:E11)`

---

## Task M3: Project Duration and Budget Status
**Sheet:** `M3_Date_Calculations`

**Prompt:**
```
This is a project tracking table: <cells>'M3_Date_Calculations'!A1:H7</cells>. Column B has start date, column C has end date, column D has budget, column E has actual cost. Please calculate: (1) Project duration in days (end date - start date). (2) Cost per day (actual cost / duration). (3) Budget status: "Under Budget" if actual < budget, "Over Budget" if actual > budget, "On Budget" if equal. Write duration here: <target>'M3_Date_Calculations'!F2:F7</target>. Write cost per day here: <target>'M3_Date_Calculations'!G2:G7</target>. Write budget status here: <target>'M3_Date_Calculations'!H2:H7</target>.
```

**Expected Formulas:**
- F2:F7: `=C2-B2`
- G2:G7: `=E2/F2`
- H2:H7: `=IF(E2<D2, "Under Budget", IF(E2>D2, "Over Budget", "On Budget"))`

---

# HARD LEVEL

## Task H1: Financial Metrics with Running Totals
**Sheet:** `H1_Financial_Analysis`

**Prompt:**
```
This is a monthly financial data table: <cells>'H1_Financial_Analysis'!A1:I13</cells>. Column B is Revenue, C is COGS (Cost of Goods Sold), D is Operating Expenses. Please calculate: (1) Gross Profit = Revenue - COGS. (2) Net Profit = Gross Profit - OpEx. (3) Gross Profit Margin % = (Gross Profit / Revenue) × 100. (4) Month-over-Month Revenue Growth % = ((Current Revenue - Previous Revenue) / Previous Revenue) × 100. For January, show "N/A" since there's no previous month. (5) Cumulative Revenue = running total of revenue from Jan to current month. Write Gross Profit here: <target>'H1_Financial_Analysis'!E2:E13</target>. Write Net Profit here: <target>'H1_Financial_Analysis'!F2:F13</target>. Write GP Margin here: <target>'H1_Financial_Analysis'!G2:G13</target>. Write MoM Growth here: <target>'H1_Financial_Analysis'!H2:H13</target>. Write Cumulative Revenue here: <target>'H1_Financial_Analysis'!I2:I13</target>.
```

**Expected Formulas:**
- E2:E13: `=B2-C2`
- F2:F13: `=E2-D2`
- G2:G13: `=(E2/B2)*100`
- H2: `="N/A"`
- H3:H13: `=((B3-B2)/B2)*100`
- I2:I13: `=SUM($B$2:B2)`

---

## Task H2: Tiered Commission with Lookup
**Sheet:** `H2_Commission_Tiers`

**Prompt:**
```
This is a sales performance table: <cells>'H2_Commission_Tiers'!A1:I9</cells>. Columns C-F contain quarterly sales. There is also a commission tier table: <cells>'H2_Commission_Tiers'!K2:M6</cells> showing rate bands based on annual sales. Please calculate: (1) Annual Sales = sum of all 4 quarters. (2) Commission Rate by looking up the annual sales in the tier table (use the rate where annual sales falls between min and max). (3) Commission Earned = Annual Sales × Commission Rate. Write Annual Sales here: <target>'H2_Commission_Tiers'!G2:G9</target>. Write Commission Rate here: <target>'H2_Commission_Tiers'!H2:H9</target>. Write Commission Earned here: <target>'H2_Commission_Tiers'!I2:I9</target>.
```

**Expected Formulas:**
- G2:G9: `=SUM(C2:F2)`
- H2:H9: `=VLOOKUP(G2, $K$3:$M$6, 3, TRUE)`
- I2:I9: `=G2*H2`

---

## Task H3: Weighted Scoring with Ranking
**Sheet:** `H3_Weighted_Scoring`

**Prompt:**
```
This is a candidate evaluation table: <cells>'H3_Weighted_Scoring'!A1:H9</cells>. Columns B-E contain scores in different categories with weights shown in the header (Technical 40%, Experience 25%, Culture Fit 20%, Communication 15%). Decision criteria is shown in <cells>'H3_Weighted_Scoring'!J1:J4</cells>. Please calculate: (1) Weighted Score = (Technical×0.4) + (Experience×0.25) + (Culture Fit×0.2) + (Communication×0.15). (2) Rank = rank of each candidate based on weighted score (1 = highest). (3) Decision based on weighted score: >= 85 show "Hire", 75-84 show "Second Interview", < 75 show "Reject". Write Weighted Score here: <target>'H3_Weighted_Scoring'!F2:F9</target>. Write Rank here: <target>'H3_Weighted_Scoring'!G2:G9</target>. Write Decision here: <target>'H3_Weighted_Scoring'!H2:H9</target>.
```

**Expected Formulas:**
- F2:F9: `=(B2*0.4)+(C2*0.25)+(D2*0.2)+(E2*0.15)`
- G2:G9: `=RANK(F2, $F$2:$F$9, 0)`
- H2:H9: `=IF(F2>=85, "Hire", IF(F2>=75, "Second Interview", "Reject"))`

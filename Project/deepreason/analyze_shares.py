from parser import extract_text_from_pdf
from tree import split_text_into_sections

pdf_path = r"D:\ClgDocs\3-2\AIAC\Project\PageIndex\deepreason\e61754b8-e28c-4a21-8d51-7d412b383f46.pdf"

print('Analyzing share transactions...')
text = extract_text_from_pdf(pdf_path)
sections = split_text_into_sections(text)

# Find the table section
table_section = None
for title, content in sections.items():
    if 'Table I' in title:
        table_section = content
        break

if table_section:
    print('Table I content:')
    print(table_section)

    # Parse the transactions - the table is all in one line
    # Split by "Common Stock" to get individual transactions
    transactions = []
    common_stock_parts = table_section.split('Common Stock')

    for part in common_stock_parts[1:]:  # Skip the first part (header)
        part = part.strip()
        if part:
            # Parse each transaction
            parts = part.split()
            if len(parts) >= 4:
                try:
                    # Skip row numbers in parentheses
                    i = 0
                    while i < len(parts) and parts[i].startswith('('):
                        i += 1

                    if i+3 < len(parts):
                        date = parts[i]
                        code = parts[i+1]
                        amount_str = parts[i+2].replace(',', '')
                        trans_type = parts[i+3]

                        if trans_type in ['A', 'D'] and amount_str.isdigit():
                            amount = int(amount_str)
                            transactions.append({
                                'date': date,
                                'code': code,
                                'amount': amount,
                                'type': 'Acquired' if trans_type == 'A' else 'Disposed'
                            })
                except (ValueError, IndexError) as e:
                    print(f"Error parsing part: {part} - {e}")
                    pass

    print(f'\nParsed {len(transactions)} transactions:')
    total_acquired = 0
    total_disposed = 0

    if transactions:
        for t in transactions:
            print(f'{t["date"]}: {t["type"]} {t["amount"]:,} shares (Code: {t["code"]})')
            if t['type'] == 'Acquired':
                total_acquired += t['amount']
            else:
                total_disposed += t['amount']
    else:
        print("No transactions found - let's debug:")
        # Debug: print all lines containing Common Stock
        for line in lines:
            if 'Common Stock' in line:
                print(f"Found line: {line}")
                parts = line.split()
                print(f"Parts: {parts}")

    net_change = total_acquired - total_disposed
    print(f'\nSUMMARY:')
    print(f'Total Acquired: {total_acquired:,} shares')
    print(f'Total Disposed: {total_disposed:,} shares')
    print(f'Net Change: {net_change:,} shares')
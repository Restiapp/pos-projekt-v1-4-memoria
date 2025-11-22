#!/usr/bin/env python3
"""
Resolve merge conflicts by keeping the Sprint 0 side (incoming/theirs)
This removes HEAD blocks and keeps the Sprint 0 modernization changes.
"""

import re
import sys
from pathlib import Path

def resolve_conflicts_in_file(filepath):
    """Resolve conflicts in a single file by keeping incoming (Sprint 0) version"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False

    original_content = content

    # Pattern to match conflict markers
    # <<<<<<< HEAD
    # ... (old code - remove this)
    # =======
    # ... (new Sprint 0 code - keep this)
    # >>>>>>> origin/...

    # Match and keep only the incoming (Sprint 0) side
    pattern = r'<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> origin/.*?\n'

    def keep_incoming(match):
        incoming_version = match.group(1)
        return incoming_version + '\n'

    # Resolve all conflicts
    resolved_content = re.sub(pattern, keep_incoming, content, flags=re.DOTALL)

    if resolved_content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resolved_content)
            print(f"Resolved {filepath}")
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return False
    else:
        print(f"No conflicts in {filepath}")
        return False

def main():
    # List of files with conflicts
    conflict_files = [
        "frontend/src/App.tsx",
        "frontend/src/components/admin/AssetEditor.tsx",
        "frontend/src/components/admin/AssetGroupEditor.tsx",
        "frontend/src/components/admin/AssetGroupList.tsx",
        "frontend/src/components/admin/AssetList.tsx",
        "frontend/src/components/admin/AssetServiceEditor.tsx",
        "frontend/src/components/admin/AssetServiceList.tsx",
        "frontend/src/components/admin/CouponEditor.tsx",
        "frontend/src/components/admin/CouponList.tsx",
        "frontend/src/components/admin/CustomerEditor.tsx",
        "frontend/src/components/admin/CustomerList.tsx",
        "frontend/src/components/admin/EmployeeEditor.tsx",
        "frontend/src/components/admin/EmployeeList.tsx",
        "frontend/src/components/admin/GiftCardEditor.tsx",
        "frontend/src/components/admin/GiftCardList.tsx",
        "frontend/src/components/admin/ProductEditor.tsx",
        "frontend/src/components/admin/ProductList.tsx",
        "frontend/src/components/admin/RoleEditor.tsx",
        "frontend/src/components/admin/RoleList.tsx",
        "frontend/src/components/admin/TableEditor.tsx",
        "frontend/src/components/admin/VehicleEditor.tsx",
        "frontend/src/components/admin/VehicleList.tsx",
        "frontend/src/components/admin/VehicleMaintenanceList.tsx",
        "frontend/src/components/admin/VehicleRefuelingList.tsx",
        "frontend/src/components/finance/CashDrawer.tsx",
        "frontend/src/components/finance/DailyClosureEditor.tsx",
        "frontend/src/components/finance/DailyClosureList.tsx",
        "frontend/src/components/kds/KdsCard.tsx",
        "frontend/src/components/payment/PaymentModal.tsx",
        "frontend/src/components/table-map/TableMap.tsx",
        "frontend/src/pages/AdminPage.tsx",
        "frontend/src/pages/OperatorPage.tsx",
    ]

    resolved_count = 0
    for filepath in conflict_files:
        if resolve_conflicts_in_file(filepath):
            resolved_count += 1

    print(f"\nResolved conflicts in {resolved_count}/{len(conflict_files)} files")

    return 0 if resolved_count > 0 else 1

if __name__ == '__main__':
    sys.exit(main())

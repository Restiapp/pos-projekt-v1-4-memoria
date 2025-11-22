#!/usr/bin/env python3
"""
Automatically resolve merge conflicts by choosing the Sprint 0 side
(the side with Toast, ConfirmDialog, and modern UI patterns)
"""

import re
import sys
from pathlib import Path

def resolve_conflicts_in_file(filepath):
    """Resolve conflicts in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    original_content = content

    # Pattern to match conflict markers
    # <<<<<<< HEAD
    # ... (old code)
    # =======
    # ... (new code)
    # >>>>>>> origin/...

    pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/.*?\n'

    def choose_version(match):
        head_version = match.group(1)
        incoming_version = match.group(2)

        # Decision rules:
        # 1. Prefer Toast/ConfirmDialog over alert/confirm/notify
        # 2. Prefer useToast, showToast, showConfirm patterns
        # 3. Prefer imports from @/components/common/Toast or @/components/ui

        head_lower = head_version.lower()
        incoming_lower = incoming_version.lower()

        # Check for Sprint 0 patterns in incoming version
        sprint0_patterns = [
            'usetoast', 'showtoast', 'showconfirm',
            '@/components/common/toast', '@/components/ui',
            'confirmdi alog', 'modal'
        ]

        # Check for old patterns in HEAD version
        old_patterns = [
            'alert(', 'confirm(', 'notify.', 'window.alert', 'window.confirm'
        ]

        incoming_has_new = any(p in incoming_lower for p in sprint0_patterns)
        head_has_old = any(p in head_lower for p in old_patterns)

        # Prefer incoming if it has new patterns OR head has old patterns
        if incoming_has_new or head_has_old:
            return incoming_version + '\n'
        else:
            # Default: prefer incoming (Sprint 0 side)
            return incoming_version + '\n'

    # Resolve all conflicts
    resolved_content = re.sub(pattern, choose_version, content, flags=re.DOTALL)

    if resolved_content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resolved_content)
            print(f"✓ Resolved conflicts in {filepath}")
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    else:
        print(f"No conflicts found in {filepath}")
        return False

def main():
    # List of files with conflicts (from git grep output)
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

    print(f"\n✓ Resolved conflicts in {resolved_count}/{len(conflict_files)} files")

    return 0 if resolved_count > 0 else 1

if __name__ == '__main__':
    sys.exit(main())

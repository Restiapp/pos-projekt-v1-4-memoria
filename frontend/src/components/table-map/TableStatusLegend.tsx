/**
 * TableStatusLegend - Displays the color legend for table statuses
 */

import { getTableStatusColor, getTableStatusLabel, type TableStatus } from '@/utils/tableStatusColor';
import './TableStatusLegend.css';

const statuses: TableStatus[] = ['free', 'active', 'preparing', 'paying', 'reserved'];

export const TableStatusLegend = () => {
    return (
        <div className="table-status-legend">
            <h3 className="legend-title">Asztal státuszok</h3>
            <div className="legend-items">
                {statuses.map(status => {
                    const colors = getTableStatusColor(status);
                    const label = getTableStatusLabel(status);
                    return (
                        <div key={status} className="legend-item">
                            <div
                                className="legend-color"
                                style={{
                                    backgroundColor: colors.primary,
                                    borderColor: colors.border
                                }}
                            />
                            <span className="legend-label">{label}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

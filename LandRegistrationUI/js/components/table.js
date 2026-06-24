import { escapeHtml } from "../core/utils.js";

export function renderTable({ columns, rows, empty = "No records found." }) {
  if (!rows?.length) return `<div class="empty-state">${escapeHtml(empty)}</div>`;
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr>
                  ${columns
                    .map((column) => {
                      const value = column.render ? column.render(row) : escapeHtml(row[column.key]);
                      return `<td>${value ?? ""}</td>`;
                    })
                    .join("")}
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}
